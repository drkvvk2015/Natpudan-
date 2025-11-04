# 🚀 Quick Start Guide - Physician AI Assistant

## Get Started in 5 Minutes!

### Step 1: Run Setup (Automated)
```powershell
# Run the setup script
.\setup.ps1
```

This automatically:
- ✅ Creates virtual environment
- ✅ Installs all dependencies
- ✅ Sets up database
- ✅ Creates data directories
- ✅ Downloads NLP models

### Step 2: Add OpenAI API Key
```powershell
cd backend
notepad .env
```

Add your API key:
```
OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Add Medical Books (Optional)
```powershell
# Copy PDF medical textbooks to:
backend/data/medical_books/

# Examples:
# - Harrison's Principles of Internal Medicine.pdf
# - Oxford Handbook of Clinical Medicine.pdf
# - Any medical PDF textbook
```

### Step 4: Start the Server
```powershell
cd backend
python run.py
```

### Step 5: Test the API
Open browser: http://localhost:8000/docs

Try the interactive API documentation!

## 🔥 Quick Test Examples

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Medical Query (via WebSocket)
Use the API docs at http://localhost:8000/docs

Click on "WebSocket" → "Try it out"

Send:
```json
{
  "content": "What are the symptoms of myocardial infarction?",
  "type": "general"
}
```

### Test 3: Upload a Medical Book
Go to http://localhost:8000/docs → `/api/upload/pdf` → "Try it out"

Upload a medical PDF and watch it get automatically processed!

### Test 4: Generate Diagnosis
```json
{
  "symptoms": ["chest pain", "shortness of breath", "diaphoresis"],
  "patient_info": {
    "age": 65,
    "gender": "male"
  }
}
```

## 🎯 What You Can Do

1. **Chat with Medical AI**
   - Ask medical questions
   - Get differential diagnoses
   - Treatment recommendations

2. **Upload Medical Books**
   - System learns automatically
   - Semantic search across all books
   - Instant knowledge updates

3. **Drug Interactions**
   - Check multiple medications
   - Get dosing recommendations
   - Safety warnings

4. **Prescription Writing**
   - AI-assisted prescription generation
   - Interaction checking
   - ICD-10 coding

## ⚡ Common Issues

### "No OpenAI API key"
- System works with limited AI features
- PDF processing still works
- Use fallback responses

### "Module not found"
```powershell
cd backend
pip install -r requirements.txt
```

### "Port already in use"
Edit .env:
```
API_PORT=8001
```

## 📚 Next Steps

1. Read full documentation: `PROJECT_README.md`
2. Explore API docs: http://localhost:8000/docs
3. Add more medical books to `data/medical_books/`
4. Build the frontend (coming soon!)

## 🆘 Need Help?

- Check `PROJECT_README.md` for detailed docs
- View logs: `backend/physician_ai.log`
- Create issue on GitHub

---

**Ready to revolutionize medical practice with AI!** 🏥✨
