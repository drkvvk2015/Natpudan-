# Bulk upload medical PDFs to knowledge base
$backendUrl = "http://127.0.0.1:8000"
$uploadEndpoint = "$backendUrl/api/upload/document"

# Get all PDF files from medical_books directory
$pdfFiles = Get-ChildItem -Path "d:\Users\CNSHO\Documents\GitHub\Natpudan-\backend\data\medical_books" -Filter "*.pdf" -File

Write-Host "Found $($pdfFiles.Count) PDF files to upload"

foreach ($pdf in $pdfFiles) {
    Write-Host "Uploading: $($pdf.Name) ($([math]::Round($pdf.Length / 1MB, 2)) MB)"

    try {
        $response = Invoke-WebRequest -Uri $uploadEndpoint -Method POST -Form @{
            file = Get-Item $pdf.FullName
        }

        if ($response.StatusCode -eq 200) {
            $result = $response.Content | ConvertFrom-Json
            Write-Host "✓ Successfully uploaded: $($pdf.Name)" -ForegroundColor Green
            Write-Host "  Indexed chunks: $($result.document.indexed_chunks)" -ForegroundColor Cyan
        } else {
            Write-Host "✗ Failed to upload: $($pdf.Name) (Status: $($response.StatusCode))" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ Error uploading $($pdf.Name): $($_.Exception.Message)" -ForegroundColor Red
    }

    # Small delay between uploads
    Start-Sleep -Milliseconds 500
}

Write-Host "`nUpload process completed!"