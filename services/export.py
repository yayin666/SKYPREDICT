import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def export_to_csv(df: pd.DataFrame) -> str:
    return df.to_csv(index=False)

def export_to_excel(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='SkyPredict Report')
    return buffer.getvalue()

def export_to_pdf(df: pd.DataFrame, title: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"SkyPredict - {title}")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    y = height - 100
    c.setFont("Helvetica-Bold", 10)
    
    # Write Headers (max 5 columns for space)
    cols = list(df.columns)[:5]
    x_positions = [50, 150, 250, 350, 450]
    for i, col in enumerate(cols):
        c.drawString(x_positions[i], y, str(col))
        
    y -= 20
    c.setFont("Helvetica", 9)
    
    # Write Rows
    for _, row in df.head(40).iterrows(): # Limit to 40 rows
        for i, col in enumerate(cols):
            c.drawString(x_positions[i], y, str(row[col])[:15])
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50
            
    c.save()
    return buffer.getvalue()
