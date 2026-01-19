"""
PDF Generator for The Cutter (Local-First).
Generates professional quote PDFs using ReportLab (no cloud services).

Architecture: Per Docs/SYSTEM_BEHAVIOR_SPEC.md Section 2 (The Price Stack)
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from typing import Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
from io import BytesIO
import qrcode


class QuotePDFGenerator:
    """
    Generates PDF quotes with Glass Box pricing transparency.
    
    Design Constraints (per Docs/UI DESIGN CONSTRAINTS):
    - Spacing: 8 / 16 / 24 / 32 px (converted to points)
    - Colors: Grayscale only (PDF standard)
    - Layout: Single column, clean hierarchy
    """
    
    def __init__(self, output_dir: str = "quotes_pdf"):
        """
        Initialize PDF generator.
        
        Args:
            output_dir: Directory to save generated PDFs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Spacing palette (convert px to points: 1px ≈ 0.75pt)
        self.SPACING_XS = 6   # 8px
        self.SPACING_SM = 12  # 16px
        self.SPACING_MD = 18  # 24px
        self.SPACING_LG = 24  # 32px
        
        # Initialize styles
        self.styles = getSampleStyleSheet()
        self._init_custom_styles()
    
    def _generate_qr_code(self, data: str, size: float = 1.5) -> Image:
        """
        Generate QR code as ReportLab Image object.
        
        Per EXECUTION_CHAT_BRIEF.md Section: QR Code Specification
        
        Args:
            data: Text to encode (typically Job ID)
            size: Size in inches (default: 1.5)
        
        Returns:
            ReportLab Image object containing QR code
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return Image(buffer, width=size*inch, height=size*inch)
    
    def _init_custom_styles(self):
        """Initialize custom paragraph styles."""
        # Header style (Quote ID, Customer Name)
        self.styles.add(ParagraphStyle(
            name='QuoteHeader',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=self.SPACING_MD,
            alignment=TA_LEFT
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=self.SPACING_SM,
            spaceBefore=self.SPACING_LG,
            alignment=TA_LEFT
        ))
        
        # Body text (custom style to avoid conflict with built-in 'BodyText')
        self.styles.add(ParagraphStyle(
            name='CutterBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=self.SPACING_XS,
            alignment=TA_LEFT
        ))
        
        # Small gray text (metadata)
        self.styles.add(ParagraphStyle(
            name='Metadata',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            spaceAfter=self.SPACING_XS,
            alignment=TA_LEFT
        ))
        
        # Right-aligned text
        self.styles.add(ParagraphStyle(
            name='RightAlign',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_RIGHT
        ))
    
    def generate_quote_pdf(
        self,
        quote_data: Dict[str, Any],
        filename: Optional[str] = None,
        customer_facing: bool = True
    ) -> str:
        """
        Generate PDF from quote data.
        
        Args:
            quote_data: Quote dictionary from database.get_all_history()
            filename: Optional custom filename (default: Q-{quote_id}.pdf)
            customer_facing: If True, hide internal pricing data (Glass Box).
                           If False, show full breakdown (anchor, variance, tags).
        
        Returns:
            Path to generated PDF file
        """
        # Generate filename
        if filename is None:
            quote_id = quote_data.get('quote_id', 'UNKNOWN')
            filename = f"{quote_id}.pdf"
        
        filepath = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build content
        content = []
        
        # Header section
        content.extend(self._build_header(quote_data))
        
        # Customer & Contact section
        content.extend(self._build_customer_section(quote_data))
        
        # Part Information section
        content.extend(self._build_part_section(quote_data))
        
        # RFQ Details section
        content.extend(self._build_rfq_section(quote_data))
        
        # Pricing Breakdown section (Glass Box or Customer-Safe)
        content.extend(self._build_pricing_section(quote_data, customer_facing))
        
        # Outside Processing & Quality Requirements
        content.extend(self._build_requirements_section(quote_data))
        
        # Notes section
        if quote_data.get('notes'):
            content.extend(self._build_notes_section(quote_data))
        
        # Footer
        content.extend(self._build_footer(quote_data))
        
        # Build PDF
        doc.build(content)
        
        return str(filepath)
    
    def _build_header(self, data: Dict[str, Any]) -> list:
        """
        Build PDF header with shop branding and quote ID.
        
        Per EXECUTION_CHAT_BRIEF.md Section: Shop Branding Specification
        - Font: Helvetica-Bold for company name (14pt)
        - Font: Helvetica for contact info (10pt)
        - Color: Grayscale only
        - Spacing: 16px (SPACING_SM) after header block
        """
        elements = []
        
        # Shop Branding Header (per UI Design Constraints Section 1)
        import database
        shop_name = database.get_config('shop_name', 'Machine Shop', str)
        shop_address = database.get_config('shop_address', '', str)
        shop_phone = database.get_config('shop_phone', '', str)
        shop_email = database.get_config('shop_email', '', str)
        
        # Company name (bold, 14pt)
        branding_style = ParagraphStyle(
            name='ShopBranding',
            parent=self.styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=4,
            alignment=TA_LEFT
        )
        elements.append(Paragraph(shop_name, branding_style))
        
        # Contact info (regular, 10pt)
        contact_style = ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=2,
            alignment=TA_LEFT
        )
        
        if shop_address:
            elements.append(Paragraph(shop_address, contact_style))
        
        # Phone and Email on one line
        contact_line = []
        if shop_phone:
            contact_line.append(shop_phone)
        if shop_email:
            contact_line.append(shop_email)
        
        if contact_line:
            elements.append(Paragraph(' | '.join(contact_line), contact_style))
        
        # Separator space (16px per UI Design Constraints)
        elements.append(Spacer(1, self.SPACING_SM))
        
        # Horizontal line separator
        from reportlab.platypus import HRFlowable
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor('#cccccc'),
            spaceAfter=self.SPACING_SM
        ))
        
        # Quote ID
        quote_id = data.get('quote_id', 'DRAFT')
        header_text = f"Quote {quote_id}"
        elements.append(Paragraph(header_text, self.styles['QuoteHeader']))
        
        # Date
        timestamp = data.get('timestamp', datetime.now().isoformat())
        try:
            date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            date_str = date_obj.strftime('%B %d, %Y')
        except:
            date_str = timestamp
        
        elements.append(Paragraph(f"Date: {date_str}", self.styles['Metadata']))
        
        # Status badge
        status = data.get('status', 'Draft')
        elements.append(Paragraph(f"Status: {status}", self.styles['Metadata']))
        
        elements.append(Spacer(1, self.SPACING_LG))
        
        return elements
    
    def _build_customer_section(self, data: Dict[str, Any]) -> list:
        """Build customer and contact information section."""
        elements = []
        
        elements.append(Paragraph("Customer Information", self.styles['SectionHeader']))
        
        # Customer details
        customer_name = data.get('customer_name', 'Walk-In Customer')
        customer_domain = data.get('customer_domain', '')
        
        customer_info = [
            ['Company:', customer_name],
        ]
        
        if customer_domain and customer_domain != 'unknown':
            customer_info.append(['Domain:', customer_domain])
        
        # Contact details
        contact_name = data.get('contact_name', '')
        contact_email = data.get('contact_email', '')
        
        if contact_name:
            customer_info.append(['Contact:', contact_name])
        if contact_email:
            customer_info.append(['Email:', contact_email])
        
        # Create table
        table = Table(customer_info, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a1a1a')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, self.SPACING_LG))
        
        return elements
    
    def _build_part_section(self, data: Dict[str, Any]) -> list:
        """Build part geometry information section."""
        elements = []
        
        elements.append(Paragraph("Part Information", self.styles['SectionHeader']))
        
        # Part details
        filename = data.get('filename', 'Unknown')
        volume = data.get('volume') or 0  # Handle None values
        dimensions = data.get('dimensions', {})
        
        part_info = [
            ['Filename:', filename],
            ['Volume:', f"{volume:.2f} in³"],
        ]
        
        # Dimensions
        if isinstance(dimensions, dict):
            dim_x = dimensions.get('x') or 0  # Handle None values
            dim_y = dimensions.get('y') or 0
            dim_z = dimensions.get('z') or 0
            part_info.append(['Bounding Box:', f"{dim_x:.2f}\" × {dim_y:.2f}\" × {dim_z:.2f}\""])
        
        # Material
        material = data.get('material', 'Unknown')
        part_info.append(['Material:', material])
        
        # Create table
        table = Table(part_info, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a1a1a')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, self.SPACING_LG))
        
        return elements
    
    def _build_rfq_section(self, data: Dict[str, Any]) -> list:
        """Build RFQ details section (quantity, lead time, etc)."""
        elements = []
        
        elements.append(Paragraph("Order Details", self.styles['SectionHeader']))
        
        rfq_info = []
        
        # Quantity
        quantity = data.get('quantity', 1)
        rfq_info.append(['Quantity:', f"{quantity} units"])
        
        # Target delivery date (from RFQ lead_time_date, fallback to target_date)
        target_date = data.get('target_date', '')
        if target_date:
            try:
                date_obj = datetime.fromisoformat(target_date)
                date_str = date_obj.strftime('%B %d, %Y')
                rfq_info.append(['Delivery Date:', date_str])
            except:
                rfq_info.append(['Delivery Date:', target_date])
        
        # Payment Terms
        payment_terms = data.get('payment_terms_days', 30)
        if payment_terms:
            rfq_info.append(['Payment Terms:', f"Net {payment_terms} days"])
        
        # Create table
        if rfq_info:
            table = Table(rfq_info, colWidths=[1.5*inch, 4.5*inch])
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a1a1a')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, self.SPACING_LG))
        
        return elements
    
    def _build_pricing_section(self, data: Dict[str, Any], customer_facing: bool = True) -> list:
        """
        Build pricing breakdown section.
        
        Args:
            data: Quote data dictionary
            customer_facing: If True, show only final price (customer-safe).
                           If False, show full Glass Box breakdown (internal).
        
        Per SYSTEM_BEHAVIOR_SPEC.md Section 2:
        - Layer 1: System Anchor (physics) - INTERNAL ONLY
        - Layer 2: Variance Attribution - INTERNAL ONLY
        - Layer 3: Final Price - ALWAYS SHOWN
        """
        elements = []
        
        elements.append(Paragraph("Pricing", self.styles['SectionHeader']))
        
        # Layer 3: Final Price (always shown, handle None values)
        final_price = data.get('final_quoted_price') or data.get('final_price') or 0
        quantity = data.get('quantity') or 1  # Handle None values
        
        if customer_facing:
            # Customer-Safe Mode: Show ONLY final price
            pricing_data = [
                ['Total Price:', f"${final_price:,.2f}"],
            ]
            
            # Per-unit price if quantity > 1
            if quantity > 1:
                per_unit = final_price / quantity
                pricing_data.append(['Price Per Unit:', f"${per_unit:,.2f}"])
                pricing_data.append(['Quantity:', f"{quantity} units"])
        else:
            # Internal Mode: Show full Glass Box breakdown
            # Layer 1: System Anchor (handle None values)
            anchor = data.get('system_price_anchor') or data.get('anchor_price') or 0
            
            # Layer 2: Variance
            variance = final_price - anchor
            variance_percent = (variance / anchor * 100) if anchor > 0 else 0
            
            # Build full pricing table
            pricing_data = [
                ['System Anchor (Physics):', f"${anchor:,.2f}"],
                ['Variance:', f"${variance:,.2f} ({variance_percent:+.1f}%)"],
                ['', ''],  # Spacer row
                ['Final Quoted Price:', f"${final_price:,.2f}"],
            ]
            
            # Per-unit price if quantity > 1
            if quantity > 1:
                per_unit = final_price / quantity
                pricing_data.append(['Price Per Unit:', f"${per_unit:,.2f}"])
        
        table = Table(pricing_data, colWidths=[3.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -2), 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a1a1a')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#333333')),
        ]))
        
        elements.append(table)
        
        # Variance Attribution (INTERNAL ONLY - Glass Box transparency)
        if not customer_facing:
            pricing_tags = data.get('pricing_tags_json', {})
            if isinstance(pricing_tags, str):
                try:
                    pricing_tags = json.loads(pricing_tags)
                except:
                    pricing_tags = {}
            
            # Only show if we have variance and tags
            if pricing_tags and variance != 0:
                elements.append(Spacer(1, self.SPACING_MD))
                elements.append(Paragraph("Variance Attribution:", self.styles['CutterBody']))
                
                # Build tag table
                tag_data = []
                for tag_name, tag_weight in pricing_tags.items():
                    if tag_weight > 0:
                        tag_amount = variance * float(tag_weight)
                        tag_percent = float(tag_weight) * 100
                        tag_data.append([f"  {tag_name}", f"{tag_percent:.1f}%", f"${tag_amount:,.2f}"])
                
                if tag_data:
                    tag_table = Table(tag_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
                    tag_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#666666')),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    elements.append(tag_table)
        
        elements.append(Spacer(1, self.SPACING_LG))
        
        # Price Breaks table (Economy of Scale)
        # Per EXECUTION_CHAT_BRIEF.md Section: Price Breaks Table Specification
        if customer_facing:
            price_breaks = self._build_price_breaks_table(data)
            if price_breaks:
                elements.extend(price_breaks)
        
        return elements
    
    def _build_price_breaks_table(self, data: Dict[str, Any]) -> list:
        """
        Build price breaks table showing economy of scale.
        
        Per SYSTEM_BEHAVIOR_SPEC.md Section 1.5:
        - Setup_Cost_Per_Unit = (Setup_Time × Shop_Rate ÷ 60) ÷ Quantity
        - Per_Unit_Price = Material_Cost_Per_Unit + Labor_Cost_Per_Unit + Setup_Cost_Per_Unit
        
        Per EXECUTION_CHAT_BRIEF.md:
        - Color-code setup % (red > 20%, amber 5-20%, green < 5%)
        - Only show if quantity tiers differ from quoted quantity
        """
        elements = []
        
        # Get price breaks tiers (default: [1, 5, 25, 100])
        price_breaks_json = data.get('price_breaks_json', '[1, 5, 25, 100]')
        if isinstance(price_breaks_json, str):
            try:
                quantity_tiers = json.loads(price_breaks_json)
            except:
                quantity_tiers = [1, 5, 25, 100]
        else:
            quantity_tiers = price_breaks_json if isinstance(price_breaks_json, list) else [1, 5, 25, 100]
        
        quoted_quantity = data.get('quantity') or 1
        
        # Only show if tiers include quantities different from quoted quantity
        if len([q for q in quantity_tiers if q != quoted_quantity]) == 0:
            return []  # All tiers match quoted quantity, skip table
        
        # Get physics snapshot for recalculation
        physics_snapshot = data.get('physics_snapshot_json', {})
        if isinstance(physics_snapshot, str):
            try:
                physics_snapshot = json.loads(physics_snapshot)
            except:
                physics_snapshot = {}
        
        # Get material and labor costs (per unit at quoted quantity)
        system_anchor = data.get('system_price_anchor') or data.get('anchor_price') or 0
        material_cost_total = physics_snapshot.get('material_cost', 0)
        labor_cost_total = physics_snapshot.get('labor_cost', 0)
        setup_cost_total = physics_snapshot.get('setup_cost', 0)
        
        # If no physics snapshot, try to reconstruct from anchor
        if material_cost_total == 0 and labor_cost_total == 0:
            # Fallback: assume setup is 60 min @ $75/hr = $75
            setup_cost_total = 75.0
            material_cost_total = system_anchor * 0.3  # Rough estimate
            labor_cost_total = system_anchor - material_cost_total
        
        # Calculate per-unit costs for each quantity tier
        table_data = [['Quantity', 'Per Unit', 'Total', 'Setup %']]
        
        for qty in quantity_tiers:
            if qty < 1:
                continue  # Skip invalid quantities
            
            # Recalculate material cost for this quantity
            if quoted_quantity > 0:
                material_per_unit = material_cost_total / quoted_quantity
            else:
                material_per_unit = 0
            
            material_cost_qty = material_per_unit * qty
            
            # Recalculate labor with setup amortization
            if setup_cost_total > 0 and quoted_quantity > 0:
                # Extract runtime without setup (approximate)
                runtime_per_unit = (labor_cost_total / quoted_quantity) if quoted_quantity > 0 else 0
                labor_without_setup = runtime_per_unit * qty
                setup_per_unit = setup_cost_total / qty
                labor_cost_qty = labor_without_setup + setup_cost_total
            else:
                labor_per_unit = labor_cost_total / quoted_quantity if quoted_quantity > 0 else 0
                labor_cost_qty = labor_per_unit * qty
                setup_per_unit = 0
            
            total_cost_qty = material_cost_qty + labor_cost_qty
            per_unit_price = total_cost_qty / qty if qty > 0 else 0
            
            # Calculate setup percentage
            if labor_cost_qty > 0:
                setup_percent = (setup_cost_total / labor_cost_qty) * 100
            else:
                setup_percent = 0
            
            # Format row data
            qty_str = str(qty)
            per_unit_str = f"${per_unit_price:,.2f}"
            total_str = f"${total_cost_qty:,.2f}"
            setup_pct_str = f"{setup_percent:.1f}%"
            
            table_data.append([qty_str, per_unit_str, total_str, setup_pct_str])
        
        # Section header
        elements.append(Paragraph("Price Breaks (Economy of Scale)", self.styles['SectionHeader']))
        
        # Build table
        table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        
        # Apply styling (per UI Design Constraints: grayscale only, spacing palette)
        table_style = [
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Header row centered
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Quantity column centered
            ('ALIGN', (1, 1), (2, -1), 'RIGHT'),   # Price columns right-aligned
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Setup % column centered
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a1a1a')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eeeeee')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#333333')),
        ]
        
        # Color-code setup % rows (per spec: red > 20%, amber 5-20%, green < 5%)
        for i, row in enumerate(table_data[1:], start=1):  # Skip header
            setup_pct_str = row[3]
            try:
                setup_pct = float(setup_pct_str.rstrip('%'))
                if setup_pct > 20:
                    # Red background for high setup %
                    table_style.append(('BACKGROUND', (3, i), (3, i), colors.HexColor('#ffcccc')))
                elif setup_pct >= 5:
                    # Amber background for moderate setup %
                    table_style.append(('BACKGROUND', (3, i), (3, i), colors.HexColor('#fff4cc')))
                else:
                    # Green background for low setup %
                    table_style.append(('BACKGROUND', (3, i), (3, i), colors.HexColor('#ccffcc')))
            except:
                pass  # Skip color coding if parsing fails
        
        table.setStyle(TableStyle(table_style))
        elements.append(table)
        elements.append(Spacer(1, self.SPACING_LG))
        
        return elements
    
    def _build_requirements_section(self, data: Dict[str, Any]) -> list:
        """Build outside processing and quality requirements section."""
        elements = []
        
        # Outside processing
        outside_processing = data.get('outside_processing_json', [])
        if isinstance(outside_processing, str):
            try:
                outside_processing = json.loads(outside_processing)
            except:
                outside_processing = []
        
        if outside_processing:
            elements.append(Paragraph("Outside Processing", self.styles['SectionHeader']))
            for op in outside_processing:
                elements.append(Paragraph(f"• {op}", self.styles['CutterBody']))
            elements.append(Spacer(1, self.SPACING_MD))
        
        # Quality requirements
        quality_reqs = data.get('quality_requirements_json', {})
        if isinstance(quality_reqs, str):
            try:
                quality_reqs = json.loads(quality_reqs)
            except:
                quality_reqs = {}
        
        if quality_reqs and isinstance(quality_reqs, dict):
            req_list = []
            if quality_reqs.get('cmm'):
                req_list.append("CMM Inspection Required")
            if quality_reqs.get('as9102'):
                req_list.append("AS9102 First Article Inspection")
            if quality_reqs.get('material_certs'):
                req_list.append("Material Certifications Required")
            
            if req_list:
                elements.append(Paragraph("Quality Requirements", self.styles['SectionHeader']))
                for req in req_list:
                    elements.append(Paragraph(f"• {req}", self.styles['CutterBody']))
                
                # Notes field
                notes = quality_reqs.get('notes', '')
                if notes:
                    elements.append(Paragraph(f"Notes: {notes}", self.styles['CutterBody']))
                
                elements.append(Spacer(1, self.SPACING_MD))
        
        # Part marking
        part_marking = data.get('part_marking_json', {})
        if isinstance(part_marking, str):
            try:
                part_marking = json.loads(part_marking)
            except:
                part_marking = {}
        
        if part_marking and isinstance(part_marking, dict):
            marking_type = part_marking.get('type', '')
            marking_content = part_marking.get('content', '')
            if marking_type and marking_content:
                elements.append(Paragraph("Part Marking", self.styles['SectionHeader']))
                elements.append(Paragraph(f"Type: {marking_type}", self.styles['CutterBody']))
                elements.append(Paragraph(f"Content: {marking_content}", self.styles['CutterBody']))
                elements.append(Spacer(1, self.SPACING_MD))
        
        return elements
    
    def _build_notes_section(self, data: Dict[str, Any]) -> list:
        """Build notes section."""
        elements = []
        
        notes = data.get('notes', '').strip()
        if notes:
            elements.append(Paragraph("Notes", self.styles['SectionHeader']))
            elements.append(Paragraph(notes, self.styles['CutterBody']))
            elements.append(Spacer(1, self.SPACING_LG))
        
        return elements
    
    def _build_footer(self, data: Dict[str, Any]) -> list:
        """Build PDF footer."""
        elements = []
        
        elements.append(Spacer(1, self.SPACING_LG))
        
        # Genesis hash (for pattern matching reference)
        genesis_hash = data.get('genesis_hash', '')
        if genesis_hash:
            hash_short = genesis_hash[:16] + '...'
            elements.append(Paragraph(
                f"Part Signature: {hash_short}",
                self.styles['Metadata']
            ))
        
        # Generated timestamp
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elements.append(Paragraph(
            f"Generated: {now}",
            self.styles['Metadata']
        ))
        
        return elements
    
    def generate_traveler_pdf(
        self,
        quote_data: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """
        Generate a Traveler PDF (Shop Floor Work Order).
        
        CRITICAL: NO PRICING INFORMATION (shop floor security).
        
        Args:
            quote_data: Quote dictionary from database
            filename: Optional custom filename (default: TRAVELER-{quote_id}.pdf)
        
        Returns:
            Path to generated PDF file
        """
        # Generate filename
        if filename is None:
            quote_id = quote_data.get('quote_id', 'UNKNOWN')
            filename = f"TRAVELER-{quote_id}.pdf"
        
        filepath = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build content
        content = []
        
        # Header section (Job ID - LARGE)
        content.extend(self._build_traveler_header(quote_data))
        
        # Part Information section
        content.extend(self._build_traveler_part_section(quote_data))
        
        # Process Routing section (The Traveler)
        content.extend(self._build_process_routing_section(quote_data))
        
        # QC Grid section
        content.extend(self._build_qc_grid_section(quote_data))
        
        # Notes section (if any)
        if quote_data.get('notes'):
            content.extend(self._build_notes_section(quote_data))
        
        # Footer (minimal - no Genesis hash for shop floor)
        content.extend(self._build_traveler_footer(quote_data))
        
        # Build PDF
        doc.build(content)
        
        return str(filepath)
    
    def _build_traveler_header(self, data: Dict[str, Any]) -> list:
        """
        Build traveler header with shop branding and large Job ID.
        
        Per EXECUTION_CHAT_BRIEF.md: Shop branding in both PDFs.
        """
        elements = []
        
        # Shop Branding (smaller for Traveler, top-right position would be ideal but keeping simple)
        import database
        shop_name = database.get_config('shop_name', 'Machine Shop', str)
        
        branding_style = ParagraphStyle(
            name='TravelerBranding',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=self.SPACING_SM,
            alignment=TA_CENTER
        )
        elements.append(Paragraph(shop_name, branding_style))
        
        # Horizontal separator
        from reportlab.platypus import HRFlowable
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor('#cccccc'),
            spaceAfter=self.SPACING_SM
        ))
        
        # Large Job ID header
        quote_id = data.get('quote_id', 'DRAFT')
        job_header = f"WORK ORDER: {quote_id}"
        
        # Custom style for large header
        large_header_style = ParagraphStyle(
            name='TravelerHeader',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=self.SPACING_LG,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph(job_header, large_header_style))
        
        # Real QR Code (per EXECUTION_CHAT_BRIEF.md)
        # Encodes Job ID for scanning on shop floor
        try:
            qr_image = self._generate_qr_code(quote_id, size=1.5)
            # Center the QR code
            qr_table = Table([[qr_image]], colWidths=[1.5*inch])
            qr_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            elements.append(qr_table)
        except Exception as e:
            # Fallback to placeholder if QR generation fails
            elements.append(Paragraph(
                f"[QR CODE ERROR: {str(e)}]",
                self.styles['Metadata']
            ))
        
        elements.append(Spacer(1, self.SPACING_LG))
        
        return elements
    
    def _build_traveler_part_section(self, data: Dict[str, Any]) -> list:
        """Build part information section for traveler."""
        elements = []
        
        elements.append(Paragraph("Part Information", self.styles['SectionHeader']))
        
        # Part details
        filename = data.get('filename', 'Unknown')
        volume = data.get('volume') or 0
        dimensions = data.get('dimensions', {})
        material = data.get('material', 'Unknown')
        quantity = data.get('quantity') or 1
        
        part_info = [
            ['Part Name:', filename],
            ['Material:', material],
            ['Quantity:', f"{quantity} units"],
            ['Volume:', f"{volume:.2f} in³"],
        ]
        
        # Dimensions
        if isinstance(dimensions, dict):
            dim_x = dimensions.get('x') or 0
            dim_y = dimensions.get('y') or 0
            dim_z = dimensions.get('z') or 0
            part_info.append(['Bounding Box:', f"{dim_x:.2f}\" × {dim_y:.2f}\" × {dim_z:.2f}\""])
        
        # Create table
        table = Table(part_info, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a1a1a')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, self.SPACING_LG))
        
        return elements
    
    def _build_process_routing_section(self, data: Dict[str, Any]) -> list:
        """Build process routing section (The Traveler Tags)."""
        elements = []
        
        elements.append(Paragraph("Process Routing", self.styles['SectionHeader']))
        
        # Get process routing from part data
        process_routing = data.get('process_routing', [])
        
        # Also check outside_processing_json from RFQ
        outside_processing = data.get('outside_processing_json', [])
        if isinstance(outside_processing, str):
            try:
                outside_processing = json.loads(outside_processing)
            except:
                outside_processing = []
        
        # Combine internal processes and outside processing
        all_processes = []
        if isinstance(process_routing, list):
            all_processes.extend(process_routing)
        if isinstance(outside_processing, list):
            all_processes.extend(outside_processing)
        
        if not all_processes:
            elements.append(Paragraph(
                "⚠ No process routing defined",
                self.styles['CutterBody']
            ))
        else:
            # Build checklist table
            process_data = []
            for i, process in enumerate(all_processes, 1):
                process_data.append([
                    f"{i}.",
                    "☐",  # Checkbox
                    process,
                    "_________"  # Initials line
                ])
            
            table = Table(process_data, colWidths=[0.4*inch, 0.4*inch, 3.2*inch, 2*inch])
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                ('ALIGN', (3, 0), (3, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (0, -1), 9),
                ('FONTSIZE', (1, 0), (1, -1), 14),
                ('FONTSIZE', (2, 0), (2, -1), 11),
                ('FONTSIZE', (3, 0), (3, -1), 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a1a1a')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ]))
            elements.append(table)
        
        elements.append(Spacer(1, self.SPACING_LG))
        
        return elements
    
    def _build_qc_grid_section(self, data: Dict[str, Any]) -> list:
        """Build QC inspection grid."""
        elements = []
        
        elements.append(Paragraph("Quality Control", self.styles['SectionHeader']))
        
        # QC checkpoints
        qc_data = [
            ['Checkpoint', 'Inspector', 'Date', 'Pass/Fail'],
            ['First Article', '________________', '________', '☐ Pass  ☐ Fail'],
            ['In-Process Check', '________________', '________', '☐ Pass  ☐ Fail'],
            ['Final Inspection', '________________', '________', '☐ Pass  ☐ Fail'],
        ]
        
        # Check if CMM required
        quality_reqs = data.get('quality_requirements_json', {})
        if isinstance(quality_reqs, str):
            try:
                quality_reqs = json.loads(quality_reqs)
            except:
                quality_reqs = {}
        
        if quality_reqs and isinstance(quality_reqs, dict):
            if quality_reqs.get('cmm'):
                qc_data.append(['CMM Inspection', '________________', '________', '☐ Pass  ☐ Fail'])
            if quality_reqs.get('as9102'):
                qc_data.append(['AS9102 (First Article)', '________________', '________', '☐ Pass  ☐ Fail'])
        
        table = Table(qc_data, colWidths=[2*inch, 1.8*inch, 1.2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a1a1a')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eeeeee')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#333333')),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, self.SPACING_LG))
        
        return elements
    
    def _build_traveler_footer(self, data: Dict[str, Any]) -> list:
        """Build traveler footer (minimal - no internal data)."""
        elements = []
        
        elements.append(Spacer(1, self.SPACING_LG))
        
        # Generated timestamp only
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elements.append(Paragraph(
            f"Generated: {now}",
            self.styles['Metadata']
        ))
        
        return elements


def generate_quote_pdf(
    quote_data: Dict[str, Any],
    output_dir: str = "quotes_pdf",
    customer_facing: bool = True
) -> str:
    """
    Convenience function to generate a PDF from quote data.
    
    Args:
        quote_data: Quote dictionary from database
        output_dir: Directory to save PDF
        customer_facing: If True, hide internal pricing data (default: True for customer safety)
    
    Returns:
        Path to generated PDF file
    """
    generator = QuotePDFGenerator(output_dir=output_dir)
    return generator.generate_quote_pdf(quote_data, customer_facing=customer_facing)


def generate_traveler_pdf(quote_data: Dict[str, Any], output_dir: str = "travelers_pdf") -> str:
    """
    Convenience function to generate a Traveler PDF (Shop Floor Work Order).
    
    CRITICAL: NO PRICING INFORMATION (shop floor security).
    
    Args:
        quote_data: Quote dictionary from database
        output_dir: Directory to save PDF (default: "travelers_pdf")
    
    Returns:
        Path to generated PDF file
    """
    generator = QuotePDFGenerator(output_dir=output_dir)
    return generator.generate_traveler_pdf(quote_data)

