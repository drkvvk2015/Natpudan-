# 🤝 Contributing to Physician AI Assistant

Thank you for your interest in contributing to the Physician AI Assistant project! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## 🤗 Code of Conduct

### Our Pledge

This project is dedicated to providing a harassment-free experience for everyone. We pledge to:

- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on constructive collaboration
- Prioritize patient safety in all decisions
- Maintain medical accuracy and ethics

### Medical Ethics

Given the medical nature of this project:

- Always prioritize patient safety
- Maintain medical accuracy
- Cite medical sources when applicable
- Follow evidence-based medicine principles
- Ensure HIPAA compliance considerations

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of:
  - FastAPI / Python async programming
  - Medical terminology (helpful but not required)
  - Machine Learning / LLMs
  - Database concepts

### First Time Setup

1. Fork the repository
2. Clone your fork
3. Run setup script
4. Create a branch for your changes

```powershell
git clone https://github.com/YOUR_USERNAME/Natpudan-.git
cd "Natpudan-/Natpudan AI project"
.\setup.ps1
git checkout -b feature/your-feature-name
```

## 💻 Development Setup

### Environment Setup

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### Development Dependencies

Create `requirements-dev.txt`:
```text
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
flake8==6.1.0
mypy==1.7.0
isort==5.12.0
```

### Configuration

Copy `.env.example` to `.env` and configure:
```bash
OPENAI_API_KEY=your-test-key
DEBUG=True
DATABASE_URL=sqlite:///./test_physician_ai.db
```

## 🎯 How to Contribute

### Types of Contributions

We welcome:

1. **Bug Fixes** - Fix issues and improve stability
2. **New Features** - Add new capabilities
3. **Documentation** - Improve docs, add examples
4. **Testing** - Add or improve tests
5. **Medical Knowledge** - Enhance medical accuracy
6. **Performance** - Optimize code
7. **UI/UX** - Frontend development

### Finding Issues to Work On

- Check [GitHub Issues](https://github.com/drkvvk2015/Natpudan-/issues)
- Look for `good-first-issue` label
- Look for `help-wanted` label
- Propose new features in discussions

## 📝 Coding Standards

### Python Style Guide

Follow PEP 8 with these specifics:

**Formatting**
```python
# Use Black for formatting
black app/

# Line length: 100 characters
# Indentation: 4 spaces
# Quote style: double quotes for strings
```

**Imports**
```python
# Standard library
import os
import sys
from typing import List, Dict

# Third-party
import fastapi
from sqlalchemy import Column

# Local
from app.services import KnowledgeBase
```

**Naming Conventions**
```python
# Classes: PascalCase
class MedicalAssistant:
    pass

# Functions/methods: snake_case
def process_medical_query():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_TOKENS = 800

# Private methods: _leading_underscore
def _internal_method():
    pass
```

**Type Hints**
```python
# Always use type hints
def analyze_symptoms(
    symptoms: List[str],
    patient_age: int,
    patient_gender: str
) -> Dict[str, Any]:
    pass

# Use Optional for nullable values
from typing import Optional

def get_patient(patient_id: str) -> Optional[Patient]:
    pass
```

**Documentation**
```python
def complex_function(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param2 is negative
    
    Example:
        >>> complex_function("test", 5)
        True
    """
    pass
```

### Medical Code Standards

**Always Include Medical Disclaimers**
```python
# In medical diagnostic functions
"""
WARNING: This is a clinical support tool.
All suggestions must be validated by licensed healthcare professionals.
Do not use for emergency situations.
"""
```

**Medical Accuracy**
```python
# Bad: Vague or inaccurate
def check_heart_attack(symptoms):
    if "chest pain" in symptoms:
        return "Heart attack likely"

# Good: Specific and accurate
def assess_acute_coronary_syndrome(
    symptoms: List[str],
    risk_factors: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Assess likelihood of acute coronary syndrome.
    
    Based on:
    - ACC/AHA Guidelines
    - TIMI Risk Score
    
    Returns differential diagnosis with confidence levels.
    Requires clinical correlation and ECG/troponin confirmation.
    """
    pass
```

**Cite Medical Sources**
```python
# Include references
HYPERTENSION_THRESHOLD = 140  # mmHg systolic (JNC 8 Guidelines)
DIABETES_THRESHOLD = 126  # mg/dL fasting glucose (ADA 2023)

# Reference major guidelines
"""
Treatment recommendations based on:
- Harrison's Principles of Internal Medicine, 21st Edition
- UpToDate Clinical Guidelines
- WHO Essential Medicines List
"""
```

## 🧪 Testing Guidelines

### Writing Tests

```python
# tests/test_medical_assistant.py
import pytest
from app.services.medical_assistant import MedicalAssistant

@pytest.mark.asyncio
async def test_symptom_analysis():
    """Test symptom analysis returns proper format"""
    assistant = MedicalAssistant()
    await assistant.initialize()
    
    result = await assistant.process_message(
        message="Patient has chest pain and dyspnea",
        user_id="test_user",
        message_type="diagnosis"
    )
    
    assert "content" in result
    assert "metadata" in result
    assert "differential_diagnoses" in result["metadata"]
```

### Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_medical_assistant.py

# Run specific test
pytest tests/test_medical_assistant.py::test_symptom_analysis
```

### Test Coverage

- Aim for 80%+ coverage
- All new features must have tests
- Medical logic must have extensive tests
- Test edge cases and error conditions

## 📚 Documentation

### Code Documentation

- Document all public functions and classes
- Use docstrings (Google style)
- Include examples where helpful
- Update README when adding features

### Medical Documentation

When adding medical features:

1. **Cite Sources**
   ```python
   # Source: Harrison's Principles, Chapter 45, Page 892
   ```

2. **Include Guidelines**
   ```python
   # Based on: ACC/AHA 2019 Guidelines
   ```

3. **Add Disclaimers**
   ```python
   # WARNING: Clinical correlation required
   ```

4. **Provide References**
   ```python
   # Reference: PMID 12345678
   ```

## 🔄 Pull Request Process

### Before Submitting

1. **Code Quality**
   ```powershell
   # Format code
   black app/
   
   # Check linting
   flake8 app/
   
   # Type checking
   mypy app/
   
   # Sort imports
   isort app/
   ```

2. **Testing**
   ```powershell
   # Run tests
   pytest
   
   # Check coverage
   pytest --cov=app
   ```

3. **Documentation**
   - Update relevant documentation
   - Add docstrings to new functions
   - Update CHANGELOG.md

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Medical accuracy improvement

## Medical Review Required?
- [ ] Yes - involves medical logic
- [ ] No - technical/infrastructure only

## Testing
- [ ] All tests pass
- [ ] Added new tests for new features
- [ ] Manual testing completed

## Documentation
- [ ] Code documented with docstrings
- [ ] README updated if needed
- [ ] CHANGELOG.md updated

## Medical Safety
- [ ] No patient safety concerns
- [ ] Medical accuracy verified
- [ ] Sources cited if applicable
- [ ] Appropriate disclaimers included

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] No console.log or debug prints
- [ ] No hardcoded secrets
- [ ] Ready for review
```

### Review Process

1. Automated checks must pass
2. Code review by maintainer
3. Medical review if applicable
4. Testing verification
5. Approval and merge

## 🏥 Medical Content Guidelines

### Adding Medical Knowledge

When contributing medical content:

1. **Use Authoritative Sources**
   - Peer-reviewed journals
   - Major textbooks (Harrison's, Oxford, etc.)
   - Clinical guidelines (ACC/AHA, WHO, etc.)
   - UpToDate, DynaMed

2. **Verify Accuracy**
   - Cross-reference multiple sources
   - Use current guidelines
   - Note year of guidelines

3. **Include Context**
   - Patient population
   - Contraindications
   - Special considerations

4. **Stay Updated**
   - Medical knowledge changes
   - Mark date of information
   - Plan for updates

### Medical Disclaimers

Always include appropriate disclaimers:

```python
"""
MEDICAL DISCLAIMER:
This is a clinical decision support tool designed to assist
healthcare professionals. It does not replace:
- Clinical judgment
- Physical examination
- Laboratory tests
- Specialist consultation
- Emergency care

All AI-generated suggestions must be validated by licensed
healthcare professionals before implementation.
"""
```

## 🐛 Bug Reports

### Good Bug Report Template

```markdown
**Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should have happened

**Actual Behavior**
What actually happened

**Screenshots/Logs**
If applicable

**Environment**
- OS: [e.g., Windows 11]
- Python version: [e.g., 3.11]
- OpenAI API: [Yes/No]

**Medical Context**
If bug involves medical logic, provide:
- Medical scenario
- Expected medical outcome
- Reference for expected outcome
```

## 💡 Feature Requests

### Good Feature Request Template

```markdown
**Feature Description**
Clear description of proposed feature

**Problem It Solves**
What clinical problem does this address?

**Proposed Solution**
How should it work?

**Medical Justification**
- Clinical need
- Evidence base
- Guidelines support

**Alternatives Considered**
Other approaches considered

**Additional Context**
Any other information
```

## 🔐 Security

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email repository owner
2. Include detailed description
3. Provide steps to reproduce
4. Allow time for fix before disclosure

### Security Guidelines

- Never commit API keys or secrets
- Use environment variables
- Follow HIPAA guidelines if handling patient data
- Implement proper authentication
- Use HTTPS in production
- Sanitize all inputs

## 📞 Getting Help

### Resources

- **Documentation**: Read all .md files in project
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub Discussions
- **Code**: Read existing code for examples

### Questions

For questions:
1. Check documentation first
2. Search closed issues
3. Open new discussion
4. Be specific and provide context

## 🙏 Thank You!

Your contributions make this project better and help improve medical care through AI. Every contribution, no matter how small, is valued and appreciated!

---

**Happy Contributing!** 🎉

For questions: Open a GitHub Discussion
For bugs: Open a GitHub Issue
For security: Contact repository owner

**Medical AI requires careful, thoughtful development. Thank you for being part of this important work!**
