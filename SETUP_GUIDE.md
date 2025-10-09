# Natpudan AI Medical Assistant - Setup Guide

This guide will walk you through setting up the Natpudan AI Medical Assistant with both frontend and backend components.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Frontend Setup](#frontend-setup)
4. [Backend Setup](#backend-setup)
5. [Configuration](#configuration)
6. [Testing the Application](#testing-the-application)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### For Frontend Only (Demo Mode)
- A modern web browser (Chrome, Firefox, Safari, or Edge)

### For Full AI Features (Backend)
- Python 3.8 or higher
- pip (Python package manager)
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- A modern web browser

## Quick Start

### Demo Mode (No Backend Required)

1. Clone or download the repository
2. Open `index.html` in your web browser
3. The application will run in demo mode with pre-programmed knowledge

### Full AI Mode (With Backend)

Follow the complete setup instructions below to enable AI-powered features.

## Frontend Setup

### Option 1: Direct File Access
Simply open `index.html` in your web browser.

### Option 2: Local Development Server (Recommended)

Using Python:
```bash
python -m http.server 8080
```

Using Node.js:
```bash
npx http-server -p 8080
```

Then open `http://localhost:8080` in your browser.

## Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment (Recommended)

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI - Web framework
- Uvicorn - ASGI server
- PyMuPDF - PDF processing
- OpenAI - AI integration
- Python-dotenv - Environment management

### Step 4: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your OpenAI API key:
```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=http://localhost:8080,http://localhost:3000,http://127.0.0.1:8080
```

**Getting an OpenAI API Key:**
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste it into your `.env` file

### Step 5: Start the Backend Server

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
```

The API is now running at `http://localhost:8000`

### Step 6: Verify Backend is Running

Open your browser and visit:
- `http://localhost:8000/health` - Should return `{"status":"healthy"}`
- `http://localhost:8000/docs` - Interactive API documentation

## Configuration

### Frontend Configuration

Edit `config.js` in the root directory:

```javascript
const config = {
    // Backend API URL
    API_URL: 'http://localhost:8000',
    
    // Enable/disable backend features
    USE_BACKEND: true,  // Set to false for demo mode
    
    // Timeout for API requests (milliseconds)
    API_TIMEOUT: 30000,
};
```

**Settings:**
- `API_URL`: URL of your backend server
- `USE_BACKEND`: 
  - `true` - Use AI-powered backend (requires backend running)
  - `false` - Use demo mode with local data only
- `API_TIMEOUT`: Maximum time to wait for API responses

### Backend Configuration

Edit `backend/.env`:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4 for better results

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:8080,http://localhost:3000
```

## Testing the Application

### 1. Check Backend Status

1. Open the frontend in your browser
2. Look for the status banner at the top of the dashboard
3. You should see: "**AI Mode:** Backend connected. AI-powered features available."

If you see "Backend Offline", verify:
- Backend server is running
- `config.js` has correct `API_URL`
- No firewall blocking the connection

### 2. Test AI Features

#### Symptom Analysis
1. Navigate to "Symptom Checker"
2. Enter: "fever, cough, shortness of breath"
3. Age: 45
4. Gender: Male
5. Click "Analyze Symptoms"
6. You should receive AI-powered analysis

#### Drug Interactions
1. Navigate to "Drug Interactions"
2. Enter medications (one per line):
   ```
   Warfarin
   Aspirin
   Ibuprofen
   ```
3. Click "Check Interactions"
4. Review AI-generated interaction analysis

#### Medical Reference
1. Navigate to "Medical Reference"
2. Search for: "diabetes"
3. Click "Search"
4. Review comprehensive medical information

#### PDF Upload
1. Navigate to "Medical Reference"
2. Select a medical PDF file
3. Click "Upload PDF"
4. The PDF content will be added to the knowledge base
5. Future queries will use this information

### 3. Test Demo Mode

1. Edit `config.js` and set `USE_BACKEND: false`
2. Refresh the browser
3. All features will work with local demo data
4. No backend required

## Troubleshooting

### Backend Not Starting

**Error: "OPENAI_API_KEY not found"**
- Solution: Make sure you created `.env` file and added your API key

**Error: "Port 8000 already in use"**
- Solution: Change PORT in `.env` to another port (e.g., 8001)
- Don't forget to update `API_URL` in `config.js`

**Error: Module not found**
- Solution: Make sure you activated virtual environment and ran `pip install -r requirements.txt`

### Frontend Can't Connect to Backend

**"Backend Offline" message**
- Verify backend is running: Check terminal for uvicorn output
- Check URL: Make sure `API_URL` in `config.js` matches backend address
- Check CORS: Add your frontend URL to `ALLOWED_ORIGINS` in `.env`
- Check firewall: Ensure firewall allows connections to port 8000

**CORS errors in browser console**
- Solution: Add your frontend URL to `ALLOWED_ORIGINS` in backend `.env`
- Restart backend server after changing `.env`

### PDF Upload Not Working

**"Upload failed" error**
- Check file is actually a PDF
- Verify backend is running and `USE_BACKEND: true` in config
- Check backend logs for specific error

### API Responses Are Slow

- OpenAI API calls can take 5-30 seconds
- Check your internet connection
- Consider upgrading to gpt-4 for better but slower results
- Or switch to gpt-3.5-turbo-16k for faster responses

### OpenAI API Errors

**"Rate limit exceeded"**
- You've hit OpenAI's rate limits
- Wait a few minutes and try again
- Consider upgrading your OpenAI plan

**"Insufficient credits"**
- Add credits to your OpenAI account
- Visit https://platform.openai.com/account/billing

## Usage Tips

1. **Upload Medical PDFs**: Add medical textbooks, guidelines, or research papers to enhance AI responses
2. **Be Specific**: Provide detailed symptoms and patient information for better analysis
3. **Verify Information**: Always cross-reference AI suggestions with current medical literature
4. **Save Important Notes**: Use the Patient Management feature to document important cases

## Security Notes

⚠️ **Important Security Considerations:**

1. **API Keys**: Never commit your `.env` file or share your OpenAI API key
2. **Patient Data**: This is a demonstration tool - implement proper HIPAA compliance for production use
3. **Authentication**: Add user authentication before deploying in a clinical environment
4. **HTTPS**: Use HTTPS in production to encrypt data in transit
5. **Data Privacy**: Patient data is stored locally in browser - implement proper database in production

## Support

For issues or questions:
1. Check this troubleshooting guide
2. Review backend logs for error messages
3. Check browser console for frontend errors
4. Open an issue on GitHub

## Next Steps

Now that you have the application running:
1. Upload medical PDFs to build your knowledge base
2. Test different medical scenarios
3. Customize the knowledge base for your specialty
4. Consider adding authentication for production use
5. Implement proper database storage for patient data

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**License**: GPL-3.0
