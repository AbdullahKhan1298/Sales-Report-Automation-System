"""
Generate a PDF sales report with embedded pie chart and daily sales plot.
This file is intentionally commented heavily (beginner-friendly).
"""

import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import mm
from pathlib import Path
import tempfile
import os
import datetime

def _safe_df_from_rows(rows):
    """
    Convert a list-of-dicts 'rows' into a pandas DataFrame.
    Ensure numeric types and compute total = quantity * unit_price.
    """
    df = pd.DataFrame(rows)
    # If quantity or unit_price not present, try fallback keys
    if 'quantity' not in df.columns:
        df['quantity'] = 1
    if 'unit_price' not in df.columns:
        if 'price' in df.columns:
            df['unit_price'] = df['price']
        else:
            df['unit_price'] = 0.0

    # ensure types
    df['quantity'] = df['quantity'].astype(int)
    df['unit_price'] = df['unit_price'].astype(float)
    df['total'] = df['quantity'] * df['unit_price']
    return df

def _create_charts(df, tmpdir):
    """
    Create two charts:
      - pie chart of sales by model (revenue share)
      - daily sales line chart
    Save both images into tmpdir and return their paths.
    """
    # Pie chart data
    by_model = df.groupby('model')['total'].sum().sort_values(ascending=False)

    pie_path = tmpdir / "pie.png"
    plt.figure(figsize=(4,4))
    # autopct shows percent; startangle rotates chart
    by_model.plot.pie(autopct='%1.1f%%', startangle=140)
    plt.ylabel('')  # remove default y-label
    plt.title('Sales by Model')
    plt.tight_layout()
    plt.savefig(pie_path)
    plt.close()

    # Daily totals
    daily = df.groupby(df['date'])['total'].sum().reset_index()
    daily['date'] = pd.to_datetime(daily['date'])
    daily = daily.sort_values('date')

    daily_path = tmpdir / "daily.png"
    plt.figure(figsize=(6,3))
    plt.plot(daily['date'], daily['total'], marker='o', linewidth=1)
    plt.title('Daily Sales')
    plt.xlabel('Date')
    plt.ylabel('Revenue ($)')
    plt.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig(daily_path)
    plt.close()

    return str(pie_path), str(daily_path)

def generate_pdf(rows, out_pdf_path, title=None):
    """
    Main function.
    - rows: list of dicts (sales rows)
    - out_pdf_path: where to save the final PDF (string or Path)
    - title: optional title to place on top
    Returns: path to generated PDF
    """
    # convert to DataFrame and compute totals
    df = _safe_df_from_rows(rows)

    # summary numbers used at top of PDF
    total_revenue = df['total'].sum()
    orders = df['order_id'].nunique() if 'order_id' in df.columns else len(df)
    top_models = df.groupby('model')['total'].sum().sort_values(ascending=False).head(5)

    # create temporary directory for images
    tmpdir = Path(tempfile.mkdtemp(prefix="report_"))

    # create charts and get their file paths
    pie_img, daily_img = _create_charts(df, tmpdir)

    # ensure output folder exists
    out_pdf_path = Path(out_pdf_path)
    out_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # create PDF document
    doc = SimpleDocTemplate(str(out_pdf_path), pagesize=A4,
                            rightMargin=20,leftMargin=20,
                            topMargin=20,bottomMargin=20)
    styles = getSampleStyleSheet()
    story = []

    # Title
    report_title = title or f"Sales Report - {datetime.datetime.now().strftime('%Y-%m-%d')}"
    story.append(Paragraph(report_title, styles['Title']))
    story.append(Spacer(1, 6))

    # Summary block
    story.append(Paragraph(f"<b>Total Revenue:</b> ${total_revenue:,.2f}", styles['Normal']))
    story.append(Paragraph(f"<b>Orders:</b> {orders}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Top models table
    story.append(Paragraph("<b>Top Models</b>", styles['Heading3']))
    table_data = [["Model", "Revenue ($)"]]
    for model, value in top_models.items():
        table_data.append([model, f"{value:,.2f}"])
    t = Table(table_data, colWidths=[90*mm, 60*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f2f2f2')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Pie chart embedded
    story.append(Paragraph("<b>Sales by Model</b>", styles['Heading3']))
    story.append(Image(pie_img, width=180, height=180))
    story.append(Spacer(1, 12))

    # Daily chart embedded
    story.append(Paragraph("<b>Sales Over Time</b>", styles['Heading3']))
    story.append(Image(daily_img, width=420, height=120))
    story.append(Spacer(1, 12))

    # Sample rows table (first 20)
    story.append(Paragraph("<b>Sample Sales Rows</b>", styles['Heading3']))
    table_rows = [["Date","Order","Model","Qty","Unit Price","Total"]]
    for _, r in df.head(20).iterrows():
        table_rows.append([
            str(r['date']),
            str(r.get('order_id','-')),
            str(r.get('model','-')),
            str(r.get('quantity',1)),
            f"{r.get('unit_price',0.0):,.2f}",
            f"{r.get('total',0.0):,.2f}"
        ])
    t2 = Table(table_rows, colWidths=[70,60,120,40,60,60])
    t2.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0'))
    ]))
    story.append(t2)
    story.append(Spacer(1, 12))

    # Footer
    story.append(Paragraph("Generated by Sales Report Automation", styles['Normal']))

    # build document
    doc.build(story)

    # cleanup temporary images and directory
    try:
        if os.path.exists(pie_img):
            os.remove(pie_img)
        if os.path.exists(daily_img):
            os.remove(daily_img)
        # remove tmpdir if empty
        try:
            os.rmdir(tmpdir)
        except OSError:
            pass
    except Exception:
        pass

    return str(out_pdf_path)
