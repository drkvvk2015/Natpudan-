import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
} from "@mui/material";
import {
  Mic,
  Stop,
  AutoAwesome,
  Save,
  Print,
  ContentCopy,
  CheckCircle,
} from "@mui/icons-material";
import { sendChatMessage } from "../services/api";

interface VoiceInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  multiline?: boolean;
  rows?: number;
  label: string;
}

const VoiceTextField: React.FC<VoiceInputProps> = ({
  value,
  onChange,
  placeholder,
  multiline = false,
  rows = 1,
  label,
}) => {
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);

  useEffect(() => {
    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
      const SpeechRecognition =
        (window as any).webkitSpeechRecognition ||
        (window as any).SpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = true;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = "en-US";

      recognitionInstance.onresult = (event: any) => {
        let interimTranscript = "";
        let finalTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + " ";
          } else {
            interimTranscript += transcript;
          }
        }

        if (finalTranscript) {
          onChange(value + finalTranscript);
        }
      };

      recognitionInstance.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        setIsListening(false);
      };

      recognitionInstance.onend = () => {
        setIsListening(false);
      };

      setRecognition(recognitionInstance);
    }
  }, []);

  const toggleListening = () => {
    if (!recognition) {
      alert(
        "Speech recognition is not supported in this browser. Please use Chrome or Edge."
      );
      return;
    }

    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      recognition.start();
      setIsListening(true);
    }
  };

  return (
    <TextField
      fullWidth
      label={label}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      multiline={multiline}
      rows={rows}
      variant="outlined"
      InputProps={{
        endAdornment: (
          <IconButton
            onClick={toggleListening}
            color={isListening ? "error" : "primary"}
            size="small"
          >
            {isListening ? <Stop /> : <Mic />}
          </IconButton>
        ),
      }}
    />
  );
};

const DischargeSummaryPage: React.FC = () => {
  // Patient Information
  const [patientName, setPatientName] = useState("");
  const [patientAge, setPatientAge] = useState("");
  const [patientGender, setPatientGender] = useState("");
  const [mrn, setMrn] = useState("");
  const [admissionDate, setAdmissionDate] = useState("");
  const [dischargeDate, setDischargeDate] = useState("");

  // Clinical Information
  const [chiefComplaint, setChiefComplaint] = useState("");
  const [historyOfPresentIllness, setHistoryOfPresentIllness] = useState("");
  const [pastMedicalHistory, setPastMedicalHistory] = useState("");
  const [physicalExamination, setPhysicalExamination] = useState("");
  const [diagnosis, setDiagnosis] = useState("");
  const [icd10Codes, setIcd10Codes] = useState<string[]>([]);
  const [icd10SearchQuery, setIcd10SearchQuery] = useState("");
  const [icd10SearchResults, setIcd10SearchResults] = useState<any[]>([]);
  const [isSearchingIcd10, setIsSearchingIcd10] = useState(false);
  const [hospitalCourse, setHospitalCourse] = useState("");
  const [proceduresPerformed, setProceduresPerformed] = useState("");
  const [medications, setMedications] = useState("");
  const [dischargeMedications, setDischargeMedications] = useState("");
  const [followUpInstructions, setFollowUpInstructions] = useState("");
  const [dietRestrictions, setDietRestrictions] = useState("");
  const [activityRestrictions, setActivityRestrictions] = useState("");

  // UI States
  const [isGenerating, setIsGenerating] = useState(false);
  const [aiSuggestion, setAiSuggestion] = useState("");
  const [showAiSuggestion, setShowAiSuggestion] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  // Search ICD-10 codes
  const searchIcd10Codes = async () => {
    if (!icd10SearchQuery.trim()) return;
    
    setIsSearchingIcd10(true);
    try {
      const response = await fetch("/api/discharge-summary/icd10/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          query: icd10SearchQuery,
          max_results: 10,
        }),
      });

      if (!response.ok) throw new Error("Failed to search ICD-10 codes");
      
      const data = await response.json();
      setIcd10SearchResults(data.results || []);
    } catch (error) {
      console.error("ICD-10 search error:", error);
      setErrorMessage("Failed to search ICD-10 codes");
    } finally {
      setIsSearchingIcd10(false);
    }
  };

  // Add ICD-10 code to list
  const addIcd10Code = (code: string) => {
    if (!icd10Codes.includes(code)) {
      setIcd10Codes([...icd10Codes, code]);
    }
    setIcd10SearchQuery("");
    setIcd10SearchResults([]);
  };

  // Remove ICD-10 code
  const removeIcd10Code = (code: string) => {
    setIcd10Codes(icd10Codes.filter(c => c !== code));
  };

  // Auto-suggest ICD-10 codes from diagnosis
  const suggestIcd10FromDiagnosis = async () => {
    if (!diagnosis.trim()) return;
    
    try {
      const response = await fetch("/api/discharge-summary/icd10/suggest", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify(diagnosis),
      });

      if (!response.ok) throw new Error("Failed to suggest ICD-10 codes");
      
      const data = await response.json();
      const suggestions = data.suggestions || [];
      
      // Add suggested codes that aren't already in the list
      const newCodes = suggestions
        .map((s: any) => s.code)
        .filter((code: string) => !icd10Codes.includes(code))
        .slice(0, 3); // Top 3 suggestions
      
      if (newCodes.length > 0) {
        setIcd10Codes([...icd10Codes, ...newCodes]);
      }
    } catch (error) {
      console.error("ICD-10 suggestion error:", error);
    }
  };

  const generateAISummary = async () => {
    setIsGenerating(true);
    setErrorMessage("");
    setShowAiSuggestion(false);

    try {
      const context = `
Patient Information:
- Name: ${patientName || "Not provided"}
- Age: ${patientAge || "Not provided"}
- Gender: ${patientGender || "Not provided"}
- MRN: ${mrn || "Not provided"}
- Admission Date: ${admissionDate || "Not provided"}
- Discharge Date: ${dischargeDate || "Not provided"}

Clinical Details:
- Chief Complaint: ${chiefComplaint || "Not provided"}
- History of Present Illness: ${historyOfPresentIllness || "Not provided"}
- Past Medical History: ${pastMedicalHistory || "Not provided"}
- Physical Examination: ${physicalExamination || "Not provided"}
- Diagnosis: ${diagnosis || "Not provided"}
- Hospital Course: ${hospitalCourse || "Not provided"}
- Procedures: ${proceduresPerformed || "Not provided"}
- Medications During Stay: ${medications || "Not provided"}

Please generate a comprehensive discharge summary based on the above information. Include:
1. A concise summary of the hospital course
2. Suggested discharge medications with dosages
3. Follow-up instructions
4. Diet and activity restrictions
5. Warning signs to watch for

Format the response as a complete discharge summary.
      `;

      const response = await sendChatMessage(context);
      setAiSuggestion(response.message.content);
      setShowAiSuggestion(true);
    } catch (error: any) {
      setErrorMessage(
        error.response?.data?.detail || "Failed to generate AI summary"
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const autoFillFromAI = () => {
    // Parse AI suggestion and auto-fill fields
    // This is a simple implementation - you can enhance with better parsing
    const suggestion = aiSuggestion;

    if (suggestion.includes("Discharge Medications:")) {
      const medsSection = suggestion
        .split("Discharge Medications:")[1]
        ?.split("\n\n")[0];
      if (medsSection) setDischargeMedications(medsSection.trim());
    }

    if (suggestion.includes("Follow-up Instructions:")) {
      const followUpSection = suggestion
        .split("Follow-up Instructions:")[1]
        ?.split("\n\n")[0];
      if (followUpSection) setFollowUpInstructions(followUpSection.trim());
    }

    if (suggestion.includes("Diet:")) {
      const dietSection = suggestion.split("Diet:")[1]?.split("\n\n")[0];
      if (dietSection) setDietRestrictions(dietSection.trim());
    }

    if (suggestion.includes("Activity:")) {
      const activitySection = suggestion
        .split("Activity:")[1]
        ?.split("\n\n")[0];
      if (activitySection) setActivityRestrictions(activitySection.trim());
    }

    setSuccessMessage("AI suggestions applied successfully!");
    setTimeout(() => setSuccessMessage(""), 3000);
  };

  const handleSave = () => {
    // TODO: Implement actual API save logic with icd10_codes
    const summaryData = {
      patient_name: patientName,
      patient_age: patientAge,
      patient_gender: patientGender,
      mrn: mrn,
      admission_date: admissionDate,
      discharge_date: dischargeDate,
      chief_complaint: chiefComplaint,
      history_present_illness: historyOfPresentIllness,
      past_medical_history: pastMedicalHistory,
      physical_examination: physicalExamination,
      diagnosis: diagnosis,
      icd10_codes: icd10Codes,  // Include ICD-10 codes
      hospital_course: hospitalCourse,
      procedures_performed: proceduresPerformed,
      medications: medications,
      discharge_medications: dischargeMedications,
      follow_up_instructions: followUpInstructions,
      diet_restrictions: dietRestrictions,
      activity_restrictions: activityRestrictions,
    };
    
    console.log("Saving discharge summary with data:", summaryData);
    setSuccessMessage("Discharge summary saved successfully!");
    setTimeout(() => setSuccessMessage(""), 3000);
  };

  const handlePrint = () => {
    window.print();
  };

  const handleCopy = () => {
    const summary = `
DISCHARGE SUMMARY

Patient Information:
Name: ${patientName}
Age: ${patientAge}
Gender: ${patientGender}
MRN: ${mrn}
Admission Date: ${admissionDate}
Discharge Date: ${dischargeDate}

Chief Complaint: ${chiefComplaint}

History of Present Illness:
${historyOfPresentIllness}

Past Medical History:
${pastMedicalHistory}

Physical Examination:
${physicalExamination}

Diagnosis:
${diagnosis}

ICD-10 Codes:
${icd10Codes.length > 0 ? icd10Codes.join(", ") : "Not specified"}

Hospital Course:
${hospitalCourse}

Procedures Performed:
${proceduresPerformed}

Medications During Hospital Stay:
${medications}

Discharge Medications:
${dischargeMedications}

Follow-up Instructions:
${followUpInstructions}

Diet Restrictions:
${dietRestrictions}

Activity Restrictions:
${activityRestrictions}
    `;

    navigator.clipboard.writeText(summary);
    setSuccessMessage("Discharge summary copied to clipboard!");
    setTimeout(() => setSuccessMessage(""), 3000);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper
        elevation={3}
        sx={{
          p: 4,
          "@media print": {
            boxShadow: "none",
            padding: 2,
            maxHeight: "none !important",
            overflow: "visible !important",
            "& *": {
              maxHeight: "none !important",
              overflow: "visible !important",
            },
          },
        }}
      >
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 3,
          }}
        >
          <Typography variant="h4" gutterBottom>
            Discharge Summary
          </Typography>
          <Box
            sx={{
              display: "flex",
              gap: 1,
              "@media print": { display: "none" },
            }}
          >
            <Button
              variant="contained"
              startIcon={<AutoAwesome />}
              onClick={generateAISummary}
              disabled={isGenerating}
            >
              {isGenerating ? <CircularProgress size={24} /> : "AI Assist"}
            </Button>
            <Button
              variant="outlined"
              startIcon={<Save />}
              onClick={handleSave}
            >
              Save
            </Button>
            <Button
              variant="outlined"
              startIcon={<Print />}
              onClick={handlePrint}
            >
              Print
            </Button>
            <Button
              variant="outlined"
              startIcon={<ContentCopy />}
              onClick={handleCopy}
            >
              Copy
            </Button>
          </Box>
        </Box>

        {successMessage && (
          <Alert severity="success" sx={{ mb: 2 }} icon={<CheckCircle />}>
            {successMessage}
          </Alert>
        )}

        {errorMessage && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {errorMessage}
          </Alert>
        )}

        {/* AI Suggestion Card */}
        {showAiSuggestion && (
          <Card
            sx={{
              mb: 3,
              bgcolor: "primary.light",
              color: "primary.contrastText",
              "@media print": { display: "none" },
            }}
          >
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 2,
                }}
              >
                <Typography variant="h6">
                  <AutoAwesome sx={{ mr: 1, verticalAlign: "middle" }} />
                  AI Generated Summary
                </Typography>
                <Button
                  variant="contained"
                  color="secondary"
                  size="small"
                  onClick={autoFillFromAI}
                >
                  Auto-Fill Fields
                </Button>
              </Box>
              <Typography
                variant="body2"
                sx={{
                  whiteSpace: "pre-wrap",
                  bgcolor: "background.paper",
                  color: "text.primary",
                  p: 2,
                  borderRadius: 1,
                  maxHeight: 400,
                  overflow: "auto",
                }}
              >
                {aiSuggestion}
              </Typography>
            </CardContent>
          </Card>
        )}

        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mb: 3, "@media print": { display: "none" } }}
        >
          <Chip
            icon={<Mic />}
            label="Click microphone icons to use voice typing"
            size="small"
            sx={{ mr: 1 }}
          />
          Voice typing is available for all text fields
        </Typography>

        {/* Patient Information Section */}
        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          Patient Information
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <VoiceTextField
              label="Patient Name"
              value={patientName}
              onChange={setPatientName}
              placeholder="Enter patient name"
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <VoiceTextField
              label="Age"
              value={patientAge}
              onChange={setPatientAge}
              placeholder="Age"
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <FormControl fullWidth>
              <InputLabel>Gender</InputLabel>
              <Select
                value={patientGender}
                onChange={(e) => setPatientGender(e.target.value)}
                label="Gender"
              >
                <MenuItem value="Male">Male</MenuItem>
                <MenuItem value="Female">Female</MenuItem>
                <MenuItem value="Other">Other</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={4}>
            <VoiceTextField
              label="MRN"
              value={mrn}
              onChange={setMrn}
              placeholder="Medical Record Number"
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              type="date"
              label="Admission Date"
              value={admissionDate}
              onChange={(e) => setAdmissionDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              type="date"
              label="Discharge Date"
              value={dischargeDate}
              onChange={(e) => setDischargeDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
        </Grid>

        {/* Clinical Information Section */}
        <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
          Clinical Information
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <VoiceTextField
              label="Chief Complaint"
              value={chiefComplaint}
              onChange={setChiefComplaint}
              placeholder="Primary reason for admission"
              multiline
              rows={2}
            />
          </Grid>
          <Grid item xs={12}>
            <VoiceTextField
              label="History of Present Illness"
              value={historyOfPresentIllness}
              onChange={setHistoryOfPresentIllness}
              placeholder="Detailed description of the current illness"
              multiline
              rows={4}
            />
          </Grid>
          <Grid item xs={12}>
            <VoiceTextField
              label="Past Medical History"
              value={pastMedicalHistory}
              onChange={setPastMedicalHistory}
              placeholder="Previous medical conditions, surgeries, etc."
              multiline
              rows={3}
            />
          </Grid>
          <Grid item xs={12}>
            <VoiceTextField
              label="Physical Examination Findings"
              value={physicalExamination}
              onChange={setPhysicalExamination}
              placeholder="Physical exam findings on admission"
              multiline
              rows={4}
            />
          </Grid>
          <Grid item xs={12}>
            <VoiceTextField
              label="Diagnosis"
              value={diagnosis}
              onChange={setDiagnosis}
              placeholder="Primary and secondary diagnoses"
              multiline
              rows={2}
            />
          </Grid>
          
          {/* ICD-10 Codes Section */}
          <Grid item xs={12}>
            <Paper elevation={1} sx={{ p: 2, bgcolor: "grey.50" }}>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                ICD-10 Codes
              </Typography>
              
              {/* Selected ICD-10 Codes */}
              {icd10Codes.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Selected Codes:
                  </Typography>
                  <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                    {icd10Codes.map((code) => (
                      <Chip
                        key={code}
                        label={code}
                        onDelete={() => removeIcd10Code(code)}
                        color="primary"
                        size="small"
                      />
                    ))}
                  </Box>
                </Box>
              )}

              {/* ICD-10 Search */}
              <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
                <TextField
                  size="small"
                  fullWidth
                  placeholder="Search ICD-10 codes (e.g., 'diabetes', 'I10', 'pneumonia')"
                  value={icd10SearchQuery}
                  onChange={(e) => setIcd10SearchQuery(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === "Enter") {
                      searchIcd10Codes();
                    }
                  }}
                />
                <Button
                  variant="contained"
                  onClick={searchIcd10Codes}
                  disabled={isSearchingIcd10 || !icd10SearchQuery.trim()}
                  size="small"
                >
                  {isSearchingIcd10 ? <CircularProgress size={20} /> : "Search"}
                </Button>
                <Button
                  variant="outlined"
                  onClick={suggestIcd10FromDiagnosis}
                  disabled={!diagnosis.trim()}
                  size="small"
                  startIcon={<AutoAwesome />}
                >
                  Suggest
                </Button>
              </Box>

              {/* Search Results */}
              {icd10SearchResults.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Search Results:
                  </Typography>
                  <Box sx={{ maxHeight: 200, overflow: "auto" }}>
                    {icd10SearchResults.map((result) => (
                      <Card key={result.code} sx={{ mb: 1 }}>
                        <CardContent sx={{ py: 1, "&:last-child": { pb: 1 } }}>
                          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                            <Box>
                              <Typography variant="body2" fontWeight={600}>
                                {result.code}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {result.description}
                              </Typography>
                            </Box>
                            <Button
                              size="small"
                              onClick={() => addIcd10Code(result.code)}
                              disabled={icd10Codes.includes(result.code)}
                            >
                              {icd10Codes.includes(result.code) ? "Added" : "Add"}
                            </Button>
                          </Box>
                        </CardContent>
                      </Card>
                    ))}
                  </Box>
                </Box>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <VoiceTextField
              label="Hospital Course"
              value={hospitalCourse}
              onChange={setHospitalCourse}
              placeholder="Summary of hospital stay and treatment"
              multiline
              rows={5}
            />
          </Grid>
          <Grid item xs={12}>
            <VoiceTextField
              label="Procedures Performed"
              value={proceduresPerformed}
              onChange={setProceduresPerformed}
              placeholder="List all procedures performed during stay"
              multiline
              rows={3}
            />
          </Grid>
          <Grid item xs={12}>
            <VoiceTextField
              label="Medications During Hospital Stay"
              value={medications}
              onChange={setMedications}
              placeholder="Medications administered during hospitalization"
              multiline
              rows={4}
            />
          </Grid>
        </Grid>

        {/* Discharge Information Section */}
        <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
          Discharge Information
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <VoiceTextField
              label="Discharge Medications"
              value={dischargeMedications}
              onChange={setDischargeMedications}
              placeholder="Medications to continue at home with dosages"
              multiline
              rows={5}
            />
          </Grid>
          <Grid item xs={12}>
            <VoiceTextField
              label="Follow-up Instructions"
              value={followUpInstructions}
              onChange={setFollowUpInstructions}
              placeholder="Follow-up appointments and instructions"
              multiline
              rows={4}
            />
          </Grid>
          <Grid item xs={12}>
            <VoiceTextField
              label="Diet Restrictions"
              value={dietRestrictions}
              onChange={setDietRestrictions}
              placeholder="Dietary recommendations and restrictions"
              multiline
              rows={3}
            />
          </Grid>
          <Grid item xs={12}>
            <VoiceTextField
              label="Activity Restrictions"
              value={activityRestrictions}
              onChange={setActivityRestrictions}
              placeholder="Activity limitations and recommendations"
              multiline
              rows={3}
            />
          </Grid>
        </Grid>

        <Box
          sx={{
            mt: 4,
            display: "flex",
            justifyContent: "flex-end",
            gap: 2,
            "@media print": { display: "none" },
          }}
        >
          <Button variant="outlined" size="large">
            Cancel
          </Button>
          <Button
            variant="contained"
            size="large"
            startIcon={<Save />}
            onClick={handleSave}
          >
            Save Discharge Summary
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default DischargeSummaryPage;
