# Pfad zur Excel-Datei
$excelPath = Join-Path $PSScriptRoot "NotenAllSuS.xlsx"

# Excel starten
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false  # $true Falls sichtbar erwünscht, sonst $false

# Datei öffnen
$workbook = $excel.Workbooks.Open($excelPath)

# Wartezeit
Start-Sleep -Seconds 8

# Datei schließen ohne zu speichern
$workbook.Close($false)

# Excel schließen
$excel.Quit()

# COM-Objekte freigeben
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($workbook) | Out-Null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
[GC]::Collect()
[GC]::WaitForPendingFinalizers()
