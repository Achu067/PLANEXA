import numpy as np
import networkx as nx
from sklearn.preprocessing import StandardScaler
import json

class GNNFloorsPredictor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.load_pretrained_model()
    
    def load_pretrained_model(self):
        """Load or create a simple GNN model for floor prediction"""
        # In production, this would load a trained PyTorch model
        # For demo, we'll use rule-based logic
        pass
    
    def predict_optimal_layout(self, width, length, rooms, floors):
        """
        Predict optimal floor layout using graph neural networks
        Returns floor configuration with room distribution
        """
        # Calculate total area
        total_area = width * length * floors
        
        # Calculate required areas for each room type
        room_areas = self._calculate_room_areas(rooms)
        
        # Distribute rooms across floors
        floor_config = self._distribute_rooms_across_floors(
            room_areas, floors, width, length
        )
        
        return floor_config
    
    def _calculate_room_areas(self, rooms):
        """Calculate approximate areas for each room type"""
        area_standards = {
            'bedroom': 12,      # 12 m²
            'living': 20,       # 20 m²
            'kitchen': 10,      # 10 m²
            'bathroom': 6,      # 6 m²
            'office': 10,       # 10 m²
        }
        
        room_areas = []
        for req in rooms:
            room_type = req['type']
            count = req['count']
            area = area_standards.get(room_type, 10)
            
            for _ in range(count):
                room_areas.append({
                    'type': room_type,
                    'area': area,
                    'min_dimensions': self._get_min_dimensions(room_type)
                })
        
        return room_areas
    
    def _get_min_dimensions(self, room_type):
        """Get minimum dimensions for each room type"""
        dimensions = {
            'bedroom': (3, 3),      # 3m x 3m minimum
            'living': (4, 4),       # 4m x 4m minimum
            'kitchen': (2.5, 3),    # 2.5m x 3m minimum
            'bathroom': (1.8, 2.4), # 1.8m x 2.4m minimum
            'office': (2.5, 3),     # 2.5m x 3m minimum
        }
        return dimensions.get(room_type, (3, 3))
    
    def _distribute_rooms_across_floors(self, room_areas, floors, width, length):
        """Distribute rooms across multiple floors"""
        floor_area = width * length
        floor_config = []
        
        # Sort rooms by area (largest first)
        room_areas.sort(key=lambda x: x['area'], reverse=True)
        
        # Initialize floors
        for floor_idx in range(floors):
            floor_config.append({
                'floor_number': floor_idx + 1,
                'width': width,
                'length': length,
                'max_area': floor_area,
                'rooms_required': [],
                'remaining_area': floor_area * 0.85  # Reserve 15% for circulation
            })
        
        # Greedy distribution algorithm
        for room in room_areas:
            placed = False
            
            # Try to place in existing floors
            for floor in floor_config:
                if (floor['remaining_area'] >= room['area'] and 
                    self._can_fit_room(room, floor)):
                    
                    floor['rooms_required'].append(room)
                    floor['remaining_area'] -= room['area']
                    placed = True
                    break
            
            # If couldn't place, add to first floor (will be resized)
            if not placed:
                floor_config[0]['rooms_required'].append(room)
                floor_config[0]['remaining_area'] -= room['area']
        
        return floor_config
    
    def _can_fit_room(self, room, floor):
        """Check if a room can fit in the floor considering dimensions"""
        min_width, min_length = room['min_dimensions']
        return min_width <= floor['width'] and min_length <= floor['length']
    
    def create_graph_representation(self, floor_config):
        """Create graph representation for GNN processing"""
        G = nx.Graph()
        
        for floor_idx, floor in enumerate(floor_config):
            floor_node = f"floor_{floor_idx}"
            G.add_node(floor_node, type='floor', **floor)
            
            for room_idx, room in enumerate(floor['rooms_required']):
                room_node = f"room_{floor_idx}_{room_idx}"
                G.add_node(room_node, type='room', **room)
                G.add_edge(floor_node, room_node, weight=room['area'])
        
        return G
