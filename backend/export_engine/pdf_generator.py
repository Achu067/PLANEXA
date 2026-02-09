from typing import Dict, List, Any
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import cairosvg

class PDFGenerator:
    def __init__(self, page_size='A4', orientation='landscape'):
        self.page_size = A4 if page_size == 'A4' else letter
        self.orientation = orientation
        
        if orientation == 'landscape':
            self.page_size = (self.page_size[1], self.page_size[0])
    
    def generate(self, building_data: Dict, svg_data: Dict = None) -> bytes:
        """
        Generate PDF with floor plans
        Returns PDF bytes
        """
        buffer = BytesIO()
        
        # Create PDF canvas
        c = canvas.Canvas(buffer, pagesize=self.page_size)
        width, height = self.page_size
        
        # Add title page
        self._add_title_page(c, building_data, width, height)
        c.showPage()
        
        # Add floor plans
        for floor in building_data['floors']:
            self._add_floor_plan_page(c, floor, svg_data, width, height)
            c.showPage()
        
        # Add summary page
        self._add_summary_page(c, building_data, width, height)
        
        # Save PDF
        c.save()
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _add_title_page(self, c, building_data, width, height):
        """Add title page to PDF"""
        # Title
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width/2, height - 100, "FLOOR PLAN DOCUMENTATION")
        
        # Building info
        c.setFont("Helvetica", 12)
        info_y = height - 180
        
        info_lines = [
            f"Project: AI Generated Floor Plan",
            f"Date: {building_data.get('generation_date', 'N/A')}",
            f"Total Floors: {building_data['total_floors']}",
            f"Architectural Style: {building_data.get('style', 'Modern')}",
            f"Total Area: {building_data['metrics']['total_area']} m²",
            f"Total Rooms: {building_data['metrics']['total_rooms']}",
        ]
        
        for i, line in enumerate(info_lines):
            c.drawString(100, info_y - i*30, line)
        
        # Legend
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, info_y - 250, "Color Legend:")
        
        legend_items = [
            ("Bedroom", "#3498db"),
            ("Living Room", "#2ecc71"),
            ("Kitchen", "#e74c3c"),
            ("Bathroom", "#9b59b6"),
            ("Office", "#f39c12"),
            ("Stairs", "#34495e"),
        ]
        
        legend_y = info_y - 290
        
        for i, (label, color) in enumerate(legend_items):
            # Draw color box
            c.setFillColor(color)
            c.rect(120, legend_y - i*25, 15, 15, fill=1, stroke=0)
            
            # Draw label
            c.setFillColor("black")
            c.setFont("Helvetica", 10)
            c.drawString(145, legend_y - i*25 + 3, label)
    
    def _add_floor_plan_page(self, c, floor_data, svg_data, width, height):
        """Add floor plan page to PDF"""
        # Floor title
        c.setFont("Helvetica-Bold", 18)
        floor_title = f"Floor {floor_data['floor_number']}"
        if floor_data.get('is_ground_floor'):
            floor_title += " - Ground Floor"
        elif floor_data.get('is_top_floor'):
            floor_title += " - Top Floor"
        
        c.drawCentredString(width/2, height - 50, floor_title)
        
        # Floor specifications
        c.setFont("Helvetica", 10)
        specs_y = height - 85
        
        specs = [
            f"Dimensions: {floor_data['width']}m x {floor_data['length']}m",
            f"Area: {floor_data['metrics']['total_area']} m²",
            f"Room Count: {floor_data['metrics']['room_count']}",
            f"Efficiency: {floor_data['metrics']['efficiency']}%",
        ]
        
        for i, spec in enumerate(specs):
            c.drawString(50, specs_y - i*15, spec)
        
        # Add floor plan image
        if svg_data:
            floor_key = f"floor_{floor_data['floor_number']}"
            if floor_key in svg_data:
                # Convert SVG to PNG for PDF
                try:
                    svg_content = svg_data[floor_key]
                    png_bytes = cairosvg.svg2png(
                        bytestring=svg_content.encode('utf-8'),
                        output_width=int(width * 0.8),
                        output_height=int(height * 0.6)
                    )
                    
                    # Create ImageReader from bytes
                    img = ImageReader(BytesIO(png_bytes))
                    
                    # Draw image centered
                    img_width = width * 0.8
                    img_height = height * 0.6
                    img_x = (width - img_width) / 2
                    img_y = (height - img_height) / 2 - 50
                    
                    c.drawImage(img, img_x, img_y, 
                               width=img_width, 
                               height=img_height)
                except Exception as e:
                    print(f"Error adding floor plan image: {e}")
                    self._add_error_message(c, width, height)
        else:
            self._add_error_message(c, width, height)
        
        # Add room list
        self._add_room_list(c, floor_data, width, height)
    
    def _add_room_list(self, c, floor_data, width, height):
        """Add room list to floor plan page"""
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 150, "Rooms on this floor:")
        
        c.setFont("Helvetica", 10)
        
        rooms = floor_data.get('rooms', [])
        y_position = 130
        
        for i, room in enumerate(rooms[:10]):  # Show first 10 rooms
            room_info = f"{room['type'].title()}: {room['area']} m²"
            c.drawString(70, y_position - i*15, room_info)
        
        if len(rooms) > 10:
            c.drawString(70, y_position - 10*15, f"... and {len(rooms) - 10} more rooms")
    
    def _add_summary_page(self, c, building_data, width, height):
        """Add summary page to PDF"""
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width/2, height - 50, "BUILDING SUMMARY")
        
        # Building metrics
        c.setFont("Helvetica", 12)
        metrics_y = height - 100
        
        metrics = [
            ("Total Building Area:", f"{building_data['metrics']['total_area']} m²"),
            ("Number of Floors:", str(building_data['total_floors'])),
            ("Total Rooms:", str(building_data['metrics']['total_rooms'])),
            ("Average Efficiency:", f"{building_data['metrics']['average_efficiency']}%"),
        ]
        
        for i, (label, value) in enumerate(metrics):
            c.drawString(100, metrics_y - i*40, label)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(300, metrics_y - i*40, value)
            c.setFont("Helvetica", 12)
        
        # Room type distribution
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, metrics_y - 200, "Room Type Distribution:")
        
        # This would include a chart or table of room distribution
        # For now, just list room counts
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(50, 30, "Generated by AI Floor Plan Generator")
        c.drawString(width - 150, 30, "Page 1 of 1")
    
    def _add_error_message(self, c, width, height):
        """Add error message when floor plan cannot be rendered"""
        c.setFont("Helvetica", 12)
        c.setFillColor("red")
        c.drawCentredString(width/2, height/2, "Error: Could not render floor plan")
        c.setFillColor("black")
    
    def generate_technical_drawing(self, building_data: Dict) -> bytes:
        """
        Generate technical drawing PDF with dimensions, notes, etc.
        """
        # This would create a more detailed technical drawing
        # For now, use the standard PDF generation
        return self.generate(building_data)
