@echo off
REM Setzt das Verzeichnis auf den Ordner der Batch-Datei
cd /d "%~dp0"

REM Öffnet die Excel-Datei NotenAlleSchuelerGesamt.xlsx
start "" "NotenAlleSchuelerGesamt.xlsx"

REM Wartet 10 Sekunden (10000 Millisekunden)
timeout /t 20 > nul

REM Schließt Excel, falls es geöffnet ist (beendet alle Excel-Prozesse)
taskkill /f /im excel.exe > nul 2>&1

REM Wartet 5 Sekunden (10000 Millisekunden)
timeout /t 3 > nul

REM Führt das Python-Skript aus
python NotenSkript_Manuell.py

REM Öffnet den Ordner im Explorer
explorer "%~dp0"

start chrome.exe "https://tiiny.host/manage"

REM Hält das Fenster offen, um Fehlermeldungen anzuzeigen
pause

