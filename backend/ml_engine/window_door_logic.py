import numpy as np
import random
from typing import List, Dict, Tuple

class WindowDoorLogic:
    def __init__(self):
        self.window_standards = {
            'bedroom': {'min': 1, 'max': 2, 'size': (1.2, 1.5)},
            'living': {'min': 2, 'max': 4, 'size': (1.5, 2.0)},
            'kitchen': {'min': 1, 'max': 2, 'size': (1.0, 1.2)},
            'bathroom': {'min': 0, 'max': 1, 'size': (0.6, 0.8)},
            'office': {'min': 1, 'max': 2, 'size': (1.0, 1.5)},
        }
        
        self.door_standards = {
            'interior': {'width': 0.9, 'height': 2.1},
            'exterior': {'width': 1.0, 'height': 2.1},
            'bathroom': {'width': 0.8, 'height': 2.0},
        }
    
    def generate_openings(self, rooms: List[Dict], walls: List[Dict], style: str) -> Tuple[List, List]:
        """
        Generate windows and doors for rooms
        Returns tuple of (windows, doors)
        """
        windows = []
        doors = []
        
        # Generate windows for each room
        for room in rooms:
            room_windows = self._generate_windows_for_room(room, style)
            windows.extend(room_windows)
        
        # Generate doors between rooms
        interior_doors = self._generate_interior_doors(rooms, style)
        doors.extend(interior_doors)
        
        # Generate exterior doors
        exterior_doors = self._generate_exterior_doors(rooms, style)
        doors.extend(exterior_doors)
        
        return windows, doors
    
    def _generate_windows_for_room(self, room: Dict, style: str) -> List[Dict]:
        """Generate windows for a single room"""
        room_type = room['type']
        
        if room_type not in self.window_standards:
            return []
        
        standards = self.window_standards[room_type]
        
        # Determine number of windows
        min_windows = standards['min']
        max_windows = standards['max']
        
        # Adjust based on style
        style_adjustments = {
            'modern': 1.2,      # More windows in modern design
            'traditional': 1.0,
            'minimalist': 0.8,  # Fewer, larger windows
            'open_plan': 1.5    # Many windows for open feel
        }
        
        adjustment = style_adjustments.get(style, 1.0)
        num_windows = int(np.clip(
            random.randint(min_windows, max_windows) * adjustment,
            min_windows, max_windows * 2
        ))
        
        windows = []
        
        # Get room walls
        room_walls = self._get_room_walls(room)
        
        # Distribute windows across walls
        walls_with_windows = random.sample(room_walls, min(num_windows, len(room_walls)))
        
        for wall in walls_with_windows:
            window = self._create_window_on_wall(wall, room_type, style)
            if window:
                windows.append(window)
        
        return windows
    
    def _get_room_walls(self, room: Dict) -> List[Dict]:
        """Get walls for a room"""
        walls = []
        
        # Create wall representations
        walls.append({
            'x1': room['x'], 'y1': room['y'],
            'x2': room['x'] + room['width'], 'y2': room['y'],
            'type': 'south', 'room': room
        })
        walls.append({
            'x1': room['x'] + room['width'], 'y1': room['y'],
            'x2': room['x'] + room['width'], 'y2': room['y'] + room['length'],
            'type': 'east', 'room': room
        })
        walls.append({
            'x1': room['x'] + room['width'], 'y1': room['y'] + room['length'],
            'x2': room['x'], 'y2': room['y'] + room['length'],
            'type': 'north', 'room': room
        })
        walls.append({
            'x1': room['x'], 'y1': room['y'] + room['length'],
            'x2': room['x'], 'y2': room['y'],
            'type': 'west', 'room': room
        })
        
        return walls
    
    def _create_window_on_wall(self, wall: Dict, room_type: str, style: str) -> Dict:
        """Create a window on a wall"""
        standards = self.window_standards[room_type]
        min_size, max_size = standards['size']
        
        # Adjust window size based on style
        style_multipliers = {
            'modern': 1.2,
            'traditional': 1.0,
            'minimalist': 1.5,  # Larger windows
            'open_plan': 1.3
        }
        
        multiplier = style_multipliers.get(style, 1.0)
        window_width = random.uniform(min_size, max_size) * multiplier
        window_width = round(window_width, 2)
        
        # Calculate wall length
        wall_length = np.sqrt((wall['x2'] - wall['x1'])**2 + (wall['y2'] - wall['y1'])**2)
        
        # Ensure window fits on wall
        if window_width > wall_length * 0.8:  # Max 80% of wall
            window_width = wall_length * 0.8
        
        # Position window on wall
        available_length = wall_length - window_width
        start_offset = random.uniform(0.1, max(0.2, available_length - 0.1))
        
        # Calculate window position
        if wall['type'] in ['south', 'north']:
            # Horizontal wall
            x1 = wall['x1'] + start_offset
            y1 = wall['y1']
            x2 = x1 + window_width
            y2 = wall['y2']
        else:
            # Vertical wall
            x1 = wall['x1']
            y1 = wall['y1'] + start_offset
            x2 = wall['x2']
            y2 = y1 + window_width
        
        return {
            'x1': round(x1, 2),
            'y1': round(y1, 2),
            'x2': round(x2, 2),
            'y2': round(y2, 2),
            'type': 'window',
            'room_type': room_type,
            'wall_type': wall['type']
        }
    
    def _generate_interior_doors(self, rooms: List[Dict], style: str) -> List[Dict]:
        """Generate doors between adjacent rooms"""
        doors = []
        
        # Find adjacent rooms
        for i, room1 in enumerate(rooms):
            for j, room2 in enumerate(rooms[i+1:], i+1):
                if self._are_rooms_adjacent(room1, room2):
                    door = self._create_door_between_rooms(room1, room2, 'interior', style)
                    if door:
                        doors.append(door)
        
        return doors
    
    def _are_rooms_adjacent(self, room1: Dict, room2: Dict) -> bool:
        """Check if two rooms are adjacent"""
        # Check horizontal adjacency
        horizontal_adjacent = (
            abs(room1['x'] + room1['width'] - room2['x']) < 0.1 or
            abs(room2['x'] + room2['width'] - room1['x']) < 0.1
        ) and (
            room1['y'] < room2['y'] + room2['length'] and
            room2['y'] < room1['y'] + room1['length']
        )
        
        # Check vertical adjacency
        vertical_adjacent = (
            abs(room1['y'] + room1['length'] - room2['y']) < 0.1 or
            abs(room2['y'] + room2['length'] - room1['y']) < 0.1
        ) and (
            room1['x'] < room2['x'] + room2['width'] and
            room2['x'] < room1['x'] + room1['width']
        )
        
        return horizontal_adjacent or vertical_adjacent
    
    def _create_door_between_rooms(self, room1: Dict, room2: Dict, 
                                 door_type: str, style: str) -> Dict:
        """Create a door between two rooms"""
        standards = self.door_standards[door_type]
        door_width = standards['width']
        
        # Find overlapping wall segment
        overlap = self._find_wall_overlap(room1, room2)
        
        if not overlap:
            return None
        
        wall_type, start, end, x, y = overlap
        
        # Ensure door fits
        if end - start < door_width:
            return None
        
        # Position door in middle of overlap
        door_start = (start + end) / 2 - door_width / 2
        
        # Calculate door coordinates
        if wall_type in ['south', 'north']:
            # Horizontal wall
            x1 = x + door_start
            y1 = y
            x2 = x1 + door_width
            y2 = y
            swing_side = 'top' if wall_type == 'south' else 'bottom'
        else:
            # Vertical wall
            x1 = x
            y1 = y + door_start
            x2 = x
            y2 = y1 + door_width
            swing_side = 'left' if wall_type == 'east' else 'right'
        
        return {
            'x1': round(x1, 2),
            'y1': round(y1, 2),
            'x2': round(x2, 2),
            'y2': round(y2, 2),
            'type': door_type,
            'width': door_width,
            'room1': room1['type'],
            'room2': room2['type'],
            'swing_side': swing_side,
            'style': style
        }
    
    def _find_wall_overlap(self, room1: Dict, room2: Dict) -> tuple:
        """Find overlapping wall segment between two rooms"""
        # Check horizontal walls
        if abs(room1['y'] + room1['length'] - room2['y']) < 0.1:  # room1 north to room2 south
            overlap_start = max(room1['x'], room2['x'])
            overlap_end = min(room1['x'] + room1['width'], room2['x'] + room2['width'])
            if overlap_end > overlap_start:
                return 'north', overlap_start, overlap_end, overlap_start, room1['y'] + room1['length']
        
        elif abs(room2['y'] + room2['length'] - room1['y']) < 0.1:  # room2 north to room1 south
            overlap_start = max(room1['x'], room2['x'])
            overlap_end = min(room1['x'] + room1['width'], room2['x'] + room2['width'])
            if overlap_end > overlap_start:
                return 'south', overlap_start, overlap_end, overlap_start, room1['y']
        
        # Check vertical walls
        elif abs(room1['x'] + room1['width'] - room2['x']) < 0.1:  # room1 east to room2 west
            overlap_start = max(room1['y'], room2['y'])
            overlap_end = min(room1['y'] + room1['length'], room2['y'] + room2['length'])
            if overlap_end > overlap_start:
                return 'east', overlap_start, overlap_end, room1['x'] + room1['width'], overlap_start
        
        elif abs(room2['x'] + room2['width'] - room1['x']) < 0.1:  # room2 east to room1 west
            overlap_start = max(room1['y'], room2['y'])
            overlap_end = min(room1['y'] + room1['length'], room2['y'] + room2['length'])
            if overlap_end > overlap_start:
                return 'west', overlap_start, overlap_end, room1['x'], overlap_start
        
        return None
    
    def _generate_exterior_doors(self, rooms: List[Dict], style: str) -> List[Dict]:
        """Generate exterior doors (entrances)"""
        doors = []
        
        # Typically, main entrance is from living room or hallway
        living_rooms = [r for r in rooms if r['type'] == 'living']
        
        if living_rooms:
            # Place main entrance
            main_entrance = self._create_exterior_door(living_rooms[0], 'main', style)
            if main_entrance:
                doors.append(main_entrance)
        
        # Add secondary exits if needed (e.g., from kitchen to garden)
        kitchens = [r for r in rooms if r['type'] == 'kitchen']
        
        if kitchens and random.random() > 0.5:  # 50% chance
            secondary_door = self._create_exterior_door(kitchens[0], 'secondary', style)
            if secondary_door:
                doors.append(secondary_door)
        
        return doors
    
    def _create_exterior_door(self, room: Dict, door_type: str, style: str) -> Dict:
        """Create an exterior door from a room"""
        standards = self.door_standards['exterior']
        door_width = standards['width']
        
        # Choose a wall for the door (prefer south wall for main entrance)
        walls = self._get_room_walls(room)
        
        if door_type == 'main':
            # Prefer south wall for main entrance
            eligible_walls = [w for w in walls if w['type'] == 'south']
            if not eligible_walls:
                eligible_walls = walls
        else:
            eligible_walls = walls
        
        if not eligible_walls:
            return None
        
        wall = random.choice(eligible_walls)
        wall_length = np.sqrt((wall['x2'] - wall['x1'])**2 + (wall['y2'] - wall['y1'])**2)
        
        # Ensure door fits
        if wall_length < door_width:
            return None
        
        # Position door (centered for main entrance, random for secondary)
        if door_type == 'main':
            door_start = wall_length / 2 - door_width / 2
        else:
            door_start = random.uniform(0.1, wall_length - door_width - 0.1)
        
        # Calculate door coordinates
        if wall['type'] in ['south', 'north']:
            # Horizontal wall
            x1 = wall['x1'] + door_start
            y1 = wall['y1']
            x2 = x1 + door_width
            y2 = wall['y2']
            swing_side = 'outward' if wall['type'] == 'south' else 'inward'
        else:
            # Vertical wall
            x1 = wall['x1']
            y1 = wall['y1'] + door_start
            x2 = wall['x2']
            y2 = y1 + door_width
            swing_side = 'outward' if wall['type'] == 'west' else 'inward'
        
        return {
            'x1': round(x1, 2),
            'y1': round(y1, 2),
            'x2': round(x2, 2),
            'y2': round(y2, 2),
            'type': 'exterior',
            'subtype': door_type,
            'width': door_width,
            'room': room['type'],
            'swing_side': swing_side,
            'style': style
        }
