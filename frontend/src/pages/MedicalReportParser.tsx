import React, { useState } from 'react'
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  Divider,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material'
import {
  CloudUpload,
  ExpandMore,
  Favorite,
  LocalHospital,
  Science,
  MedicalServices,
  Warning,
  CheckCircle,
} from '@mui/icons-material'
import { parseMedicalReport } from '../services/api'

interface VitalSigns {
  blood_pressure?: string
  heart_rate?: number
  temperature?: number
  respiratory_rate?: number
  oxygen_saturation?: number
  height?: string
  weight?: number
  bmi?: number
}

interface Medication {
  name: string
  dose?: string
  frequency?: string
  route?: string
}

interface LabResult {
  test: string
  value: string
  unit?: string
  reference_range?: string
}

interface Diagnosis {
  description: string
  icd10_code?: string
}

interface Allergy {
  allergen: string
  reaction?: string
  severity?: string
}

interface ParsedReport {
  vitals: VitalSigns
  medications: Medication[]
  lab_results: LabResult[]
  diagnoses: Diagnosis[]
  allergies: Allergy[]
}

const MedicalReportParser: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [parsedData, setParsedData] = useState<ParsedReport | null>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (file.type !== 'application/pdf') {
        setError('Please select a PDF file')
        return
      }
      setSelectedFile(file)
      setError(null)
      setParsedData(null)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const data = await parseMedicalReport(selectedFile)
      setParsedData(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to parse medical report. Please try again.')
      console.error('Parse error:', err)
    } finally {
      setLoading(false)
    }
  }

  const hasData = (arr: any[] | undefined) => arr && arr.length > 0

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h3"
          gutterBottom
          sx={{
            fontWeight: 700,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 1,
          }}
        >
          📋 Medical Report Parser
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 800 }}>
          Upload a PDF medical report to automatically extract structured data including vital signs,
          medications, lab results, diagnoses, and allergies using AI-powered analysis.
        </Typography>
      </Box>

      {/* Upload Section */}
      <Paper sx={{ p: 4, mb: 4 }}>
        <Box sx={{ textAlign: 'center' }}>
          <input
            accept="application/pdf"
            style={{ display: 'none' }}
            id="pdf-upload"
            type="file"
            onChange={handleFileSelect}
          />
          <label htmlFor="pdf-upload">
            <Button
              variant="outlined"
              component="span"
              startIcon={<CloudUpload />}
              size="large"
              sx={{ mr: 2, mb: 2 }}
            >
              Select PDF Report
            </Button>
          </label>

          {selectedFile && (
            <Box sx={{ mt: 2, mb: 2 }}>
              <Chip
                label={selectedFile.name}
                onDelete={() => setSelectedFile(null)}
                color="primary"
                sx={{ fontSize: '0.9rem', py: 2.5 }}
              />
            </Box>
          )}

          <Button
            variant="contained"
            size="large"
            onClick={handleUpload}
            disabled={!selectedFile || loading}
            startIcon={loading ? <CircularProgress size={20} /> : <MedicalServices />}
            sx={{ mb: 2 }}
          >
            {loading ? 'Parsing Report...' : 'Parse Report'}
          </Button>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </Box>
      </Paper>

      {/* Results Section */}
      {parsedData && (
        <Box>
          <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 600 }}>
            📊 Parsed Results
          </Typography>

          {/* Vital Signs */}
          {hasData(Object.keys(parsedData.vitals).filter(key => parsedData.vitals[key as keyof VitalSigns])) && (
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Favorite color="error" />
                  <Typography variant="h6">Vital Signs</Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  {parsedData.vitals.blood_pressure && (
                    <Grid item xs={12} sm={6} md={4}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography color="text.secondary" variant="body2">
                            Blood Pressure
                          </Typography>
                          <Typography variant="h6">{parsedData.vitals.blood_pressure}</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  )}
                  {parsedData.vitals.heart_rate && (
                    <Grid item xs={12} sm={6} md={4}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography color="text.secondary" variant="body2">
                            Heart Rate
                          </Typography>
                          <Typography variant="h6">{parsedData.vitals.heart_rate} bpm</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  )}
                  {parsedData.vitals.temperature && (
                    <Grid item xs={12} sm={6} md={4}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography color="text.secondary" variant="body2">
                            Temperature
                          </Typography>
                          <Typography variant="h6">{parsedData.vitals.temperature}°F</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  )}
                  {parsedData.vitals.respiratory_rate && (
                    <Grid item xs={12} sm={6} md={4}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography color="text.secondary" variant="body2">
                            Respiratory Rate
                          </Typography>
                          <Typography variant="h6">{parsedData.vitals.respiratory_rate} /min</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  )}
                  {parsedData.vitals.oxygen_saturation && (
                    <Grid item xs={12} sm={6} md={4}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography color="text.secondary" variant="body2">
                            SpO2
                          </Typography>
                          <Typography variant="h6">{parsedData.vitals.oxygen_saturation}%</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  )}
                  {parsedData.vitals.height && (
                    <Grid item xs={12} sm={6} md={4}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography color="text.secondary" variant="body2">
                            Height
                          </Typography>
                          <Typography variant="h6">{parsedData.vitals.height}</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  )}
                  {parsedData.vitals.weight && (
                    <Grid item xs={12} sm={6} md={4}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography color="text.secondary" variant="body2">
                            Weight
                          </Typography>
                          <Typography variant="h6">{parsedData.vitals.weight} lbs</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  )}
                  {parsedData.vitals.bmi && (
                    <Grid item xs={12} sm={6} md={4}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography color="text.secondary" variant="body2">
                            BMI
                          </Typography>
                          <Typography variant="h6">{parsedData.vitals.bmi}</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  )}
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Medications */}
          {hasData(parsedData.medications) && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LocalHospital color="primary" />
                  <Typography variant="h6">
                    Medications ({parsedData.medications.length})
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Medication</TableCell>
                        <TableCell>Dose</TableCell>
                        <TableCell>Frequency</TableCell>
                        <TableCell>Route</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {parsedData.medications.map((med, index) => (
                        <TableRow key={index}>
                          <TableCell sx={{ fontWeight: 600 }}>{med.name}</TableCell>
                          <TableCell>{med.dose || '-'}</TableCell>
                          <TableCell>{med.frequency || '-'}</TableCell>
                          <TableCell>{med.route || '-'}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Lab Results */}
          {hasData(parsedData.lab_results) && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Science color="secondary" />
                  <Typography variant="h6">
                    Lab Results ({parsedData.lab_results.length})
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Test</TableCell>
                        <TableCell>Value</TableCell>
                        <TableCell>Unit</TableCell>
                        <TableCell>Reference Range</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {parsedData.lab_results.map((lab, index) => (
                        <TableRow key={index}>
                          <TableCell sx={{ fontWeight: 600 }}>{lab.test}</TableCell>
                          <TableCell>{lab.value}</TableCell>
                          <TableCell>{lab.unit || '-'}</TableCell>
                          <TableCell>{lab.reference_range || '-'}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Diagnoses */}
          {hasData(parsedData.diagnoses) && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircle color="success" />
                  <Typography variant="h6">
                    Diagnoses ({parsedData.diagnoses.length})
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  {parsedData.diagnoses.map((diagnosis, index) => (
                    <Grid item xs={12} key={index}>
                      <Card variant="outlined">
                        <CardContent>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="body1" sx={{ fontWeight: 600 }}>
                              {diagnosis.description}
                            </Typography>
                            {diagnosis.icd10_code && (
                              <Chip label={`ICD-10: ${diagnosis.icd10_code}`} size="small" color="info" />
                            )}
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Allergies */}
          {hasData(parsedData.allergies) && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Warning color="warning" />
                  <Typography variant="h6">
                    Allergies ({parsedData.allergies.length})
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Allergen</TableCell>
                        <TableCell>Reaction</TableCell>
                        <TableCell>Severity</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {parsedData.allergies.map((allergy, index) => (
                        <TableRow key={index}>
                          <TableCell sx={{ fontWeight: 600 }}>{allergy.allergen}</TableCell>
                          <TableCell>{allergy.reaction || '-'}</TableCell>
                          <TableCell>
                            {allergy.severity ? (
                              <Chip
                                label={allergy.severity}
                                size="small"
                                color={
                                  allergy.severity.toLowerCase() === 'severe'
                                    ? 'error'
                                    : allergy.severity.toLowerCase() === 'moderate'
                                    ? 'warning'
                                    : 'default'
                                }
                              />
                            ) : (
                              '-'
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </AccordionDetails>
            </Accordion>
          )}

          {/* No Data Message */}
          {!hasData(Object.keys(parsedData.vitals).filter(key => parsedData.vitals[key as keyof VitalSigns])) &&
            !hasData(parsedData.medications) &&
            !hasData(parsedData.lab_results) &&
            !hasData(parsedData.diagnoses) &&
            !hasData(parsedData.allergies) && (
              <Alert severity="info" sx={{ mt: 2 }}>
                No structured medical data was extracted from this report. The report may not contain
                recognizable medical information or may be in an unsupported format.
              </Alert>
            )}
        </Box>
      )}
    </Container>
  )
}

export default MedicalReportParser
