import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Chip,
  Collapse,
  IconButton,
  FormGroup,
  FormControlLabel,
  Checkbox,
  TextField,
  Alert,
  CircularProgress,
  Grid
} from '@mui/material'
// Removed dependency on @mui/lab Timeline components to avoid extra peer version requirements.
import {
  PersonAdd as PersonAddIcon,
  Flight as FlightIcon,
  FamilyRestroom as FamilyRestroomIcon,
  LocalHospital as LocalHospitalIcon,
  Medication as MedicationIcon,
  EventNote as EventNoteIcon,
  MonitorHeart as MonitorHeartIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  FilterList as FilterListIcon
} from '@mui/icons-material'
import { getPatientTimeline, getEventTypes, TimelineEvent, EventType } from '../services/api'

interface MedicalTimelineProps {
  patientIntakeId: string
}

const MedicalTimeline: React.FC<MedicalTimelineProps> = ({ patientIntakeId }) => {
  const [events, setEvents] = useState<TimelineEvent[]>([])
  const [patientName, setPatientName] = useState('')
  const [totalEvents, setTotalEvents] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedEvents, setExpandedEvents] = useState<Set<string>>(new Set())
  const [showFilters, setShowFilters] = useState(false)
  const [eventTypes, setEventTypes] = useState<EventType[]>([])
  const [selectedTypes, setSelectedTypes] = useState<string[]>([])
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  // Icon mapping
  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'intake':
        return <PersonAddIcon />
      case 'travel':
        return <FlightIcon />
      case 'family_history':
        return <FamilyRestroomIcon />
      case 'treatment_plan':
        return <LocalHospitalIcon />
      case 'medication':
        return <MedicationIcon />
      case 'follow_up':
        return <EventNoteIcon />
      case 'monitoring':
        return <MonitorHeartIcon />
      default:
        return <EventNoteIcon />
    }
  }

  // Color mapping
  const getEventColor = (eventType: string): "primary" | "secondary" | "success" | "error" | "info" | "warning" => {
    switch (eventType) {
      case 'intake':
        return 'primary'
      case 'travel':
        return 'info'
      case 'family_history':
        return 'secondary'
      case 'treatment_plan':
        return 'error'
      case 'medication':
        return 'success'
      case 'follow_up':
        return 'warning'
      case 'monitoring':
        return 'info'
      default:
        return 'primary'
    }
  }

  // Status chip color
  const getStatusColor = (status?: string): "default" | "primary" | "secondary" | "success" | "error" | "warning" => {
    if (!status) return 'default'
    switch (status.toLowerCase()) {
      case 'active':
      case 'completed':
        return 'success'
      case 'discontinued':
      case 'missed':
      case 'cancelled':
        return 'error'
      case 'scheduled':
      case 'on_hold':
        return 'warning'
      case 'noted':
        return 'secondary'
      default:
        return 'default'
    }
  }

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Toggle event expansion
  const toggleEventExpansion = (eventId: string) => {
    setExpandedEvents(prev => {
      const newSet = new Set(prev)
      if (newSet.has(eventId)) {
        newSet.delete(eventId)
      } else {
        newSet.add(eventId)
      }
      return newSet
    })
  }

  // Fetch event types
  useEffect(() => {
    const fetchEventTypes = async () => {
      try {
        const data = await getEventTypes()
        setEventTypes(data.event_types)
      } catch (err) {
        console.error('Error fetching event types:', err)
      }
    }
    fetchEventTypes()
  }, [])

  // Fetch timeline data
  const fetchTimeline = async () => {
    setLoading(true)
    setError(null)
    try {
      const filters = {
        eventTypes: selectedTypes.length > 0 ? selectedTypes : undefined,
        startDate: startDate || undefined,
        endDate: endDate || undefined
      }
      const data = await getPatientTimeline(patientIntakeId, filters)
      setEvents(data.events)
      setPatientName(data.patient_name)
      setTotalEvents(data.total_events)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load timeline')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTimeline()
  }, [patientIntakeId, selectedTypes, startDate, endDate])

  // Handle type filter change
  const handleTypeFilterChange = (type: string) => {
    setSelectedTypes(prev => {
      if (prev.includes(type)) {
        return prev.filter(t => t !== type)
      } else {
        return [...prev, type]
      }
    })
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    )
  }

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" gutterBottom>
            Medical History Timeline
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {patientName} - {totalEvents} events
          </Typography>
        </Box>
        <IconButton
          onClick={() => setShowFilters(!showFilters)}
          color={showFilters ? 'primary' : 'default'}
        >
          <FilterListIcon />
        </IconButton>
      </Box>

      {/* Filters */}
      <Collapse in={showFilters}>
        <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Filter Events
          </Typography>
          
          {/* Event Type Filters */}
          <FormGroup row sx={{ mb: 2 }}>
            {eventTypes.map(type => (
              <FormControlLabel
                key={type.value}
                control={
                  <Checkbox
                    checked={selectedTypes.includes(type.value)}
                    onChange={() => handleTypeFilterChange(type.value)}
                    size="small"
                  />
                }
                label={type.label}
              />
            ))}
          </FormGroup>

          {/* Date Range Filters */}
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Start Date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                size="small"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="End Date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                size="small"
              />
            </Grid>
          </Grid>
        </Paper>
      </Collapse>

      {/* Timeline */}
      {events.length === 0 && (
        <Alert severity="info">No events found for the selected filters.</Alert>
      )}
      {events.length > 0 && (
        <Box>
          {events.map((event, index) => (
            <Box key={event.id} sx={{ display: 'flex', alignItems: 'stretch' }}>
              {/* Date column */}
              <Box sx={{ width: 140, pr: 2, textAlign: 'right' }}>
                <Typography variant="body2" fontWeight="bold">
                  {formatDate(event.date)}
                </Typography>
                <Typography variant="caption">{formatTime(event.date)}</Typography>
              </Box>
              {/* Marker */}
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mr: 2 }}>
                <Box sx={{
                  width: 18,
                  height: 18,
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  bgcolor: (theme) => theme.palette[getEventColor(event.event_type)].light,
                  color: (theme) => theme.palette[getEventColor(event.event_type)].main,
                  border: (theme) => `2px solid ${theme.palette[getEventColor(event.event_type)].main}`
                }}>
                  {getEventIcon(event.event_type)}
                </Box>
                {index < events.length - 1 && (
                  <Box sx={{ flex: 1, width: 2, bgcolor: 'divider', mt: 0.5 }} />
                )}
              </Box>
              {/* Content */}
              <Box sx={{ flex: 1 }}>
                <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                    <Box flex={1}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {event.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                        {event.description}
                      </Typography>
                    </Box>
                    <Box display="flex" gap={1} alignItems="center">
                      {event.status && (
                        <Chip
                          label={event.status}
                          size="small"
                          color={getStatusColor(event.status)}
                        />
                      )}
                      <IconButton
                        size="small"
                        onClick={() => toggleEventExpansion(event.id)}
                      >
                        {expandedEvents.has(event.id) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                    </Box>
                  </Box>
                  <Collapse in={expandedEvents.has(event.id)}>
                    <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e0e0e0' }}>
                      <Typography variant="caption" fontWeight="bold" display="block" mb={1}>
                        Additional Details:
                      </Typography>
                      {event.metadata && Object.keys(event.metadata).length > 0 ? (
                        <Grid container spacing={1}>
                          {Object.entries(event.metadata).map(([key, value]) => (
                            <Grid item xs={12} sm={6} key={key}>
                              <Typography variant="caption" color="text.secondary">
                                {key.replace(/_/g, ' ').toUpperCase()}:
                              </Typography>
                              <Typography variant="body2">
                                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                              </Typography>
                            </Grid>
                          ))}
                        </Grid>
                      ) : (
                        <Typography variant="caption" color="text.secondary">
                          No additional details available
                        </Typography>
                      )}
                    </Box>
                  </Collapse>
                </Paper>
              </Box>
            </Box>
          ))}
        </Box>
      )}
    </Paper>
  )
}

export default MedicalTimeline
