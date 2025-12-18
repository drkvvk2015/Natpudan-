"""
API endpoints for Self-Healing System monitoring and control
"""

from fastapi import APIRouter, BackgroundTasks
from typing import Dict, Any
import logging

from app.services.self_healing_system import get_self_healing_system

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/self-healing", tags=["Self-Healing System"])


@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """Get current self-healing system status and metrics"""
    system = get_self_healing_system()
    return system.get_system_report()


@router.get("/health-check")
async def health_check() -> Dict[str, Any]:
    """Get current system health with predictions"""
    system = get_self_healing_system()
    return system.prevention_engine.check_system_health()


@router.post("/run-maintenance")
async def run_maintenance(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Trigger preventive maintenance cycle"""
    system = get_self_healing_system()
    background_tasks.add_task(system.run_preventive_maintenance)
    return {
        "message": "Preventive maintenance scheduled",
        "status": "running"
    }


@router.get("/error-patterns")
async def get_error_patterns() -> Dict[str, Any]:
    """Get learned error patterns"""
    system = get_self_healing_system()
    
    patterns = {}
    for error_type, count in system.pattern_analyzer.frequencies.most_common(20):
        patterns[error_type] = {
            'occurrences': count,
            'likelihood': system.pattern_analyzer.predict_likelihood(error_type),
            'recent_contexts': system.pattern_analyzer.get_common_contexts(error_type, 3)
        }
    
    return {
        'patterns': patterns,
        'total_unique_errors': len(system.pattern_analyzer.frequencies)
    }


@router.get("/solutions")
async def get_known_solutions() -> Dict[str, Any]:
    """Get database of learned solutions"""
    system = get_self_healing_system()
    
    # Sort by success rate
    solutions = []
    for sig, sol in system.solution_generator.known_solutions.items():
        total = sol.get('success_count', 0) + sol.get('failure_count', 0)
        success_rate = sol.get('success_count', 0) / total if total > 0 else 0
        
        solutions.append({
            'signature': sig,
            'type': sol.get('type'),
            'success_count': sol.get('success_count', 0),
            'failure_count': sol.get('failure_count', 0),
            'success_rate': success_rate,
            'deprecated': sol.get('deprecated', False),
            'created_at': sol.get('created_at')
        })
    
    # Sort by success rate descending
    solutions.sort(key=lambda x: x['success_rate'], reverse=True)
    
    return {
        'solutions': solutions,
        'total_solutions': len(solutions),
        'active_solutions': len([s for s in solutions if not s['deprecated']])
    }


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Get detailed system metrics"""
    system = get_self_healing_system()
    return {
        'metrics': system.metrics,
        'success_rate': system._calculate_success_rate(),
        'uptime_status': 'operational'
    }


@router.post("/reset-metrics")
async def reset_metrics() -> Dict[str, Any]:
    """Reset system metrics (for testing/maintenance)"""
    system = get_self_healing_system()
    system.metrics = {
        'total_errors_handled': 0,
        'successful_fixes': 0,
        'failed_fixes': 0,
        'prevented_errors': 0,
        'system_uptime_hours': 0,
        'last_reset': system.metrics.get('last_reset')
    }
    system._save_metrics()
    return {"message": "Metrics reset successfully"}


@router.get("/predict")
async def predict_errors() -> Dict[str, Any]:
    """Predict likely errors in next 24 hours"""
    system = get_self_healing_system()
    
    predictions = []
    for error_type in system.pattern_analyzer.frequencies.keys():
        likelihood = system.pattern_analyzer.predict_likelihood(error_type)
        if likelihood > 0.3:  # Only show significant predictions
            predictions.append({
                'error_type': error_type,
                'likelihood': likelihood,
                'risk_level': 'high' if likelihood > 0.7 else 'medium' if likelihood > 0.5 else 'low',
                'recommended_action': f"Monitor {error_type} closely"
            })
    
    predictions.sort(key=lambda x: x['likelihood'], reverse=True)
    
    return {
        'predictions': predictions,
        'highest_risk': predictions[0] if predictions else None
    }
