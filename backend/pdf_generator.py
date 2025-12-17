from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

def generate_contract_pdf(application_id: str, amount: float, duration: int, filename: str):
    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("Helvetica", 14)
    c.drawString(100, 800, f"Loan Contract for Application: {application_id}")
    c.drawString(100, 770, f"Amount: ${amount}")
    c.drawString(100, 740, f"Duration: {duration} months")
    c.drawString(100, 710, f"Congratulations, your loan is approved!")
    c.save()

def generate_amortization_pdf(schedule: list, filename: str):
    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("Helvetica", 12)
    y = 800
    c.drawString(50, y, "Amortization Schedule")
    y -= 30
    for item in schedule:
        line = f"Month {item['month']}: Payment ${item['payment']} | Principal ${item['principal']} | Interest ${item['interest']} | Remaining ${item['remaining']}"
        c.drawString(50, y, line)
        y -= 20
        if y < 50:
            c.showPage()
            y = 800
    c.save()
