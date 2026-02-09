import numpy as np
import random
from collections import deque

class RoomPlacer:
    def __init__(self):
        self.room_spacing = 0.5  # meters between rooms
        self.min_room_size = 2.0  # minimum room dimension
    
    def place_rooms(self, width, length, rooms_required, style):
        """
        Place rooms optimally within floor boundaries
        Returns list of rooms with positions and dimensions
        """
        # Initialize grid
        grid_width = int(width * 10)  # 10cm resolution
        grid_length = int(length * 10)
        grid = np.zeros((grid_width, grid_length))
        
        rooms = []
        placed_rooms = []
        
        # Sort rooms by area (largest first for better placement)
        sorted_rooms = sorted(rooms_required, key=lambda x: x['area'], reverse=True)
        
        for room_spec in sorted_rooms:
            room = self._create_room_object(room_spec, style)
            
            # Find best position for room
            position_found = False
            
            # Try multiple placement strategies
            strategies = [
                self._place_along_wall,
                self._place_in_corner,
                self._place_adjacent_to_existing
            ]
            
            for strategy in strategies:
                if strategy(room, grid, placed_rooms, width, length):
                    position_found = True
                    break
            
            # If no position found, place randomly
            if not position_found:
                room = self._place_randomly(room, grid, width, length)
            
            if room:
                self._mark_grid(room, grid)
                placed_rooms.append(room)
                rooms.append(room)
        
        # Adjust room positions for better flow
        rooms = self._optimize_layout(rooms, width, length, style)
        
        return rooms
    
    def _create_room_object(self, room_spec, style):
        """Create room object with calculated dimensions"""
        room_type = room_spec['type']
        target_area = room_spec['area']
        
        # Get aspect ratio based on room type and style
        aspect_ratio = self._get_aspect_ratio(room_type, style)
        
        # Calculate dimensions
        width = np.sqrt(target_area * aspect_ratio)
        length = target_area / width
        
        # Round to nearest 0.1m
        width = round(width, 1)
        length = round(length, 1)
        
        return {
            'type': room_type,
            'width': width,
            'length': length,
            'area': round(width * length, 2),
            'x': 0,
            'y': 0,
            'aspect_ratio': aspect_ratio
        }
    
    def _get_aspect_ratio(self, room_type, style):
        """Get appropriate aspect ratio for room type and style"""
        ratios = {
            'modern': {
                'bedroom': 1.2,
                'living': 1.5,
                'kitchen': 1.8,
                'bathroom': 1.3,
                'office': 1.4
            },
            'traditional': {
                'bedroom': 1.1,
                'living': 1.3,
                'kitchen': 1.5,
                'bathroom': 1.2,
                'office': 1.3
            },
            'minimalist': {
                'bedroom': 1.0,
                'living': 1.2,
                'kitchen': 1.4,
                'bathroom': 1.1,
                'office': 1.2
            },
            'open_plan': {
                'bedroom': 1.3,
                'living': 1.7,
                'kitchen': 2.0,
                'bathroom': 1.4,
                'office': 1.5
            }
        }
        
        style_ratios = ratios.get(style, ratios['modern'])
        return style_ratios.get(room_type, 1.2)
    
    def _place_along_wall(self, room, grid, placed_rooms, width, length):
        """Try to place room along an exterior wall"""
        walls = [
            (0, 0, 'horizontal'),  # Bottom wall
            (0, length - room['length'], 'horizontal'),  # Top wall
            (0, 0, 'vertical'),  # Left wall
            (width - room['width'], 0, 'vertical')  # Right wall
        ]
        
        random.shuffle(walls)
        
        for x, y, orientation in walls:
            if self._can_place_at(room, x, y, grid, width, length):
                room['x'] = x
                room['y'] = y
                return True
        
        return False
    
    def _place_in_corner(self, room, grid, placed_rooms, width, length):
        """Try to place room in a corner"""
        corners = [
            (0, 0),  # Bottom-left
            (0, length - room['length']),  # Top-left
            (width - room['width'], 0),  # Bottom-right
            (width - room['width'], length - room['length'])  # Top-right
        ]
        
        random.shuffle(corners)
        
        for x, y in corners:
            if self._can_place_at(room, x, y, grid, width, length):
                room['x'] = x
                room['y'] = y
                return True
        
        return False
    
    def _place_adjacent_to_existing(self, room, grid, placed_rooms, width, length):
        """Try to place room adjacent to existing rooms"""
        if not placed_rooms:
            return False
        
        for existing_room in placed_rooms:
            # Try all sides
            positions = [
                (existing_room['x'] + existing_room['width'] + self.room_spacing, existing_room['y']),  # Right
                (existing_room['x'] - room['width'] - self.room_spacing, existing_room['y']),  # Left
                (existing_room['x'], existing_room['y'] + existing_room['length'] + self.room_spacing),  # Top
                (existing_room['x'], existing_room['y'] - room['length'] - self.room_spacing),  # Bottom
            ]
            
            for x, y in positions:
                if self._can_place_at(room, x, y, grid, width, length):
                    room['x'] = x
                    room['y'] = y
                    return True
        
        return False
    
    def _place_randomly(self, room, grid, width, length):
        """Place room at random valid position"""
        max_attempts = 100
        
        for _ in range(max_attempts):
            x = random.uniform(0, width - room['width'])
            y = random.uniform(0, length - room['length'])
            
            x = round(x, 1)
            y = round(y, 1)
            
            if self._can_place_at(room, x, y, grid, width, length):
                room['x'] = x
                room['y'] = y
                return room
        
        # If no position found, reduce size
        room['width'] *= 0.9
        room['length'] *= 0.9
        room['area'] = room['width'] * room['length']
        
        return self._place_randomly(room, grid, width, length)
    
    def _can_place_at(self, room, x, y, grid, width, length):
        """Check if room can be placed at given position"""
        # Check boundaries
        if x < 0 or y < 0:
            return False
        if x + room['width'] > width or y + room['length'] > length:
            return False
        
        # Check grid (simplified collision detection)
        grid_x = int(x * 10)
        grid_y = int(y * 10)
        grid_w = int(room['width'] * 10)
        grid_l = int(room['length'] * 10)
        
        # Check if area is free
        if (grid_x + grid_w >= grid.shape[0] or 
            grid_y + grid_l >= grid.shape[1]):
            return False
        
        region = grid[grid_x:grid_x+grid_w, grid_y:grid_y+grid_l]
        if np.any(region > 0):
            return False
        
        return True
    
    def _mark_grid(self, room, grid):
        """Mark room position on grid"""
        grid_x = int(room['x'] * 10)
        grid_y = int(room['y'] * 10)
        grid_w = int(room['width'] * 10)
        grid_l = int(room['length'] * 10)
        
        grid[grid_x:grid_x+grid_w, grid_y:grid_y+grid_l] = 1
    
    def _optimize_layout(self, rooms, width, length, style):
        """Optimize room layout for better flow and aesthetics"""
        # Group rooms by type
        room_groups = {}
        for room in rooms:
            if room['type'] not in room_groups:
                room_groups[room['type']] = []
            room_groups[room['type']].append(room)
        
        # Apply style-specific optimizations
        if style == 'open_plan':
            rooms = self._optimize_open_plan(rooms, width, length)
        elif style == 'traditional':
            rooms = self._optimize_traditional(rooms, width, length)
        
        # Align rooms to grid
        for room in rooms:
            room['x'] = round(room['x'], 1)
            room['y'] = round(room['y'], 1)
        
        return rooms
    
    def _optimize_open_plan(self, rooms, width, length):
        """Optimize for open plan style"""
        # Merge living areas
        living_rooms = [r for r in rooms if r['type'] in ['living', 'kitchen']]
        
        if len(living_rooms) >= 2:
            # Position living areas together
            base_x = width * 0.1
            base_y = length * 0.1
            
            for i, room in enumerate(living_rooms):
                room['x'] = base_x + (i % 2) * (room['width'] + self.room_spacing)
                room['y'] = base_y + (i // 2) * (room['length'] + self.room_spacing)
        
        return rooms
    
    def _optimize_traditional(self, rooms, width, length):
        """Optimize for traditional style"""
        # Create clear separation between public and private areas
        public_rooms = [r for r in rooms if r['type'] in ['living', 'kitchen']]
        private_rooms = [r for r in rooms if r['type'] in ['bedroom', 'bathroom', 'office']]
        
        # Place public rooms near entrance (bottom-left)
        base_x_public = width * 0.1
        base_y_public = length * 0.1
        
        for i, room in enumerate(public_rooms):
            room['x'] = base_x_public + (i % 2) * (room['width'] + self.room_spacing)
            room['y'] = base_y_public + (i // 2) * (room['length'] + self.room_spacing)
        
        # Place private rooms further in (top-right)
        base_x_private = width * 0.6
        base_y_private = length * 0.6
        
        for i, room in enumerate(private_rooms):
            room['x'] = base_x_private + (i % 2) * (room['width'] + self.room_spacing)
            room['y'] = base_y_private + (i // 2) * (room['length'] + self.room_spacing)
        
        return rooms
    
    def generate_walls(self, rooms):
        """
        Generate walls between rooms
        Returns list of wall segments
        """
        walls = []
        
        # Add exterior walls (simplified - would be more complex in production)
        # For now, just mark room boundaries
        
        for room in rooms:
            # Room boundaries
            walls.append({
                'x1': room['x'],
                'y1': room['y'],
                'x2': room['x'] + room['width'],
                'y2': room['y'],
                'type': 'exterior'
            })
            walls.append({
                'x1': room['x'] + room['width'],
                'y1': room['y'],
                'x2': room['x'] + room['width'],
                'y2': room['y'] + room['length'],
                'type': 'exterior'
            })
            walls.append({
                'x1': room['x'] + room['width'],
                'y1': room['y'] + room['length'],
                'x2': room['x'],
                'y2': room['y'] + room['length'],
                'type': 'exterior'
            })
            walls.append({
                'x1': room['x'],
                'y1': room['y'] + room['length'],
                'x2': room['x'],
                'y2': room['y'],
                'type': 'exterior'
            })
        
        return walls
