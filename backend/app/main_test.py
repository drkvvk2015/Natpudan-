"""Completely isolated main.py replacement for testing"""
import logging
logging.basicConfig(level=logging.INFO)

print("[STEP 1] Starting imports...")

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    print("[STEP 2] FastAPI imported")
    
    app = FastAPI(title="Natpudan Backend - Test Mode")
    print("[STEP 3] App created")
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print("[STEP 4] CORS added")
    
    @app.get("/api/health")
    def health():
        return {"status": "healthy", "message": "Backend is running in test mode"}
    
    @app.get("/")
    def root():
        return {"message": "Test backend working"}
    
    print("[STEP 5] Routes added")
    print("[SUCCESS] App ready to start!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
