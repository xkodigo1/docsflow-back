import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch

OUTPUT_DIR = os.path.join("samples")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "comprehensive_sample.pdf")

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def build_pdf(path: str):
    styles = getSampleStyleSheet()
    story = []

    # Página 1: Factura Completa
    story.append(Paragraph("FACTURA COMERCIAL - ACME CORPORATION", styles["Title"]))
    story.append(Spacer(1, 12))
    
    # Información de la empresa
    company_info = """
    <b>ACME CORPORATION</b><br/>
    Dirección: Av. Principal 123, Ciudad, País<br/>
    Teléfono: +1-555-0123 | Email: info@acme.com<br/>
    RUC: 12345678901 | Código Postal: 12345
    """
    story.append(Paragraph(company_info, styles["Normal"]))
    story.append(Spacer(1, 18))

    # Información del cliente
    client_info = """
    <b>FACTURAR A:</b><br/>
    Cliente: Tech Solutions S.A.<br/>
    Dirección: Calle Secundaria 456<br/>
    Ciudad: Metropolis, Estado 54321<br/>
    Contacto: Juan Pérez | juan@techsolutions.com
    """
    story.append(Paragraph(client_info, styles["Normal"]))
    story.append(Spacer(1, 18))

    # Detalles de la factura
    invoice_details = """
    <b>DETALLES DE LA FACTURA:</b><br/>
    Número: INV-2024-001234<br/>
    Fecha de Emisión: 15 de Enero, 2024<br/>
    Fecha de Vencimiento: 15 de Febrero, 2024<br/>
    Términos de Pago: Neto 30 días<br/>
    Método de Pago: Transferencia Bancaria
    """
    story.append(Paragraph(invoice_details, styles["Normal"]))
    story.append(Spacer(1, 24))

    # Tabla principal de productos/servicios
    data = [
        ["Código", "Descripción", "Cantidad", "Precio Unit.", "Descuento", "Subtotal"],
        ["SRV-001", "Consultoría Técnica Especializada", "40", "$125.00", "5%", "$4,750.00"],
        ["SRV-002", "Desarrollo de Software Personalizado", "80", "$95.00", "10%", "$6,840.00"],
        ["LIC-001", "Licencia de Software Empresarial", "5", "$2,500.00", "0%", "$12,500.00"],
        ["TRN-001", "Capacitación del Personal", "16", "$200.00", "15%", "$2,720.00"],
        ["MNT-001", "Mantenimiento y Soporte Técnico", "12", "$150.00", "0%", "$1,800.00"]
    ]

    table = Table(data, hAlign='LEFT', colWidths=[1*inch, 2.5*inch, 0.8*inch, 1*inch, 0.8*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('ALIGN', (2,1), (5,-1), 'RIGHT'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#ecf0f1')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,1), (-1,-1), 9)
    ]))

    story.append(table)
    story.append(Spacer(1, 18))

    # Resumen financiero
    summary_data = [
        ["Subtotal:", "$28,610.00"],
        ["Descuento Adicional (2%):", "-$572.20"],
        ["Impuesto (IVA 18%):", "$5,046.84"],
        ["Cargo por Servicio:", "$50.00"],
        ["TOTAL A PAGAR:", "$33,134.64"]
    ]

    summary_table = Table(summary_data, hAlign='RIGHT', colWidths=[2*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (0,-1), 'RIGHT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), 12),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e8f5e9')),
        ('LINEBELOW', (0,-2), (-1,-2), 1, colors.black)
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 24))

    # Información de pago
    payment_info = """
    <b>INFORMACIÓN DE PAGO:</b><br/>
    Banco: Banco Nacional de Comercio<br/>
    Cuenta Corriente: 1234567890<br/>
    Código SWIFT: BNCOUS33<br/>
    Referencia: INV-2024-001234
    """
    story.append(Paragraph(payment_info, styles["Normal"]))
    story.append(Spacer(1, 12))

    # Notas adicionales
    notes = """
    <b>NOTAS IMPORTANTES:</b><br/>
    • Esta factura debe ser pagada dentro de los 30 días siguientes a la fecha de emisión.<br/>
    • Los pagos tardíos están sujetos a una tasa de interés del 1.5% mensual.<br/>
    • Para consultas sobre esta factura, contacte a nuestro departamento de facturación.<br/>
    • Todos los precios están expresados en dólares estadounidenses (USD).
    """
    story.append(Paragraph(notes, styles["Normal"]))
    story.append(PageBreak())

    # Página 2: Reporte de Ventas Mensual
    story.append(Paragraph("REPORTE DE VENTAS - ENERO 2024", styles["Title"]))
    story.append(Spacer(1, 12))

    # Resumen ejecutivo
    executive_summary = """
    <b>RESUMEN EJECUTIVO:</b><br/>
    El mes de enero 2024 ha mostrado un crecimiento significativo en nuestras ventas, 
    con un incremento del 23.5% comparado con el mismo período del año anterior. 
    Los departamentos de Tecnología y Servicios Profesionales han sido los principales 
    contribuyentes a este crecimiento.
    """
    story.append(Paragraph(executive_summary, styles["Normal"]))
    story.append(Spacer(1, 18))

    # Tabla de ventas por departamento
    sales_data = [
        ["Departamento", "Ventas Q1", "Ventas Q2", "Ventas Q3", "Ventas Q4", "Total Anual", "% del Total"],
        ["Tecnología", "$125,450", "$142,300", "$158,900", "$175,200", "$600,950", "35.2%"],
        ["Servicios Profesionales", "$98,750", "$112,400", "$128,600", "$145,800", "$485,550", "28.4%"],
        ["Consultoría", "$87,200", "$95,300", "$108,400", "$122,100", "$413,000", "24.2%"],
        ["Capacitación", "$45,600", "$52,100", "$58,900", "$65,400", "$222,000", "13.0%"],
        ["Otros Servicios", "$12,500", "$15,200", "$18,700", "$22,100", "$68,500", "4.0%"],
        ["TOTAL", "$389,500", "$417,300", "$453,500", "$530,600", "$1,791,000", "100.0%"]
    ]

    sales_table = Table(sales_data, hAlign='LEFT', colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
    sales_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e8f5e9')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,1), (-1,-1), 8)
    ]))

    story.append(sales_table)
    story.append(Spacer(1, 18))

    # Tabla de clientes principales
    clients_data = [
        ["Cliente", "Contrato", "Valor Mensual", "Duración", "Estado"],
        ["Tech Solutions S.A.", "TS-2024-001", "$15,000", "12 meses", "Activo"],
        ["Global Corp Ltd.", "GC-2024-002", "$22,500", "24 meses", "Activo"],
        ["Innovation Inc.", "II-2024-003", "$18,750", "18 meses", "Activo"],
        ["StartupXYZ", "SX-2024-004", "$8,500", "6 meses", "Pendiente"],
        ["Enterprise Co.", "EC-2024-005", "$35,000", "36 meses", "Activo"]
    ]

    clients_table = Table(clients_data, hAlign='LEFT', colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1*inch, 1*inch])
    clients_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#8e44ad')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('ALIGN', (2,1), (2,-1), 'RIGHT'),
        ('FONTSIZE', (0,1), (-1,-1), 8)
    ]))

    story.append(clients_table)
    story.append(Spacer(1, 18))

    # Métricas de rendimiento
    metrics = """
    <b>MÉTRICAS CLAVE DE RENDIMIENTO:</b><br/>
    • Tasa de Conversión: 12.3% (objetivo: 10%)<br/>
    • Tiempo Promedio de Cierre: 45 días (objetivo: 60 días)<br/>
    • Satisfacción del Cliente: 4.7/5.0 (objetivo: 4.5/5.0)<br/>
    • Retención de Clientes: 94.2% (objetivo: 90%)<br/>
    • Crecimiento Interanual: +23.5% (objetivo: +15%)
    """
    story.append(Paragraph(metrics, styles["Normal"]))
    story.append(Spacer(1, 12))

    # Proyecciones
    projections = """
    <b>PROYECCIONES PARA EL PRÓXIMO TRIMESTRE:</b><br/>
    Basado en el rendimiento actual y las tendencias del mercado, se proyecta un crecimiento 
    del 18-22% en el próximo trimestre. Los departamentos de Tecnología y Servicios 
    Profesionales continuarán siendo los principales motores de crecimiento.
    """
    story.append(Paragraph(projections, styles["Normal"]))
    story.append(PageBreak())

    # Página 3: Análisis Financiero Detallado
    story.append(Paragraph("ANÁLISIS FINANCIERO DETALLADO", styles["Title"]))
    story.append(Spacer(1, 12))

    # Estado de resultados
    income_statement = """
    <b>ESTADO DE RESULTADOS - ENERO 2024</b><br/>
    Ingresos Totales: $1,791,000<br/>
    Costo de Ventas: $1,074,600 (60%)<br/>
    Utilidad Bruta: $716,400 (40%)<br/>
    Gastos Operativos: $358,200 (20%)<br/>
    Utilidad Operativa: $358,200 (20%)<br/>
    Gastos Financieros: $17,910 (1%)<br/>
    Utilidad Neta: $340,290 (19%)
    """
    story.append(Paragraph(income_statement, styles["Normal"]))
    story.append(Spacer(1, 18))

    # Tabla de análisis de costos
    costs_data = [
        ["Categoría", "Presupuesto", "Real", "Variación", "% del Total"],
        ["Personal", "$450,000", "$465,200", "+$15,200", "43.3%"],
        ["Tecnología", "$180,000", "$175,800", "-$4,200", "16.4%"],
        ["Marketing", "$120,000", "$128,500", "+$8,500", "12.0%"],
        ["Administración", "$95,000", "$98,300", "+$3,300", "9.2%"],
        ["Capacitación", "$60,000", "$58,900", "-$1,100", "5.5%"],
        ["Otros", "$45,000", "$47,200", "+$2,200", "4.4%"],
        ["TOTAL", "$935,000", "$973,900", "+$38,900", "100.0%"]
    ]

    costs_table = Table(costs_data, hAlign='LEFT', colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    costs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
        ('FONTSIZE', (0,1), (-1,-1), 8)
    ]))

    story.append(costs_table)
    story.append(Spacer(1, 18))

    # Análisis de rentabilidad por producto
    profitability_data = [
        ["Producto/Servicio", "Ingresos", "Costos", "Margen", "ROI"],
        ["Consultoría Premium", "$485,550", "$291,330", "40%", "67%"],
        ["Desarrollo Software", "$600,950", "$360,570", "40%", "67%"],
        ["Capacitación Corporativa", "$222,000", "$155,400", "30%", "43%"],
        ["Soporte Técnico", "$413,000", "$330,400", "20%", "25%"],
        ["Licencias", "$68,500", "$20,550", "70%", "233%"]
    ]

    profitability_table = Table(profitability_data, hAlign='LEFT', colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 0.8*inch, 0.8*inch])
    profitability_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
        ('FONTSIZE', (0,1), (-1,-1), 8)
    ]))

    story.append(profitability_table)
    story.append(Spacer(1, 18))

    # Conclusiones y recomendaciones
    conclusions = """
    <b>CONCLUSIONES Y RECOMENDACIONES:</b><br/>
    1. <b>Rendimiento Sólido:</b> El crecimiento del 23.5% supera significativamente nuestros objetivos.<br/>
    2. <b>Optimización de Costos:</b> Se recomienda revisar la categoría de Personal para controlar el sobrecosto.<br/>
    3. <b>Oportunidades de Crecimiento:</b> Las licencias muestran el mayor ROI y deben ser priorizadas.<br/>
    4. <b>Eficiencia Operativa:</b> El tiempo de cierre mejorado indica procesos optimizados.<br/>
    5. <b>Inversión en Tecnología:</b> La reducción en costos tecnológicos sugiere eficiencia en esta área.
    """
    story.append(Paragraph(conclusions, styles["Normal"]))

    doc = SimpleDocTemplate(path, pagesize=A4, title="DocsFlow Comprehensive Sample")
    doc.build(story)


def main():
    ensure_dirs()
    build_pdf(OUTPUT_PATH)
    print(f"PDF generado: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
