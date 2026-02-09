from typing import Dict
from io import BytesIO
from PIL import Image, ImageDraw
import cairosvg
import xml.etree.ElementTree as ET

class PNGGenerator:
    def __init__(self, dpi=300):
        self.dpi = dpi
    
    def generate(self, svg_content: str, width: int = 1024, 
                height: int = 768) -> bytes:
        """
        Convert SVG to PNG
        Returns PNG bytes
        """
        try:
            # Convert SVG to PNG using cairosvg
            png_bytes = cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                output_width=width,
                output_height=height,
                dpi=self.dpi
            )
            
            # Optionally, add watermark or metadata
            png_bytes = self._add_watermark(png_bytes)
            
            return png_bytes
            
        except Exception as e:
            print(f"Error converting SVG to PNG: {e}")
            # Fallback: create simple PNG
            return self._create_fallback_png(width, height)
    
    def generate_from_data(self, floor_data: Dict, width: int = 1024, 
                          height: int = 768) -> bytes:
        """
        Generate PNG directly from floor data
        """
        from svg_renderer.svg_builder import SVGBuilder
        
        # Create SVG
        svg_builder = SVGBuilder()
        svg_content = svg_builder.build_svg(floor_data)
        
        # Convert to PNG
        return self.generate(svg_content, width, height)
    
    def _add_watermark(self, png_bytes: bytes) -> bytes:
        """Add watermark to PNG"""
        try:
            # Open PNG image
            image = Image.open(BytesIO(png_bytes))
            draw = ImageDraw.Draw(image)
            
            # Add simple text watermark (bottom right)
            width, height = image.size
            watermark_text = "AI Floor Plan Generator"
            
            # You would add proper text drawing here
            # For now, return original
            image.close()
            
        except Exception as e:
            print(f"Error adding watermark: {e}")
        
        # Convert back to bytes
        output = BytesIO()
        image.save(output, format='PNG')
        return output.getvalue()
    
    def _create_fallback_png(self, width: int, height: int) -> bytes:
        """Create fallback PNG if SVG conversion fails"""
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Draw simple error message
        text = "Floor Plan\n(SVG rendering failed)"
        # Add text drawing logic here
        
        # Save to bytes
        output = BytesIO()
        image.save(output, format='PNG')
        return output.getvalue()
    
    def generate_tiled_png(self, building_data: Dict, tile_width: int = 1024,
                          tile_height: int = 768) -> Dict:
        """
        Generate tiled PNGs for large floor plans
        Returns dict with tile coordinates and PNG bytes
        """
        tiles = {}
        
        # This would implement tiling logic for large floor plans
        # For now, return single tile
        from svg_renderer.svg_builder import SVGBuilder
        
        svg_builder = SVGBuilder()
        
        for floor in building_data['floors']:
            svg_content = svg_builder.build_svg(floor)
            png_bytes = self.generate(svg_content, tile_width, tile_height)
            
            tiles[f"floor_{floor['floor_number']}"] = {
                'tile': (0, 0),
                'png': png_bytes
            }
        
        return tiles
