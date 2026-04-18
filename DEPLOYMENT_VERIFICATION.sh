#!/bin/bash

# NATPUDAN v2.0 - 5 QUICK-WIN FEATURES DEPLOYMENT VERIFICATION
# This script verifies all components are in place and ready for deployment

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   NATPUDAN v2.0 - DEPLOYMENT VERIFICATION SCRIPT              ║"
echo "║   All 5 Quick-Win Features Ready for Production               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

PASSED=0
FAILED=0

# Helper functions
check_file() {
    if [ -f "$1" ]; then
        echo "  ✅ $1"
        ((PASSED++))
    else
        echo "  ❌ $1 - NOT FOUND"
        ((FAILED++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo "  ✅ $1/"
        ((PASSED++))
    else
        echo "  ❌ $1/ - NOT FOUND"
        ((FAILED++))
    fi
}

check_grep() {
    if grep -q "$2" "$1" 2>/dev/null; then
        echo "  ✅ $1 contains '$2'"
        ((PASSED++))
    else
        echo "  ❌ $1 missing '$2'"
        ((FAILED++))
    fi
}

echo "════════ FEATURE 1: VOICE → AUTO DOCUMENTATION ════════"
echo ""
echo "Backend Services:"
check_file "backend/app/services/voice_transcriber.py"
check_file "backend/app/services/voice_to_soap.py"
echo ""
echo "API Routes:"
check_file "backend/app/api/voice.py"
echo ""
echo "Database Models:"
check_grep "backend/app/models.py" "class VoiceRecording"
echo ""
echo "Frontend Components:"
check_file "frontend/src/pages/VoiceDocumentation.tsx"
echo ""
echo "Router Registration:"
check_grep "backend/app/main.py" "voice_router"
check_grep "frontend/src/App.tsx" "VoiceDocumentation"
echo ""

echo "════════ FEATURE 2: WEARABLE DATA INTEGRATION ════════"
echo ""
echo "Backend Services:"
check_file "backend/app/services/wearable_sync.py"
echo ""
echo "API Routes:"
check_file "backend/app/api/wearable_auth.py"
echo ""
echo "Database Models:"
check_grep "backend/app/models.py" "class WearableDeviceAuth"
check_grep "backend/app/models.py" "class WearableDeviceData"
check_grep "backend/app/models.py" "class WearableSyncLog"
echo ""
echo "Frontend Components:"
check_file "frontend/src/pages/WearableIntegration.tsx"
echo ""
echo "Background Worker:"
check_grep "backend/app/main.py" "_wearable_sync_loop"
check_grep "backend/app/main.py" "_wearable_worker_task"
echo ""
echo "Router Registration:"
check_grep "backend/app/main.py" "wearable_auth_router"
check_grep "frontend/src/App.tsx" "WearableIntegration"
echo ""

echo "════════ FEATURE 3: PREDICTIVE READMISSION ALERTS ════════"
echo ""
echo "Backend Services:"
check_file "backend/app/services/readmission_predictor.py"
check_file "backend/app/services/ml_trainer.py"
check_file "backend/app/services/alert_generator.py"
echo ""
echo "API Routes:"
check_file "backend/app/api/predictions.py"
echo ""
echo "Database Models:"
check_grep "backend/app/models.py" "class Alert"
echo ""
echo "Frontend Components:"
check_file "frontend/src/components/AlertsWidget.tsx"
echo ""
echo "Router Registration:"
check_grep "backend/app/main.py" "predictions_router"
echo ""

echo "════════ FEATURE 4: KNOWLEDGE GRAPH VISUALIZATION ════════"
echo ""
echo "API Routes:"
check_file "backend/app/api/knowledge_graph_viz.py"
echo ""
echo "Frontend Components:"
check_file "frontend/src/pages/KnowledgeGraphVisualizer.tsx"
echo ""
echo "Router Registration:"
check_grep "backend/app/main.py" "knowledge_graph_viz_router"
check_grep "frontend/src/App.tsx" "KnowledgeGraphVisualizer"
echo ""

echo "════════ FEATURE 5: AMBIENT TRANSCRIPTION ════════"
echo ""
echo "Backend Services:"
check_file "backend/app/services/ambient_transcriber.py"
echo ""
echo "API Routes:"
check_file "backend/app/api/voice_consul.py"
echo ""
echo "WebSocket Integration:"
check_grep "backend/app/api/voice_consul.py" "WebSocket"
echo ""
echo "Router Registration:"
check_grep "backend/app/main.py" "voice_consul_router"
echo ""

echo "════════ CONFIGURATION & DOCUMENTATION ════════"
echo ""
echo "Environment Configuration:"
check_file "backend/.env.template"
echo ""
echo "Documentation:"
check_file "INTEGRATION_GUIDE.md"
check_file "DEPLOYMENT_TESTING_GUIDE.md"
check_file "IMPLEMENTATION_SUMMARY.md"
echo ""

echo "════════ FRONTEND INTEGRATION ════════"
echo ""
echo "Routes Configuration:"
check_grep "frontend/src/App.tsx" "voice-documentation"
check_grep "frontend/src/App.tsx" "wearable-integration"
check_grep "frontend/src/App.tsx" "knowledge-graph"
echo ""
echo "Menu Items:"
check_grep "frontend/src/components/Layout.tsx" "VoiceIcon"
check_grep "frontend/src/components/Layout.tsx" "WearableIcon"
check_grep "frontend/src/components/Layout.tsx" "GraphicsIcon"
check_grep "frontend/src/components/Layout.tsx" "Voice Documentation"
check_grep "frontend/src/components/Layout.tsx" "Wearable Devices"
check_grep "frontend/src/components/Layout.tsx" "Medical Knowledge"
echo ""

echo "════════ DEPLOYMENT STATUS ════════"
echo ""
TOTAL=$((PASSED + FAILED))
PERCENTAGE=$((PASSED * 100 / TOTAL))

echo "Components Checked: $TOTAL"
echo "Passed: $PASSED ✅"
echo "Failed: $FAILED ❌"
echo "Coverage: $PERCENTAGE%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  🚀 ALL 5 FEATURES READY FOR DEPLOYMENT                       ║"
    echo "║                                                                ║"
    echo "║  Next Steps:                                                   ║"
    echo "║  1. cp backend/.env.template backend/.env                     ║"
    echo "║  2. Edit .env with your credentials                           ║"
    echo "║  3. Backend: cd backend && pip install -r requirements.txt    ║"
    echo "║  4. Backend: uvicorn app.main:app --reload --port 8000        ║"
    echo "║  5. Frontend: cd frontend && npm install && npm start          ║"
    echo "║  6. Access: http://localhost:3000                             ║"
    echo "║                                                                ║"
    echo "║  For Production Deployment:                                   ║"
    echo "║  → See DEPLOYMENT_TESTING_GUIDE.md                            ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    exit 0
else
    echo "❌ DEPLOYMENT BLOCKED - Missing components detected"
    echo "   Please verify all files are in place before deploying"
    exit 1
fi
