import pandas as pd
from datetime import datetime, timedelta
import os
import json

#Log funktion



def update_log_file(message):
    now = datetime.now()
    new_entry = f"{now.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n"
    cutoff = now - timedelta(days=14)

    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            old_lines = f.readlines()
    else:
        old_lines = []

    filtered_lines = []
    for line in old_lines:
        try:
            timestamp_str = line.split(" - ")[0]
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            if timestamp >= cutoff:
                filtered_lines.append(line)
        except Exception:
            continue

    new_lines = [new_entry] + filtered_lines

    with open(log_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

# Basisverzeichnis (Ordner, in dem das Skript liegt)
base_path = os.path.dirname(os.path.abspath(__file__))
# Pfad zur Log-Datei
log_path = os.path.join(base_path, "log.txt")

# Dateinamen
excel_file_name = "NotenAlleSchuelerGesamt.xlsx"
html_output_name = "Notenübersicht.html"

# Pfade
file_path = os.path.join(base_path, "..", excel_file_name)
output_path = os.path.join(base_path, html_output_name)

def generate_html_from_excel(file_path, output_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel-Datei nicht gefunden: {file_path}")

        # Zeitstempel aus Blatt "Meta"
        try:
            meta_df = pd.read_excel(file_path, sheet_name="Meta", nrows=1, usecols="A")
            zeitstempel = meta_df.iloc[0, 0] if not meta_df.empty else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            zeitstempel = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Schülerdaten aus Blatt "Noten"
        df = pd.read_excel(file_path, sheet_name="NotenAlleSchuelerGesamt")

        # Sicherstellen, dass relevante Spalten numerisch sind
        numeric_columns = ['GesamtMitarbeit', 'GesamtTest', 'Endnote']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Funktion zur Umwandlung der Test- und Endnoten
        def transform_grade(grade):
            if not isinstance(grade, (int, float)):
                return "0"
            if grade == "K" or grade == "ND":
                return grade
            if 1 <= grade <= 1.3:
                return "1"
            elif 1.31 <= grade <= 1.69:
                return "1-2"
            elif 1.7 <= grade <= 2.3:
                return "2"
            elif 2.31 <= grade <= 2.69:
                return "2-3"
            elif 2.7 <= grade <= 3.3:
                return "3"
            elif 3.31 <= grade <= 3.69:
                return "3-4"
            elif 3.7 <= grade <= 4.19:
                return "4"
            elif 4.2 <= grade <= 4.49:
                return "4-5"
            elif 4.5 <= grade <= 5.55:
                return "5"
            else:
                return "Nur MA"

        # Funktion zur Umwandlung der Mitarbeitsnoten
        def transform_participation_grade(grade):
            if grade == "K" or grade == "ND":
                return grade
            elif grade == 1:
                return "+"
            elif grade == 2:
                return "+o"
            elif grade == 3:
                return "o"
            elif grade == 4:
                return "o-"
            elif grade == 5:
                return "-"
            else:
                return "0"

        # Erstellen eines Dictionaries, um Noten nach Schülercode zu gruppieren
        student_data = {}
        for _, row in df.iterrows():
            code = str(row['StudentCode'])
            subject = row['Fach']
            if code not in student_data:
                student_data[code] = []

            # Mitarbeitsnoten (bis zu 34 Einträge)
            participation_notes = [
                {
                    "Name": row[f"MA_Name{i}"],
                    "Note": transform_participation_grade(row[f"MA_Beurteilung{i}"])
                }
                for i in range(1, 35)
                if f"MA_Name{i}" in df.columns and f"MA_Beurteilung{i}" in df.columns and (row[f"MA_Beurteilung{i}"] != 0 or row[f"MA_Beurteilung{i}"] in ["K", "ND"])
            ]

            # Testnoten und Schularbeitsnoten im Originalformat beibehalten
            test_notes = []
            for i in range(1, 5):
                if row[f"Test{i}Note"] != 0:
                    test_notes.append({
                        "TestNote": f"{row[f'Test{i}Note']:.1f}",  # Formatieren mit einer Nachkommastelle
                        "TestPunkte": row[f"Test{i}Punkte"],
                        "MaxPunkte": row[f"Test{i}maxPunkte"]
                    })

            # Kommentar hinzufügen
            comment = row.get("Kommentar", "")

            student_data[code].append({
                "Fach": subject,
                "GesamtMitarbeit": transform_grade(row['GesamtMitarbeit']),
                "GesamtTest": "Nur MA" if row['GesamtTest'] == 0 else f"{row['GesamtTest']:.1f}",
                "Endnote": transform_grade(row['Endnote']),
                "Mitarbeit": participation_notes,
                "Testnoten": test_notes,
                "Kommentar": comment
            })

        # Konvertieren des Dictionaries in ein JSON-Objekt für die Verwendung in JavaScript
        student_data_json = json.dumps(student_data, default=str)

        # Start der HTML-Struktur mit den neuen Stilen
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Notenübersicht</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    font-size: 1rem; 
                    line-height: 1.5; 
                    background-color: #f0f0f0; 
                    color: #333;
                    margin: 20px;
                }}
                h1, h2 {{ font-size: 1.2rem; font-weight: bold; }}
                p, label, input, select {{ font-size: 1rem; }}

                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    background-color: #fff;
                    color: #333;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
                    font-size: 1.3rem; /* Größere Schriftgröße speziell für die Tabelle */
                    table-layout: auto; /* Automatische Anpassung der Spaltenbreite */
                }}
                th, td {{ 
                    border: 1px solid #ddd; 
                    text-align: center; 
                    padding: 12px; /* Erhöhte Polsterung für bessere Lesbarkeit */
                    white-space: nowrap; /* Verhindert Umbrüche, falls gewünscht */
                }}
                .note {{ font-style: italic; }}

                /* Anpassung für verschiedene Bildschirmgrößen */
                @media (max-width: 1200px) {{
                    body, p, label, input, select {{ font-size: 1.1rem; }}
                    table {{ font-size: 1.2rem; }}
                }}

                @media (max-width: 768px) {{
                    body, p, label, input, select {{ font-size: 1.2rem; }}
                    table {{ font-size: 1.2rem; }}
                }}

                @media (max-width: 480px) {{
                    body, p, label, input, select {{ font-size: 1.3rem; }}
                    table {{ font-size: 1.3rem; }}
                }}

                input#schuelerCode {{
                    font-size: 1.1rem; 
                    padding: 8px;
                }}
            </style>

            <script>
                const studentData = {student_data_json};

                function updateSubjects() {{
                    const codeInput = document.getElementById('schuelerCode').value;
                    const subjectDropdown = document.getElementById('fach');
                    subjectDropdown.innerHTML = ""; 

                    if (studentData[codeInput]) {{
                        studentData[codeInput].forEach(function(entry) {{
                            const option = document.createElement("option");
                            option.value = entry.Fach;
                            option.textContent = entry.Fach;
                            subjectDropdown.appendChild(option);
                        }});
                        subjectDropdown.style.display = "block";
                    }} else {{
                        subjectDropdown.style.display = "none";
                    }}
                    showStudentData();
                }}

                function showStudentData() {{
                    const codeInput = document.getElementById('schuelerCode').value;
                    const subject = document.getElementById('fach').value;
                    const tableBody = document.getElementById('notenTableBody');
                    tableBody.innerHTML = "";

                    if (studentData[codeInput]) {{
                        studentData[codeInput].forEach(function(entry) {{
                            if (entry.Fach === subject) {{
                                const row = document.createElement("tr");
                                row.innerHTML = `<td colspan="2">${{entry.Fach}}</td>`;
                                tableBody.appendChild(row);

                                const row1 = document.createElement("tr");
                                row1.innerHTML = `<td>GesamtMitarbeit</td><td>${{entry.GesamtMitarbeit}}</td>`;
                                tableBody.appendChild(row1);

                                if (entry.GesamtTest !== "") {{
                                    const row2 = document.createElement("tr");
                                    row2.innerHTML = `<td>GesamtTest</td><td>${{entry.GesamtTest}}</td>`;
                                    tableBody.appendChild(row2);
                                }}

                                const row3 = document.createElement("tr");
                                row3.innerHTML = `<td>(Vorläufige-)Endnote</td><td>${{entry.Endnote}}</td>`;
                                tableBody.appendChild(row3);

                                if (entry.Mitarbeit.length > 0) {{
                                    const participationHeader = document.createElement("tr");
                                    participationHeader.innerHTML = `<th colspan="2">Mitarbeit</th>`;
                                    tableBody.appendChild(participationHeader);

                                    entry.Mitarbeit.forEach(function(part) {{
                                        const partRow = document.createElement("tr");
                                        partRow.innerHTML = `<td>${{part.Name}}</td><td>${{part.Note}}</td>`;
                                        tableBody.appendChild(partRow);
                                    }});
                                }}

                                if (entry.Testnoten.length > 0) {{
                                    const testHeader = document.createElement("tr");
                                    testHeader.innerHTML = `<th colspan="2">Testnoten/Schularbeitsnoten</th>`;
                                    tableBody.appendChild(testHeader);

                                    entry.Testnoten.forEach(function(test) {{
                                        const testRow = document.createElement("tr");
                                        testRow.innerHTML = `<td>TestNote</td><td>${{test.TestNote}}</td>`;
                                        tableBody.appendChild(testRow);

                                        const pointsRow = document.createElement("tr");
                                        pointsRow.innerHTML = `<td>Punkte</td><td>${{test.TestPunkte}}</td>`;
                                        tableBody.appendChild(pointsRow);

                                        const maxPointsRow = document.createElement("tr");
                                        maxPointsRow.innerHTML = `<td>Max Punkte</td><td>${{test.MaxPunkte}}</td>`;
                                        tableBody.appendChild(maxPointsRow);
                                    }});
                                }}

                                if (entry.Kommentar) {{
                                    const commentRow = document.createElement("tr");
                                    commentRow.innerHTML = `<th colspan="2">Kommentar</th>`;
                                    tableBody.appendChild(commentRow);

                                    const commentTextRow = document.createElement("tr");
                                    commentTextRow.innerHTML = `<td colspan="2">${{entry.Kommentar}}</td>`;
                                    tableBody.appendChild(commentTextRow);
                                }}
                            }}
                        }});
                    }}
                }}
            </script>
        </head>
        <body>
            <p>Aktualisiert am: {zeitstempel}</p>
            <p class="note">Angaben ohne Gewähr – Unverbindlich, Fehler könnten enthalten sein.</p>

            <label for="schuelerCode">SchuelerCode:</label>
            <input type="text" id="schuelerCode" name="schuelerCode" oninput="updateSubjects()"><br><br>

            <label for="fach" style="display: none;">Fach:</label>
            <select id="fach" name="fach" onchange="showStudentData()" style="display: none;"></select><br><br>

            <h2>Noten</h2>
            <table>
                <tbody id="notenTableBody">
                    <!-- Die Noten und Mitarbeitsnoten werden hier dynamisch eingefügt -->
                </tbody>
            </table>

            <h2>Legende</h2>
            <p>+: Plus; o: Ringerl; -: Minus; K: Krank; ND: Nicht Durchgeführt; 0: Kein Wert eingetragen; MAK: Mitarbeit/Quiz; W: Woche, je nach Lehrgang nicht unbedingt (Mo bis Fr)</p>
            <p>In Fächern mit Schularbeiten sind die Testnoten Schularbeitsnoten :).</p>

            <!-- Fünf Leerzeilen -->
            <br><br><br><br><br>
        </body>
        </html>
        """

        # Speichern der HTML-Datei
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f"HTML-Datei erfolgreich erstellt: {output_path}")
        update_log_file(f"HTML-Datei '{html_output_name}' wurde neu erstellt.")

    except FileNotFoundError as e:
        print(f"Fehler: {e}")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")


# Aufruf der Funktion mit den definierten Pfaden
generate_html_from_excel(file_path, output_path)