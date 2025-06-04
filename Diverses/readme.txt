Zweck

Dieses Projekt automatisiert die Erstellung und Veröffentlichung einer HTML-Notenübersicht, basierend auf einer Excel-Datei mit allen Schülerdaten. Die HTML-Datei wird bei jedem passenden Zeit-Trigger automatisch neu erzeugt und auf GitHub veröffentlicht.
Hauptbestandteile

    NotenAlleSchuelerGesamt.xlsx: Die zentrale Excel-Datei mit allen Noten (verlinkt mit anderen Tabellen).

    NotenSkript.py: Python-Skript zur Erzeugung der HTML-Übersicht aus der Excel-Datei.

    index.html: Die veröffentlichte Version der HTML-Datei für GitHub Pages.

    noten_git_automatisch.sh: Shell-Skript, das zyklisch prüft, ob ein definierter Trigger-Zeitpunkt erreicht wurde, dann NotenSkript.py ausführt und Änderungen zu GitHub pusht.

    trigger: Eine Textdatei, die Zeiten im Format Wochentag;HH:MM enthält (z. B. 5;07:00 für Freitag 7 Uhr).

    log.txt: Log-Datei zur Protokollierung aller Schritte.

Ablauf

    Das noten_git_automatisch.sh-Skript wird regelmäßig ausgeführt (z. B. per cron oder Synology Taskplaner).

    Es prüft, ob die aktuelle Uhrzeit einem definierten Zeit-Trigger entspricht (±1 Minute).

    Bei Übereinstimmung wird:

        das Python-Skript NotenSkript.py gestartet,

        die Datei Notenübersicht.html erzeugt und als index.html gespeichert,

        per git add/commit/push auf GitHub veröffentlicht.

    Die Seite ist über GitHub Pages öffentlich einsehbar.

Voraussetzungen

    Python3 installiert auf dem System

    Git konfiguriert mit SSH-Zugriff auf das Repository

    Schreibrechte auf dem Zielverzeichnis

    Ausführungsrechte für das Shell-Skript (chmod +x noten_git_automatisch.sh)