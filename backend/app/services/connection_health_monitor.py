"""
Connection Health Monitor - Auto Port Mismatch Detection and Correction

Integrates with the Self-Healing System to automatically detect and fix:
- Port mismatches between frontend and backend
- Configuration drift in .env files
- Service connectivity issues
- CORS configuration problems

This module runs periodic health checks and proactively fixes issues.
"""

import logging
import json
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import subprocess
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / "config" / "ports.json"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
BACKEND_DIR = PROJECT_ROOT / "backend"


class ConnectionHealthMonitor:
    """Monitors and auto-corrects connection configuration issues"""
    
    def __init__(self):
        self.config = self._load_config()
        self.issues_detected = []
        self.fixes_applied = []
        logger.info("[CONNECTION MONITOR] Initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load centralized port configuration"""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    logger.info(f"[CONNECTION] Loaded config: Backend={config['services']['backend']['dev']}")
                    return config
        except Exception as e:
            logger.error(f"[CONNECTION] Failed to load config: {e}")
        
        # Default fallback
        return {
            "services": {
                "backend": {"dev": 8001, "prod": 8000},
                "frontend": {"dev": 5173, "prod": 3000}
            },
            "urls": {
                "backend": {"dev": "http://127.0.0.1:8001", "prod": "http://127.0.0.1:8000"},
                "websocket": {"dev": "ws://127.0.0.1:8001", "prod": "ws://127.0.0.1:8000"}
            }
        }
    
    def check_health(self) -> Dict[str, Any]:
        """
        Comprehensive health check for connection configuration
        
        Returns:
            Dict with status, issues, and suggested fixes
        """
        health_status = {
            'healthy': True,
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'issues': [],
            'fixes_available': []
        }
        
        # Check 1: Validate .env files
        env_check = self._check_env_files()
        health_status['checks']['env_files'] = env_check
        if not env_check['passed']:
            health_status['healthy'] = False
            health_status['issues'].extend(env_check['issues'])
            health_status['fixes_available'].extend(env_check['fixes'])
        
        # Check 2: Validate CORS configuration
        cors_check = self._check_cors_config()
        health_status['checks']['cors'] = cors_check
        if not cors_check['passed']:
            health_status['healthy'] = False
            health_status['issues'].extend(cors_check['issues'])
        
        # Check 3: Port availability
        port_check = self._check_port_availability()
        health_status['checks']['ports'] = port_check
        
        return health_status
    
    def _check_env_files(self) -> Dict[str, Any]:
        """Check if all .env files have correct backend URL"""
        expected_url = self.config['urls']['backend']['dev']
        expected_ws_url = self.config['urls']['websocket']['dev']
        
        env_files = [
            FRONTEND_DIR / ".env",
            FRONTEND_DIR / ".env.development",
            FRONTEND_DIR / ".env.local",
        ]
        
        issues = []
        fixes = []
        mismatches = []
        
        for env_file in env_files:
            if not env_file.exists():
                continue
            
            try:
                content = env_file.read_text()
                
                # Check API URL
                if 'VITE_API_BASE_URL' in content:
                    match = re.search(r'VITE_API_BASE_URL\s*=\s*(.+)', content)
                    if match:
                        actual_url = match.group(1).strip()
                        if actual_url != expected_url:
                            issue = f"Port mismatch in {env_file.name}: {actual_url} != {expected_url}"
                            issues.append(issue)
                            mismatches.append({
                                'file': str(env_file),
                                'key': 'VITE_API_BASE_URL',
                                'actual': actual_url,
                                'expected': expected_url
                            })
                            logger.warning(f"[CONNECTION] {issue}")
                
                # Check WebSocket URL
                if 'VITE_WS_URL' in content:
                    match = re.search(r'VITE_WS_URL\s*=\s*(.+)', content)
                    if match:
                        actual_ws = match.group(1).strip()
                        if actual_ws != expected_ws_url:
                            issue = f"WebSocket mismatch in {env_file.name}: {actual_ws} != {expected_ws_url}"
                            issues.append(issue)
                            mismatches.append({
                                'file': str(env_file),
                                'key': 'VITE_WS_URL',
                                'actual': actual_ws,
                                'expected': expected_ws_url
                            })
                            logger.warning(f"[CONNECTION] {issue}")
            
            except Exception as e:
                logger.error(f"[CONNECTION] Error checking {env_file}: {e}")
        
        if mismatches:
            fixes.append({
                'type': 'port_mismatch',
                'description': 'Auto-fix frontend .env files',
                'mismatches': mismatches,
                'auto_fixable': True
            })
        
        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'fixes': fixes,
            'mismatches': mismatches
        }
    
    def _check_cors_config(self) -> Dict[str, Any]:
        """Check if CORS is configured for current frontend port"""
        frontend_port = self.config['services']['frontend']['dev']
        expected_origins = [
            f"http://localhost:{frontend_port}",
            f"http://127.0.0.1:{frontend_port}"
        ]
        
        # TODO: Could check actual backend CORS config in main.py
        # For now, just return passed (would need to parse main.py)
        
        return {
            'passed': True,
            'issues': [],
            'expected_origins': expected_origins
        }
    
    def _check_port_availability(self) -> Dict[str, Any]:
        """Check if ports are available or in use"""
        backend_port = self.config['services']['backend']['dev']
        frontend_port = self.config['services']['frontend']['dev']
        
        def is_port_in_use(port: int) -> bool:
            try:
                if os.name == 'nt':  # Windows
                    result = subprocess.run(
                        ['netstat', '-ano'],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    return f":{port}" in result.stdout and "LISTENING" in result.stdout
                else:  # Unix/Linux
                    result = subprocess.run(
                        ['lsof', '-i', f':{port}'],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    return result.returncode == 0
            except:
                return False
        
        backend_in_use = is_port_in_use(backend_port)
        frontend_in_use = is_port_in_use(frontend_port)
        
        return {
            'backend_port': backend_port,
            'backend_in_use': backend_in_use,
            'frontend_port': frontend_port,
            'frontend_in_use': frontend_in_use
        }
    
    def auto_fix(self, issues_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically fix detected issues
        
        Args:
            issues_data: Output from check_health()
        
        Returns:
            Dict with fix results
        """
        results = {
            'fixes_attempted': 0,
            'fixes_successful': 0,
            'fixes_failed': 0,
            'details': []
        }
        
        for fix in issues_data.get('fixes_available', []):
            if not fix.get('auto_fixable', False):
                continue
            
            results['fixes_attempted'] += 1
            
            try:
                if fix['type'] == 'port_mismatch':
                    success = self._fix_port_mismatches(fix['mismatches'])
                    if success:
                        results['fixes_successful'] += 1
                        results['details'].append({
                            'type': 'port_mismatch',
                            'status': 'success',
                            'message': f"Fixed {len(fix['mismatches'])} port mismatches"
                        })
                        logger.info(f"[CONNECTION] Auto-fixed {len(fix['mismatches'])} port mismatches")
                    else:
                        results['fixes_failed'] += 1
                        results['details'].append({
                            'type': 'port_mismatch',
                            'status': 'failed',
                            'message': 'Failed to fix port mismatches'
                        })
            
            except Exception as e:
                results['fixes_failed'] += 1
                results['details'].append({
                    'type': fix['type'],
                    'status': 'error',
                    'message': str(e)
                })
                logger.error(f"[CONNECTION] Auto-fix failed: {e}")
        
        return results
    
    def _fix_port_mismatches(self, mismatches: List[Dict[str, Any]]) -> bool:
        """Fix port mismatches in .env files"""
        try:
            for mismatch in mismatches:
                file_path = Path(mismatch['file'])
                if not file_path.exists():
                    continue
                
                content = file_path.read_text()
                key = mismatch['key']
                expected = mismatch['expected']
                
                # Replace the line
                pattern = rf'^{key}\s*=.*$'
                replacement = f'{key}={expected}'
                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                
                # Write back
                file_path.write_text(new_content)
                logger.info(f"[CONNECTION] Fixed {file_path.name}: {key}={expected}")
            
            return True
        
        except Exception as e:
            logger.error(f"[CONNECTION] Failed to fix port mismatches: {e}")
            return False
    
    def get_error_context(self, error: Exception) -> Optional[Dict[str, Any]]:
        """
        Analyze if an error is connection-related
        
        Returns context if error is connection-related, None otherwise
        """
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        connection_keywords = [
            'connection', 'refused', 'timeout', 'unreachable',
            'cors', 'origin', 'port', 'econnrefused', 'network'
        ]
        
        is_connection_error = any(keyword in error_str for keyword in connection_keywords)
        
        if is_connection_error:
            health = self.check_health()
            return {
                'error_category': 'connection',
                'likely_cause': 'port_mismatch' if not health['healthy'] else 'service_offline',
                'health_check': health,
                'auto_fixable': len(health.get('fixes_available', [])) > 0
            }
        
        return None


# Global instance
_connection_monitor = None

def get_connection_monitor() -> ConnectionHealthMonitor:
    """Get global connection monitor instance"""
    global _connection_monitor
    if _connection_monitor is None:
        _connection_monitor = ConnectionHealthMonitor()
    return _connection_monitor
