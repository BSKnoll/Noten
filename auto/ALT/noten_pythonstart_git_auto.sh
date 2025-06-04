#!/bin/bash

# Konfiguration
BASE_DIR="/volume1/homes/Markus/Drive/Studium Skripten Unterlagen/BS/Sonstiges/NotenListeGesamt"
SCRIPT_DIR="$BASE_DIR/auto"
TRIGGER_DIR="$BASE_DIR/triggerfiles"
PYTHON="/bin/python3"

SCRIPT_FILE="$SCRIPT_DIR/NotenSkript.py"
HTML_FILE="$SCRIPT_DIR/Notenuebersicht.html"
INDEX_FILE="$BASE_DIR/index.html"
ARCHIV_DIR="$SCRIPT_DIR/archiv"
TRIGGER_FILE="$TRIGGER_DIR/trigger.txt"
FORCE_FILE="$TRIGGER_DIR/FORCE.txt"
LOG_FILE="$SCRIPT_DIR/logdat.txt"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")

# Aktuelle Zeit
JETZT=$(date '+%Y-%m-%d %H:%M:%S')
NOW_DAY=$(date +%u)  # 1 = Montag, 7 = Sonntag

# Logging
echo "[$JETZT] ✳️ Aufruf durch Aufgabenplaner oder manuell" >> "$LOG_FILE"

# Zeitfenster (±1 Minute)
pad() { printf "%02d" "$1"; }
hour=$(pad $(date +%-H))
minute=$(pad $(date +%-M))

valid_times=()
valid_times+=("${hour}:${minute}")

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

# FORCE prüfen (Zeile oder Datei)
if grep -q "^FORCE$" "$TRIGGER_FILE" 2>/dev/null || [ -f "$FORCE_FILE" ]; then
    echo "[$JETZT] 🚀 FORCE erkannt (Zeile oder Datei) – Triggerprüfung übersprungen." >> "$LOG_FILE"
    should_run=true
fi

# Zeitbasierte Trigger prüfen (wenn kein FORCE)
if ! $should_run && [ -f "$TRIGGER_FILE" ]; then
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
    cd "$SCRIPT_DIR" || exit 1

    git fetch origin main >> "$LOG_FILE" 2>&1
    git reset --hard origin/main >> "$LOG_FILE" 2>&1

    $PYTHON "$SCRIPT_FILE" >> "$LOG_FILE" 2>&1

    if [ -f "$HTML_FILE" ]; then
        cp "$HTML_FILE" "$INDEX_FILE"
        cp "$HTML_FILE" "$ARCHIV_DIR/Notenuebersicht_$TIMESTAMP.html"
        echo "[$JETZT] ✅ HTML erstellt, archiviert & kopiert." >> "$LOG_FILE"

        cd "$BASE_DIR" || exit 1
        git add -A >> "$LOG_FILE" 2>&1
        git commit -m "Automatisches Update vom $TIMESTAMP" >> "$LOG_FILE" 2>&1
        git push origin main >> "$LOG_FILE" 2>&1
        echo "[$JETZT] ✅ GitHub Push erfolgreich." >> "$LOG_FILE"
    else
        echo "[$JETZT] ❌ Fehler: HTML wurde nicht erstellt!" >> "$LOG_FILE"
    fi

    # Aufräumen: FORCE-Zeile aus trigger.txt entfernen, FORCE.txt löschen
    if [ -f "$TRIGGER_FILE" ]; then
        sed -i '/^FORCE$/d' "$TRIGGER_FILE"
    fi
    rm -f "$FORCE_FILE"
else
    echo "[$JETZT] ⏭️ Kein passender Trigger – Skript übersprungen." >> "$LOG_FILE"
fi
