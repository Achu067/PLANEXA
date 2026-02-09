import numpy as np
import random
from typing import List, Dict

class FurnitureLayoutAI:
    def __init__(self):
        self.furniture_templates = self._load_furniture_templates()
        self.clearance_requirements = {
            'bed': 0.6,      # 60cm clearance around bed
            'desk': 0.8,     # 80cm clearance for chair
            'sofa': 0.5,     # 50cm clearance
            'table': 0.9,    # 90cm clearance for chairs
            'wardrobe': 0.4, # 40cm clearance for doors
            'toilet': 0.6,   # 60cm clearance
            'sink': 0.5,     # 50cm clearance
        }
    
    def _load_furniture_templates(self):
        """Load furniture templates with standard dimensions"""
        return {
            'bedroom': [
                {'type': 'bed', 'width': 1.9, 'length': 2.0, 'placement': 'against_wall'},
                {'type': 'wardrobe', 'width': 1.2, 'length': 0.6, 'placement': 'against_wall'},
                {'type': 'desk', 'width': 1.4, 'length': 0.6, 'placement': 'against_wall'},
                {'type': 'nightstand', 'width': 0.5, 'length': 0.4, 'placement': 'next_to_bed'},
            ],
            'living': [
                {'type': 'sofa', 'width': 2.0, 'length': 0.9, 'placement': 'against_wall'},
                {'type': 'coffee_table', 'width': 1.2, 'length': 0.6, 'placement': 'center'},
                {'type': 'tv_stand', 'width': 1.8, 'length': 0.4, 'placement': 'against_wall'},
                {'type': 'armchair', 'width': 0.9, 'length': 0.9, 'placement': 'corner'},
            ],
            'kitchen': [
                {'type': 'kitchen_counter', 'width': 3.0, 'length': 0.6, 'placement': 'against_wall'},
                {'type': 'refrigerator', 'width': 0.7, 'length': 0.7, 'placement': 'corner'},
                {'type': 'sink', 'width': 0.8, 'length': 0.5, 'placement': 'on_counter'},
                {'type': 'stove', 'width': 0.6, 'length': 0.6, 'placement': 'on_counter'},
            ],
            'bathroom': [
                {'type': 'toilet', 'width': 0.7, 'length': 0.8, 'placement': 'against_wall'},
                {'type': 'sink', 'width': 0.6, 'length': 0.5, 'placement': 'against_wall'},
                {'type': 'shower', 'width': 0.9, 'length': 0.9, 'placement': 'corner'},
                {'type': 'bathtub', 'width': 1.7, 'length': 0.7, 'placement': 'against_wall'},
            ],
            'office': [
                {'type': 'desk', 'width': 1.6, 'length': 0.8, 'placement': 'center'},
                {'type': 'office_chair', 'width': 0.6, 'length': 0.6, 'placement': 'at_desk'},
                {'type': 'bookshelf', 'width': 1.0, 'length': 0.3, 'placement': 'against_wall'},
                {'type': 'filing_cabinet', 'width': 0.5, 'length': 0.6, 'placement': 'corner'},
            ]
        }
    
    def layout_furniture(self, rooms: List[Dict], style: str) -> Dict:
        """
        Generate furniture layout for each room
        Returns furniture data for the entire floor
        """
        floor_furniture = {}
        
        for room in rooms:
            room_type = room['type']
            room_furniture = self._layout_room_furniture(room, room_type, style)
            
            if room_furniture:
                floor_furniture[room['type']] = room_furniture
        
        return floor_furniture
    
    def _layout_room_furniture(self, room: Dict, room_type: str, style: str) -> List[Dict]:
        """Generate furniture layout for a single room"""
        if room_type not in self.furniture_templates:
            return []
        
        templates = self.furniture_templates[room_type]
        
        # Adjust furniture based on room size and style
        adjusted_templates = self._adjust_furniture_for_room(templates, room, style)
        
        # Place furniture in room
        placed_furniture = []
        occupied_positions = []
        
        # Sort furniture by size (largest first)
        sorted_templates = sorted(adjusted_templates, 
                                key=lambda x: x['width'] * x['length'], 
                                reverse=True)
        
        for template in sorted_templates:
            furniture_item = self._place_furniture_item(
                template, room, placed_furniture, occupied_positions, style
            )
            
            if furniture_item:
                placed_furniture.append(furniture_item)
                
                # Mark occupied area
                self._mark_occupied_area(furniture_item, occupied_positions)
        
        return placed_furniture
    
    def _adjust_furniture_for_room(self, templates: List[Dict], room: Dict, style: str) -> List[Dict]:
        """Adjust furniture dimensions based on room size and style"""
        adjusted = []
        
        # Calculate room area
        room_area = room['width'] * room['length']
        
        # Style multipliers
        style_multipliers = {
            'modern': 0.9,        # More compact in modern design
            'traditional': 1.0,   # Standard size
            'minimalist': 0.8,    # Smaller, minimal furniture
            'open_plan': 1.1      # Larger furniture for open spaces
        }
        
        multiplier = style_multipliers.get(style, 1.0)
        
        for template in templates:
            item = template.copy()
            
            # Adjust size based on style
            item['width'] = round(item['width'] * multiplier, 2)
            item['length'] = round(item['length'] * multiplier, 2)
            
            # Ensure furniture fits in room
            max_item_area = room_area * 0.3  # Max 30% of room area for any item
            
            if item['width'] * item['length'] > max_item_area:
                # Scale down proportionally
                scale_factor = np.sqrt(max_item_area / (item['width'] * item['length']))
                item['width'] = round(item['width'] * scale_factor, 2)
                item['length'] = round(item['length'] * scale_factor, 2)
            
            adjusted.append(item)
        
        return adjusted
    
    def _place_furniture_item(self, template: Dict, room: Dict, 
                            existing_furniture: List[Dict], 
                            occupied_positions: List, style: str) -> Dict:
        """Place a single furniture item in the room"""
        item = template.copy()
        
        # Get clearance requirement
        clearance = self.clearance_requirements.get(item['type'], 0.5)
        
        # Determine placement strategy
        placement = item['placement']
        
        if placement == 'against_wall':
            position = self._place_against_wall(item, room, occupied_positions, clearance)
        elif placement == 'center':
            position = self._place_center(item, room, occupied_positions, clearance)
        elif placement == 'corner':
            position = self._place_in_corner(item, room, occupied_positions, clearance)
        elif placement == 'next_to_bed':
            position = self._place_next_to_bed(item, room, existing_furniture, occupied_positions, clearance)
        elif placement == 'on_counter':
            position = self._place_on_counter(item, room, existing_furniture, occupied_positions)
        elif placement == 'at_desk':
            position = self._place_at_desk(item, room, existing_furniture, occupied_positions)
        else:
            position = self._place_randomly(item, room, occupied_positions, clearance)
        
        if position:
            item['x'], item['y'], item['rotation'] = position
            return item
        
        return None
    
    def _place_against_wall(self, item: Dict, room: Dict, 
                          occupied_positions: List, clearance: float) -> tuple:
        """Place item against a wall"""
        walls = [
            (room['x'], room['y'], 0),  # Bottom wall
            (room['x'] + room['width'] - item['width'], room['y'], 0),  # Top wall
            (room['x'], room['y'], 90),  # Left wall (rotated)
            (room['x'], room['y'] + room['length'] - item['length'], 90),  # Right wall (rotated)
        ]
        
        random.shuffle(walls)
        
        for x, y, rotation in walls:
            # Adjust for clearance
            if rotation == 0:
                y_adjusted = y + clearance
            else:
                x_adjusted = x + clearance
            
            if self._is_position_valid(item, x, y, room, occupied_positions, clearance, rotation):
                return x, y, rotation
        
        return None
    
    def _place_center(self, item: Dict, room: Dict, 
                     occupied_positions: List, clearance: float) -> tuple:
        """Place item in center of room"""
        center_x = room['x'] + room['width'] / 2 - item['width'] / 2
        center_y = room['y'] + room['length'] / 2 - item['length'] / 2
        
        if self._is_position_valid(item, center_x, center_y, room, occupied_positions, clearance, 0):
            return center_x, center_y, 0
        
        # Try nearby positions if center is occupied
        for offset_x in [-0.5, 0, 0.5]:
            for offset_y in [-0.5, 0, 0.5]:
                x = center_x + offset_x
                y = center_y + offset_y
                
                if self._is_position_valid(item, x, y, room, occupied_positions, clearance, 0):
                    return x, y, 0
        
        return None
    
    def _place_in_corner(self, item: Dict, room: Dict, 
                        occupied_positions: List, clearance: float) -> tuple:
        """Place item in a corner"""
        corners = [
            (room['x'] + clearance, room['y'] + clearance, 0),  # Bottom-left
            (room['x'] + room['width'] - item['width'] - clearance, 
             room['y'] + clearance, 0),  # Bottom-right
            (room['x'] + clearance, 
             room['y'] + room['length'] - item['length'] - clearance, 0),  # Top-left
            (room['x'] + room['width'] - item['width'] - clearance,
             room['y'] + room['length'] - item['length'] - clearance, 0),  # Top-right
        ]
        
        random.shuffle(corners)
        
        for x, y, rotation in corners:
            if self._is_position_valid(item, x, y, room, occupied_positions, 0, rotation):
                return x, y, rotation
        
        return None
    
    def _place_next_to_bed(self, item: Dict, room: Dict, 
                          existing_furniture: List[Dict],
                          occupied_positions: List, clearance: float) -> tuple:
        """Place item next to bed"""
        # Find bed in existing furniture
        bed = next((f for f in existing_furniture if f['type'] == 'bed'), None)
        
        if not bed:
            return self._place_against_wall(item, room, occupied_positions, clearance)
        
        # Try positions next to bed
        positions = [
            (bed['x'] + bed['width'] + clearance, bed['y'], 0),  # Right side
            (bed['x'] - item['width'] - clearance, bed['y'], 0),  # Left side
            (bed['x'], bed['y'] + bed['length'] + clearance, 0),  # Top side
            (bed['x'], bed['y'] - item['length'] - clearance, 0),  # Bottom side
        ]
        
        for x, y, rotation in positions:
            if self._is_position_valid(item, x, y, room, occupied_positions, 0, rotation):
                return x, y, rotation
        
        return None
    
    def _place_on_counter(self, item: Dict, room: Dict,
                         existing_furniture: List[Dict],
                         occupied_positions: List) -> tuple:
        """Place item on kitchen counter"""
        # Find counter in existing furniture
        counter = next((f for f in existing_furniture if f['type'] == 'kitchen_counter'), None)
        
        if not counter:
            return self._place_against_wall(item, room, occupied_positions, 0.1)
        
        # Place on counter (small clearance)
        x = counter['x'] + 0.1
        y = counter['y'] + 0.1
        
        return x, y, 0
    
    def _place_at_desk(self, item: Dict, room: Dict,
                      existing_furniture: List[Dict],
                      occupied_positions: List) -> tuple:
        """Place item at desk (e.g., office chair)"""
        # Find desk in existing furniture
        desk = next((f for f in existing_furniture if f['type'] == 'desk'), None)
        
        if not desk:
            return self._place_center(item, room, occupied_positions, 0.3)
        
        # Place chair in front of desk
        x = desk['x'] + desk['width'] / 2 - item['width'] / 2
        y = desk['y'] - item['length'] - 0.3
        
        if self._is_position_valid(item, x, y, room, occupied_positions, 0.1, 0):
            return x, y, 0
        
        return None
    
    def _place_randomly(self, item: Dict, room: Dict,
                       occupied_positions: List, clearance: float) -> tuple:
        """Place item at random valid position"""
        max_attempts = 50
        
        for _ in range(max_attempts):
            x = random.uniform(room['x'] + clearance, 
                              room['x'] + room['width'] - item['width'] - clearance)
            y = random.uniform(room['y'] + clearance,
                              room['y'] + room['length'] - item['length'] - clearance)
            rotation = random.choice([0, 90, 180, 270])
            
            x = round(x, 2)
            y = round(y, 2)
            
            if self._is_position_valid(item, x, y, room, occupied_positions, 0, rotation):
                return x, y, rotation
        
        return None
    
    def _is_position_valid(self, item: Dict, x: float, y: float, 
                          room: Dict, occupied_positions: List,
                          clearance: float, rotation: float) -> bool:
        """Check if position is valid for furniture placement"""
        # Check if within room boundaries (with clearance)
        if (x < room['x'] + clearance or 
            y < room['y'] + clearance or
            x + item['width'] > room['x'] + room['width'] - clearance or
            y + item['length'] > room['y'] + room['length'] - clearance):
            return False
        
        # Check for overlap with existing furniture
        item_rect = self._get_bounding_rect(item, x, y, rotation)
        
        for occupied in occupied_positions:
            if self._rectangles_overlap(item_rect, occupied):
                return False
        
        # Check clearance requirements
        clearance_rect = self._get_clearance_rect(item_rect, clearance)
        
        for occupied in occupied_positions:
            if self._rectangles_overlap(clearance_rect, occupied):
                return False
        
        return True
    
    def _get_bounding_rect(self, item: Dict, x: float, y: float, rotation: float) -> Dict:
        """Get bounding rectangle for rotated item"""
        if rotation in [0, 180]:
            width = item['width']
            length = item['length']
        else:
            width = item['length']
            length = item['width']
        
        return {
            'x': x,
            'y': y,
            'width': width,
            'length': length
        }
    
    def _get_clearance_rect(self, rect: Dict, clearance: float) -> Dict:
        """Get rectangle expanded by clearance"""
        return {
            'x': rect['x'] - clearance,
            'y': rect['y'] - clearance,
            'width': rect['width'] + 2 * clearance,
            'length': rect['length'] + 2 * clearance
        }
    
    def _rectangles_overlap(self, rect1: Dict, rect2: Dict) -> bool:
        """Check if two rectangles overlap"""
        return not (rect1['x'] + rect1['width'] <= rect2['x'] or
                   rect2['x'] + rect2['width'] <= rect1['x'] or
                   rect1['y'] + rect1['length'] <= rect2['y'] or
                   rect2['y'] + rect2['length'] <= rect1['y'])
    
    def _mark_occupied_area(self, furniture: Dict, occupied_positions: List):
        """Mark area as occupied by furniture"""
        rect = self._get_bounding_rect(furniture, furniture['x'], furniture['y'], furniture['rotation'])
        occupied_positions.append(rect)
