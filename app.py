import os
import pandas as pd
from flask import Flask, render_template, request, send_file, flash
from openpyxl import load_workbook
from openpyxl.styles import Alignment

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Render-la temporary files-ku /tmp folder thaan use pannanum
UPLOAD_FOLDER = '/tmp/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- 1. CRON-JOB KKAANA PING ROUTE ---
@app.route('/ping')
def ping():
    # Idhu cron-job-kku mattum "OK" sollum, appo "Output too large" error varaathu
    return "OK", 200

# --- 2. HOME PAGE ---
@app.route('/')
def index():
    return render_template('index.html')

# --- 3. EXCEL PROCESSING ROUTE ---
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    
    if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        # File-ah /tmp folder-la save pandrom
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(input_path)
        
        output_filename = "Arranged_" + file.filename
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)

        try:
            # --- Inga unga logic-ah start pannunga ---
            df = pd.read_excel(input_path)
            
            # (Inga neenga seating arrangement logic-ah add pannikkalam)
            # Sample logic: Data-va thirumbavum excel-ah mathuroam
            df.to_excel(output_path, index=False)
            
            # Processing mudinja apram file-ah download panna anuppuroam
            return send_file(output_path, as_attachment=True)
            
        except Exception as e:
            return f"Error processing file: {str(e)}"
    
    return "Invalid file format. Please upload an Excel file."

if __name__ == '__main__':
    # Render automatic-ah PORT assign pannum, illana 5000-la run aagum
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

