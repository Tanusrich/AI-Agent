
# AI Agent Dashboard

This project is an AI-powered dashboard built using Streamlit, integrating Groq API, SerpAPI, and Google Sheets. The dashboard allows users to upload data, dynamically generate search queries, extract information from web results using Groq, and manage the results via CSV downloads or Google Sheets updates.

---

## Project Description

The AI Agent Dashboard enables seamless integration of multiple data processing and AI technologies. It offers the following features:
- **Data Handling**: Upload a CSV file or connect to a Google Sheet for data input.
- **Dynamic Query Generation**: Create search queries dynamically using placeholders.
- **Web Search Integration**: Fetch web results via SerpAPI.
- **AI-Powered Extraction**: Extract relevant information from web results using Groq's LLM capabilities.
- **Result Management**: View, download, and update extracted data in Google Sheets.

---

## Setup Instructions

### **1. Clone the Repository**
```bash
git clone <repository-url>
cd <repository-name>
```

### **2. Install Dependencies**
Ensure you have Python 3.8+ installed, then run:
```bash
pip install -r requirements.txt
```

### **3. Set Up Environment Variables**
Create a `.env` file in the project directory and add the following:
```plaintext
SERP_API_KEY=your_serpapi_key
SCRAPER_API_KEY=your_scraperapi_key
GROQ_API_KEY=your_groq_api_key
```

### **4. Add Google Sheets Credentials**
Download the `credentials.json` file from the Google Cloud Console and save it in the project directory.

### **5. Run the App**
Start the Streamlit app using:
```bash
streamlit run app.py
```
Open the URL displayed in the terminal (e.g., `http://localhost:8501`) to access the dashboard.

---

## Usage Guide

### **Step 1: Input Data**
- **Option 1**: Upload a CSV file containing the data.
- **Option 2**: Connect to a Google Sheet by providing the spreadsheet ID and sheet name.

### **Step 2: Configure Search Queries**
- Enter a query template using placeholders like `{company}` or `{name}`.
- Select the main column to dynamically generate search queries for each entity.

### **Step 3: Perform Web Search**
- Execute the web search via SerpAPI to retrieve relevant web results.

### **Step 4: Extract Information**
- Use Groq to process the web results and extract specific information based on the given prompt.

### **Step 5: Manage Results**
- View the extracted information in a table.
- **Download Results**: Export the extracted data as a CSV file.
- **Update Google Sheets**: Append the extracted data to the connected Google Sheet.

---

## API Keys and Environment Variables

### **Required API Keys**
1. **SerpAPI Key**: For performing web searches.
2. **Groq API Key**: For using Groq's AI-powered extraction services.
3. **Google Sheets Credentials**: JSON file for accessing Google Sheets.

### **Setting Environment Variables**
Add the API keys to a `.env` file in the following format:
```plaintext
SERP_API_KEY=your_serpapi_key
SCRAPER_API_KEY=your_scraperapi_key
GROQ_API_KEY=your_groq_api_key
```

---

## Optional Features

- **Google Sheets Integration**: Dynamically fetch and update data.
- **Error Handling**: Comprehensive error handling for web searches and API calls.
- **Dynamic Query Generator**: Customizable templates for creating search queries.

---

## Loom Video Walkthrough

