import { useCallback, useEffect, useRef, useState } from 'react'
import apiClient from '../services/apiClient'

type UseLiveDiagnosisParams = {
  isEnabled: boolean
  buildPayload: () => Record<string, unknown>
  delayMs?: number
}

export function useLiveDiagnosis<T>({
  isEnabled,
  buildPayload,
  delayMs = 1500,
}: UseLiveDiagnosisParams) {
  const [liveDiagnosis, setLiveDiagnosis] = useState<T | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const debounceTimerRef = useRef<number | null>(null)

  const fetchLiveDiagnosis = useCallback(async () => {
    if (!isEnabled) {
      setLiveDiagnosis(null)
      return
    }

    setIsAnalyzing(true)
    try {
      const response = await apiClient.post('/api/medical/live-diagnosis', buildPayload())
      setLiveDiagnosis(response.data as T)
    } catch (error) {
      console.error('Error in live diagnosis:', error)
      setLiveDiagnosis(null)
    } finally {
      setIsAnalyzing(false)
    }
  }, [buildPayload, isEnabled])

  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current)
    }

    debounceTimerRef.current = window.setTimeout(() => {
      void fetchLiveDiagnosis()
    }, delayMs)

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
    }
  }, [delayMs, fetchLiveDiagnosis])

  return {
    liveDiagnosis,
    isAnalyzing,
    refreshLiveDiagnosis: fetchLiveDiagnosis,
  }
}
