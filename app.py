from flask import Flask, render_template, request, send_file
import os
import csv
import pandas as pd
from openpyxl import load_workbook
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = "secret_key_here"

# Render-la temporary files-ku /tmp thaan correct
UPLOAD_FOLDER = "/tmp/uploads"
PDF_FILE = "/tmp/Hall_Seat_Arrangement.pdf"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

students_global = []
hall_data_global = []

@app.route('/ping')
def ping():
    return "OK", 200

@app.route("/")
def home():
    # Unga html file name 'upload.html' thaane? Adhu correct-ah irukanum.
    return render_template("upload.html")

# -------- EXCEL/CSV PROCESSING LOGIC --------
def read_excel(filepath):
    students = []
    try:
        df = pd.read_excel(filepath)
        for _, row in df.iterrows():
            students.append({
                "roll": str(row.iloc[0]),
                "name": str(row.iloc[1]),
                "dept": str(row.iloc[2]) if len(row) > 2 else "NA"
            })
    except Exception as e:
        print(f"Excel error: {e}")
    return students

def read_csv(filepath):
    students = []
    try:
        with open(filepath, newline='', encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    students.append({"roll": row[0], "name": row[1], "dept": row[2] if len(row) > 2 else "NA"})
    except Exception as e:
        print(f"CSV error: {e}")
    return students

def round_robin_merge(file_lists):
    merged = []
    if not file_lists: return []
    max_len = max(len(lst) for lst in file_lists)
    for i in range(max_len):
        for lst in file_lists:
            if i < len(lst): merged.append(lst[i])
    return merged

def distribute_students(students, halls, seats_per_row, rows_per_hall, alternate=True):
    hall_data = []
    index = 0
    for h in range(halls):
        arranged = [[None for _ in range(seats_per_row)] for _ in range(rows_per_hall)]
        for r in range(rows_per_hall):
            for c in range(seats_per_row):
                if alternate:
                    if (r + c) % 2 == 0 and index < len(students):
                        arranged[r][c] = students[index]
                        index += 1
                else:
                    if index < len(students):
                        arranged[r][c] = students[index]
                        index += 1
        hall_data.append(arranged)
    return hall_data

@app.route("/upload", methods=["POST"])
def upload():
    global students_global, hall_data_global
    files = request.files.getlist("files")
    halls = int(request.form.get("halls", 0))
    seats_per_row = int(request.form.get("seats", 0))
    rows_per_hall = int(request.form.get("rows", 0))

    file_lists = []
    for file in files:
        if not file.filename: continue
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        if file.filename.lower().endswith((".xlsx", ".xls")):
            file_lists.append(read_excel(filepath))
        elif file.filename.lower().endswith(".csv"):
            file_lists.append(read_csv(filepath))
    
    if not file_lists: return "No valid files."

    if len(file_lists) == 1:
        students_global = file_lists[0]
        hall_data_global = distribute_students(students_global, halls, seats_per_row, rows_per_hall, alternate=True)
    else:
        students_global = round_robin_merge(file_lists)
        hall_data_global = distribute_students(students_global, halls, seats_per_row, rows_per_hall, alternate=False)

    # Make sure 'hall.html' exists in your templates folder
    return render_template("hall.html", halls=hall_data_global)

@app.route("/download_pdf")
def download_pdf():
    global hall_data_global
    if not hall_data_global: return "No data."
    doc = SimpleDocTemplate(PDF_FILE)
    elements = []
    styles = getSampleStyleSheet()
    for i, hall in enumerate(hall_data_global):
        elements.append(Paragraph(f"Hall {i + 1}", styles["Title"]))
        table_data = []
        for row in hall:
            row_data = [f"{s['roll']}\n{s['name']}" if s else "" for s in row]
            table_data.append(row_data)
        table = Table(table_data)
        table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        elements.append(table)
        elements.append(PageBreak())
    doc.build(elements)
    return send_file(PDF_FILE, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
