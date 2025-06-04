#!/bin/bash

# Konfiguration
PYTHON="/volume1/@appstore/python3/bin/python3"
SCRIPT_DIR="/volume1/homes/Markus/Drive/Studium Skripten Unterlagen/BS/Sonstiges/NotenListeGesamt"
SCRIPT_FILE="NotenSkript.py"
LOG_FILE="$SCRIPT_DIR/log.txt"
HTML_FILE="$SCRIPT_DIR/Notenübersicht.html"
ARCHIV_DIR="$SCRIPT_DIR/archiv"

# Zeitstempel
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")

# Sicherstellen, dass Archivordner existiert
mkdir -p "$ARCHIV_DIR"

# Ausführung des Scripts und Logging
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Starte Skript..." >> "$LOG_FILE"
$PYTHON "$SCRIPT_DIR/$SCRIPT_FILE" >> "$LOG_FILE" 2>&1

# Wenn HTML erzeugt wurde, archivieren
if [ -f "$HTML_FILE" ]; then
    cp "$HTML_FILE" "$ARCHIV_DIR/Notenübersicht_$TIMESTAMP.html"
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] HTML archiviert." >> "$LOG_FILE"
else
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] Fehler: HTML-Datei wurde nicht gefunden!" >> "$LOG_FILE"
fi

# Alte Archivdateien (älter als 2 Tage) löschen
find "$ARCHIV_DIR" -name 'Notenübersicht_*.html' -type f -mtime +2 -delete
