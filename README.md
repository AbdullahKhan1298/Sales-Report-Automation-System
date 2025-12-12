# Sales Report Automation System — Local Demo

## Project Problem Statement
Management needed monthly car-sales reports in a readable format. Raw monthly sales were stored as CSV/JSON files; manually converting those files to a clear PDF each month was repetitive and error-prone.

## What I built
A small, local end-to-end system that:
- Reads monthly sales files from `sample_data/` (CSV or JSON).
- Generates a polished PDF report with charts (pie chart for sales-by-model and a daily sales line).
- Simulates sending the PDF by storing metadata and copying the PDF into `sent_emails/`.
- Provides a clean Flask dashboard to generate reports, view sent emails, and download PDFs — everything runs locally for reproducible demos.

## Why this project
It combines practical skills used in real work:
- Data ingestion and normalization (pandas),
- Visual summaries (matplotlib),
- PDF creation (ReportLab),
- Lightweight web UI for verification and distribution (Flask),
- Simple automation pattern: source → transform → publish.


## Project Structure

<img width="333" height="871" alt="Folder-Structure" src="https://github.com/user-attachments/assets/971c98f4-cdd7-4fb3-ae31-ef9153e7e130" />


## Simple Dashboard

<img width="1915" height="962" alt="Reports-Dashboard" src="https://github.com/user-attachments/assets/cb51f829-8954-47ba-857b-074bef904760" />


## Generated Report

<img width="1925" height="1037" alt="Generated-Report" src="https://github.com/user-attachments/assets/9bb7f85e-a853-4ae2-8707-e067cc9138ad" />

