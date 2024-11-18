from dotenv import load_dotenv
import os
import requests
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import requests
import time
from groq import Groq

# Load environment variables
load_dotenv()

# Get API keys from environment variables
serp_api_key = os.getenv("SERP_API_KEY")
scraper_api_key = os.getenv("SCRAPER_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=groq_api_key)

# Set up Google Sheets authorization
def google_sheets_auth():
    scope = ["https://www.googleapis.com/auth/spreadsheets", 
             "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file("credentials.json", scopes=scope)
    client = gspread.authorize(credentials)
    return client

# Function to get Google Sheet data
def get_sheet_data(spreadsheet_id, sheet_name):
    client = google_sheets_auth()
    sheet = client.open_by_key(spreadsheet_id)
    worksheet = sheet.worksheet(sheet_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

# Function to perform a web search using SerpAPI
def perform_web_search(query, api_key):
    search_url = f"https://serpapi.com/search?q={query}&api_key={api_key}"
    response = requests.get(search_url)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error performing search: {response.status_code}")
        return None

# Function to handle rate limiting
def handle_rate_limiting():
    time.sleep(2)  # Sleep for 2 seconds to avoid hitting API rate limits

# Function to interact with OpenAI's API for information extraction
def extract_information_with_groq(results, prompt):
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{prompt}\n\nWeb Results:\n{results}"}
            ],
            temperature=0.5,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error using Groq API: {e}")
        return None


# Streamlit UI
st.title("AI Agent Dashboard")

# Option to upload a CSV or enter Google Sheets ID
option = st.radio("Choose an option", ("Upload CSV File", "Enter Google Sheets ID"))

# File upload section (only appears if "Upload CSV File" is selected)
if option == "Upload CSV File":
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("Uploaded CSV Data:")
        st.dataframe(df)

# Google Sheets section (only appears if "Enter Google Sheets ID" is selected)
if option == "Enter Google Sheets ID":
    spreadsheet_id = st.text_input("Enter Google Spreadsheet ID")
    sheet_name = st.text_input("Enter Sheet Name")

    sheet_data = None  # Initialize sheet_data

    if st.button("Load Google Sheet Data"):
        if spreadsheet_id and sheet_name:
            try:
                sheet_data = get_sheet_data(spreadsheet_id, sheet_name)
                st.write("Google Sheet Data:")
                st.dataframe(sheet_data)
            except Exception as e:
                st.error(f"Error loading Google Sheet: {e}")
        else:
            st.warning("Please enter both Spreadsheet ID and Sheet Name.")

# Dynamic Query Input
st.subheader("Enter Custom Query Template")

# Prompt input section
query_template = st.text_area("Enter your query template")

# Example placeholders
st.write("Example placeholders: {company}, {name}, {email}, etc.")

# Select main column for entity (e.g., {company})
if option == "Upload CSV File" and uploaded_file:
    column_name = st.selectbox("Select the column that represents the main entity", df.columns)
elif option == "Enter Google Sheets ID" and sheet_data is not None:
    column_name = st.selectbox("Select the column that represents the main entity", sheet_data.columns)
else:
    column_name = None

# Create a button to generate dynamic queries for each entity
if st.button("Generate Queries"):
    if (option == "Upload CSV File" and uploaded_file) or (option == "Enter Google Sheets ID" and sheet_data is not None):
        # Use the data to generate dynamic queries
        data = df if option == "Upload CSV File" else sheet_data
        
        # Get the unique entities in the selected column
        entities = data[column_name].dropna().unique()

        # Generate queries for each entity by replacing the placeholders
        generated_queries = []
        for entity in entities:
            query_with_entity = query_template.replace(f"{{{column_name}}}", str(entity))
            generated_queries.append(query_with_entity)

        # Display the generated queries
        st.write(f"Generated Queries for each entity in '{column_name}':")
        for query in generated_queries:
            st.write(query)
    else:
        st.warning("Please upload a file or load data from Google Sheets first.")

if st.button("Start Web Search"):
    if (option == "Upload CSV File" and uploaded_file) or (option == "Enter Google Sheets ID" and sheet_data is not None):
        data = df if option == "Upload CSV File" else sheet_data
        entities = data[column_name].dropna().unique()
        all_results = []

        for entity in entities:
            query_with_entity = query_template.replace(f"{{{column_name}}}", str(entity))
            st.write(f"Searching for: {query_with_entity}")
            results = perform_web_search(query_with_entity, serp_api_key)

            if results:
                search_results = [
                    {
                        "entity": entity,
                        "title": result.get("title"),
                        "snippet": result.get("snippet"),
                        "url": result.get("link")
                    }
                    for result in results.get('organic_results', [])
                ]
                all_results.extend(search_results)
            handle_rate_limiting()

        if all_results:
            results_df = pd.DataFrame(all_results)
            st.write("Search Results:")
            st.dataframe(results_df)

            prompt = st.text_area("Enter the extraction prompt", "Extract the email address of {company} from the following web results.")
            llm_results = []

            for entity in entities:
                relevant_results = [result for result in all_results if result['entity'] == entity]
                result_text = "\n".join([f"Title: {res['title']}\nSnippet: {res['snippet']}\nURL: {res['url']}" for res in relevant_results])
                st.write(f"Processing entity: {entity}")
                extracted_info = extract_information_with_groq(result_text, prompt.replace("{company}", entity))

                if extracted_info:
                    llm_results.append({"entity": entity, "extracted_info": extracted_info})
                else:
                    st.warning(f"Failed to extract information for entity: {entity}.")

            # Display the extracted information
            if llm_results:
                llm_results_df = pd.DataFrame(llm_results)
                st.write("Extracted Information:")
                st.dataframe(llm_results_df)
            
                # Download as CSV
                csv_data = llm_results_df.to_csv(index=False)
                st.download_button(
                    label="Download Results as CSV",
                    data=csv_data,
                    file_name="extracted_information.csv",
                    mime="text/csv"
                )
            
                # Option to update Google Sheet
                if option == "Enter Google Sheets ID":
                    if st.button("Update Google Sheet"):
                        if spreadsheet_id and sheet_name:
                            update_google_sheet(spreadsheet_id, sheet_name, llm_results_df)
                        else:
                            st.warning("Please provide both Spreadsheet ID and Sheet Name.")
            else:
                st.warning("No information could be extracted for any entity.")