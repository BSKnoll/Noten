@echo off
cd /d "%~dp0"

start "" "NotenAlleSchuelerGesamt.xlsx"
timeout /t 20 > nul

REM Nur die Excel-Datei mit bestimmtem Pfad schließen
powershell -Command "& {
  $filepath = Join-Path $PWD 'NotenAlleSchuelerGesamt.xlsx'
  $xl = Get-Process excel -ErrorAction SilentlyContinue | Where-Object {
    ($_ | Get-ProcessWindow | Where-Object { $_.MainWindowTitle -like '*NotenAlleSchuelerGesamt*' })
  }
  if ($xl) { $xl.Kill() }
}"

if not exist "triggerfiles" mkdir "triggerfiles"
echo Trigger erstellt > "triggerfiles\trigger.txt"
exit
