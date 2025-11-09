import React, { useState, useEffect } from 'react'
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  Card,
  CardContent,
  Tabs,
  Tab,
  Chip,
  Divider,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material'
import {
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  Person as PersonIcon,
  LocalHospital as HospitalIcon,
  Medication as MedicationIcon,
  EventNote as EventIcon,
  Info as InfoIcon
} from '@mui/icons-material'
import {
  getFHIRPatient,
  searchFHIRPatients,
  searchFHIRConditions,
  searchFHIRMedications,
  getFHIRCapabilityStatement,
  FHIRBundle
} from '../services/api'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

const FHIRExplorer: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Search states
  const [patientSearchName, setPatientSearchName] = useState('')
  const [patientSearchId, setPatientSearchId] = useState('')
  const [patientResults, setPatientResults] = useState<FHIRBundle | null>(null)
  
  const [conditionPatientId, setConditionPatientId] = useState('')
  const [conditionResults, setConditionResults] = useState<FHIRBundle | null>(null)
  
  const [medicationPatientId, setMedicationPatientId] = useState('')
  const [medicationResults, setMedicationResults] = useState<FHIRBundle | null>(null)
  
  const [capabilityStatement, setCapabilityStatement] = useState<any>(null)

  // Fetch capability statement on mount
  useEffect(() => {
    fetchCapabilityStatement()
  }, [])

  const fetchCapabilityStatement = async () => {
    try {
      const data = await getFHIRCapabilityStatement()
      setCapabilityStatement(data)
    } catch (err) {
      console.error('Error fetching capability statement:', err)
    }
  }

  const handleSearchPatients = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = {
        name: patientSearchName || undefined,
        identifier: patientSearchId || undefined
      }
      const data = await searchFHIRPatients(params)
      setPatientResults(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to search patients')
    } finally {
      setLoading(false)
    }
  }

  const handleSearchConditions = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await searchFHIRConditions(conditionPatientId || undefined)
      setConditionResults(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to search conditions')
    } finally {
      setLoading(false)
    }
  }

  const handleSearchMedications = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await searchFHIRMedications(medicationPatientId || undefined)
      setMedicationResults(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to search medications')
    } finally {
      setLoading(false)
    }
  }

  const renderJSON = (obj: any) => {
    return (
      <Box
        component="pre"
        sx={{
          bgcolor: '#f5f5f5',
          p: 2,
          borderRadius: 1,
          overflow: 'auto',
          fontSize: '0.875rem'
        }}
      >
        {JSON.stringify(obj, null, 2)}
      </Box>
    )
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          <InfoIcon sx={{ mr: 1, verticalAlign: 'middle', fontSize: 40 }} />
          FHIR API Explorer
        </Typography>
        <Typography variant="body2" color="text.secondary">
          HL7 FHIR R4 compliant API for healthcare data interoperability
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Tabs */}
      <Paper elevation={3}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab icon={<PersonIcon />} label="Patients" />
          <Tab icon={<HospitalIcon />} label="Conditions" />
          <Tab icon={<MedicationIcon />} label="Medications" />
          <Tab icon={<InfoIcon />} label="Capability" />
        </Tabs>

        {/* Patient Search */}
        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Search by Name"
                value={patientSearchName}
                onChange={(e) => setPatientSearchName(e.target.value)}
                placeholder="Enter patient name"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Search by Identifier"
                value={patientSearchId}
                onChange={(e) => setPatientSearchId(e.target.value)}
                placeholder="Enter UHID or Intake ID"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                fullWidth
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                onClick={handleSearchPatients}
                disabled={loading}
                sx={{ height: 56 }}
              >
                Search Patients
              </Button>
            </Grid>
          </Grid>

          {patientResults && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Results: {patientResults.total} patients found
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {patientResults.entry.map((entry, index) => (
                <Accordion key={index}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box display="flex" alignItems="center" gap={2}>
                      <PersonIcon color="primary" />
                      <Box>
                        <Typography variant="subtitle1">
                          {entry.resource.name?.[0]?.text || 'Unknown'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          ID: {entry.resource.id} | Gender: {entry.resource.gender || 'N/A'}
                        </Typography>
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    {renderJSON(entry.resource)}
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          )}
        </TabPanel>

        {/* Condition Search */}
        <TabPanel value={activeTab} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Filter by Patient ID"
                value={conditionPatientId}
                onChange={(e) => setConditionPatientId(e.target.value)}
                placeholder="Enter patient intake ID (optional)"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                fullWidth
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                onClick={handleSearchConditions}
                disabled={loading}
                sx={{ height: 56 }}
              >
                Search Conditions
              </Button>
            </Grid>
          </Grid>

          {conditionResults && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Results: {conditionResults.total} conditions found
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {conditionResults.entry.map((entry, index) => (
                <Accordion key={index}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box display="flex" alignItems="center" gap={2}>
                      <HospitalIcon color="error" />
                      <Box>
                        <Typography variant="subtitle1">
                          {entry.resource.code?.text || 'Unknown Condition'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          ICD-10: {entry.resource.code?.coding?.[0]?.code || 'N/A'} | 
                          Status: {entry.resource.clinicalStatus?.coding?.[0]?.code || 'N/A'}
                        </Typography>
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    {renderJSON(entry.resource)}
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          )}
        </TabPanel>

        {/* Medication Search */}
        <TabPanel value={activeTab} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Filter by Patient ID"
                value={medicationPatientId}
                onChange={(e) => setMedicationPatientId(e.target.value)}
                placeholder="Enter patient intake ID (optional)"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                fullWidth
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                onClick={handleSearchMedications}
                disabled={loading}
                sx={{ height: 56 }}
              >
                Search Medications
              </Button>
            </Grid>
          </Grid>

          {medicationResults && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Results: {medicationResults.total} medications found
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {medicationResults.entry.map((entry, index) => (
                <Accordion key={index}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box display="flex" alignItems="center" gap={2}>
                      <MedicationIcon color="success" />
                      <Box>
                        <Typography variant="subtitle1">
                          {entry.resource.medicationCodeableConcept?.text || 'Unknown Medication'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Status: {entry.resource.status || 'N/A'}
                        </Typography>
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    {renderJSON(entry.resource)}
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          )}
        </TabPanel>

        {/* Capability Statement */}
        <TabPanel value={activeTab} index={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Server Capability Statement
              </Typography>
              <Divider sx={{ my: 2 }} />
              
              {capabilityStatement && (
                <>
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">Status:</Typography>
                      <Chip label={capabilityStatement.status} color="success" size="small" />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">FHIR Version:</Typography>
                      <Chip label={capabilityStatement.fhirVersion} color="primary" size="small" />
                    </Grid>
                  </Grid>

                  <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                    Supported Resources:
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    {capabilityStatement.rest?.[0]?.resource?.map((resource: any, index: number) => (
                      <Chip
                        key={index}
                        label={resource.type}
                        size="small"
                        sx={{ mr: 1, mb: 1 }}
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                  </Box>

                  <Typography variant="subtitle2" gutterBottom sx={{ mt: 3 }}>
                    Full Capability Statement:
                  </Typography>
                  {renderJSON(capabilityStatement)}
                </>
              )}
            </CardContent>
          </Card>
        </TabPanel>
      </Paper>

      {/* Info Card */}
      <Paper elevation={2} sx={{ p: 3, mt: 3, bgcolor: '#f0f9ff' }}>
        <Typography variant="h6" gutterBottom>
          About FHIR Integration
        </Typography>
        <Typography variant="body2" paragraph>
          This system implements HL7 FHIR R4 (Fast Healthcare Interoperability Resources) standard for healthcare data exchange.
        </Typography>
        <Typography variant="body2">
          <strong>Supported Resources:</strong> Patient, Condition, MedicationRequest, Appointment
        </Typography>
        <Typography variant="body2">
          <strong>Supported Operations:</strong> Read, Search
        </Typography>
        <Typography variant="body2">
          <strong>Base URL:</strong> /api/fhir/
        </Typography>
      </Paper>
    </Container>
  )
}

export default FHIRExplorer
