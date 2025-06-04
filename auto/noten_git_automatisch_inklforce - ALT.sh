#!/bin/bash

# Konfiguration
SCRIPT_DIR="/volume1/homes/Markus/Drive/Studium Skripten Unterlagen/BS/Sonstiges/NotenListeGesamt/auto"
PYTHON="/bin/python3"
SCRIPT_FILE="$SCRIPT_DIR/NotenSkript.py"
HTML_FILE="$SCRIPT_DIR/Notenübersicht.html"
INDEX_FILE="/volume1/homes/Markus/Drive/Studium Skripten Unterlagen/BS/Sonstiges/NotenListeGesamt/index.html"
ARCHIV_DIR="$SCRIPT_DIR/archiv"
TRIGGER_FILE="/volume1/homes/Markus/Drive/Studium Skripten Unterlagen/BS/Sonstiges/NotenListeGesamt/trigger.txt"
LOG_FILE="$SCRIPT_DIR/log.txt"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")

# Aktuelle Zeitwerte
JETZT=$(date '+%Y-%m-%d %H:%M:%S')
NOW_DAY=$(date +%u)

# Logging
echo "[$JETZT] ✳️ Aufruf durch Aufgabenplaner oder manuell" >> "$LOG_FILE"

# Stunde und Minute korrekt zweistellig formatieren
pad() { printf "%02d" "$1"; }

hour=$(pad $(date +%-H))
minute=$(pad $(date +%-M))

# Vergleichszeiten (±1 Minute)
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

should_run=false

# FORCE prüfen
if grep -q "^FORCE$" "$TRIGGER_FILE"; then
    echo "[$JETZT] 🚀 FORCE-Zeile erkannt – Triggerprüfung übersprungen." >> "$LOG_FILE"
    should_run=true
fi

# Zeit-Trigger prüfen (nur wenn kein FORCE)
if ! $should_run; then
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
fi

# Ausführung
if $should_run; then
    echo "[$JETZT] ✅ Trigger erkannt – Skript wird ausgeführt." >> "$LOG_FILE"
    mkdir -p "$ARCHIV_DIR"
    cd "$SCRIPT_DIR" || exit

    git fetch origin main >> "$LOG_FILE" 2>&1
    git reset --hard origin/main >> "$LOG_FILE" 2>&1

    $PYTHON "$SCRIPT_FILE" >> "$LOG_FILE" 2>&1

    if [ -f "$HTML_FILE" ]; then
        cp "$HTML_FILE" "$SCRIPT_DIR/index.html"
        cp "$HTML_FILE" "$INDEX_FILE"
        cp "$HTML_FILE" "$ARCHIV_DIR/Notenübersicht_$TIMESTAMP.html"
        echo "[$JETZT] ✅ HTML erstellt, archiviert & kopiert." >> "$LOG_FILE"

        git add "$SCRIPT_DIR/index.html" "$INDEX_FILE" >> "$LOG_FILE" 2>&1
        git commit -m "Automatisches Update vom $TIMESTAMP" >> "$LOG_FILE" 2>&1
        git push origin main >> "$LOG_FILE" 2>&1
        echo "[$JETZT] ✅ GitHub Push erfolgreich." >> "$LOG_FILE"
    else
        echo "[$JETZT] ❌ Fehler: HTML wurde nicht erstellt!" >> "$LOG_FILE"
    fi

    # FORCE-Zeile löschen
    sed -i '/^FORCE$/d' "$TRIGGER_FILE"
else
    echo "[$JETZT] ⏭️ Kein passender Zeit-Trigger – Skript übersprungen." >> "$LOG_FILE"
fi
