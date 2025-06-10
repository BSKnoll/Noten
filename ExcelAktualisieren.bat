@echo off
cd /d "%~dp0"

@echo Starte PowerShell zum Oeffnen und Schliessen der Excel-Datei
powershell -ExecutionPolicy Bypass -File "%~dp0run_excel.ps1"

REM Sicherstellen, dass Ordner existiert
mkdir "triggerfiles" 2>nul
@echo Erstelle FORCE TRIGGER
REM Trigger-Datei sicher schreiben
break > "triggerfiles\FORCE.txt"
@echo Pfiat god - baba
REM Warte 5 Sekunden vor dem Beenden
timeout /t 5 > nul

exit
