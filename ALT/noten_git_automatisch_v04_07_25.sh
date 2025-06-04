#!/bin/bash

# Konfiguration
SCRIPT_DIR="/volume1/homes/Markus/Drive/Studium Skripten Unterlagen/BS/Sonstiges/NotenListeGesamt"
PYTHON="/bin/python3"
SCRIPT_FILE="$SCRIPT_DIR/NotenSkript.py"
HTML_FILE="$SCRIPT_DIR/Notenübersicht.html"
INDEX_FILE="$SCRIPT_DIR/index.html"
ARCHIV_DIR="$SCRIPT_DIR/archiv"
TRIGGER_FILE="$SCRIPT_DIR/trigger.txt"
LOG_FILE="$SCRIPT_DIR/log.txt"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")

# Aktuelle Zeitwerte
JETZT=$(date '+%Y-%m-%d %H:%M:%S')
NOW_TIME=$(date +%H:%M)
NOW_DAY=$(date +%u)

# Logging
echo "[$JETZT] Starte Skript..." >> "$LOG_FILE"

# Unterstützte Zeiten (±1 Minute)
hour=$(date +%H)
minute=$(date +%M)
pad() { printf "%02d" "$1"; }

valid_times=()
valid_times+=("${hour}:$(pad $minute)")

m_plus=$((10#$minute + 1))
if [ "$m_plus" -eq 60 ]; then
    h_plus=$((10#$hour + 1))
    valid_times+=("$(pad $h_plus):00")
else
    valid_times+=("${hour}:$(pad $m_plus)")
fi

if [ "$minute" -eq 0 ]; then
    h_minus=$((10#$hour - 1))
    valid_times+=("$(pad $h_minus):59")
else
    m_minus=$((10#$minute - 1))
    valid_times+=("${hour}:$(pad $m_minus)")
fi

# Trigger prüfen
should_run=false
while IFS= read -r line || [ -n "$line" ]; do
    [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
    day=$(echo "$line" | cut -d';' -f1)
    time=$(echo "$line" | cut -d';' -f2)

    if [[ "$day" == "$NOW_DAY" ]]; then
        for t in "${valid_times[@]}"; do
            if [[ "$t" == "$time" ]]; then
                should_run=true
                break 2
            fi
        done
    fi
done < "$TRIGGER_FILE"

# HTML generieren unabhängig von Excel-Änderung
if $should_run; then
    echo "[$JETZT] Zeit-Trigger erkannt – führe Skript aus." >> "$LOG_FILE"
    mkdir -p "$ARCHIV_DIR"

    $PYTHON "$SCRIPT_FILE" >> "$LOG_FILE" 2>&1

    if [ -f "$HTML_FILE" ]; then
        cp "$HTML_FILE" "$INDEX_FILE"
        cp "$HTML_FILE" "$ARCHIV_DIR/Notenübersicht_$TIMESTAMP.html"
        echo "HTML-Datei erfolgreich erstellt: $INDEX_FILE" >> "$LOG_FILE"

        cd "$SCRIPT_DIR" || exit
        git add index.html >> "$LOG_FILE" 2>&1
        git commit -m "Automatisches Update vom $TIMESTAMP" >> "$LOG_FILE" 2>&1
        git push origin main >> "$LOG_FILE" 2>&1
        echo "GitHub Push erfolgreich." >> "$LOG_FILE"
    else
        echo "Fehler: HTML-Datei wurde nicht erstellt!" >> "$LOG_FILE"
    fi
else
    echo "[$JETZT] Kein passender Zeit-Trigger – Skript wird übersprungen." >> "$LOG_FILE"
fi
