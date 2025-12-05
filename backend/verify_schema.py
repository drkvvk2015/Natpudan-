"""
Quick script to verify the patient_intakes table schema after migration
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "natpudan.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get table schema
cursor.execute("PRAGMA table_info(patient_intakes)")
columns = cursor.fetchall()

print("=" * 80)
print("Patient Intakes Table Schema")
print("=" * 80)
print(f"\nTotal Columns: {len(columns)}\n")

# Group columns by category
basic_fields = []
anthropometry_fields = []
vital_fields = []
complaint_fields = []
other_fields = []

for col in columns:
    col_id, name, col_type, not_null, default, pk = col
    
    if name in ['height_cm', 'weight_kg', 'bmi', 'waist_cm', 'hip_cm', 'whr', 
                'muac_cm', 'head_circumference_cm', 'chest_expansion_cm', 
                'sitting_height_cm', 'standing_height_cm', 'arm_span_cm', 'body_fat_percent']:
        anthropometry_fields.append((name, col_type))
    elif name in ['bp_systolic', 'bp_diastolic', 'pulse_per_min', 'resp_rate_per_min', 'temperature_c']:
        vital_fields.append((name, col_type))
    elif name in ['chief_complaints', 'present_history']:
        complaint_fields.append((name, col_type))
    elif name in ['id', 'intake_id', 'name', 'age', 'gender', 'blood_type', 'created_at', 'updated_at']:
        basic_fields.append((name, col_type))
    else:
        other_fields.append((name, col_type))

# Display grouped columns
print("[INFO] BASIC FIELDS:")
for name, col_type in basic_fields:
    print(f"   - {name:30} {col_type}")

print(f"\n[MEASURE] ANTHROPOMETRY FIELDS ({len(anthropometry_fields)}):")
for name, col_type in anthropometry_fields:
    print(f"   - {name:30} {col_type}")

print(f"\n[VITALS] VITAL SIGNS ({len(vital_fields)}):")
for name, col_type in vital_fields:
    print(f"   - {name:30} {col_type}")

print(f"\n[SYMPTOM] COMPLAINT FIELDS ({len(complaint_fields)}):")
for name, col_type in complaint_fields:
    print(f"   - {name:30} {col_type}")

if other_fields:
    print(f"\n[INFO] OTHER FIELDS ({len(other_fields)}):")
    for name, col_type in other_fields:
        print(f"   - {name:30} {col_type}")

print("\n" + "=" * 80)
print("[OK] Schema verification complete!")
print(f"   Total: {len(columns)} columns")
print(f"   Basic: {len(basic_fields)} | Anthropometry: {len(anthropometry_fields)} | "
      f"Vitals: {len(vital_fields)} | Complaints: {len(complaint_fields)}")
print("=" * 80)

conn.close()
