#!/bin/bash

# Konfiguration
PYTHON="/bin/python3"
SCRIPT_DIR="/volume1/homes/Markus/Drive/Studium Skripten Unterlagen/BS/Sonstiges/NotenListeGesamt"
SCRIPT_FILE="NotenSkript.py"
HTML_FILE="$SCRIPT_DIR/Notenübersicht.html"
INDEX_FILE="$SCRIPT_DIR/index.html"
ARCHIV_DIR="$SCRIPT_DIR/archiv"
TRIGGER_FILE="$SCRIPT_DIR/trigger"
LOG_FILE="$SCRIPT_DIR/log.txt"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")

# Aktuellen Zeitstempel im Format "Mo 08:00"
NOW=$(date +"%a %H:%M")

# Trigger prüfen
if grep -q "$NOW" "$TRIGGER_FILE"; then
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] Trigger erkannt ($NOW), führe Update durch." >> "$LOG_FILE"

    mkdir -p "$ARCHIV_DIR"

    echo "Starte Python-Skript..." >> "$LOG_FILE"
    $PYTHON "$SCRIPT_DIR/$SCRIPT_FILE" >> "$LOG_FILE" 2>&1

    if [ -f "$HTML_FILE" ]; then
        cp "$HTML_FILE" "$ARCHIV_DIR/Notenübersicht_$TIMESTAMP.html"
        echo "HTML archiviert." >> "$LOG_FILE"

        cp "$HTML_FILE" "$INDEX_FILE"
        touch "$INDEX_FILE"

        cd "$SCRIPT_DIR"
        git add index.html
        git commit -m "Automatisches Update vom $TIMESTAMP" --allow-empty
        git push origin main
        echo "GitHub Push durchgeführt." >> "$LOG_FILE"
    else
        echo "Fehler: HTML-Datei nicht gefunden!" >> "$LOG_FILE"
    fi
else
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] Kein Triggerzeitpunkt ($NOW) – Skript wird übersprungen." >> "$LOG_FILE"
fi
