import React from 'react'
import { Box, Typography, Paper } from '@mui/material'

const DrugChecker: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>Drug Interaction Checker</Typography>
      <Paper sx={{ p:2 }}>Add drug interaction form and results table.</Paper>
    </Box>
  )
}

export default DrugChecker
