import os
import pandas as pd
import json
from datetime import datetime

# Konfiguration NotenAllSuS
excel_file_name = "NotenAllSuS.xlsx"
html_output_name = "Notenuebersicht.html"

# Basisverzeichnis
base_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_path, "..", excel_file_name)
output_path = os.path.join(base_path, html_output_name)

def update_log_file(message, log_file_name="logdat.txt"):
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

        df = pd.read_excel(file_path, sheet_name="NotenAllSuS", dtype={"Klasse": str})

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
            if grade in ["K", "ND"]:
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

        student_data_json = json.dumps(student_data, ensure_ascii=False)

        html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset=\"UTF-8\">
<title>Notenübersicht</title>
<style>
body {{ font-family: Arial; font-size: 1rem; background: #f0f0f0; margin: 20px; color: #333; }}
table {{ width: 100%; border-collapse: collapse; background: #fff; font-size: 1.3rem; box-shadow: 0 0 10px rgba(0,0,0,0.5); }}
th, td {{ border: 1px solid #ddd; padding: 12px; text-align: center; white-space: nowrap; }}
.note {{ font-style: italic; }}
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
                function addRow(col1, col2, isHeader = false) {{
                    const row = document.createElement("tr");
                    const td1 = document.createElement(isHeader ? "th" : "td");
                    const td2 = document.createElement(isHeader ? "th" : "td");
                    td1.textContent = col1;
                    td2.textContent = col2;
                    row.appendChild(td1);
                    row.appendChild(td2);
                    tableBody.appendChild(row);
                }}

                const rowFach = document.createElement("tr");
                const fachCell = document.createElement("td");
                fachCell.colSpan = 2;
                fachCell.textContent = entry.Fach;
                rowFach.appendChild(fachCell);
                tableBody.appendChild(rowFach);

                addRow("GesamtMitarbeit", entry.GesamtMitarbeit);
                if (entry.GesamtTest !== "") {{
                    addRow("GesamtTest", entry.GesamtTest);
                }}
                addRow("(Vorläufige-)Endnote", entry.Endnote);

                if (entry.Mitarbeit.length > 0) {{
                    const header = document.createElement("tr");
                    const th = document.createElement("th");
                    th.colSpan = 2;
                    th.textContent = "Mitarbeit";
                    header.appendChild(th);
                    tableBody.appendChild(header);

                    entry.Mitarbeit.forEach(function(part) {{
                        addRow(part.Name, part.Note);
                    }});
                }}

                if (entry.Testnoten.length > 0) {{
                    const header = document.createElement("tr");
                    const th = document.createElement("th");
                    th.colSpan = 2;
                    th.textContent = "Testnoten/Schularbeitsnoten";
                    header.appendChild(th);
                    tableBody.appendChild(header);

                    entry.Testnoten.forEach(function(test) {{
                        addRow("TestNote", test.TestNote);
                        addRow("Punkte", test.TestPunkte);
                        addRow("Max Punkte", test.MaxPunkte);
                    }});
                }}

                if (entry.Kommentar) {{
                    const header = document.createElement("tr");
                    const th = document.createElement("th");
                    th.colSpan = 2;
                    th.textContent = "Kommentar";
                    header.appendChild(th);
                    tableBody.appendChild(header);

                    const textRow = document.createElement("tr");
                    const td = document.createElement("td");
                    td.colSpan = 2;
                    td.textContent = entry.Kommentar;
                    textRow.appendChild(td);
                    tableBody.appendChild(textRow);
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
<input type="text" id="schuelerCode" oninput="updateSubjects()"><br><br>
<label for="fach" style="display:none">Fach:</label>
<select id="fach" onchange="showStudentData()" style="display:none"></select><br><br>
<h2>Noten</h2>
<table><tbody id="notenTableBody"></tbody></table>
<h2>Legende</h2>
<p>+: Plus; o: Ringerl; -: Minus; K: Krank; ND: Nicht Durchgeführt; 0: Kein Wert eingetragen; MAK: Mitarbeit/Quiz; W: Woche</p>
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