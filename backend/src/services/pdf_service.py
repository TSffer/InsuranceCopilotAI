from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from typing import List, Dict, Any, Optional

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

class PDFService:
    def __init__(self):
        fonts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'fonts')
        
        try:
            pdfmetrics.registerFont(TTFont('Poppins-Bold', os.path.join(fonts_dir, 'Poppins-Bold.ttf')))
            pdfmetrics.registerFont(TTFont('Poppins-Regular', os.path.join(fonts_dir, 'Poppins-Regular.ttf')))
            self.title_font = 'Poppins-Bold'
            self.subtitle_font = 'Poppins-Regular'
        except Exception:
            self.title_font = 'Helvetica-Bold'
            self.subtitle_font = 'Helvetica'
            
        try:
            pdfmetrics.registerFont(TTFont('Inter-Regular', os.path.join(fonts_dir, 'Inter-Regular.ttf')))
            pdfmetrics.registerFont(TTFont('Inter-Bold', os.path.join(fonts_dir, 'Inter-Bold.ttf')))
            self.body_font = 'Inter-Regular'
            self.bold_font = 'Inter-Bold'
        except Exception:
            self.body_font = 'Helvetica'
            self.bold_font = 'Helvetica-Bold'

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
            fontSize=24,
            fontName=self.title_font
        )
        subtitle_style = ParagraphStyle(
            name='SlipSubtitle', 
            parent=styles['Heading2'], 
            alignment=1, # Center
            spaceAfter=10, 
            textColor=colors.HexColor("#3b82f6"),
            fontSize=16,
            fontName=self.subtitle_font
        )
        body_style = ParagraphStyle(
            name='BodyTextCustom',
            parent=styles['BodyText'],
            spaceAfter=6,
            leading=14,
            fontName=self.body_font
        )
        
        styles['Heading2'].fontName = self.title_font
        styles['Heading3'].fontName = self.title_font
        styles['Heading4'].fontName = self.title_font
        
        story = []
        
        story.append(Paragraph("INSURANCE COPILOT", title_style))
        story.append(Paragraph(f"{title}", subtitle_style))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("Resumen de Información Generada", styles['Italic']))
        story.append(Spacer(1, 1*cm))
        
        lines = content.split('\n')
        
        in_table = False
        table_rows = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if in_table and table_rows:
                    self._render_markdown_table(story, table_rows, styles)
                    in_table = False
                    table_rows = []
                continue
                
            if '|' in line and line.startswith('|') and line.endswith('|'):
                in_table = True
                if set(line.replace('|', '').replace('-', '').replace(':', '').strip()) == set():
                    continue
                
                row_data = [col.strip() for col in line.split('|')[1:-1]]
                table_rows.append(row_data)
                continue
            import re
            
            formatted_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            
            formatted_line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', formatted_line)
            
            p_style = body_style
            if line.startswith('# '):
                p_style = styles['Heading2']
                formatted_line = formatted_line.replace('# ', '')
            elif line.startswith('## '):
                p_style = styles['Heading3']
                formatted_line = formatted_line.replace('## ', '')
            elif line.startswith('### '):
                p_style = styles['Heading4']
                formatted_line = formatted_line.replace('### ', '')
            elif line.startswith('- '):
                formatted_line = f"• {formatted_line[2:]}"
                
            try:
                story.append(Paragraph(formatted_line, p_style))
            except:
                story.append(Paragraph(line, p_style))
                
        if in_table and table_rows:
            self._render_markdown_table(story, table_rows, styles)

        story.append(Spacer(1, 1*cm))

        if table_data and len(table_data) > 0:
            story.append(Paragraph("Tabla Comparativa", styles['Heading2']))
            story.append(Spacer(1, 0.5*cm))
            
            comparison_rows = []
            
            # Headers
            first_row = table_data[0]
            headers = ["Atributo", "Opción A", "Opción B"] # Default fallback
            
            if isinstance(first_row, dict):
                keys = list(first_row.keys())
                headers = keys
                
                comparison_rows.append(headers)
                
                for row in table_data:
                    comparison_rows.append([str(row.get(k, '')) for k in keys])
            
            col_width = (17/len(headers))*cm if headers else 5*cm
            
            cell_style = styles['BodyText']
            formatted_data = []
            for row in comparison_rows:
                formatted_row = [Paragraph(str(cell), cell_style) for cell in row]
                formatted_data.append(formatted_row)
            
            t = Table(formatted_data, colWidths=[col_width]*len(headers))
            
            # Table Style
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e0f2fe")), 
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0f172a")), 
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8fafc")), 
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(t)
            
        doc.build(story)
        buffer.seek(0)
        return buffer

    def _render_markdown_table(self, story: List[Any], table_rows: List[List[str]], styles: Any) -> None:
        if not table_rows:
            return
            
        num_cols = len(table_rows[0])
        col_width = (17/num_cols)*cm if num_cols else 5*cm
        
        cell_style = styles['BodyText']
        cell_style.fontSize = 8
        cell_style.leading = 10
        
        header_style = ParagraphStyle('TableHeader', parent=cell_style, fontName='Helvetica-Bold')
        
        formatted_table = []
        for i, row in enumerate(table_rows):
            style_to_use = header_style if i == 0 else cell_style
            formatted_row = []
            import re
            for cell in row:
                cell_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', cell)
                formatted_row.append(Paragraph(cell_text, style_to_use))
            formatted_table.append(formatted_row)
        
        t = Table(formatted_table, colWidths=[col_width]*num_cols)
        
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e0f2fe")), # Header bg
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0f172a")), # Header text
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8fafc")), # Row bg
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(t)
        story.append(Spacer(1, 0.5*cm))
