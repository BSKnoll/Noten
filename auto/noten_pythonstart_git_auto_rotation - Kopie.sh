#!/bin/bash

# Konfiguration
BASE_DIR="/volume1/homes/Markus/Drive/Studium Skripten Unterlagen/BS/Sonstiges/NotenListeGesamt"
SCRIPT_DIR="$BASE_DIR/auto"
TRIGGER_DIR="$BASE_DIR/triggerfiles"
PYTHON="/bin/python3"

SCRIPT_FILE="$SCRIPT_DIR/HTMLgenerierenV3.py"
HTML_FILE="$SCRIPT_DIR/Notenuebersicht.html"
INDEX_FILE="$BASE_DIR/index.html"
ARCHIV_DIR="$SCRIPT_DIR/archiv"
TRIGGER_FILE="$TRIGGER_DIR/trigger.txt"
FORCE_FILE="$TRIGGER_DIR/FORCE.txt"
LOG_FILE="$SCRIPT_DIR/logdat.txt"
LOG_ARCHIV_DIR="$SCRIPT_DIR/log_archiv"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")
LOG_DATE=$(date +%Y-%m-%d)
JETZT=$(date '+%Y-%m-%d %H:%M:%S')
JETZT_MIN=$(date '+%H:%M')
NOW_DAY=$(date +%u)  # 1 = Montag, 7 = Sonntag

mkdir -p "$LOG_ARCHIV_DIR"

# Log Rotation im Zeitfenster 23:54 – 23:56 (nur ein Archiv-Log pro Tag)
if [[ "$JETZT_MIN" =~ ^(23:54|23:55|23:56)$ ]] && [ -f "$LOG_FILE" ]; then
    if [ ! -f "$LOG_ARCHIV_DIR/log_$LOG_DATE.txt" ]; then
        cp "$LOG_FILE" "$LOG_ARCHIV_DIR/log_$LOG_DATE.txt"
        > "$LOG_FILE"
        echo "[$JETZT] 🔁 Logfile rotiert nach log_$LOG_DATE.txt" >> "$LOG_FILE"
    fi
fi

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
    valid_times+=("${hour}:59")
else
    m_minus=$((10#$minute - 1))
    valid_times+=("${hour}:$(pad $m_minus)")
fi

should_run=false

if grep -q "^FORCE$" "$TRIGGER_FILE" 2>/dev/null || [ -f "$FORCE_FILE" ]; then
    echo "[$JETZT] 🚀 FORCE erkannt (Zeile oder Datei) – Triggerprüfung übersprungen." >> "$LOG_FILE"
    should_run=true
fi

if ! $should_run && [ -f "$TRIGGER_FILE" ]; then
    while IFS= read -r line || [ -n "$line" ]; do
        [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
        day=$(echo "$line" | cut -d';' -f1 | xargs)
        time=$(echo "$line" | cut -d';' -f2 | xargs)

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

if $should_run; then
    echo "[$JETZT] ✅ Trigger erkannt – Skript wird ausgeführt." >> "$LOG_FILE"
    mkdir -p "$ARCHIV_DIR"
    cd "$SCRIPT_DIR" || exit 1

    git fetch origin main >> "$LOG_FILE" 2>&1
    git pull --rebase origin main >> "$LOG_FILE" 2>&1

    $PYTHON "$SCRIPT_FILE" >> "$LOG_FILE" 2>&1
    sync
    sleep 2

    if [ -f "$HTML_FILE" ]; then
        echo "[$JETZT] 🔄 HTML-Synchronisierung abgeschlossen. Beginne Kopie." >> "$LOG_FILE"
        cp "$HTML_FILE" "$INDEX_FILE"
        cp "$HTML_FILE" "$ARCHIV_DIR/Notenuebersicht_$TIMESTAMP.html"
        echo "[$JETZT] ✅ HTML erstellt, archiviert & index.html aktualisiert." >> "$LOG_FILE"

        cd "$BASE_DIR" || exit 1
        git add -A >> "$LOG_FILE" 2>&1
        git commit -m "Automatisches Update vom $TIMESTAMP" >> "$LOG_FILE" 2>&1
        git push origin main >> "$LOG_FILE" 2>&1
        if [ $? -ne 0 ]; then
            echo "[$JETZT] ❌ GitHub Push fehlgeschlagen – bitte manuell prüfen." >> "$LOG_FILE"
        else
            echo "[$JETZT] ✅ GitHub Push erfolgreich." >> "$LOG_FILE"
        fi
    else
        echo "[$JETZT] ❌ Fehler: HTML-Datei existiert nicht nach Skript-Ausführung!" >> "$LOG_FILE"
    fi

    if [ -f "$TRIGGER_FILE" ]; then
        sed -i '/^FORCE$/d' "$TRIGGER_FILE"
    fi
    rm -f "$FORCE_FILE"
else
    echo "[$JETZT] ⏭️ Kein passender Trigger – Skript übersprungen." >> "$LOG_FILE"
fi
