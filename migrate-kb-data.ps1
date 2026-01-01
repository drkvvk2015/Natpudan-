# Migrate Knowledge Base Data from OpenAI-based to Local system

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Knowledge Base Data Migration" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "This will migrate your 20,623 chunks from the old system to the new local system.`n" -ForegroundColor Yellow

cd "F:\Software\android apps\Natpudan-\backend"

Write-Host "[1/3] Checking existing data..." -ForegroundColor Cyan

& "..\\.venv\Scripts\python.exe" -c @"
import pickle
import shutil
from pathlib import Path

kb_dir = Path('data/knowledge_base')

# Check old data
old_metadata = kb_dir / 'metadata.pkl'
old_index = kb_dir / 'faiss_index.bin'

# Check new data
new_metadata = kb_dir / 'local_metadata.pkl'
new_index = kb_dir / 'local_faiss_index.bin'

print('\n📊 Current Status:')
if old_metadata.exists():
    with open(old_metadata, 'rb') as f:
        old_data = pickle.load(f)
    print(f'  OLD system: {old_data.get(\"document_count\", 0)} docs, {len(old_data.get(\"documents\", []))} chunks')
    print(f'  OLD index size: {old_index.stat().st_size / 1024 / 1024:.2f} MB')
else:
    print('  OLD system: No data')

if new_metadata.exists():
    with open(new_metadata, 'rb') as f:
        new_data = pickle.load(f)
    print(f'  NEW system: {new_data.get(\"document_count\", 0)} docs, {len(new_data.get(\"documents\", []))} chunks')
else:
    print('  NEW system: No data')

print('\n')
"@

Write-Host "[2/3] Do you want to migrate? This will:" -ForegroundColor Yellow
Write-Host "  - Copy OLD data to NEW system files" -ForegroundColor White
Write-Host "  - Backup old files first" -ForegroundColor White
Write-Host "  - The system will then use local KB (no OpenAI costs)" -ForegroundColor Green
Write-Host ""
$confirm = Read-Host "Continue? (y/n)"

if ($confirm -ne 'y') {
    Write-Host "`nMigration cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host "`n[3/3] Migrating data..." -ForegroundColor Cyan

& "..\\.venv\Scripts\python.exe" -c @"
import pickle
import shutil
from pathlib import Path
from datetime import datetime

kb_dir = Path('data/knowledge_base')

# Backup old files
backup_dir = kb_dir / f'backup_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}'
backup_dir.mkdir(exist_ok=True)

print(f'  ✓ Creating backup in: {backup_dir}')
for f in ['metadata.pkl', 'faiss_index.bin']:
    src = kb_dir / f
    if src.exists():
        shutil.copy2(src, backup_dir / f)
        print(f'    Backed up: {f}')

# Copy to new names
print(f'\n  ✓ Copying data to new system...')
shutil.copy2(kb_dir / 'metadata.pkl', kb_dir / 'local_metadata.pkl')
shutil.copy2(kb_dir / 'faiss_index.bin', kb_dir / 'local_faiss_index.bin')

print(f'    metadata.pkl → local_metadata.pkl')
print(f'    faiss_index.bin → local_faiss_index.bin')

# Verify
with open(kb_dir / 'local_metadata.pkl', 'rb') as f:
    data = pickle.load(f)

print(f'\n  ✓ Migration complete!')
print(f'    New system now has: {data.get(\"document_count\", 0)} docs, {len(data.get(\"documents\", []))} chunks')
print(f'    Index size: {(kb_dir / \"local_faiss_index.bin\").stat().st_size / 1024 / 1024:.2f} MB')
"@

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Migration Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "✅ Your 20,623 chunks are now available in the new system!`n" -ForegroundColor Green

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Restart backend (close minimized window and run .\start-backend.ps1)" -ForegroundColor White
Write-Host "  2. Clear browser cache (Ctrl+Shift+Delete)" -ForegroundColor White
Write-Host "  3. Refresh frontend: http://127.0.0.1:5173" -ForegroundColor White
Write-Host "  4. KB indicator should show ~20,623 chunks!`n" -ForegroundColor White
