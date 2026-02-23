from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from typing import List, Dict, Any, Optional

class PDFService:
    def generate_slip(self, title: str, content: str, table_data: Optional[List[Dict[str, Any]]] = None) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            rightMargin=2*cm, 
            leftMargin=2*cm, 
            topMargin=2*cm, 
            bottomMargin=2*cm
        )
        
        styles = getSampleStyleSheet()
        # Custom Styles
        title_style = ParagraphStyle(
            name='SlipTitle', 
            parent=styles['Heading1'], 
            alignment=1, # Center
            spaceAfter=20, 
            textColor=colors.HexColor("#1e3a8a"),
            fontSize=24
        )
        subtitle_style = ParagraphStyle(
            name='SlipSubtitle', 
            parent=styles['Heading2'], 
            alignment=1, # Center
            spaceAfter=10, 
            textColor=colors.HexColor("#3b82f6"),
            fontSize=16
        )
        body_style = ParagraphStyle(
            name='BodyTextCustom',
            parent=styles['BodyText'],
            spaceAfter=6,
            leading=14
        )
        
        story = []
        
        # Header
        story.append(Paragraph("INSURANCE COPILOT", title_style))
        story.append(Paragraph(f"{title}", subtitle_style))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("Resumen de Información Generada", styles['Italic']))
        story.append(Spacer(1, 1*cm))
        
        # Content Parsing (Simple Markdown to Paragraphs)
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Basic styling
            # Replace **bold** with <b>bold</b>
            formatted_line = line.replace('**', '<b>').replace('**', '</b>')
            # Replace *italic* with <i>italic</i>
            formatted_line = formatted_line.replace('*', '<i>').replace('*', '</i>')
            
            p_style = body_style
            if line.startswith('# '):
                p_style = styles['Heading2']
                formatted_line = formatted_line.replace('# ', '')
            elif line.startswith('## '):
                p_style = styles['Heading3']
                formatted_line = formatted_line.replace('## ', '')
            elif line.startswith('- '):
                formatted_line = f"• {formatted_line[2:]}"
                
            try:
                story.append(Paragraph(formatted_line, p_style))
            except:
                # Fallback for weird characters
                story.append(Paragraph(line, p_style))
                
        story.append(Spacer(1, 1*cm))
        
        # Table Data Section (if present)
        if table_data and len(table_data) > 0:
            story.append(Paragraph("Tabla Comparativa", styles['Heading2']))
            story.append(Spacer(1, 0.5*cm))
            
            # Extract headers from the first row keys
            # Assumption: table_data is a list of dictionaries with consistent keys
            comparison_rows = []
            
            # Headers
            first_row = table_data[0]
            headers = ["Atributo", "Opción A", "Opción B"] # Default fallback
            
            if isinstance(first_row, dict):
                # Try to infer meaningful headers or just take keys
                keys = list(first_row.keys())
                headers = keys
                
                comparison_rows.append(headers)
                
                # Rows
                for row in table_data:
                    comparison_rows.append([str(row.get(k, '')) for k in keys])
            
            # Constants for column width
            # A4 width ~21cm, margins 4cm total -> 17cm usable
            col_width = (17/len(headers))*cm if headers else 5*cm
            
            t = Table(comparison_rows, colWidths=[col_width]*len(headers))
            
            # Table Style
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e0f2fe")), # Header bg
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0f172a")), # Header text
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8fafc")), # Row bg
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('WORDWRAP', (0, 0), (-1, -1), True),
            ]))
            story.append(t)
            
        doc.build(story)
        buffer.seek(0)
        return buffer
