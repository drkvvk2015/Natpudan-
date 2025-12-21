"""
Code-Level Error Detection and Analysis

Detects code-level issues like:
1. Missing database columns/fields
2. Missing API endpoints
3. Incorrect method/function calls
4. Type mismatches
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import inspect

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyzes code for potential issues and misconfigurations."""
    
    def __init__(self):
        self.detected_issues = []
        self.schema_cache = {}
    
    def analyze_attribute_error(self, error: AttributeError, context: Dict) -> Optional[Dict]:
        """Detect and suggest fix for AttributeError.
        
        Examples:
        - PatientIntake' has no attribute 'sex' -> suggests 'gender'
        - User' has no attribute 'blood_group' -> suggests 'blood_type'
        """
        error_msg = str(error)
        
        # Pattern: "type object 'ClassName' has no attribute 'field_name'"
        match = re.search(r"type object '(\w+)' has no attribute '(\w+)'", error_msg)
        if not match:
            # Try another pattern: "'ClassName' object has no attribute 'field_name'"
            match = re.search(r"'(\w+)' (?:object|type) has no attribute '(\w+)'", error_msg)
        
        if match:
            class_name = match.group(1)
            field_name = match.group(2)
            
            # Get suggestions for common field mismatches
            suggestions = self._get_field_suggestions(class_name, field_name)
            
            if suggestions:
                return {
                    'type': 'attribute_error',
                    'class': class_name,
                    'wrong_field': field_name,
                    'suggestions': suggestions,
                    'severity': 'high',
                    'auto_fixable': True,
                    'message': f"Field '{field_name}' not found in {class_name}. Did you mean: {suggestions[0]}?"
                }
        
        return None
    
    def analyze_404_error(self, status_code: int, path: str) -> Optional[Dict]:
        """Detect missing API endpoints.
        
        Example:
        - POST /api/error-correction/log not found
        """
        if status_code == 404:
            return {
                'type': 'missing_endpoint',
                'path': path,
                'severity': 'high',
                'auto_fixable': False,
                'message': f"API endpoint {path} is missing. Check router registration in main.py"
            }
        
        return None
    
    def check_model_schema(self, model_class) -> Dict:
        """Get available columns/fields in a model."""
        try:
            # Get all columns from SQLAlchemy model
            columns = {}
            if hasattr(model_class, '__table__'):
                for column in model_class.__table__.columns:
                    columns[column.name] = str(column.type)
            elif hasattr(model_class, '__annotations__'):
                columns = model_class.__annotations__
            
            return columns
        except Exception as e:
            logger.error(f"Failed to check schema for {model_class}: {e}")
            return {}
    
    def _get_field_suggestions(self, class_name: str, wrong_field: str) -> List[str]:
        """Get suggestions for mistyped field names."""
        
        # Common field name mappings
        field_mappings = {
            'PatientIntake': {
                'sex': ['gender', 'sex_type'],
                'blood_group': ['blood_type', 'blood_type_group'],
                'age_group': ['age_range'],
            },
            'User': {
                'username': ['email', 'full_name'],
                'name': ['full_name'],
            },
        }
        
        if class_name in field_mappings:
            if wrong_field in field_mappings[class_name]:
                return field_mappings[class_name][wrong_field]
        
        # Try to find similar field names using string similarity
        suggestions = self._find_similar_fields(class_name, wrong_field)
        return suggestions
    
    def _find_similar_fields(self, class_name: str, field_name: str) -> List[str]:
        """Find similar field names in model using string similarity."""
        try:
            # Import the model class dynamically
            from app.models import PatientIntake, User
            
            models = {
                'PatientIntake': PatientIntake,
                'User': User,
            }
            
            if class_name not in models:
                return []
            
            model = models[class_name]
            schema = self.check_model_schema(model)
            
            if not schema:
                return []
            
            # Find fields with similar names (Levenshtein distance)
            similar = []
            for col_name in schema.keys():
                similarity = self._string_similarity(field_name, col_name)
                if similarity > 0.6:  # 60% similarity threshold
                    similar.append((col_name, similarity))
            
            # Sort by similarity and return top 3
            similar.sort(key=lambda x: x[1], reverse=True)
            return [col for col, _ in similar[:3]]
        
        except Exception as e:
            logger.error(f"Failed to find similar fields: {e}")
            return []
    
    def _string_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using simple heuristic."""
        # Normalize strings
        str1 = str1.lower()
        str2 = str2.lower()
        
        # Levenshtein distance
        if len(str1) < len(str2):
            return self._string_similarity(str2, str1)
        
        if len(str2) == 0:
            return 1.0 if len(str1) == 0 else 0.0
        
        previous_row = range(len(str2) + 1)
        for i, c1 in enumerate(str1):
            current_row = [i + 1]
            for j, c2 in enumerate(str2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        distance = previous_row[-1]
        max_len = max(len(str1), len(str2))
        return 1.0 - (distance / max_len)
    
    def generate_fix_report(self, issues: List[Dict]) -> str:
        """Generate human-readable fix report."""
        if not issues:
            return "No issues detected."
        
        report = "=== CODE ANALYSIS REPORT ===\n\n"
        
        for i, issue in enumerate(issues, 1):
            report += f"{i}. {issue['type'].upper()}\n"
            report += f"   Severity: {issue['severity']}\n"
            report += f"   Message: {issue['message']}\n"
            
            if 'suggestions' in issue and issue['suggestions']:
                report += f"   Suggestions: {', '.join(issue['suggestions'])}\n"
            
            if 'auto_fixable' in issue:
                report += f"   Auto-fixable: {'Yes' if issue['auto_fixable'] else 'No'}\n"
            
            report += "\n"
        
        return report


# Global analyzer instance
_code_analyzer = None


def get_code_analyzer() -> CodeAnalyzer:
    """Get global code analyzer instance."""
    global _code_analyzer
    if _code_analyzer is None:
        _code_analyzer = CodeAnalyzer()
    return _code_analyzer
