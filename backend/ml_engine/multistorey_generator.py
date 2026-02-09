import numpy as np
import random
from typing import List, Dict

class MultiStoreyGenerator:
    def __init__(self):
        self.stair_standards = {
            'width': 1.0,      # Staircase width
            'rise': 0.18,      # Step rise
            'run': 0.28,       # Step run
            'landing': 1.2,    # Landing length
        }
        
        self.floor_height = 3.0  # Standard floor height
    
    def generate_building(self, floor_config: List[Dict], style: str) -> Dict:
        """
        Generate multi-storey building with consistent layout across floors
        """
        building = {
            'floors': [],
            'stairs': [],
            'elevators': [],
            'style': style,
            'total_floors': len(floor_config)
        }
        
        # Generate each floor
        for i, config in enumerate(floor_config):
            floor = self._generate_floor(config, i, style)
            building['floors'].append(floor)
        
        # Generate vertical circulation
        building['stairs'] = self._generate_stairs(building['floors'], style)
        
        # Generate elevators if building has 3+ floors
        if len(floor_config) >= 3:
            building['elevators'] = self._generate_elevators(building['floors'], style)
        
        # Connect floors with stairs
        self._connect_floors_with_stairs(building)
        
        return building
    
    def _generate_floor(self, config: Dict, floor_number: int, style: str) -> Dict:
        """Generate a single floor"""
        floor = {
            'floor_number': floor_number + 1,
            'level': floor_number,
            'width': config['width'],
            'length': config['length'],
            'height': self.floor_height,
            'rooms_required': config['rooms_required'],
            'style': style,
            'is_ground_floor': floor_number == 0,
            'is_top_floor': floor_number == len(config) - 1,
        }
        
        # Add floor-specific features
        if floor['is_ground_floor']:
            floor['features'] = ['main_entrance', 'lobby']
        elif floor['is_top_floor']:
            floor['features'] = ['roof_access']
        else:
            floor['features'] = []
        
        return floor
    
    def _generate_stairs(self, floors: List[Dict], style: str) -> List[Dict]:
        """Generate staircases for the building"""
        stairs = []
        
        # Determine number of staircases (minimum 2 for fire safety)
        num_staircases = max(2, len(floors) // 2)
        
        for stair_idx in range(num_staircases):
            staircase = self._create_staircase(floors, stair_idx, style)
            if staircase:
                stairs.append(staircase)
        
        return stairs
    
    def _create_staircase(self, floors: List[Dict], stair_idx: int, style: str) -> Dict:
        """Create a single staircase"""
        # Position staircase (distributed around building)
        first_floor = floors[0]
        
        # Calculate positions (corners or mid-walls)
        positions = self._get_stair_positions(first_floor['width'], first_floor['length'])
        
        if stair_idx >= len(positions):
            return None
        
        pos_x, pos_y, orientation = positions[stair_idx]
        
        # Calculate staircase dimensions
        stair_width = self.stair_standards['width']
        stair_length = self._calculate_stair_length(len(floors))
        
        # Adjust for orientation
        if orientation == 'north_south':
            actual_width = stair_width
            actual_length = stair_length
        else:
            actual_width = stair_length
            actual_length = stair_width
        
        # Create staircase object
        staircase = {
            'id': f'stair_{stair_idx}',
            'type': 'staircase',
            'x': pos_x,
            'y': pos_y,
            'width': actual_width,
            'length': actual_length,
            'orientation': orientation,
            'floors_served': [f['floor_number'] for f in floors],
            'steps_per_floor': int(self.floor_height / self.stair_standards['rise']),
            'style': style,
            'has_landing': True,
            'landing_position': 'mid',  # mid or quarter
        }
        
        # Generate steps for visualization
        staircase['steps'] = self._generate_steps(staircase, len(floors))
        
        return staircase
    
    def _get_stair_positions(self, width: float, length: float) -> List[tuple]:
        """Get positions for staircases"""
        positions = []
        margin = 2.0  # Distance from walls
        
        # Corner positions
        positions.append((margin, margin, 'north_south'))  # SW corner
        positions.append((width - margin - 1.2, margin, 'east_west'))  # SE corner
        positions.append((margin, length - margin - 2.5, 'east_west'))  # NW corner
        positions.append((width - margin - 1.2, length - margin - 2.5, 'north_south'))  # NE corner
        
        # Mid-wall positions (if needed)
        if width > 15:
            positions.append((width / 2 - 0.6, margin, 'north_south'))  # South mid
            positions.append((width / 2 - 0.6, length - margin - 2.5, 'north_south'))  # North mid
        
        if length > 15:
            positions.append((margin, length / 2 - 1.25, 'east_west'))  # West mid
            positions.append((width - margin - 1.2, length / 2 - 1.25, 'east_west'))  # East mid
        
        return positions
    
    def _calculate_stair_length(self, num_floors: int) -> float:
        """Calculate total length of staircase"""
        # Length for one floor
        steps_per_floor = int(self.floor_height / self.stair_standards['rise'])
        run_per_floor = steps_per_floor * self.stair_standards['run']
        
        # Add landing every floor
        total_length = num_floors * (run_per_floor + self.stair_standards['landing'])
        
        return round(total_length, 2)
    
    def _generate_steps(self, staircase: Dict, num_floors: int) -> List[Dict]:
        """Generate step objects for visualization"""
        steps = []
        
        x, y = staircase['x'], staircase['y']
        width = staircase['width']
        length = staircase['length']
        orientation = staircase['orientation']
        
        steps_per_floor = int(self.floor_height / self.stair_standards['rise'])
        
        for floor in range(num_floors):
            floor_y_offset = floor * (steps_per_floor * self.stair_standards['rise'])
            
            for step in range(steps_per_floor):
                step_num = floor * steps_per_floor + step
                
                if orientation == 'north_south':
                    step_x = x
                    step_y = y + step * self.stair_standards['run']
                    step_width = width
                    step_length = self.stair_standards['rise']
                else:
                    step_x = x + step * self.stair_standards['run']
                    step_y = y
                    step_width = self.stair_standards['rise']
                    step_length = width
                
                steps.append({
                    'number': step_num + 1,
                    'floor': floor + 1,
                    'x': round(step_x, 2),
                    'y': round(step_y, 2),
                    'width': round(step_width, 2),
                    'length': round(step_length, 2),
                    'height': floor_y_offset + step * self.stair_standards['rise']
                })
        
        return steps
    
    def _generate_elevators(self, floors: List[Dict], style: str) -> List[Dict]:
        """Generate elevator shafts"""
        if len(floors) < 3:
            return []
        
        elevators = []
        first_floor = floors[0]
        
        # Position elevators (typically near main entrance/staircase)
        elevator_width = 2.2
        elevator_length = 2.5
        
        # Create elevator bank (2-4 elevators)
        num_elevators = min(4, max(2, len(floors) // 2))
        
        base_x = first_floor['width'] * 0.7
        base_y = first_floor['length'] * 0.3
        
        for i in range(num_elevators):
            elevator = {
                'id': f'elevator_{i}',
                'type': 'elevator',
                'x': base_x + i * (elevator_width + 0.3),
                'y': base_y,
                'width': elevator_width,
                'length': elevator_length,
                'floors_served': [f['floor_number'] for f in floors],
                'capacity': 8,  # persons
                'speed': 1.0,   # m/s
                'style': style,
            }
            elevators.append(elevator)
        
        return elevators
    
    def _connect_floors_with_stairs(self, building: Dict):
        """Connect floors with staircases"""
        for stair in building['stairs']:
            # Add stair access points on each floor
            stair['floor_access'] = []
            
            for floor in building['floors']:
                access_point = {
                    'floor': floor['floor_number'],
                    'x': stair['x'],
                    'y': stair['y'],
                    'door_orientation': self._get_door_orientation(stair['orientation'])
                }
                stair['floor_access'].append(access_point)
                
                # Add stair reference to floor
                if 'stairs' not in floor:
                    floor['stairs'] = []
                floor['stairs'].append({
                    'id': stair['id'],
                    'x': stair['x'],
                    'y': stair['y'],
                    'width': stair['width'],
                    'length': stair['length']
                })
    
    def _get_door_orientation(self, stair_orientation: str) -> str:
        """Get door orientation for stair access"""
        if stair_orientation == 'north_south':
            return 'east'  # Door on east side
        else:
            return 'south'  # Door on south side
    
    def optimize_vertical_circulation(self, building: Dict):
        """Optimize vertical circulation for efficiency"""
        # Ensure staircases are evenly distributed
        stairs = building['stairs']
        floors = building['floors']
        
        # Calculate travel distances
        for floor in floors:
            floor['max_stair_distance'] = self._calculate_max_stair_distance(floor, stairs)
        
        # Optimize elevator placement if applicable
        if building['elevators']:
            self._optimize_elevator_placement(building)
        
        return building
    
    def _calculate_max_stair_distance(self, floor: Dict, stairs: List[Dict]) -> float:
        """Calculate maximum distance to any staircase on a floor"""
        max_distance = 0
        
        # Simplified: use center of floor
        floor_center_x = floor['width'] / 2
        floor_center_y = floor['length'] / 2
        
        for stair in stairs:
            stair_center_x = stair['x'] + stair['width'] / 2
            stair_center_y = stair['y'] + stair['length'] / 2
            
            distance = np.sqrt(
                (stair_center_x - floor_center_x)**2 + 
                (stair_center_y - floor_center_y)**2
            )
            
            max_distance = max(max_distance, distance)
        
        return round(max_distance, 2)
    
    def _optimize_elevator_placement(self, building: Dict):
        """Optimize elevator placement for accessibility"""
        elevators = building['elevators']
        first_floor = building['floors'][0]
        
        # Place elevators near main entrance (assumed at center of south wall)
        main_entrance_x = first_floor['width'] / 2
        main_entrance_y = 0
        
        # Adjust elevator positions to be near entrance
        for i, elevator in enumerate(elevators):
            elevator['x'] = main_entrance_x - (len(elevators) * 2.5) / 2 + i * 2.5
            elevator['y'] = main_entrance_y + 3.0  # 3m from entrance
