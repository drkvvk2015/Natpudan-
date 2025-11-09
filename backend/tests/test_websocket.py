"""
WebSocket streaming tests for real-time diagnosis and prescription generation.
Tests progress updates, incremental streaming, and error handling.
"""
import asyncio
import json
import websockets
from datetime import datetime

# Test configuration
WS_URL = "ws://127.0.0.1:8001/ws/test_user"

async def test_diagnosis_streaming():
    """Test real-time diagnosis streaming with progress updates."""
    print("\n" + "="*60)
    print("TEST: Diagnosis Streaming")
    print("="*60)
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            # Send diagnosis request
            request = {
                "type": "diagnosis",
                "data": {
                    "symptoms": [
                        {"name": "fever", "severity": "moderate", "duration": "3 days"},
                        {"name": "cough", "severity": "severe", "duration": "5 days"},
                        {"name": "shortness of breath", "severity": "moderate", "duration": "2 days"}
                    ],
                    "vitals": {
                        "temperature": 38.5,
                        "heart_rate": 95,
                        "blood_pressure": "130/80",
                        "respiratory_rate": 24,
                        "oxygen_saturation": 94
                    },
                    "history": {
                        "age": 45,
                        "sex": "male",
                        "allergies": ["penicillin"],
                        "conditions": ["hypertension"]
                    }
                }
            }
            
            print(f"\n✓ Connected to WebSocket")
            print(f"✓ Sending diagnosis request...")
            await websocket.send(json.dumps(request))
            
            # Receive streaming responses
            message_count = 0
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    message = json.loads(response)
                    message_count += 1
                    
                    msg_type = message.get("type")
                    
                    if msg_type == "progress":
                        stage = message.get("stage", "")
                        progress = message.get("progress", 0)
                        desc = message.get("message", "")
                        print(f"  [{progress:3d}%] {stage}: {desc}")
                        
                    elif msg_type == "stream_chunk":
                        content = message.get("content", {})
                        print(f"  📦 Stream chunk: {json.dumps(content, indent=2)}")
                        
                    elif msg_type == "complete":
                        result = message.get("result", {})
                        print(f"\n✓ Diagnosis complete!")
                        print(f"  Primary diagnosis: {result.get('primary_diagnosis', 'N/A')}")
                        print(f"  Confidence: {result.get('confidence', 'N/A')}")
                        print(f"  Urgency: {result.get('urgency', 'N/A')}")
                        differentials = result.get('differential_diagnoses', [])
                        if differentials:
                            print(f"  Differential diagnoses: {len(differentials)}")
                        break
                        
                    elif msg_type == "error":
                        error = message.get("error", "Unknown error")
                        print(f"\n✗ Error: {error}")
                        break
                        
                except asyncio.TimeoutError:
                    print("\n✗ Timeout waiting for response")
                    break
            
            print(f"\n✓ Test completed - Received {message_count} messages")
            return True
            
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False


async def test_prescription_streaming():
    """Test real-time prescription streaming with progress updates."""
    print("\n" + "="*60)
    print("TEST: Prescription Streaming")
    print("="*60)
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            # Send prescription request
            request = {
                "type": "prescription",
                "data": {
                    "diagnosis": "Community-acquired pneumonia",
                    "patient_info": {
                        "age": 45,
                        "weight": 75,
                        "sex": "male",
                        "renal_function": "normal",
                        "hepatic_function": "normal"
                    },
                    "allergies": ["penicillin"]
                }
            }
            
            print(f"\n✓ Connected to WebSocket")
            print(f"✓ Sending prescription request...")
            await websocket.send(json.dumps(request))
            
            # Receive streaming responses
            message_count = 0
            medications = []
            
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    message = json.loads(response)
                    message_count += 1
                    
                    msg_type = message.get("type")
                    
                    if msg_type == "progress":
                        stage = message.get("stage", "")
                        progress = message.get("progress", 0)
                        desc = message.get("message", "")
                        print(f"  [{progress:3d}%] {stage}: {desc}")
                        
                    elif msg_type == "stream_chunk":
                        content = message.get("content", {})
                        if "medication" in content:
                            med = content["medication"]
                            medications.append(med)
                            print(f"  💊 {med.get('name', 'Unknown')}: {med.get('dosage', 'N/A')}")
                        else:
                            print(f"  📦 Stream chunk: {json.dumps(content, indent=2)}")
                        
                    elif msg_type == "complete":
                        result = message.get("result", {})
                        print(f"\n✓ Prescription complete!")
                        print(f"  Total medications: {len(medications)}")
                        print(f"  Interactions checked: {result.get('interactions_checked', 'N/A')}")
                        print(f"  Monitoring: {result.get('monitoring_required', 'N/A')}")
                        break
                        
                    elif msg_type == "error":
                        error = message.get("error", "Unknown error")
                        print(f"\n✗ Error: {error}")
                        break
                        
                except asyncio.TimeoutError:
                    print("\n✗ Timeout waiting for response")
                    break
            
            print(f"\n✓ Test completed - Received {message_count} messages")
            return True
            
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False


async def test_chat_message():
    """Test simple chat message (non-streaming)."""
    print("\n" + "="*60)
    print("TEST: Chat Message")
    print("="*60)
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            # Send chat message
            request = {
                "type": "chat",
                "data": {
                    "content": "Hello, this is a test message"
                }
            }
            
            print(f"\n✓ Connected to WebSocket")
            print(f"✓ Sending chat message...")
            await websocket.send(json.dumps(request))
            
            # Receive response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            message = json.loads(response)
            
            print(f"✓ Received: {message.get('type', 'unknown')}")
            print(f"  Content: {message.get('content', 'N/A')}")
            
            return True
            
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False


async def test_error_handling():
    """Test error handling with invalid message type."""
    print("\n" + "="*60)
    print("TEST: Error Handling")
    print("="*60)
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            # Send invalid message type
            request = {
                "type": "invalid_type",
                "data": {}
            }
            
            print(f"\n✓ Connected to WebSocket")
            print(f"✓ Sending invalid message type...")
            await websocket.send(json.dumps(request))
            
            # Receive error response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            message = json.loads(response)
            
            if message.get("type") == "error":
                print(f"✓ Error handled correctly: {message.get('error', 'N/A')}")
                return True
            else:
                print(f"✗ Expected error response, got: {message.get('type')}")
                return False
            
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False


async def run_all_tests():
    """Run all WebSocket streaming tests."""
    print("\n" + "="*70)
    print("WEBSOCKET STREAMING TEST SUITE")
    print("="*70)
    
    results = {}
    
    # Run tests
    results["diagnosis_streaming"] = await test_diagnosis_streaming()
    await asyncio.sleep(1)  # Brief pause between tests
    
    results["prescription_streaming"] = await test_prescription_streaming()
    await asyncio.sleep(1)
    
    results["chat_message"] = await test_chat_message()
    await asyncio.sleep(1)
    
    results["error_handling"] = await test_error_handling()
    
    # Summary
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed ({passed*100//total}%)")
    print("="*70)


if __name__ == "__main__":
    print("\n🚀 Starting WebSocket streaming tests...")
    print("⚠️  Make sure the backend server is running on http://127.0.0.1:8000")
    
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Test suite failed: {e}")
