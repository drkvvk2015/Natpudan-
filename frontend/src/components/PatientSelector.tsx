import React, { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  IconButton,
  InputAdornment,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  Search as SearchIcon,
  Close as CloseIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material'
import { listPatientIntakes } from '../services/api'
import { RiskBadge } from './RiskAssessment'

interface Patient {
  intake_id: string
  name: string
  age: string
  gender: string
  blood_type: string
  created_at: string
  travel_history?: any[]
  family_history?: any[]
  risk_level?: 'low' | 'medium' | 'high' | 'critical'
}

interface PatientSelectorProps {
  open: boolean
  onClose: () => void
  onSelectPatient: (patient: Patient) => void
}

const PatientSelector: React.FC<PatientSelectorProps> = ({ open, onClose, onSelectPatient }) => {
  const [patients, setPatients] = useState<Patient[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filteredPatients, setFilteredPatients] = useState<Patient[]>([])

  useEffect(() => {
    if (open) {
      loadPatients()
    }
  }, [open])

  useEffect(() => {
    if (searchTerm) {
      const filtered = patients.filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.intake_id.toLowerCase().includes(searchTerm.toLowerCase())
      )
      setFilteredPatients(filtered)
    } else {
      setFilteredPatients(patients)
    }
  }, [searchTerm, patients])

  const loadPatients = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await listPatientIntakes({ limit: 100, sort_by: 'created_at', order: 'desc' })
      setPatients(response.patients as any)
      setFilteredPatients(response.patients as any)
    } catch (err) {
      console.error('Failed to load patients:', err)
      setError('Failed to load patients. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectPatient = (patient: Patient) => {
    onSelectPatient(patient)
    onClose()
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            Select Patient
          </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent dividers>
        <Box sx={{ mb: 2 }}>
          <TextField
            fullWidth
            placeholder="Search by name or patient ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            size="small"
          />
        </Box>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {!loading && !error && filteredPatients.length === 0 && (
          <Alert severity="info">
            No patients found. {searchTerm && 'Try a different search term.'}
          </Alert>
        )}

        {!loading && !error && filteredPatients.length > 0 && (
          <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 400 }}>
            <Table stickyHeader size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 700, bgcolor: '#f5f7fa' }}>Patient ID</TableCell>
                  <TableCell sx={{ fontWeight: 700, bgcolor: '#f5f7fa' }}>Name</TableCell>
                  <TableCell sx={{ fontWeight: 700, bgcolor: '#f5f7fa' }}>Age/Gender</TableCell>
                  <TableCell sx={{ fontWeight: 700, bgcolor: '#f5f7fa' }}>Blood Type</TableCell>
                  <TableCell sx={{ fontWeight: 700, bgcolor: '#f5f7fa' }}>Risk</TableCell>
                  <TableCell sx={{ fontWeight: 700, bgcolor: '#f5f7fa' }}>Date</TableCell>
                  <TableCell sx={{ fontWeight: 700, bgcolor: '#f5f7fa' }} align="center">Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredPatients.map((patient) => (
                  <TableRow
                    key={patient.intake_id}
                    hover
                    sx={{ 
                      cursor: 'pointer',
                      '&:hover': { bgcolor: '#f5f7fa' }
                    }}
                    onClick={() => handleSelectPatient(patient)}
                  >
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                        {patient.intake_id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {patient.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {patient.age} / {patient.gender}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={patient.blood_type || 'Unknown'}
                        size="small"
                        variant="outlined"
                        sx={{ fontSize: '0.75rem' }}
                      />
                    </TableCell>
                    <TableCell>
                      {patient.risk_level && <RiskBadge level={patient.risk_level} size="small" />}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {formatDate(patient.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Button
                        size="small"
                        variant="contained"
                        startIcon={<CheckCircleIcon />}
                        onClick={(e) => {
                          e.stopPropagation()
                          handleSelectPatient(patient)
                        }}
                      >
                        Select
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} color="inherit">
          Cancel
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default PatientSelector
