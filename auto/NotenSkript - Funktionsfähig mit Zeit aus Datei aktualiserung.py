import os
import pandas as pd
import json
from datetime import datetime

# Konfiguration
excel_file_name = "NotenAlleSchuelerGesamt.xlsx"
html_output_name = "Notenübersicht.html"

# Basisverzeichnis bestimmen (dieses Skript befindet sich im Unterordner 'auto')
base_path = os.path.dirname(os.path.abspath(__file__))

# Pfade
file_path = os.path.join(base_path, "..", excel_file_name)
output_path = os.path.join(base_path, html_output_name)

def update_log_file(message, log_file_name="log.txt"):
    log_path = os.path.join(base_path, log_file_name)
    zeitstempel = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{zeitstempel}] {message}\n")

def generate_html_from_excel(file_path, output_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel-Datei nicht gefunden: {file_path}")

        mod_time = os.path.getmtime(file_path)
        timestamp = datetime.fromtimestamp(mod_time).strftime("%d.%m.%Y %H:%M:%S")
        print(f"Verwendeter Zeitstempel: {timestamp}")

        df = pd.read_excel(file_path, sheet_name="NotenAlleSchuelerGesamt", dtype={"Klasse": str})

        numeric_columns = ['GesamtMitarbeit', 'GesamtTest', 'Endnote']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        def transform_grade(grade):
            if grade in ["K", "ND"]:
                return grade
            try:
                grade = float(grade)
            except:
                return "0"
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

        def transform_participation_grade(grade):
            if grade == "K" or grade == "ND":
                return grade
            try:
                grade = int(grade)
            except:
                return "0"
            return {
                1: "+",
                2: "+o",
                3: "o",
                4: "o-",
                5: "-"
            }.get(grade, "0")

        student_data = {}
        for _, row in df.iterrows():
            code = str(row['StudentCode'])
            subject = row['Fach']
            if code not in student_data:
                student_data[code] = []

            participation_notes = [
                {
                    "Name": row[f"MA_Name{i}"],
                    "Note": transform_participation_grade(row[f"MA_Beurteilung{i}"])
                }
                for i in range(1, 35)
                if f"MA_Name{i}" in df.columns and f"MA_Beurteilung{i}" in df.columns and (row[f"MA_Beurteilung{i}"] != 0 or row[f"MA_Beurteilung{i}"] in ["K", "ND"])
            ]

            test_notes = []
            for i in range(1, 5):
                note_key = f"Test{i}Note"
                if note_key in row and pd.notna(row[note_key]) and row[note_key] != 0:
                    test_notes.append({
                        "TestNote": f"{row[note_key]:.1f}",
                        "TestPunkte": row.get(f"Test{i}Punkte", ""),
                        "MaxPunkte": row.get(f"Test{i}maxPunkte", "")
                    })

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

        student_data_json = json.dumps(student_data, ensure_ascii=False, default=str)

        # HTML-Code wie vorher eingefügt:
        html_content = f"""<!DOCTYPE html>
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
    box-shadow: 0 0 10px rgba(0,0,0,0.5);
    font-size: 1.3rem;
    table-layout: auto;
}}
th, td {{
    border: 1px solid #ddd;
    text-align: center;
    padding: 12px;
    white-space: nowrap;
}}
.note {{ font-style: italic; }}
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
                tableBody.innerHTML += `<tr><td colspan="2">${{entry.Fach}}</td></tr>`;
                tableBody.innerHTML += `<tr><td>GesamtMitarbeit</td><td>${{entry.GesamtMitarbeit}}</td></tr>`;
                if (entry.GesamtTest !== "") {{
                    tableBody.innerHTML += `<tr><td>GesamtTest</td><td>${{entry.GesamtTest}}</td></tr>`;
                }}
                tableBody.innerHTML += `<tr><td>(Vorläufige-)Endnote</td><td>${{entry.Endnote}}</td></tr>`;

                if (entry.Mitarbeit.length > 0) {{
                    tableBody.innerHTML += `<tr><th colspan="2">Mitarbeit</th></tr>`;
                    entry.Mitarbeit.forEach(function(part) {{
                        tableBody.innerHTML += `<tr><td>${{part.Name}}</td><td>${{part.Note}}</td></tr>`;
                    }});
                }}

                if (entry.Testnoten.length > 0) {{
                    tableBody.innerHTML += `<tr><th colspan="2">Testnoten/Schularbeitsnoten</th></tr>`;
                    entry.Testnoten.forEach(function(test) {{
                        tableBody.innerHTML += `<tr><td>TestNote</td><td>${{test.TestNote}}</td></tr>`;
                        tableBody.innerHTML += `<tr><td>Punkte</td><td>${{test.TestPunkte}}</td></tr>`;
                        tableBody.innerHTML += `<tr><td>Max Punkte</td><td>${{test.MaxPunkte}}</td></tr>`;
                    }});
                }}

                if (entry.Kommentar) {{
                    tableBody.innerHTML += `<tr><th colspan="2">Kommentar</th></tr>`;
                    tableBody.innerHTML += `<tr><td colspan="2">${{entry.Kommentar}}</td></tr>`;
                }}
            }}
        }});
    }}
}}
</script>
</head>
<body>
<p>Aktualisiert am: {timestamp}</p>
<p class="note">Angaben ohne Gewähr – Unverbindlich, Fehler könnten enthalten sein.</p>

<label for="schuelerCode">SchuelerCode:</label>
<input type="text" id="schuelerCode" name="schuelerCode" oninput="updateSubjects()"><br><br>

<label for="fach" style="display: none;">Fach:</label>
<select id="fach" name="fach" onchange="showStudentData()" style="display: none;"></select><br><br>

<h2>Noten</h2>
<table><tbody id="notenTableBody"></tbody></table>

<h2>Legende</h2>
<p>+: Plus; o: Ringerl; -: Minus; K: Krank; ND: Nicht Durchgeführt; 0: Kein Wert eingetragen; MAK: Mitarbeit/Quiz; W: Woche, je nach Lehrgang nicht unbedingt (Mo bis Fr)</p>
<p>In Fächern mit Schularbeiten sind die Testnoten Schularbeitsnoten :)</p>
<br><br><br><br><br>
</body>
</html>"""

        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f"HTML-Datei erfolgreich erstellt: {output_path}")
        update_log_file(f"HTML-Datei '{html_output_name}' wurde neu erstellt.")

    except FileNotFoundError as e:
        print(f"Fehler: {e}")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

# Aufruf
generate_html_from_excel(file_path, output_path)
