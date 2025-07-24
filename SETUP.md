# 🚀 HR Assistant Setup Guide

## 📋 Prerequisites

1. **Google AI API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Google Sheets** - Create a new Google Sheet for storing candidate data
3. **Google Service Account** - For Google Sheets API access

## 🔧 Environment Variables

Create a `.env` file in your project root with these variables:

```bash
# Google AI API Key (Required)
GOOGLE_API_KEY=your_google_ai_api_key_here

# Google Sheets Configuration
GOOGLE_SHEET_ID=your_google_sheet_id_here

# Google Service Account Credentials
GOOGLE_PROJECT_ID=your_project_id
GOOGLE_PRIVATE_KEY_ID=your_private_key_id
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour_private_key_here\n-----END PRIVATE KEY-----\n"
GOOGLE_CLIENT_EMAIL=your_service_account_email@your_project.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=your_client_id

# Optional: OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here
```

## 📊 Google Sheets Setup

### Step 1: Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new blank spreadsheet
3. Copy the **Sheet ID** from the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`
4. Make sure the sheet is **accessible to anyone with the link** (for service account access)

### Step 2: Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable **Google Sheets API**:
   - Go to APIs & Services > Library
   - Search for "Google Sheets API"
   - Click Enable
4. Create Service Account:
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > "Service Account"
   - Fill in details and create
5. Generate Key:
   - Click on your service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key" > JSON
   - Download the JSON file

### Step 3: Extract Credentials

From the downloaded JSON file, extract these values for your `.env`:

```json
{
  "project_id": "your_project_id",
  "private_key_id": "your_private_key_id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your_service_account_email@your_project.iam.gserviceaccount.com",
  "client_id": "your_client_id"
}
```

### Step 4: Share Sheet with Service Account

1. Open your Google Sheet
2. Click "Share" button
3. Add your service account email (`client_email` from JSON)
4. Give it "Editor" permissions

## 🖥️ Local Development

1. **Clone repository**:

   ```bash
   git clone <your-repo-url>
   cd HR_LANGCHAIN
   ```

2. **Create virtual environment**:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file** with your credentials

5. **Run the app**:
   ```bash
   streamlit run streamlit_app.py
   ```

## 🌐 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add environment variables in **App Settings > Secrets**:
   ```
   GOOGLE_API_KEY = "your_key_here"
   GOOGLE_SHEET_ID = "your_sheet_id"
   GOOGLE_PROJECT_ID = "your_project_id"
   GOOGLE_PRIVATE_KEY_ID = "your_private_key_id"
   GOOGLE_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
   your_private_key_here
   -----END PRIVATE KEY-----"""
   GOOGLE_CLIENT_EMAIL = "your_service_account_email"
   GOOGLE_CLIENT_ID = "your_client_id"
   ```

### Other Platforms

- **Heroku**: Use config vars
- **Railway**: Use environment variables
- **Docker**: Use environment file or build args

## ✅ Features

- ✅ **Secure API Keys** - Hidden from users
- ✅ **Google Sheets Integration** - Auto-save candidate data
- ✅ **Multi-Agent Processing** - Resume parsing, job analysis, HR report
- ✅ **Beautiful UI** - Modern Streamlit interface
- ✅ **Export Options** - JSON download + Google Sheets
- ✅ **Candidate Tracking** - Summary statistics in sidebar

## 🆘 Troubleshooting

### Google Sheets Not Connected

- Check service account email is added to sheet with Editor access
- Verify all environment variables are set correctly
- Ensure Google Sheets API is enabled in your project

### API Key Issues

- Verify Google AI API key is valid
- Check API quota and usage limits
- Ensure proper environment variable format

### Deployment Issues

- Double-check environment variables in deployment platform
- Verify newlines in private key are properly escaped
- Check logs for specific error messages
