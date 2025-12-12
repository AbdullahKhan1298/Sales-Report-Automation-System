"""
Flask dashboard for Sales Report Generation.

- Shows available sample data files to generate reports
- Lets you generate a PDF for a chosen month (calls generator + email simulator)
- Lists generated PDFs in generated_reports/
- Lists sent emails from sent_emails/
"""

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from pathlib import Path
import json
import os
import datetime
from src.report_generator import generate_pdf
from src.email_service import send_simulated_email

app = Flask(__name__)
app.secret_key = "dev-key"  # simple secret for flash messages in dev

# directories
BASE = Path(__file__).parent
SAMPLE = BASE / "sample_data"
REPORTS = BASE / "generated_reports"
SENT = BASE / "sent_emails"

REPORTS.mkdir(parents=True, exist_ok=True)
SENT.mkdir(parents=True, exist_ok=True)

def list_sample_files():
    """
    List all files in sample_data that end with .csv or .json
    This feeds the <select> in the dashboard
    """
    files = []
    for ext in ("*.csv","*.json"):
        for p in SAMPLE.glob(ext):
            files.append(p.name)
    # sort so order is predictable
    return sorted(files)

def load_rows_from_sample(filename):
    """
    Read rows from sample CSV or JSON and return list of dicts ready for generator.
    For CSV, expects headers like date,order_id,model,quantity,unit_price,country
    For JSON, expects list of objects with similar keys.
    """
    p = SAMPLE / filename
    if not p.exists():
        return []

    if p.suffix.lower() == ".csv":
        import csv
        rows = []
        with p.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                # normalize keys and types
                # convert numeric fields if present
                r['quantity'] = int(r.get('quantity', 1))
                r['unit_price'] = float(r.get('unit_price', r.get('price', 0)))
                rows.append(r)
        return rows
    else:
        # JSON
        with p.open(encoding='utf-8') as f:
            data = json.load(f)
            # Ensure numeric conversion
            for r in data:
                r['quantity'] = int(r.get('quantity', 1))
                r['unit_price'] = float(r.get('unit_price', r.get('price', 0)))
            return data

@app.route("/", methods=["GET"])
def index():
    files = list_sample_files()
    # list PDFs in generated_reports
    pdfs = sorted([p.name for p in REPORTS.glob("*.pdf")], reverse=True)
    # list sent emails metadata (read JSON files)
    emails = []
    for j in sorted(SENT.glob("*.json"), key=lambda x: x.name, reverse=True):
        try:
            with j.open(encoding='utf-8') as f:
                emails.append(json.load(f))
        except Exception:
            pass
    return render_template("index.html", data_files=files, reports=pdfs, emails=emails)

@app.route("/generate", methods=["POST"])
def generate():
    """
    Form POST handler:
    - read chosen sample filename from form
    - parse rows
    - call generate_pdf to create a PDF inside generated_reports/
    - then call send_simulated_email to "send" it (copy into sent_emails and save metadata)
    - redirect back to index
    """
    filename = request.form.get("file")
    if not filename:
        flash("No file selected", "error")
        return redirect(url_for('index'))

    rows = load_rows_from_sample(filename)
    if not rows:
        flash(f"No rows found in {filename}", "error")
        return redirect(url_for('index'))

    # Build a friendly output PDF name based on filename
    base_name = Path(filename).stem
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_pdf = REPORTS / f"{base_name}_{timestamp}.pdf"

    try:
        # Generate the PDF with charts embedded
        pdf_path = generate_pdf(rows, out_pdf, title=f"Sales Report - {base_name}")
    except Exception as e:
        flash(f"Error generating PDF: {e}", "error")
        return redirect(url_for('index'))

    # "Send" the PDF via the simulated email service (copy + metadata)
    try:
        meta = send_simulated_email(pdf_path)
        flash(f"Report generated and sent (id {meta['id']})", "success")
    except Exception as e:
        flash(f"Report generated but error sending: {e}", "warning")

    return redirect(url_for('index'))

@app.route("/download/<filename>", methods=["GET"])
def download(filename):
    # Serve file from generated_reports folder
    return send_from_directory(REPORTS, filename, as_attachment=True)

@app.route("/sent/<filename>")
def sent_file(filename):
    # serve sent PDFs from sent_emails folder
    return send_from_directory(SENT, filename, as_attachment=True)

if __name__ == "__main__":
    # run app on port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
