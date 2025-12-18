# Phase 4 API Specification (OpenAPI 3.0)

This file defines all Phase 4 endpoints in OpenAPI format for documentation and client generation.

```yaml
openapi: 3.0.0
info:
  title: Natpudan Phase 4 API
  description: Advanced Medical Image Analysis, Report Generation, Outcome Tracking, and Population Analytics
  version: 4.0.0

servers:
  - url: http://127.0.0.1:8000
    description: Local Development
  - url: https://api.natpudan.example.com
    description: Production

# ============================================================================
# Phase 4 Medical Image Analysis APIs
# ============================================================================

paths:
  /api/phase-4/image/analyze:
    post:
      summary: Analyze a single medical image
      tags:
        - Medical Images
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                image:
                  type: string
                  format: base64
                  description: Base64 encoded image data
                image_type:
                  type: string
                  enum: [xray, ecg, ultrasound, pathology, mri, ct]
                patient_id:
                  type: integer
                patient_context:
                  type: object
                  properties:
                    age:
                      type: integer
                    gender:
                      type: string
                    comorbidities:
                      type: array
                      items:
                        type: string
              required: [image, image_type, patient_id]
      responses:
        200:
          description: Image analysis successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  image_id:
                    type: integer
                  findings:
                    type: array
                    items:
                      type: string
                  confidence:
                    type: number
                    format: float
                  severity:
                    type: string
                    enum: [CRITICAL, HIGH, MODERATE, LOW, NORMAL]
                  differential:
                    type: array
                    items:
                      type: string
                  recommendations:
                    type: array
                    items:
                      type: string
                  execution_time_ms:
                    type: number
                  from_cache:
                    type: boolean
                  model:
                    type: string
        400:
          description: Invalid image or parameters
        500:
          description: Analysis failed

  /api/phase-4/image/batch-analyze:
    post:
      summary: Analyze multiple medical images
      tags:
        - Medical Images
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                patient_id:
                  type: integer
                images:
                  type: array
                  items:
                    type: object
                    properties:
                      image:
                        type: string
                        format: base64
                      image_type:
                        type: string
                      priority:
                        type: string
                        enum: [urgent, high, normal]
      responses:
        200:
          description: Batch analysis results
          content:
            application/json:
              schema:
                type: object
                properties:
                  total_images:
                    type: integer
                  successful:
                    type: integer
                  failed:
                    type: integer
                  results:
                    type: array
                    items:
                      $ref: '#/components/schemas/ImageAnalysisResult'
                  total_execution_time_ms:
                    type: number

  /api/phase-4/image/{image_id}:
    get:
      summary: Get image analysis details
      tags:
        - Medical Images
      parameters:
        - name: image_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Image analysis details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MedicalImageFull'
        404:
          description: Image not found

  /api/phase-4/image/{image_id}/verify:
    post:
      summary: Radiologist verification of AI analysis
      tags:
        - Medical Images
      parameters:
        - name: image_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: [approved, amended, rejected]
                notes:
                  type: string
                corrections:
                  type: object
              required: [status]
      responses:
        200:
          description: Verification recorded
        400:
          description: Invalid status or missing radiologist

  /api/phase-4/image/{image_id}/report:
    get:
      summary: Generate structured report for image analysis
      tags:
        - Medical Images
      parameters:
        - name: image_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Report generated
          content:
            application/json:
              schema:
                type: object
                properties:
                  pdf_url:
                    type: string
                  report_html:
                    type: string

# ============================================================================
# Phase 4 Medical Report Generation APIs
# ============================================================================

  /api/phase-4/report/generate:
    post:
      summary: Generate a medical report
      tags:
        - Medical Reports
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                report_type:
                  type: string
                  enum: [discharge, progress, treatment_plan, follow_up]
                patient_id:
                  type: integer
                context:
                  type: object
                  description: Patient-specific context for report
              required: [report_type, patient_id]
      responses:
        200:
          description: Report generated successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  report_id:
                    type: integer
                  status:
                    type: string
                    enum: [draft, final, signed]
                  pdf_url:
                    type: string
                  preview:
                    type: string
                    description: HTML preview of report
                  citations_count:
                    type: integer
        400:
          description: Invalid report type or missing required data

  /api/phase-4/report/{report_id}:
    get:
      summary: Get report details
      tags:
        - Medical Reports
      parameters:
        - name: report_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Report details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MedicalReport'

  /api/phase-4/report/{report_id}/sign:
    post:
      summary: Digitally sign a report
      tags:
        - Medical Reports
      parameters:
        - name: report_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                physician_id:
                  type: integer
                timestamp:
                  type: string
                  format: date-time
                signature_base64:
                  type: string
              required: [physician_id]
      responses:
        200:
          description: Report signed successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  report_id:
                    type: integer
                  status:
                    type: string
                    enum: [signed]
                  signed_at:
                    type: string
                    format: date-time
                  signature_valid:
                    type: boolean

  /api/phase-4/report/{report_id}/download:
    get:
      summary: Download report as PDF
      tags:
        - Medical Reports
      parameters:
        - name: report_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: PDF file
          content:
            application/pdf:
              schema:
                type: string
                format: binary
        404:
          description: Report not found or PDF not generated

# ============================================================================
# Phase 4 Patient Outcome Tracking APIs
# ============================================================================

  /api/phase-4/patient/{patient_id}/outcomes/record:
    post:
      summary: Record patient outcome following visit/treatment
      tags:
        - Patient Outcomes
      parameters:
        - name: patient_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                follow_up_date:
                  type: string
                  format: date
                outcome_status:
                  type: string
                  enum: [improved, stable, worsened]
                clinical_notes:
                  type: string
                lab_results:
                  type: object
                vital_signs:
                  type: object
              required: [follow_up_date, outcome_status]
      responses:
        201:
          description: Outcome recorded
          content:
            application/json:
              schema:
                type: object
                properties:
                  outcome_id:
                    type: integer
                  patient_id:
                    type: integer
                  risk_scores:
                    type: object
                    properties:
                      hospitalization_risk:
                        type: number
                      readmission_risk:
                        type: number
                      complication_risk:
                        type: number

  /api/phase-4/patient/{patient_id}/risk-score:
    get:
      summary: Get current risk scores for patient
      tags:
        - Patient Outcomes
      parameters:
        - name: patient_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Risk scores
          content:
            application/json:
              schema:
                type: object
                properties:
                  patient_id:
                    type: integer
                  hospitalization_risk:
                    type: number
                    format: float
                  readmission_risk:
                    type: number
                    format: float
                  complication_risk:
                    type: number
                    format: float
                  mortality_risk:
                    type: number
                    format: float
                  risk_factors:
                    type: array
                    items:
                      type: string
                  updated_at:
                    type: string
                    format: date-time

  /api/phase-4/patient/{patient_id}/predict-progression:
    post:
      summary: Predict disease progression
      tags:
        - Patient Outcomes
      parameters:
        - name: patient_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                condition:
                  type: string
                  description: Condition to predict (e.g., Type 2 Diabetes)
                current_state:
                  type: object
                  description: Current clinical values
              required: [condition]
      responses:
        200:
          description: Progression prediction
          content:
            application/json:
              schema:
                type: object
                properties:
                  condition:
                    type: string
                  progression:
                    type: string
                    enum: [stable, slow_decline, rapid_decline, improvement]
                  confidence:
                    type: number
                    format: float
                  months_to_intervention:
                    type: integer
                  recommendations:
                    type: array
                    items:
                      type: string
                  predicted_values:
                    type: object

  /api/phase-4/patient/{patient_id}/timeline:
    get:
      summary: Get patient medical timeline
      tags:
        - Patient Outcomes
      parameters:
        - name: patient_id
          in: path
          required: true
          schema:
            type: integer
        - name: start_date
          in: query
          schema:
            type: string
            format: date
        - name: end_date
          in: query
          schema:
            type: string
            format: date
      responses:
        200:
          description: Patient timeline events
          content:
            application/json:
              schema:
                type: object
                properties:
                  patient_id:
                    type: integer
                  events:
                    type: array
                    items:
                      type: object
                      properties:
                        date:
                          type: string
                          format: date-time
                        event_type:
                          type: string
                        description:
                          type: string
                        data:
                          type: object

# ============================================================================
# Phase 4 Population Health Analytics APIs
# ============================================================================

  /api/phase-4/analytics/disease-prevalence:
    get:
      summary: Get disease prevalence in population
      tags:
        - Population Analytics
      parameters:
        - name: disease
          in: query
          required: true
          schema:
            type: string
        - name: date_range
          in: query
          schema:
            type: string
            enum: [1_month, 3_months, 6_months, 1_year]
        - name: demographic_filters
          in: query
          schema:
            type: string
            description: JSON object for filtering
      responses:
        200:
          description: Prevalence data
          content:
            application/json:
              schema:
                type: object
                properties:
                  disease:
                    type: string
                  prevalence_percent:
                    type: number
                  trend:
                    type: string
                    enum: [up, down, stable]
                  total_affected:
                    type: integer
                  demographics:
                    type: object

  /api/phase-4/analytics/comorbidity-network:
    get:
      summary: Get comorbidity network for a diagnosis
      tags:
        - Population Analytics
      parameters:
        - name: diagnosis
          in: query
          required: true
          schema:
            type: string
        - name: top_k
          in: query
          schema:
            type: integer
            default: 10
      responses:
        200:
          description: Comorbidity network
          content:
            application/json:
              schema:
                type: object
                properties:
                  primary_diagnosis:
                    type: string
                  comorbidities:
                    type: array
                    items:
                      type: object
                      properties:
                        diagnosis:
                          type: string
                        co_occurrence_rate:
                          type: number
                        relative_risk:
                          type: number

  /api/phase-4/analytics/treatment-comparison:
    post:
      summary: Compare effectiveness of two treatments
      tags:
        - Population Analytics
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                condition:
                  type: string
                treatment_1:
                  type: string
                treatment_2:
                  type: string
                metric:
                  type: string
                  description: Outcome metric to compare
              required: [condition, treatment_1, treatment_2]
      responses:
        200:
          description: Treatment comparison
          content:
            application/json:
              schema:
                type: object
                properties:
                  condition:
                    type: string
                  treatment_1:
                    type: object
                    properties:
                      n_patients:
                        type: integer
                      mean_improvement:
                        type: number
                      adverse_events_rate:
                        type: number
                  treatment_2:
                    type: object
                  p_value:
                    type: number
                  winner:
                    type: string

  /api/phase-4/analytics/health-equity:
    get:
      summary: Analyze health disparities by demographic group
      tags:
        - Population Analytics
      parameters:
        - name: metric
          in: query
          required: true
          schema:
            type: string
            description: Metric to analyze (mortality_rate, complications, etc.)
        - name: demographic
          in: query
          required: true
          schema:
            type: string
            enum: [gender, race, age_group, socioeconomic]
      responses:
        200:
          description: Health equity analysis
          content:
            application/json:
              schema:
                type: object
                properties:
                  metric:
                    type: string
                  demographic:
                    type: string
                  by_group:
                    type: object
                  disparity_index:
                    type: number
                  recommendations:
                    type: array
                    items:
                      type: string

# ============================================================================
# Components
# ============================================================================

components:
  schemas:
    ImageAnalysisResult:
      type: object
      properties:
        image_id:
          type: integer
        findings:
          type: array
          items:
            type: string
        confidence:
          type: number
        severity:
          type: string
        differential:
          type: array
        recommendations:
          type: array

    MedicalImageFull:
      type: object
      properties:
        id:
          type: integer
        patient_id:
          type: integer
        image_type:
          type: string
        ai_findings:
          type: object
        verified_by:
          type: integer
        verification_status:
          type: string
        radiologist_notes:
          type: string
        created_at:
          type: string
          format: date-time

    MedicalReport:
      type: object
      properties:
        id:
          type: integer
        patient_id:
          type: integer
        report_type:
          type: string
        status:
          type: string
        content:
          type: object
        citations:
          type: array
        signed_by:
          type: integer
        created_at:
          type: string
          format: date-time

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []
```

## Usage

1. **Generate OpenAPI documentation**: Use Swagger UI
   ```bash
   # Swagger UI automatically available at /docs
   curl http://127.0.0.1:8000/docs
   ```

2. **Generate API clients**: Use OpenAPI generators
   ```bash
   # TypeScript client
   openapi-generator-cli generate -i phase_4_api.yaml -g typescript-axios -o generated-clients/typescript
   
   # Python client
   openapi-generator-cli generate -i phase_4_api.yaml -g python -o generated-clients/python
   ```

3. **Test endpoints**: Use curl or Postman
   ```bash
   curl -X POST http://127.0.0.1:8000/api/phase-4/image/analyze \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "image": "base64_data...",
       "image_type": "xray",
       "patient_id": 42
     }'
   ```

## Implementation Notes

- All endpoints require JWT authentication (Bearer token)
- Responses follow standard format: `{status: "success"|"error", data: {...}, message: "..."}`
- Error responses include detailed messages for debugging
- Pagination supported on list endpoints (limit, offset)
- Rate limiting: 100 requests/minute per API key
