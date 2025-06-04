@echo off
REM Setzt das Verzeichnis auf den Ordner der Batch-Datei
cd /d "%~dp0"

REM Öffnet die Excel-Datei
start "" "NotenAlleSchuelerGesamt.xlsx"

REM Wartet 20 Sekunden
timeout /t 20 > nul

REM Schließt alle laufenden Excel-Prozesse (falls noch offen)
taskkill /f /im excel.exe > nul 2>&1

