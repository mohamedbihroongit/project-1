from flask import Flask, render_template, request, send_file
import os
import csv
import pandas as pd  # Pandas use pannuradhala idhu mela irukkanum
from openpyxl import load_workbook
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# --- SERVER PATH UPDATES (Render Friendly) ---
# Render-la files save panna /tmp folder thaan best
UPLOAD_FOLDER = "/tmp/uploads"
PDF_FILE = "/tmp/Hall_Seat_Arrangement.pdf"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

students_global = []
hall_data_global = []

# -------- NEW PING ROUTE (For Cron-job) --------
@app.route('/ping')
def ping():
    return "OK", 200
# -----------------------------------------------

# -------- READ EXCEL --------
def read_excel(filepath):
    students = []
    # Pandas use panni easy-ah read pannalam (Error kammiyaagum)
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

# -------- READ CSV --------
def read_csv(filepath):
    students = []
    try:
        with open(filepath, newline='', encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    students.append({
                        "roll": row[0],
                        "name": row[1],
                        "dept": row[2] if len(row) > 2 else "NA"
                    })
    except Exception as e:
        print(f"CSV error: {e}")
    return students

# -------- ROUND ROBIN --------
def round_robin_merge(file_lists):
    merged = []
    if not file_lists: return []
    max_len = max(len(lst) for lst in file_lists)
    for i in range(max_len):
        for lst in file_lists:
            if i < len(lst):
                merged.append(lst[i])
    return merged

# -------- DISTRIBUTE --------
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

# -------- ROUTES --------
@app.route("/")
def home():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload():
    global students_global, hall_data_global
    students_global = []
    hall_data_global = []

    files = request.files.getlist("files")
    halls = int(request.form.get("halls", 0))
    seats_per_row = int(request.form.get("seats", 0))
    rows_per_hall = int(request.form.get("rows", 0))

    file_lists = []
    for file in files:
        if file.filename == '': continue
        filename = file.filename.lower()
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_lists.append(read_excel(filepath))
        elif filename.endswith(".csv"):
            file_lists.append(read_csv(filepath))
    
    if not file_lists:
        return "No valid files uploaded."

    if len(file_lists) == 1:
        students_global = file_lists[0]
        hall_data_global = distribute_students(students_global, halls, seats_per_row, rows_per_hall, alternate=True)
    else:
        students_global = round_robin_merge(file_lists)
        hall_data_global = distribute_students(students_global, halls, seats_per_row, rows_per_hall, alternate=False)

    return render_template("hall.html", halls=hall_data_global)

@app.route("/download_pdf")
def download_pdf():
    global hall_data_global
    if not hall_data_global:
        return "No data to generate PDF."

    doc = SimpleDocTemplate(PDF_FILE)
    elements = []
    styles = getSampleStyleSheet()

    for i, hall in enumerate(hall_data_global):
        elements.append(Paragraph(f"Hall {i + 1}", styles["Title"]))
        elements.append(Spacer(1, 20))
        table_data = []
        for row in hall:
            row_data = []
            for student in row:
                if student:
                    row_data.append(f"{student['roll']}\n{student['name']}\n{student['dept']}")
                else:
                    row_data.append("")
            table_data.append(row_data)
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)
        elements.append(PageBreak())

    doc.build(elements)
    return send_file(PDF_FILE, as_attachment=True)

# -------- SERVER CONFIG --------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


