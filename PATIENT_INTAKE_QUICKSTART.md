# Patient Intake Quick Start Guide

## 🚀 Quick Start

### Step 1: Start the Backend
```powershell
.\start-backend.ps1
```

Wait for: `✅ Application startup complete`

### Step 2: Verify API is Working
```powershell
python test_patient_intake_api.py
```

Expected output:
```
✅ Complaint Options: PASS
✅ Create Patient: NEEDS AUTH
✅ List Patients: NEEDS AUTH
✅ ALL TESTS PASSED!
```

### Step 3: Test in Browser

1. **Get Complaint Options**:
   ```
   http://localhost:8000/api/medical/complaints/options
   ```
   Should show 80+ complaints, relieving/aggravating factors, etc.

2. **API Documentation**:
   ```
   http://localhost:8000/docs
   ```
   Look for "patient-intake" section

## 📱 Frontend Integration

### Install Dependencies (if needed)
```bash
cd frontend
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material
```

### Use ComplaintSelector Component

```tsx
import { ComplaintSelector, ChiefComplaint } from '@/components/ComplaintSelector';

function YourForm() {
  const [complaints, setComplaints] = useState<ChiefComplaint[]>([]);

  return (
    <ComplaintSelector
      complaints={complaints}
      onChange={setComplaints}
    />
  );
}
```

### Save Patient Intake

```typescript
import { savePatientIntake } from '@/services/api';

const handleSave = async () => {
  const data = {
    name: "John Doe",
    age: 45,
    gender: "Male",
    blood_type: "O+",
    chief_complaints: complaints,  // From ComplaintSelector
    past_medical_history: ["Hypertension"],
    current_medications: ["Metformin 500mg"],
    allergies: ["Penicillin"],
    smoking: "Never",
    alcohol: "Occasional",
    occupation: "Teacher",
    travel_history: [],
    family_history: []
  };

  try {
    const response = await savePatientIntake(data);
    console.log('Saved!', response);
  } catch (error) {
    console.error('Error:', error);
  }
};
```

## 🎯 Key Features

### Mouse-Click Complaint Selection
1. Click "Add Complaint"
2. Select from 80+ common complaints
3. Or type custom complaint (autocomplete)

### Structured Data Entry
- **Onset**: Select from dropdown (Today, 1 week ago, etc.)
- **Severity**: Click Mild/Moderate/Severe buttons
- **Character**: Auto-shows relevant options (e.g., Sharp/Dull for pain)
- **Relieving Factors**: Multi-select with green chips
- **Aggravating Factors**: Multi-select with red chips
- **Associated Symptoms**: Multi-select from other complaints

### Chronological Display
- Complaints sorted by onset (oldest first)
- Expandable accordions for details
- Visual progression indicators (↑ worse, ↓ better, ⏰ stable)
- Edit/delete buttons for each complaint

## 🔧 Troubleshooting

### Backend Won't Start
```powershell
# Check if port 8000 is already in use
Get-NetTCPConnection -LocalPort 8000

# Kill process if needed
Stop-Process -Id <PID> -Force

# Or let script auto-select port 8001
.\start-backend.ps1
```

### Import Error in Backend
```powershell
# Activate virtual environment
cd backend
.\venv\Scripts\Activate.ps1

# Verify imports work
python -c "from app.api.patient_intake import router; print('OK')"
```

### Frontend Component Not Found
```bash
# Make sure file exists
ls frontend/src/components/ComplaintSelector.tsx

# Install dependencies
cd frontend
npm install
```

### API Returns 401 Unauthorized
```typescript
// Make sure token is set
const token = localStorage.getItem('token');
if (!token) {
  // Redirect to login
  window.location.href = '/login';
}
```

### Complaints Not Saving
- Check browser console for errors
- Verify required fields are filled (Complaint, Onset, Severity)
- Check network tab for API response

## 📊 Database Schema

The new fields added to `patient_intakes` table:

```sql
chief_complaints          JSON          -- Structured complaint list
associated_symptoms       JSON          -- Associated symptoms
past_medical_history      JSON          -- Past medical conditions
past_surgical_history     JSON          -- Past surgeries
current_medications       JSON          -- Current medications
allergies                 JSON          -- Allergies list
smoking                   VARCHAR(100)  -- Smoking status
alcohol                   VARCHAR(100)  -- Alcohol use
occupation                VARCHAR(200)  -- Occupation
created_by                INTEGER       -- Foreign key to users.id
```

### Migration Required

If database already exists, you need to migrate:

```powershell
# Development: Just delete the database
cd backend
Remove-Item natpudan.db
# Backend will recreate on next start

# Production: Use Alembic
alembic revision --autogenerate -m "Add patient intake fields"
alembic upgrade head
```

## 🎨 Customization

### Add More Complaints

Edit `frontend/src/components/ComplaintSelector.tsx`:

```typescript
const COMPLAINT_CATEGORIES = {
  'Your Category': [
    'New Complaint 1',
    'New Complaint 2',
  ],
  // ... existing categories
};
```

### Add More Relieving/Aggravating Factors

```typescript
const RELIEVING_FACTORS = [
  'Your New Factor',
  // ... existing factors
];

const AGGRAVATING_FACTORS = [
  'Your New Factor',
  // ... existing factors
];
```

### Change Color Scheme

```typescript
// Modify getSeverityColor function
const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'Mild':
      return 'info';     // Blue
    case 'Moderate':
      return 'warning';  // Orange
    case 'Severe':
      return 'error';    // Red
  }
};
```

## 📚 API Reference

### Get Complaint Options
```http
GET /api/medical/complaints/options
```

Response:
```json
{
  "common_complaints": ["Fever", "Cough", ...],
  "relieving_factors": [...],
  "aggravating_factors": [...],
  "severity_options": ["Mild", "Moderate", "Severe"],
  ...
}
```

### Create Patient Intake
```http
POST /api/medical/patient-intake
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "John Doe",
  "age": 45,
  "gender": "Male",
  "chief_complaints": [...]
}
```

### Get Patient Intake
```http
GET /api/medical/patient-intake/{intake_id}
Authorization: Bearer <token>
```

### Update Patient Intake
```http
PUT /api/medical/patient-intake/{intake_id}
Authorization: Bearer <token>
Content-Type: application/json

{...updated data...}
```

### List Patient Intakes
```http
GET /api/medical/patient-intake?skip=0&limit=10
Authorization: Bearer <token>
```

## ✅ Verification Checklist

Before using in production:

- [ ] Backend starts without errors
- [ ] Test script passes all tests
- [ ] API documentation shows patient-intake endpoints
- [ ] Frontend component renders correctly
- [ ] Can add/edit/delete complaints
- [ ] Complaints display in chronological order
- [ ] Save patient intake succeeds
- [ ] Load patient intake shows correct data
- [ ] Database migration complete
- [ ] Authentication works correctly

## 📖 Full Documentation

See [PATIENT_INTAKE_FIX_COMPLETE.md](./PATIENT_INTAKE_FIX_COMPLETE.md) for:
- Complete implementation details
- Medical standards compliance
- Full API examples
- Testing procedures
- Architecture overview

## 🆘 Support

If you encounter issues:

1. Check [PATIENT_INTAKE_FIX_COMPLETE.md](./PATIENT_INTAKE_FIX_COMPLETE.md) troubleshooting section
2. Run test script: `python test_patient_intake_api.py`
3. Check backend logs for errors
4. Check browser console for frontend errors
5. Verify all dependencies installed
6. Ensure database migrated

## 🎉 Success Indicators

You'll know it's working when:

✅ Test script shows all tests passed  
✅ API documentation shows 5 patient-intake endpoints  
✅ Complaint options endpoint returns 80+ complaints  
✅ Frontend component renders with "Add Complaint" button  
✅ Can select complaints from dropdown  
✅ Can add relieving/aggravating factors  
✅ Complaints display chronologically  
✅ Save operation succeeds  
✅ No errors in backend/frontend logs  

**You're all set! 🚀**
