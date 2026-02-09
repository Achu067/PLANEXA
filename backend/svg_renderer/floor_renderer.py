from .svg_builder import SVGBuilder
import json

class FloorRenderer:
    def __init__(self):
        self.svg_builder = SVGBuilder()
    
    def render_floor(self, floor_data: Dict, options: Dict = None) -> str:
        """
        Render a floor with given options
        """
        if options is None:
            options = {}
        
        # Apply rendering options
        render_data = self._prepare_render_data(floor_data, options)
        
        # Generate SVG
        svg_content = self.svg_builder.build_svg(
            render_data,
            include_furniture=options.get('include_furniture', True),
            include_windows=options.get('include_windows', True)
        )
        
        return svg_content
    
    def render_multiple_floors(self, building_data: Dict, options: Dict = None) -> Dict:
        """
        Render all floors of a building
        Returns dict with floor_number: svg_content
        """
        if options is None:
            options = {}
        
        floor_svgs = {}
        
        for floor in building_data['floors']:
            svg_content = self.render_floor(floor, options)
            floor_svgs[floor['floor_number']] = svg_content
        
        return floor_svgs
    
    def _prepare_render_data(self, floor_data: Dict, options: Dict) -> Dict:
        """Prepare data for rendering"""
        render_data = floor_data.copy()
        
        # Filter furniture based on options
        if not options.get('include_furniture', True) and 'furniture' in render_data:
            del render_data['furniture']
        
        # Filter windows based on options
        if not options.get('include_windows', True):
            if 'windows' in render_data:
                del render_data['windows']
            if 'doors' in render_data:
                # Keep doors but mark them differently?
                pass
        
        # Apply style-specific rendering
        style = render_data.get('style', 'modern')
        self._apply_style_rendering(render_data, style)
        
        return render_data
    
    def _apply_style_rendering(self, render_data: Dict, style: str):
        """Apply style-specific rendering options"""
        # This would adjust colors, line styles, etc. based on architectural style
        # For now, just pass through
        pass
    
    def create_floor_plan_sheet(self, building_data: Dict, floor_number: int, 
                               options: Dict = None) -> str:
        """
        Create a complete floor plan sheet with title, notes, etc.
        """
        if options is None:
            options = {}
        
        # Get floor data
        floor = next((f for f in building_data['floors'] 
                     if f['floor_number'] == floor_number), None)
        
        if not floor:
            return ""
        
        # Create main SVG
        svg_content = self.render_floor(floor, options)
        
        # Convert to complete sheet (would add title block, notes, etc.)
        # For simplicity, return basic SVG for now
        return svg_content
