# Natpudan - AI Clinical Assistant

An AI-powered clinical assistant designed to support doctors and healthcare professionals in their daily practice. Natpudan provides intelligent tools for symptom analysis, drug interaction checking, medical reference lookup, and patient management.

## Features

### 🔍 AI Symptom Checker
- Analyzes patient symptoms using medical knowledge base
- Provides differential diagnosis suggestions
- Considers age and gender factors
- Confidence-based scoring system

### 💊 Drug Interaction Checker
- Checks for potential drug-drug interactions
- Severity-based warnings (High, Medium, Low)
- Comprehensive interaction database
- Safety recommendations

### 📚 Medical Reference
- Quick lookup of medical conditions
- Detailed information on symptoms, treatments, and monitoring
- Searchable medical database
- Clinical guidelines and definitions

### 👨‍⚕️ Patient Management
- Secure patient note storage
- Organized patient records
- Easy access to clinical notes
- Timestamped entries

## Getting Started

### Installation
1. Clone or download the repository
2. Open `index.html` in a modern web browser
3. No additional installation required - pure web application

### Usage

#### Symptom Analysis
1. Navigate to the "Symptom Checker" tab
2. Enter detailed patient symptoms
3. Provide age and gender if available
4. Click "Analyze Symptoms" for AI-powered differential diagnosis

#### Drug Interactions
1. Go to "Drug Interactions" tab
2. Enter medication names (one per line)
3. Click "Check Interactions" to identify potential conflicts
4. Review severity levels and recommendations

#### Medical Reference
1. Select "Medical Reference" tab
2. Search for medical conditions or terms
3. Access detailed clinical information
4. Review treatment guidelines and monitoring requirements

#### Patient Notes
1. Navigate to "Patient Notes" tab
2. Enter patient ID, name, and clinical notes
3. Save notes for future reference
4. View all stored patient records

## Technical Details

### Architecture
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Responsive design with CSS Grid and Flexbox
- **Data Storage**: Local browser storage (localStorage)
- **Icons**: Font Awesome 6.0

### Browser Compatibility
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

### Security Considerations
- Patient data stored locally in browser
- No external data transmission
- HIPAA compliance considerations for production use
- Implement proper authentication for clinical environments

## Medical Disclaimer

⚠️ **Important Medical Disclaimer**

This AI clinical assistant is designed as a support tool for healthcare professionals and should NOT replace:
- Clinical judgment and expertise
- Proper medical examination
- Laboratory tests and diagnostic procedures
- Professional medical consultation
- Emergency medical care

Always verify information with current medical literature and consult with specialists when appropriate.

## Development

### File Structure
```
Natpudan-/
├── index.html          # Main application interface
├── styles.css          # Application styling
├── script.js           # JavaScript functionality
├── README.md           # Documentation
└── LICENSE            # GPL v3 License
```

### Extending the Knowledge Base
The medical knowledge base is stored in the `medicalKnowledge` object in `script.js`. To add new information:

1. **Symptoms**: Add entries to `symptoms` object
2. **Drug Interactions**: Add entries to `drugInteractions` object  
3. **Medical Info**: Add entries to `medicalInfo` object

### Customization
- Modify `styles.css` for visual customization
- Update `medicalKnowledge` in `script.js` for medical content
- Extend functionality by adding new sections to `index.html`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contact

For questions, suggestions, or medical content contributions, please open an issue in the repository.

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Medical Knowledge Base**: Basic clinical reference (expand for production use)
