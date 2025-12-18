"""Test Phase 4 health endpoint"""
import requests

try:
    r = requests.get('http://localhost:8000/api/phase-4/health', timeout=2)
    print(f'✅ Status: {r.status_code}')
    if r.status_code == 200:
        print(f'✅ Response: {r.json()}')
        print('\n🎉 Phase 4 API is working!')
    else:
        print(f'❌ Error: {r.text}')
except requests.exceptions.ConnectionError:
    print('⚠️  Server not running. Start with: python -m uvicorn app.main:app --reload --port 8000')
except Exception as e:
    print(f'❌ Error: {e}')
