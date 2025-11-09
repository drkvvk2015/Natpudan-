import React from 'react'
import {
  Box,
  Paper,
  Typography,
  Chip,
  Alert,
  AlertTitle,
  LinearProgress,
  Card,
  CardContent,
  Grid,
  Divider,
} from '@mui/material'
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'
import { assessRisk, getRiskDisplay, RiskFactors, RiskScore } from '../utils/riskAssessment'

interface RiskAssessmentProps {
  patientData: RiskFactors
  showDetails?: boolean
}

const RiskAssessment: React.FC<RiskAssessmentProps> = ({ patientData, showDetails = true }) => {
  const riskScore: RiskScore = assessRisk(patientData)
  const display = getRiskDisplay(riskScore.level)

  const getRiskIcon = () => {
    switch (riskScore.level) {
      case 'critical':
        return <ErrorIcon sx={{ color: display.color, fontSize: 40 }} />
      case 'high':
        return <WarningIcon sx={{ color: display.color, fontSize: 40 }} />
      case 'medium':
        return <WarningIcon sx={{ color: display.color, fontSize: 40 }} />
      default:
        return <CheckCircleIcon sx={{ color: display.color, fontSize: 40 }} />
    }
  }

  const getProgressColor = () => {
    switch (riskScore.level) {
      case 'critical':
        return 'error'
      case 'high':
        return 'error'
      case 'medium':
        return 'warning'
      default:
        return 'success'
    }
  }

  return (
    <Paper
      elevation={3}
      sx={{
        p: 3,
        background: display.bgColor,
        border: `2px solid ${display.color}`,
        borderRadius: 2,
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        {getRiskIcon()}
        <Box sx={{ flex: 1 }}>
          <Typography variant="h5" sx={{ fontWeight: 700, color: display.color }}>
            {display.label}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Overall Risk Score: {riskScore.total} / 45
          </Typography>
          <LinearProgress
            variant="determinate"
            value={(riskScore.total / 45) * 100}
            color={getProgressColor()}
            sx={{ mt: 1, height: 8, borderRadius: 4 }}
          />
        </Box>
      </Box>

      {/* Risk Factors Breakdown */}
      {showDetails && (
        <>
          <Divider sx={{ my: 2 }} />
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
            Risk Factor Breakdown
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6} sm={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography color="text.secondary" variant="body2">
                    Age
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700 }}>
                    {riskScore.factors.age}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    / 3 points
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography color="text.secondary" variant="body2">
                    Travel
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700 }}>
                    {riskScore.factors.travel}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    / 10 points
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography color="text.secondary" variant="body2">
                    Family History
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700 }}>
                    {riskScore.factors.family}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    / 10 points
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography color="text.secondary" variant="body2">
                    Chronic Conditions
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700 }}>
                    {riskScore.factors.chronic}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    / 10 points
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography color="text.secondary" variant="body2">
                    Symptoms
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700 }}>
                    {riskScore.factors.symptoms}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    / 15 points
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Alerts */}
          {riskScore.alerts.length > 0 && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                ⚠️ Risk Alerts
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {riskScore.alerts.map((alert, index) => (
                  <Alert
                    key={index}
                    severity={alert.includes('CRITICAL') ? 'error' : 'warning'}
                    sx={{ fontSize: '0.875rem' }}
                  >
                    {alert}
                  </Alert>
                ))}
              </Box>
            </>
          )}

          {/* Recommendations */}
          <Divider sx={{ my: 2 }} />
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
            📋 Recommendations
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {riskScore.recommendations.map((rec, index) => (
              <Alert
                key={index}
                severity={
                  riskScore.level === 'critical'
                    ? 'error'
                    : riskScore.level === 'high'
                    ? 'warning'
                    : 'info'
                }
                sx={{ fontSize: '0.875rem' }}
              >
                {rec}
              </Alert>
            ))}
          </Box>
        </>
      )}
    </Paper>
  )
}

export default RiskAssessment

/**
 * Compact Risk Badge Component for use in lists and cards
 */
interface RiskBadgeProps {
  level: 'low' | 'medium' | 'high' | 'critical'
  size?: 'small' | 'medium'
  showIcon?: boolean
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, size = 'medium', showIcon = true }) => {
  const display = getRiskDisplay(level)
  
  return (
    <Chip
      label={showIcon ? `${display.icon} ${display.label}` : display.label}
      size={size}
      sx={{
        backgroundColor: display.color,
        color: 'white',
        fontWeight: 700,
        fontSize: size === 'small' ? '0.75rem' : '0.875rem',
      }}
    />
  )
}
