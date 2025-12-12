# src/email_service.py
"""
Simple email simulator:
- Save a metadata JSON into sent_emails/
- Copy the PDF file there (so dashboard can list it)
"""

import json
from pathlib import Path
import shutil
import datetime
import os

SENT_DIR = Path.cwd() / "sent_emails"
SENT_DIR.mkdir(parents=True, exist_ok=True)

def send_simulated_email(pdf_path, sender="abdullahkh1298@gmail.com", recipient="boss@example.com", subject="Monthly Sales Report", body="Please find attached."):
    """
    pdf_path: path to PDF that was generated
    This function will:
      - copy the PDF to sent_emails/
      - save a small JSON with metadata for the dashboard to read
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # create unique timestamped filename
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    saved_pdf_name = f"{ts}_{pdf_path.name}"
    dest_pdf = SENT_DIR / saved_pdf_name
    shutil.copyfile(pdf_path, dest_pdf)

    # metadata
    meta = {
        "id": len(list(SENT_DIR.glob("*.json"))) + 1,
        "timestamp": ts,
        "from": sender,
        "to": recipient,
        "subject": subject,
        "body": body,
        "attachment": saved_pdf_name
    }

    # write metadata to file
    meta_file = SENT_DIR / f"{meta['id']}.json"
    with meta_file.open('w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)

    # return meta for logging
    return meta
