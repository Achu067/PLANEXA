from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime
from ml_engine.gnn_predictor import GNNFloorsPredictor
from ml_engine.room_placer import RoomPlacer
from ml_engine.furniture_layout import FurnitureLayoutAI
from ml_engine.window_door_logic import WindowDoorLogic
from ml_engine.multistorey_generator import MultiStoreyGenerator
from svg_renderer.svg_builder import SVGBuilder
from export_engine.png_generator import PNGGenerator
from export_engine.pdf_generator import PDFGenerator

app = Flask(__name__)
CORS(app)

# Initialize ML components
gnn_predictor = GNNFloorsPredictor()
room_placer = RoomPlacer()
furniture_ai = FurnitureLayoutAI()
window_door_logic = WindowDoorLogic()
multistorey_gen = MultiStoreyGenerator()
svg_builder = SVGBuilder()

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "service": "AI Floor Plan Generator",
        "version": "1.0.0"
    })

@app.route('/generate', methods=['POST'])
def generate_floorplan():
    try:
        data = request.json
        print(f"Received generation request: {data}")
        
        # Step 1: Predict optimal floor configuration using GNN
        floor_config = gnn_predictor.predict_optimal_layout(
            width=data['width'],
            length=data['length'],
            rooms=data['rooms'],
            floors=data['floors']
        )
        
        # Step 2: Generate multi-storey layout
        building = multistorey_gen.generate_building(
            floor_config=floor_config,
            style=data['style']
        )
        
        # Step 3: Place rooms on each floor
        for floor in building['floors']:
            floor['rooms'] = room_placer.place_rooms(
                floor['width'],
                floor['length'],
                floor['rooms_required'],
                data['style']
            )
            
            # Step 4: Generate walls
            floor['walls'] = room_placer.generate_walls(floor['rooms'])
            
            # Step 5: Add windows and doors
            if data.get('include_windows', True):
                floor['windows'], floor['doors'] = window_door_logic.generate_openings(
                    floor['rooms'],
                    floor['walls'],
                    data['style']
                )
            
            # Step 6: Add furniture if requested
            if data.get('include_furniture', True):
                floor['furniture'] = furniture_ai.layout_furniture(
                    floor['rooms'],
                    floor['style']
                )
            
            # Step 7: Calculate metrics
            floor['metrics'] = calculate_floor_metrics(floor)
        
        # Step 8: Generate overall building metrics
        building['metrics'] = calculate_building_metrics(building)
        
        # Step 9: Generate SVG for each floor
        building['svg_data'] = {}
        for i, floor in enumerate(building['floors']):
            building['svg_data'][f'floor_{i+1}'] = svg_builder.build_svg(
                floor,
                include_furniture=data.get('include_furniture', True),
                include_windows=data.get('include_windows', True)
            )
        
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "building": building,
            "floors": building['floors'],
            "metrics": building['metrics']
        })
        
    except Exception as e:
        print(f"Error in generation: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/export/png', methods=['POST'])
def export_png():
    try:
        data = request.json
        floor_index = data.get('floor_index', 0)
        
        png_generator = PNGGenerator()
        png_bytes = png_generator.generate(
            data['svg_data'][f'floor_{floor_index+1}'],
            width=1024,
            height=768
        )
        
        # Save temporarily
        filename = f"floorplan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join('temp', filename)
        
        with open(filepath, 'wb') as f:
            f.write(png_bytes)
        
        return send_file(filepath, mimetype='image/png', as_attachment=True)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/export/pdf', methods=['POST'])
def export_pdf():
    try:
        data = request.json
        
        pdf_generator = PDFGenerator()
        pdf_bytes = pdf_generator.generate(
            data['building'],
            data['svg_data']
        )
        
        # Save temporarily
        filename = f"floorplan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join('temp', filename)
        
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)
        
        return send_file(filepath, mimetype='application/pdf', as_attachment=True)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def calculate_floor_metrics(floor):
    """Calculate metrics for a single floor"""
    total_area = sum(room['area'] for room in floor['rooms'])
    circulation_area = total_area * 0.15  # Approximate
    efficiency = (total_area - circulation_area) / total_area * 100
    
    return {
        'total_area': round(total_area, 2),
        'room_count': len(floor['rooms']),
        'efficiency': round(efficiency, 1),
        'circulation_area': round(circulation_area, 2)
    }

def calculate_building_metrics(building):
    """Calculate overall building metrics"""
    total_area = sum(floor['metrics']['total_area'] for floor in building['floors'])
    total_rooms = sum(floor['metrics']['room_count'] for floor in building['floors'])
    
    return {
        'total_area': round(total_area, 2),
        'total_rooms': total_rooms,
        'floors': len(building['floors']),
        'average_efficiency': round(
            sum(floor['metrics']['efficiency'] for floor in building['floors']) / len(building['floors']), 
            1
        )
    }

if __name__ == '__main__':
    # Create temp directory if it doesn't exist
    os.makedirs('temp', exist_ok=True)
    
    app.run(debug=True, port=5000, host='0.0.0.0')
