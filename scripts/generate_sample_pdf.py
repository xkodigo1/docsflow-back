import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

OUTPUT_DIR = os.path.join("samples")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "sample_invoice.pdf")

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def build_pdf(path: str):
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("DocsFlow - Sample Invoice", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Cliente: ACME Corp", styles["Normal"]))
    story.append(Paragraph("Departamento: Finanzas", styles["Normal"]))
    story.append(Paragraph("Fecha: 2025-09-29", styles["Normal"]))
    story.append(Spacer(1, 18))

    data = [["Item", "Cantidad", "Precio Unitario", "Total"],
            ["Servicio A", "2", "$50.00", "$100.00"],
            ["Servicio B", "3", "$30.00", "$90.00"],
            ["Producto C", "5", "$10.00", "$50.00"],
            ["TOTAL", "", "", "$240.00"]]

    table = Table(data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e8f5e9')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold')
    ]))

    story.append(table)
    story.append(Spacer(1, 24))
    story.append(Paragraph("Notas: Este PDF contiene texto y una tabla para pruebas de extracción.", styles["Italic"]))

    doc = SimpleDocTemplate(path, pagesize=A4, title="DocsFlow Sample Invoice")
    doc.build(story)


def main():
    ensure_dirs()
    build_pdf(OUTPUT_PATH)
    print(f"PDF generado: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
