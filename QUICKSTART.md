# Natpudan AI Medical Assistant - Quick Start Guide

Get up and running in 5 minutes!

## Option 1: Demo Mode (No Backend) - 30 Seconds

Perfect for trying out the interface without any setup.

1. **Open the app**:
   ```bash
   # Simply open index.html in your browser
   open index.html
   # Or double-click index.html
   ```

2. **You're done!** The app works with built-in demo data. Try:
   - Symptom Checker with "fever, cough"
   - Drug Interactions with "warfarin, aspirin"
   - Medical Reference search for "diabetes"

## Option 2: Full AI Mode - 5 Minutes

Get the full AI-powered experience with OpenAI GPT.

### Prerequisites
- Python 3.8+
- OpenAI API key ([Get one free](https://platform.openai.com/api-keys))

### Steps

1. **Install backend dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure API key**:
   ```bash
   # Copy the example
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # Replace 'your_openai_api_key_here' with your actual key
   ```

3. **Start backend**:
   ```bash
   python main.py
   ```
   
   You should see:
   ```
   INFO: Uvicorn running on http://0.0.0.0:8000
   ```

4. **Open frontend**:
   ```bash
   # In a new terminal
   cd ..
   python -m http.server 8080
   ```
   
   Or just open `index.html` in your browser.

5. **Check connection**:
   - Look for green "AI Mode: Backend connected" banner
   - If it's yellow/orange, check that backend is running

6. **Try AI features**:
   - Symptom analysis now uses GPT AI
   - Drug interactions use intelligent analysis
   - Medical search provides comprehensive answers

## What Can You Do?

### 1. Analyze Symptoms 🔍
```
Go to: Symptom Checker
Enter: "patient has fever, headache, stiff neck"
Add: Age 35, Male
Click: Analyze Symptoms
Get: AI-powered differential diagnosis
```

### 2. Check Drug Interactions 💊
```
Go to: Drug Interactions
Enter: warfarin
       aspirin
       ibuprofen
Click: Check Interactions
Get: Detailed interaction warnings
```

### 3. Search Medical Info 📚
```
Go to: Medical Reference
Search: "hypertension treatment"
Click: Search
Get: Comprehensive medical information
```

### 4. Upload Medical PDFs 📄
```
Go to: Medical Reference
Choose: medical_guideline.pdf
Click: Upload PDF
Result: Content added to AI knowledge base
```

### 5. Save Patient Notes 👨‍⚕️
```
Go to: Patient Notes
Enter: Patient ID, Name, Notes
Click: Save Notes
View: All saved notes with timestamps
```

## Troubleshooting

### Backend won't start?
```bash
# Check Python version (need 3.8+)
python --version

# Try installing dependencies again
pip install -r backend/requirements.txt
```

### "OPENAI_API_KEY not found"?
```bash
# Make sure .env file exists in backend/
cd backend
ls -la .env

# Edit .env and add your key
nano .env  # or use any text editor
```

### Frontend can't connect to backend?
```bash
# Check backend is running
# Visit http://localhost:8000/health
# Should see: {"status":"healthy"}

# Update config.js if using different port
# Edit config.js and change API_URL
```

### Port 8000 already in use?
```bash
# Change port in backend/.env
PORT=8001

# Update frontend config.js
API_URL: 'http://localhost:8001'
```

## Tips & Tricks

### 🎯 Best Practices
- **Be specific**: More details = better AI analysis
- **Use context**: Upload relevant PDFs for better results
- **Verify results**: Always double-check AI suggestions
- **Save often**: Patient notes stored in browser

### 🚀 Advanced Usage
- **Batch queries**: Multiple symptoms/medications at once
- **PDF library**: Build knowledge base with textbooks
- **Custom prompts**: Modify ai_service.py for specialty
- **Local demo**: Set USE_BACKEND: false in config.js

### 📊 Performance
- **AI queries**: 5-15 seconds (normal)
- **PDF upload**: 2-5 seconds per document
- **Search**: Instant with local, 5s with AI
- **Status check**: Updates on page load

## What's Next?

### Learn More
- **Full Setup**: Read SETUP_GUIDE.md
- **Architecture**: See ARCHITECTURE.md
- **Features**: Check FEATURES.md
- **API Docs**: Visit http://localhost:8000/docs

### Customize
- **Styling**: Edit styles.css
- **Knowledge**: Add to medicalKnowledge in script.js
- **Prompts**: Modify ai_service.py
- **Features**: Add new sections to index.html

### Deploy
- **Frontend**: Netlify, Vercel, GitHub Pages
- **Backend**: Heroku, AWS, Google Cloud
- **Database**: PostgreSQL for production
- **Security**: Add authentication, HTTPS

## Getting Help

### Check These First
1. **SETUP_GUIDE.md** - Detailed setup instructions
2. **ARCHITECTURE.md** - How everything works
3. **Backend logs** - Terminal output from python main.py
4. **Browser console** - Press F12 for errors

### Common Issues

**"Module not found"**
```bash
cd backend
pip install -r requirements.txt
```

**"CORS error"**
```bash
# Add your frontend URL to backend/.env
ALLOWED_ORIGINS=http://localhost:8080
```

**"No response from AI"**
```bash
# Check OpenAI API key is valid
# Check you have credits at platform.openai.com
# Try simpler query first
```

## Quick Commands Reference

```bash
# Install backend
cd backend && pip install -r requirements.txt

# Start backend
cd backend && python main.py

# Start frontend (option 1)
python -m http.server 8080

# Start frontend (option 2)
open index.html

# Test backend
cd backend && python test_api.py

# Check health
curl http://localhost:8000/health
```

## Success Checklist

- [ ] Python 3.8+ installed
- [ ] Backend dependencies installed
- [ ] OpenAI API key configured
- [ ] Backend running on port 8000
- [ ] Frontend accessible in browser
- [ ] Green "AI Mode" banner visible
- [ ] Symptom analysis works
- [ ] Drug checker works
- [ ] Medical search works

## Support

- **Documentation**: Comprehensive guides included
- **Test Script**: `python backend/test_api.py`
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

**You're ready to go! Start analyzing symptoms and building your medical knowledge base.**

🏥 Built for healthcare professionals  
🤖 Powered by AI  
📚 Open source (GPL-3.0)

Version: 1.0.0
