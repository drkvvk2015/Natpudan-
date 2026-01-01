# ICD-10 Integration for Discharge Summary

## Overview
Integrated ICD-10 code management into the discharge summary system, allowing medical staff to search, select, and auto-suggest standard diagnosis codes for proper medical billing and record-keeping.

## Features Implemented

### 1. Backend API Endpoints

#### Search ICD-10 Codes
**Endpoint:** `POST /api/discharge-summary/icd10/search`

Search for ICD-10 codes by code or description.

**Request:**
```json
{
  "query": "diabetes",
  "max_results": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "code": "E11.9",
      "description": "Type 2 diabetes mellitus without complications"
    },
    {
      "code": "E11.65",
      "description": "Type 2 diabetes mellitus with hyperglycemia"
    }
  ]
}
```

#### Auto-Suggest ICD-10 from Diagnosis
**Endpoint:** `POST /api/discharge-summary/icd10/suggest`

Automatically suggest ICD-10 codes based on diagnosis text.

**Request:**
```json
"Type 2 diabetes mellitus, hypertension"
```

**Response:**
```json
{
  "suggestions": [
    {
      "code": "E11.9",
      "description": "Type 2 diabetes mellitus without complications"
    },
    {
      "code": "I10",
      "description": "Essential (primary) hypertension"
    }
  ]
}
```

#### Enhanced AI Generation
**Endpoint:** `POST /api/discharge-summary/ai-generate`

Now returns both AI-generated summary AND suggested ICD-10 codes.

**Response:**
```json
{
  "ai_summary": "...",
  "suggested_icd10_codes": [
    {
      "code": "E11.9",
      "description": "Type 2 diabetes mellitus without complications"
    }
  ]
}
```

### 2. Database Changes

Added `icd10_codes` column to `discharge_summaries` table:
- **Type:** TEXT (stores JSON array)
- **Nullable:** Yes
- **Format:** `["E11.9", "I10", "J18.9"]`

### 3. Frontend UI Components

#### ICD-10 Code Manager
Located in the discharge summary form, below the diagnosis field:

**Features:**
- **Search Bar:** Search codes by keyword or code number
- **Auto-Suggest Button:** Automatically suggest codes from diagnosis text
- **Selected Codes:** Display chips of currently selected codes
- **Search Results:** Interactive list with "Add" buttons
- **Remove Codes:** Click X on chip to remove

**UI Layout:**
```
┌─────────────────────────────────────────┐
│ ICD-10 Codes                            │
│                                         │
│ Selected Codes:                         │
│ [E11.9 ×] [I10 ×] [J44.9 ×]           │
│                                         │
│ [Search: diabetes        ] [Search] [⚡Suggest] │
│                                         │
│ Search Results:                         │
│ ┌───────────────────────────────────┐   │
│ │ E11.9                     [Add]   │   │
│ │ Type 2 diabetes mellitus...       │   │
│ └───────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 4. ICD-10 Service Integration

The existing `icd10_service.py` is used for:
- Code search by keyword or code number
- Symptom-to-code mapping
- Code suggestions from diagnosis text
- Comprehensive ICD-10 database (600+ codes)

**Supported Categories:**
- Infectious diseases (A00-B99)
- Neoplasms (C00-D49)
- Blood diseases (D50-D89)
- Endocrine/metabolic (E00-E89)
- Mental disorders (F01-F99)
- Nervous system (G00-G99)
- Eye diseases (H00-H59)
- Ear diseases (H60-H95)
- Circulatory system (I00-I99)
- Respiratory system (J00-J99)
- Digestive system (K00-K95)
- Skin diseases (L00-L99)
- Musculoskeletal (M00-M99)
- Genitourinary (N00-N99)
- Pregnancy (O00-O9A)
- Symptoms/signs (R00-R99)
- Injury/poisoning (S00-T88)
- External causes (V00-Y99)
- Health factors (Z00-Z99)

## Usage Examples

### Frontend Usage

```typescript
// Search ICD-10 codes
const searchResults = await fetch("/api/discharge-summary/icd10/search", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({
    query: "pneumonia",
    max_results: 10,
  }),
});

// Auto-suggest from diagnosis
const suggestions = await fetch("/api/discharge-summary/icd10/suggest", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify("Community-acquired pneumonia"),
});

// Save discharge summary with ICD-10 codes
const summary = {
  patient_name: "John Doe",
  diagnosis: "Type 2 diabetes mellitus",
  icd10_codes: ["E11.9", "I10"],  // Array of codes
  // ... other fields
};
```

### Backend Usage

```python
from app.services.icd10_service import get_icd10_service

# Search codes
icd_service = get_icd10_service()
results = icd_service.search_codes("diabetes", max_results=10)

# Suggest codes from symptoms
suggestions = icd_service.suggest_codes(["fever", "cough", "shortness of breath"])

# Get specific code details
code_info = icd_service.get_code("E11.9")
# Returns: {"code": "E11.9", "description": "...", "category": "..."}
```

## Database Migration

Run the migration to add the `icd10_codes` column:

```bash
cd backend
python migrations/add_icd10_to_discharge_summary.py
```

The migration:
- ✅ Checks if column already exists
- ✅ Adds TEXT column for JSON array storage
- ✅ Works with both SQLite and PostgreSQL
- ✅ Safe to run multiple times

## Testing

### Backend Tests
```bash
# Test ICD-10 search
curl -X POST http://localhost:8000/api/discharge-summary/icd10/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "diabetes", "max_results": 5}'

# Test auto-suggest
curl -X POST http://localhost:8000/api/discharge-summary/icd10/suggest \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '"Type 2 diabetes, hypertension"'
```

### Frontend Testing
1. Navigate to Discharge Summary page
2. Fill in diagnosis field (e.g., "Type 2 diabetes mellitus")
3. Click "Suggest" button - should auto-populate ICD-10 codes
4. Or search manually for codes
5. Click "Add" to select codes
6. Save discharge summary
7. Verify codes are saved in database

## Integration Points

### 1. Diagnosis Page
The diagnosis page already shows ICD-10 codes for differential diagnoses. This can be extended to:
- Export selected ICD-10 codes to discharge summary
- Pre-populate discharge summary diagnosis field

### 2. Patient Intake
Can integrate ICD-10 lookup during initial patient assessment.

### 3. Analytics Dashboard
Future enhancement: Track most common ICD-10 codes, disease trends by code.

### 4. Billing Integration
ICD-10 codes can be exported for:
- Insurance claims
- Medical billing systems
- Healthcare analytics

## API Reference

### Models

#### DischargeSummaryRequest
```python
class DischargeSummaryRequest(BaseModel):
    patient_name: str
    diagnosis: Optional[str] = None
    icd10_codes: Optional[List[str]] = None  # NEW
    # ... other fields
```

#### ICD10SearchRequest
```python
class ICD10SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 10
```

### Database Schema

```sql
ALTER TABLE discharge_summaries 
ADD COLUMN icd10_codes TEXT;  -- Stores JSON: ["E11.9", "I10"]
```

## Benefits

1. **Standardization:** Use internationally recognized ICD-10 codes
2. **Accuracy:** Reduce coding errors with search and auto-suggest
3. **Billing:** Proper codes for insurance claims
4. **Analytics:** Track disease prevalence and trends
5. **Interoperability:** Standard codes for EHR integration
6. **Compliance:** Meet healthcare reporting requirements

## Future Enhancements

1. **ICD-10 Code Validation:** Verify codes are valid and current
2. **Code Hierarchy:** Show parent/child code relationships
3. **Favorite Codes:** Save frequently used codes per user
4. **Code Details:** Show full code information (billable, category, etc.)
5. **External API:** Integrate with official ICD-10 API for latest codes
6. **CPT Code Integration:** Add procedure codes alongside diagnosis codes
7. **Code Recommendations:** ML-based code suggestions from diagnosis text
8. **Bulk Import:** Import codes from external sources (CSV, HL7)

## Files Modified

### Backend
- `backend/app/api/discharge.py` - Added ICD-10 endpoints
- `backend/app/models.py` - Added icd10_codes column
- `backend/app/crud.py` - Handle JSON serialization of codes
- `backend/migrations/add_icd10_to_discharge_summary.py` - Database migration

### Frontend
- `frontend/src/pages/DischargeSummaryPage.tsx` - Added ICD-10 UI components

### Existing (Utilized)
- `backend/app/services/icd10_service.py` - ICD-10 code database and search

## Documentation
- `ICD10_DISCHARGE_INTEGRATION.md` - This file

---

## Quick Start

1. **Run Migration:**
   ```bash
   cd backend
   python migrations/add_icd10_to_discharge_summary.py
   ```

2. **Restart Backend:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

3. **Test in Frontend:**
   - Open discharge summary page
   - Enter diagnosis text
   - Click "Suggest" button
   - Or search manually
   - Select and save codes

4. **Verify:**
   - Check database: `SELECT icd10_codes FROM discharge_summaries;`
   - Should see JSON arrays like: `["E11.9", "I10"]`

## Support

For issues or questions:
1. Check backend logs for errors
2. Verify migration ran successfully
3. Test API endpoints with curl/Postman
4. Check browser console for frontend errors
5. Review ICD-10 service logs

## License

Part of Natpudan Medical AI Assistant system.
