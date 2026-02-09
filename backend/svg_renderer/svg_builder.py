from typing import Dict, List, Any
import svgwrite
from svgwrite import cm, mm
import math

class SVGBuilder:
    def __init__(self):
        self.colors = {
            'bedroom': '#3498db',
            'living': '#2ecc71',
            'kitchen': '#e74c3c',
            'bathroom': '#9b59b6',
            'office': '#f39c12',
            'hallway': '#bdc3c7',
            'stairs': '#34495e',
            'wall': '#2c3e50',
            'window': '#3498db',
            'door': '#e74c3c',
            'furniture': '#7f8c8d',
            'grid': '#e0e0e0'
        }
        
        self.scale = 50  # pixels per meter
    
    def build_svg(self, floor_data: Dict, include_furniture: bool = True, 
                 include_windows: bool = True) -> str:
        """
        Build SVG representation of floor plan
        Returns SVG string
        """
        width_m = floor_data['width']
        length_m = floor_data['length']
        
        # Create SVG drawing
        drawing = svgwrite.Drawing(
            size=(f'{width_m * self.scale}px', f'{length_m * self.scale}px'),
            viewBox=f'0 0 {width_m * self.scale} {length_m * self.scale}'
        )
        
        # Add grid background
        self._add_grid(drawing, width_m, length_m)
        
        # Add rooms
        for room in floor_data.get('rooms', []):
            self._add_room(drawing, room)
        
        # Add walls
        for wall in floor_data.get('walls', []):
            self._add_wall(drawing, wall)
        
        # Add windows
        if include_windows:
            for window in floor_data.get('windows', []):
                self._add_window(drawing, window)
        
        # Add doors
        for door in floor_data.get('doors', []):
            self._add_door(drawing, door)
        
        # Add furniture
        if include_furniture and 'furniture' in floor_data:
            for room_type, furniture_list in floor_data['furniture'].items():
                for furniture in furniture_list:
                    self._add_furniture(drawing, furniture)
        
        # Add stairs
        for stair in floor_data.get('stairs', []):
            self._add_stairs(drawing, stair)
        
        # Add dimensions
        self._add_dimensions(drawing, width_m, length_m)
        
        # Add legend
        self._add_legend(drawing, width_m, length_m)
        
        return drawing.tostring()
    
    def _add_grid(self, drawing, width_m, length_m):
        """Add grid background"""
        grid_size = 1 * self.scale  # 1m grid
        
        # Create grid pattern
        pattern = drawing.pattern(
            id='grid',
            size=(grid_size, grid_size),
            patternUnits='userSpaceOnUse'
        )
        
        pattern.add(drawing.line(
            start=(0, 0),
            end=(grid_size, 0),
            stroke=self.colors['grid'],
            stroke_width=1
        ))
        
        pattern.add(drawing.line(
            start=(0, 0),
            end=(0, grid_size),
            stroke=self.colors['grid'],
            stroke_width=1
        ))
        
        drawing.defs.add(pattern)
        
        # Apply pattern
        drawing.add(drawing.rect(
            insert=(0, 0),
            size=(width_m * self.scale, length_m * self.scale),
            fill='url(#grid)'
        ))
    
    def _add_room(self, drawing, room):
        """Add room to SVG"""
        x = room['x'] * self.scale
        y = room['y'] * self.scale
        width = room['width'] * self.scale
        length = room['length'] * self.scale
        
        # Room rectangle
        drawing.add(drawing.rect(
            insert=(x, y),
            size=(width, length),
            fill=self.colors.get(room['type'], '#95a5a6'),
            stroke=self.colors['wall'],
            stroke_width=2,
            opacity=0.8
        ))
        
        # Room label
        text_x = x + width / 2
        text_y = y + length / 2
        
        drawing.add(drawing.text(
            f"{room['type'].title()}\n{room['area']}m²",
            insert=(text_x, text_y),
            fill='white',
            text_anchor='middle',
            dominant_baseline='middle',
            font_size='14px',
            font_weight='bold'
        ))
    
    def _add_wall(self, drawing, wall):
        """Add wall to SVG"""
        x1 = wall['x1'] * self.scale
        y1 = wall['y1'] * self.scale
        x2 = wall['x2'] * self.scale
        y2 = wall['y2'] * self.scale
        
        drawing.add(drawing.line(
            start=(x1, y1),
            end=(x2, y2),
            stroke=self.colors['wall'],
            stroke_width=4,
            stroke_linecap='round'
        ))
    
    def _add_window(self, drawing, window):
        """Add window to SVG"""
        x1 = window['x1'] * self.scale
        y1 = window['y1'] * self.scale
        x2 = window['x2'] * self.scale
        y2 = window['y2'] * self.scale
        
        drawing.add(drawing.line(
            start=(x1, y1),
            end=(x2, y2),
            stroke=self.colors['window'],
            stroke_width=3,
            stroke_dasharray='5,5'
        ))
    
    def _add_door(self, drawing, door):
        """Add door to SVG"""
        x = door['x1'] * self.scale
        y = door['y1'] * self.scale
        width = (door['x2'] - door['x1']) * self.scale
        height = (door['y2'] - door['y1']) * self.scale
        
        # Door as rectangle with arc for swing
        drawing.add(drawing.rect(
            insert=(x, y),
            size=(width, height),
            fill='none',
            stroke=self.colors['door'],
            stroke_width=2
        ))
        
        # Door swing arc
        if 'swing_side' in door:
            swing_radius = width if width > height else height
            
            if door['swing_side'] == 'outward':
                arc = drawing.path(
                    d=f'M {x} {y} A {swing_radius} {swing_radius} 0 0 1 {x + width} {y + height}',
                    fill='none',
                    stroke=self.colors['door'],
                    stroke_width=1,
                    stroke_dasharray='2,2'
                )
                drawing.add(arc)
    
    def _add_furniture(self, drawing, furniture):
        """Add furniture to SVG"""
        x = furniture['x'] * self.scale
        y = furniture['y'] * self.scale
        width = furniture['width'] * self.scale
        length = furniture['length'] * self.scale
        
        # Furniture rectangle
        drawing.add(drawing.rect(
            insert=(x, y),
            size=(width, length),
            fill=self.colors['furniture'],
            stroke='#7f8c8d',
            stroke_width=1,
            rx=2
        ))
        
        # Furniture label
        text_x = x + width / 2
        text_y = y + length / 2
        
        drawing.add(drawing.text(
            furniture['type'].replace('_', ' ').title(),
            insert=(text_x, text_y),
            fill='white',
            text_anchor='middle',
            dominant_baseline='middle',
            font_size='10px'
        ))
    
    def _add_stairs(self, drawing, stairs):
        """Add stairs to SVG"""
        if isinstance(stairs, list):
            # Multiple steps
            for i, step in enumerate(stairs):
                x = step['x'] * self.scale
                y = step['y'] * self.scale
                width = step['width'] * self.scale
                length = step['length'] * self.scale
                
                drawing.add(drawing.rect(
                    insert=(x, y),
                    size=(width, length),
                    fill=self.colors['stairs'],
                    stroke='#2c3e50',
                    stroke_width=1
                ))
                
                # Step number
                text_x = x + width / 2
                text_y = y + length / 2
                
                drawing.add(drawing.text(
                    str(i + 1),
                    insert=(text_x, text_y),
                    fill='white',
                    text_anchor='middle',
                    dominant_baseline='middle',
                    font_size='8px'
                ))
        else:
            # Single staircase representation
            x = stairs['x'] * self.scale
            y = stairs['y'] * self.scale
            width = stairs['width'] * self.scale
            length = stairs['length'] * self.scale
            
            drawing.add(drawing.rect(
                insert=(x, y),
                size=(width, length),
                fill=self.colors['stairs'],
                stroke='#2c3e50',
                stroke_width=2
            ))
            
            # Stairs label
            text_x = x + width / 2
            text_y = y + length / 2
            
            drawing.add(drawing.text(
                'STAIRS',
                insert=(text_x, text_y),
                fill='white',
                text_anchor='middle',
                dominant_baseline='middle',
                font_size='12px',
                font_weight='bold'
            ))
    
    def _add_dimensions(self, drawing, width_m, length_m):
        """Add dimension lines"""
        # Horizontal dimensions
        drawing.add(drawing.line(
            start=(0, length_m * self.scale + 20),
            end=(width_m * self.scale, length_m * self.scale + 20),
            stroke='black',
            stroke_width=1
        ))
        
        drawing.add(drawing.text(
            f'{width_m}m',
            insert=(width_m * self.scale / 2, length_m * self.scale + 35),
            fill='black',
            text_anchor='middle',
            font_size='12px'
        ))
        
        # Vertical dimensions
        drawing.add(drawing.line(
            start=(width_m * self.scale + 20, 0),
            end=(width_m * self.scale + 20, length_m * self.scale),
            stroke='black',
            stroke_width=1
        ))
        
        drawing.add(drawing.text(
            f'{length_m}m',
            insert=(width_m * self.scale + 35, length_m * self.scale / 2),
            fill='black',
            text_anchor='middle',
            font_size='12px',
            writing_mode='tb'  # Top to bottom
        ))
    
    def _add_legend(self, drawing, width_m, length_m):
        """Add color legend"""
        legend_x = width_m * self.scale - 150
        legend_y = 20
        
        # Legend background
        drawing.add(drawing.rect(
            insert=(legend_x - 10, legend_y - 10),
            size=(160, 180),
            fill='white',
            stroke='#ccc',
            stroke_width=1,
            opacity=0.9
        ))
        
        # Legend title
        drawing.add(drawing.text(
            'Legend',
            insert=(legend_x + 70, legend_y + 20),
            fill='black',
            text_anchor='middle',
            font_size='14px',
            font_weight='bold'
        ))
        
        # Legend items
        items = [
            ('Bedroom', self.colors['bedroom']),
            ('Living Room', self.colors['living']),
            ('Kitchen', self.colors['kitchen']),
            ('Bathroom', self.colors['bathroom']),
            ('Office', self.colors['office']),
            ('Stairs', self.colors['stairs']),
            ('Wall', self.colors['wall']),
            ('Window', self.colors['window']),
            ('Door', self.colors['door']),
        ]
        
        for i, (label, color) in enumerate(items):
            y_offset = legend_y + 40 + i * 15
            
            # Color box
            drawing.add(drawing.rect(
                insert=(legend_x, y_offset - 5),
                size=(10, 10),
                fill=color,
                stroke='#666',
                stroke_width=0.5
            ))
            
            # Label
            drawing.add(drawing.text(
                label,
                insert=(legend_x + 20, y_offset + 2),
                fill='black',
                font_size='10px'
            ))
