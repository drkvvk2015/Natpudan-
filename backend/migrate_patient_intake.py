"""
Migration script to add extended anthropometry and complaints columns to patient_intakes table.

Run this script ONCE to migrate your existing database:
    python backend/migrate_patient_intake.py

This adds 22 new columns:
- 13 anthropometry fields (height, weight, BMI, waist, hip, WHR, MUAC, etc.)
- 5 vital signs (BP, pulse, resp rate, temperature)
- 2 complaint fields (chief_complaints JSON, present_history JSON)
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "natpudan.db"

def migrate_patient_intake():
    """Add new columns to patient_intakes table"""
    
    if not DB_PATH.exists():
        print(f"[ERROR] Database not found at {DB_PATH}")
        print("   Run the backend server first to create the database.")
        return False
    
    print(f" Migrating database: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='patient_intakes'")
    if not cursor.fetchone():
        print("[ERROR] Table 'patient_intakes' not found. Create it first by running the backend.")
        conn.close()
        return False
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(patient_intakes)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    # Columns to add
    new_columns = [
        # Anthropometry (13 columns)
        ("height_cm", "INTEGER"),
        ("weight_kg", "INTEGER"),
        ("bmi", "INTEGER"),
        ("waist_cm", "INTEGER"),
        ("hip_cm", "INTEGER"),
        ("whr", "INTEGER"),
        ("muac_cm", "INTEGER"),
        ("head_circumference_cm", "INTEGER"),
        ("chest_expansion_cm", "INTEGER"),
        ("sitting_height_cm", "INTEGER"),
        ("standing_height_cm", "INTEGER"),
        ("arm_span_cm", "INTEGER"),
        ("body_fat_percent", "INTEGER"),
        
        # Vitals (5 columns)
        ("bp_systolic", "INTEGER"),
        ("bp_diastolic", "INTEGER"),
        ("pulse_per_min", "INTEGER"),
        ("resp_rate_per_min", "INTEGER"),
        ("temperature_c", "INTEGER"),
        
        # Complaints (2 JSON columns stored as TEXT)
        ("chief_complaints", "TEXT"),
        ("present_history", "TEXT"),
    ]
    
    # Track changes
    added_count = 0
    skipped_count = 0
    
    print("\n Adding columns...")
    
    for column_name, column_type in new_columns:
        if column_name in existing_columns:
            print(f"     {column_name} - Already exists, skipping")
            skipped_count += 1
        else:
            try:
                cursor.execute(f"ALTER TABLE patient_intakes ADD COLUMN {column_name} {column_type}")
                print(f"   [OK] {column_name} - Added successfully")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"   [WARNING]  {column_name} - Error: {e}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    # Summary
    print("\n" + "="*60)
    print(f"[OK] Migration complete!")
    print(f"   - Added: {added_count} columns")
    print(f"   - Skipped: {skipped_count} columns (already exist)")
    print(f"   - Total new columns: {len(new_columns)}")
    print("="*60)
    
    if added_count > 0:
        print("\n[READY] Your database is now ready for extended patient intake features!")
        print("   You can now:")
        print("   1. Restart the backend server")
        print("   2. Use the Patient Intake form with all new fields")
        print("   3. Store anthropometry, vitals, and structured complaints")
    else:
        print("\n[TIP] All columns already exist. Database is up to date!")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Patient Intake Database Migration")
    print("=" * 60)
    print()
    
    try:
        success = migrate_patient_intake()
        if not success:
            print("\n[ERROR] Migration failed. Please check the errors above.")
            exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    print("\n[OK] Migration script finished successfully!")
    exit(0)
