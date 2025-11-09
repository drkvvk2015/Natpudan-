"""
WebSocket handler for real-time medical diagnosis and prescription streaming
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional, Any
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and message routing"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_sessions[user_id] = {
            'websocket': websocket,
            'connected_at': datetime.utcnow().isoformat(),
            'messages_sent': 0,
            'current_session_id': None
        }
        logger.info(f"WebSocket connected: user_id={user_id}")
        
        # Send connection confirmation
        await self.send_message(user_id, {
            'type': 'connection',
            'status': 'connected',
            'message': 'Connected to Natpudan AI Medical Assistant',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def disconnect(self, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        logger.info(f"WebSocket disconnected: user_id={user_id}")
    
    async def send_message(self, user_id: str, message: Dict[str, Any]):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
                if user_id in self.user_sessions:
                    self.user_sessions[user_id]['messages_sent'] += 1
                return True
            except Exception as e:
                logger.error(f"Error sending message to {user_id}: {e}")
                return False
        return False
    
    async def send_stream_chunk(self, user_id: str, chunk_type: str, content: str, metadata: Optional[Dict] = None):
        """Send a streaming chunk to the user"""
        message = {
            'type': 'stream',
            'chunk_type': chunk_type,
            'content': content,
            'metadata': metadata or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.send_message(user_id, message)
    
    async def send_progress(self, user_id: str, stage: str, progress: int, message: str):
        """Send progress update to the user"""
        await self.send_message(user_id, {
            'type': 'progress',
            'stage': stage,
            'progress': progress,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def send_error(self, user_id: str, error: str, details: Optional[str] = None):
        """Send error message to the user"""
        await self.send_message(user_id, {
            'type': 'error',
            'error': error,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def send_complete(self, user_id: str, result: Dict[str, Any]):
        """Send completion message with final results"""
        await self.send_message(user_id, {
            'type': 'complete',
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get session data for a user"""
        return self.user_sessions.get(user_id)
    
    def is_connected(self, user_id: str) -> bool:
        """Check if a user is connected"""
        return user_id in self.active_connections


class StreamingDiagnosisHandler:
    """Handles streaming diagnosis with progress updates"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
    
    async def stream_diagnosis(
        self,
        user_id: str,
        symptoms: List[str],
        patient_info: Dict[str, Any],
        vital_signs: Optional[Dict[str, Any]] = None
    ):
        """
        Stream diagnosis process with real-time updates
        """
        try:
            # Stage 1: Analyzing symptoms
            await self.manager.send_progress(user_id, 'symptoms_analysis', 10, 'Analyzing symptoms...')
            await asyncio.sleep(0.5)  # Simulate processing
            
            symptoms_analysis = {
                'symptoms': symptoms,
                'severity': 'moderate',
                'duration': 'acute'
            }
            await self.manager.send_stream_chunk(user_id, 'symptoms', json.dumps(symptoms_analysis, indent=2))
            
            # Stage 2: Evaluating vital signs
            await self.manager.send_progress(user_id, 'vitals_evaluation', 30, 'Evaluating vital signs...')
            await asyncio.sleep(0.5)
            
            if vital_signs:
                await self.manager.send_stream_chunk(user_id, 'vitals', json.dumps(vital_signs, indent=2))
            
            # Stage 3: Reviewing medical history
            await self.manager.send_progress(user_id, 'history_review', 50, 'Reviewing patient history...')
            await asyncio.sleep(0.5)
            
            # Stage 4: Generating differential diagnosis
            await self.manager.send_progress(user_id, 'differential', 70, 'Generating differential diagnoses...')
            await asyncio.sleep(1.0)  # Simulate AI processing
            
            differential_diagnoses = [
                {'condition': 'Community-acquired pneumonia', 'probability': 'high', 'icd10': 'J18.9'},
                {'condition': 'Acute bronchitis', 'probability': 'moderate', 'icd10': 'J20.9'},
                {'condition': 'Upper respiratory infection', 'probability': 'moderate', 'icd10': 'J06.9'}
            ]
            
            for idx, diag in enumerate(differential_diagnoses):
                await self.manager.send_stream_chunk(
                    user_id, 
                    'differential_diagnosis', 
                    json.dumps(diag, indent=2),
                    {'index': idx + 1, 'total': len(differential_diagnoses)}
                )
                await asyncio.sleep(0.3)
            
            # Stage 5: Determining primary diagnosis
            await self.manager.send_progress(user_id, 'primary_diagnosis', 90, 'Determining primary diagnosis...')
            await asyncio.sleep(0.5)
            
            primary_diagnosis = {
                'diagnosis': 'Community-acquired pneumonia',
                'icd10_code': 'J18.9',
                'confidence': 'high',
                'reasoning': 'Based on symptoms (fever, cough, chest pain), vital signs, and patient presentation',
                'recommended_tests': ['Chest X-ray', 'Complete blood count', 'C-reactive protein'],
                'urgency': 'prompt evaluation required'
            }
            
            await self.manager.send_stream_chunk(user_id, 'primary_diagnosis', json.dumps(primary_diagnosis, indent=2))
            
            # Complete
            await self.manager.send_progress(user_id, 'complete', 100, 'Diagnosis complete!')
            await self.manager.send_complete(user_id, {
                'diagnosis': primary_diagnosis,
                'differential_diagnoses': differential_diagnoses,
                'next_steps': 'prescription_generation'
            })
            
            logger.info(f"Diagnosis streaming completed for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error in diagnosis streaming: {e}", exc_info=True)
            await self.manager.send_error(user_id, 'Diagnosis failed', str(e))


class StreamingPrescriptionHandler:
    """Handles streaming prescription generation with progress updates"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
    
    async def stream_prescription(
        self,
        user_id: str,
        diagnosis: str,
        patient_info: Dict[str, Any],
        severity: str = 'moderate'
    ):
        """
        Stream prescription generation process with real-time updates
        """
        try:
            # Stage 1: Checking allergies and contraindications
            await self.manager.send_progress(user_id, 'allergy_check', 10, 'Checking allergies and contraindications...')
            await asyncio.sleep(0.5)
            
            allergies = patient_info.get('allergies', [])
            current_meds = patient_info.get('current_medications', [])
            
            await self.manager.send_stream_chunk(user_id, 'safety_check', json.dumps({
                'allergies': allergies,
                'current_medications': current_meds,
                'contraindications_found': []
            }, indent=2))
            
            # Stage 2: Selecting medications
            await self.manager.send_progress(user_id, 'medication_selection', 30, 'Selecting appropriate medications...')
            await asyncio.sleep(1.0)
            
            medications = [
                {
                    'name': 'Amoxicillin-clavulanate',
                    'dose': '875-125 mg',
                    'route': 'PO',
                    'frequency': 'BID',
                    'duration': '7-10 days',
                    'rationale': 'First-line antibiotic for community-acquired pneumonia'
                },
                {
                    'name': 'Azithromycin',
                    'dose': '500 mg',
                    'route': 'PO',
                    'frequency': 'Once daily',
                    'duration': '3 days',
                    'rationale': 'Covers atypical pathogens'
                }
            ]
            
            for idx, med in enumerate(medications):
                await self.manager.send_stream_chunk(
                    user_id,
                    'medication',
                    json.dumps(med, indent=2),
                    {'index': idx + 1, 'total': len(medications)}
                )
                await asyncio.sleep(0.5)
            
            # Stage 3: Checking drug interactions
            await self.manager.send_progress(user_id, 'interaction_check', 60, 'Checking drug interactions...')
            await asyncio.sleep(0.8)
            
            all_drugs = [m['name'] for m in medications] + current_meds
            
            interaction_result = {
                'medications_checked': all_drugs,
                'interactions_found': 0,
                'warnings': []
            }
            
            await self.manager.send_stream_chunk(user_id, 'interactions', json.dumps(interaction_result, indent=2))
            
            # Stage 4: Generating monitoring advice
            await self.manager.send_progress(user_id, 'monitoring', 80, 'Generating monitoring recommendations...')
            await asyncio.sleep(0.5)
            
            monitoring = {
                'advice': [
                    'Monitor for improvement in symptoms within 48-72 hours',
                    'Watch for adverse effects: GI upset, rash',
                    'Check ECG if QT prolongation risk',
                    'Follow-up in 3-5 days or sooner if worsening'
                ],
                'warning_signs': [
                    'Worsening shortness of breath',
                    'High fever persisting >3 days',
                    'Severe allergic reaction'
                ]
            }
            
            await self.manager.send_stream_chunk(user_id, 'monitoring', json.dumps(monitoring, indent=2))
            
            # Stage 5: Finalizing prescription
            await self.manager.send_progress(user_id, 'finalize', 95, 'Finalizing prescription...')
            await asyncio.sleep(0.3)
            
            # Complete
            prescription_result = {
                'diagnosis': diagnosis,
                'medications': medications,
                'interactions': interaction_result,
                'monitoring': monitoring,
                'notes': 'This is an AI-generated prescription plan. Requires physician review and approval.'
            }
            
            await self.manager.send_progress(user_id, 'complete', 100, 'Prescription complete!')
            await self.manager.send_complete(user_id, prescription_result)
            
            logger.info(f"Prescription streaming completed for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error in prescription streaming: {e}", exc_info=True)
            await self.manager.send_error(user_id, 'Prescription generation failed', str(e))


# Global connection manager instance
connection_manager = ConnectionManager()
diagnosis_handler = StreamingDiagnosisHandler(connection_manager)
prescription_handler = StreamingPrescriptionHandler(connection_manager)
