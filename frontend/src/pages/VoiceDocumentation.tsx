import React, { useState, useRef, useEffect } from "react";
import {
  Container,
  Paper,
  Box,
  Button,
  TextField,
  Typography,
  Card,
  CardContent,
  Divider,
  Grid,
  LinearProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from "@mui/material";
import {
  Mic,
  Stop,
  Upload,
  Close,
  CheckCircle,
  Error as ErrorIcon,
} from "@mui/icons-material";
import axios from "axios";

interface MedicalEntity {
  text: string;
  confidence: number;
}

interface SOAPNote {
  subjective: {
    chief_complaint: string;
    history_present_illness: string;
    medications: string[];
  };
  objective: {
    vital_signs: Record<string, number>;
    physical_examination: string;
  };
  assessment: {
    assessment: string;
    differential_diagnoses: string[];
  };
  plan: {
    medications: Array<{ name: string; dose: string; frequency: string }>;
    follow_up: { timeframe: string };
  };
}

interface TranscriptionResult {
  recording_id: string;
  raw_transcription: string;
  medical_entities: {
    symptoms: MedicalEntity[];
    medications: MedicalEntity[];
    conditions: MedicalEntity[];
  };
  soap_note_preview: SOAPNote;
  transcription_confidence: number;
  created_at: string;
}

const VoiceDocumentation: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [transcript, setTranscript] = useState("");
  const [soapNote, setSoapNote] = useState<SOAPNote | null>(null);
  const [entities, setEntities] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [editedTranscript, setEditedTranscript] = useState("");
  const [recordingId, setRecordingId] = useState("");

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isRecording]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.ondataavailable = (event: BlobEvent) => {
        audioChunksRef.current.push(event.data);
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/wav",
        });
        await uploadRecording(audioBlob);
      };

      recorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      setError("");
    } catch (err: any) {
      setError("Failed to access microphone: " + err.message);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const uploadRecording = async (audioBlob: Blob) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", audioBlob, "recording.wav");

      const response = await axios.post<TranscriptionResult>(
        "/api/voice/upload",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      const result = response.data;
      setRecordingId(result.recording_id);
      setTranscript(result.raw_transcription);
      setEditedTranscript(result.raw_transcription);
      setEntities(result.medical_entities);
      setSoapNote(result.soap_note_preview);
      setSuccess("Voice recording transcribed successfully!");
    } catch (err: any) {
      setError("Failed to upload recording: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const generateDocumentation = async () => {
    if (!recordingId) return;

    setLoading(true);
    try {
      const response = await axios.post("/api/voice/generate-documentation", {
        recording_id: recordingId,
        edited_transcription: editedTranscript,
      });

      setSuccess(
        `Discharge summary created: #${response.data.discharge_summary_id}`
      );
      setSoapNote(response.data.soap_note);
    } catch (err: any) {
      setError("Failed to generate documentation: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: "bold" }}>
        Voice Documentation
      </Typography>

      <Grid container spacing={3}>
        {/* Recording Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Record Consultation
            </Typography>

            <Box
              sx={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                flexDirection: "column",
                gap: 2,
                py: 4,
                border: "2px dashed #1976d2",
                borderRadius: 2,
                bgcolor: "#f5f5f5",
              }}
            >
              {isRecording ? (
                <>
                  <Box
                    sx={{
                      width: 80,
                      height: 80,
                      borderRadius: "50%",
                      bgcolor: "#ff4444",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      animation: "pulse 1s infinite",
                      "@keyframes pulse": {
                        "0%, 100%": { opacity: 1 },
                        "50%": { opacity: 0.5 },
                      },
                    }}
                  >
                    <Mic sx={{ color: "white", fontSize: 40 }} />
                  </Box>
                  <Typography variant="h6">{formatTime(recordingTime)}</Typography>
                  <Button
                    variant="contained"
                    color="error"
                    startIcon={<Stop />}
                    onClick={stopRecording}
                  >
                    Stop Recording
                  </Button>
                </>
              ) : (
                <>
                  <Mic sx={{ fontSize: 60, color: "#1976d2" }} />
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<Mic />}
                    onClick={startRecording}
                    disabled={loading}
                  >
                    Start Recording
                  </Button>
                </>
              )}
            </Box>

            {loading && (
              <Box sx={{ mt: 3 }}>
                <LinearProgress />
                <Typography sx={{ mt: 1, textAlign: "center" }}>
                  Processing audio...
                </Typography>
              </Box>
            )}

            {error && (
              <Alert severity="error" sx={{ mt: 3 }} onClose={() => setError("")}>
                {error}
              </Alert>
            )}
            {success && (
              <Alert severity="success" sx={{ mt: 3 }} onClose={() => setSuccess("")}>
                {success}
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Entities Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Extracted Medical Entities
            </Typography>

            {entities ? (
              <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                {entities.symptoms && entities.symptoms.length > 0 && (
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: "bold", mb: 1 }}>
                      Symptoms
                    </Typography>
                    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                      {entities.symptoms.map((s: MedicalEntity, i: number) => (
                        <Chip
                          key={i}
                          label={s.text}
                          color="primary"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>
                )}

                {entities.medications && entities.medications.length > 0 && (
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: "bold", mb: 1 }}>
                      Medications
                    </Typography>
                    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                      {entities.medications.map((m: MedicalEntity, i: number) => (
                        <Chip
                          key={i}
                          label={m.text}
                          color="success"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>
                )}

                {entities.conditions && entities.conditions.length > 0 && (
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: "bold", mb: 1 }}>
                      Conditions
                    </Typography>
                    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                      {entities.conditions.map((c: MedicalEntity, i: number) => (
                        <Chip
                          key={i}
                          label={c.text}
                          color="error"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </Box>
            ) : (
              <Typography variant="body2" sx={{ color: "text.secondary" }}>
                No entities extracted yet
              </Typography>
            )}
          </Paper>
        </Grid>

        {/* Transcription Section */}
        {transcript && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Raw Transcription
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={4}
                value={editedTranscript}
                onChange={(e) => setEditedTranscript(e.target.value)}
                variant="outlined"
                placeholder="Edit transcription if needed..."
              />
              <Typography variant="caption" sx={{ display: "block", mt: 1 }}>
                Confidence: {((entities?.transcription_confidence || 0) * 100).toFixed(1)}%
              </Typography>
            </Paper>
          </Grid>
        )}

        {/* SOAP Note Preview */}
        {soapNote && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                SOAP Note Preview
              </Typography>

              <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                {/* Subjective */}
                <Card>
                  <CardContent>
                    <Typography
                      variant="subtitle1"
                      sx={{ fontWeight: "bold", mb: 1 }}
                    >
                      Subjective
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Chief Complaint:</strong>{" "}
                      {soapNote.subjective.chief_complaint}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>HPI:</strong>{" "}
                      {soapNote.subjective.history_present_illness}
                    </Typography>
                    {soapNote.subjective.medications.length > 0 && (
                      <Typography variant="body2">
                        <strong>Medications:</strong>{" "}
                        {soapNote.subjective.medications.join(", ")}
                      </Typography>
                    )}
                  </CardContent>
                </Card>

                {/* Objective */}
                <Card>
                  <CardContent>
                    <Typography
                      variant="subtitle1"
                      sx={{ fontWeight: "bold", mb: 1 }}
                    >
                      Objective
                    </Typography>
                    {Object.keys(soapNote.objective.vital_signs).length > 0 && (
                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Vital Sign</TableCell>
                              <TableCell align="right">Value</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {Object.entries(soapNote.objective.vital_signs).map(
                              ([key, value]) => (
                                <TableRow key={key}>
                                  <TableCell>{key}</TableCell>
                                  <TableCell align="right">{value}</TableCell>
                                </TableRow>
                              )
                            )}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    )}
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      <strong>Physical Exam:</strong>{" "}
                      {soapNote.objective.physical_examination}
                    </Typography>
                  </CardContent>
                </Card>

                {/* Assessment */}
                <Card>
                  <CardContent>
                    <Typography
                      variant="subtitle1"
                      sx={{ fontWeight: "bold", mb: 1 }}
                    >
                      Assessment
                    </Typography>
                    <Typography variant="body2">
                      {soapNote.assessment.assessment}
                    </Typography>
                    {soapNote.assessment.differential_diagnoses.length > 0 && (
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        <strong>Differential:</strong>{" "}
                        {soapNote.assessment.differential_diagnoses.join(", ")}
                      </Typography>
                    )}
                  </CardContent>
                </Card>

                {/* Plan */}
                <Card>
                  <CardContent>
                    <Typography
                      variant="subtitle1"
                      sx={{ fontWeight: "bold", mb: 1 }}
                    >
                      Plan
                    </Typography>
                    {soapNote.plan.medications.length > 0 && (
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="body2">
                          <strong>Medications:</strong>
                        </Typography>
                        <Typography variant="body2" sx={{ pl: 2 }}>
                          {soapNote.plan.medications
                            .map((m) => `${m.name} (${m.dose}, ${m.frequency})`)
                            .join("\n")}
                        </Typography>
                      </Box>
                    )}
                    <Typography variant="body2">
                      <strong>Follow-up:</strong> {soapNote.plan.follow_up.timeframe}
                    </Typography>
                  </CardContent>
                </Card>
              </Box>

              {recordingId && (
                <Button
                  variant="contained"
                  color="success"
                  onClick={generateDocumentation}
                  disabled={loading}
                  sx={{ mt: 3 }}
                >
                  Generate Final Documentation
                </Button>
              )}
            </Paper>
          </Grid>
        )}
      </Grid>
    </Container>
  );
};

export default VoiceDocumentation;
