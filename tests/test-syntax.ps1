foreach ($i in 1..3) {
    try {
        if ($i -eq 1) {
            Write-Host "One"
        }
        elseif ($i -eq 2) {
            foreach ($j in 1..2) {
                if ($j -eq 1) {
                    Write-Host "Two-One"
                }
            }
        }
    }
    catch {
        Write-Host "Error"
    }
}
Write-Host "Done"
