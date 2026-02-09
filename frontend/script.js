class FloorPlanGenerator {
    constructor() {
        this.currentFloor = 1;
        this.totalFloors = 1;
        this.floorPlanData = null;
        
        this.initializeEventListeners();
        this.initializeChart();
        
        // For debugging
        console.log("FloorPlanGenerator initialized");
    }

    initializeEventListeners() {
        console.log("Initializing event listeners...");
        
        // Generate button
        document.getElementById('generate-btn').addEventListener('click', () => {
            console.log("Generate button clicked");
            this.generateFloorPlan();
        });

        // Export buttons (simplified for now)
        document.getElementById('export-png').addEventListener('click', () => {
            this.exportAsPNG();
        });

        document.getElementById('export-pdf').addEventListener('click', () => {
            this.exportAsPDF();
        });

        // Floor navigation
        document.getElementById('prev-floor').addEventListener('click', () => {
            if (this.currentFloor > 1) {
                this.currentFloor--;
                this.updateFloorDisplay();
            }
        });

        document.getElementById('next-floor').addEventListener('click', () => {
            if (this.currentFloor < this.totalFloors) {
                this.currentFloor++;
                this.updateFloorDisplay();
            }
        });

        // Tabs
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });

        // Room management
        document.getElementById('add-room').addEventListener('click', () => {
            this.addRoomInput();
        });

        // Initialize 3D view if Three.js is loaded
        if (typeof THREE !== 'undefined') {
            this.initialize3DView();
        } else {
            console.log("Three.js not loaded, skipping 3D view");
        }
        
        // Add test button for debugging
        this.addTestButton();
    }

    initializeChart() {
        try {
            const ctx = document.getElementById('stats-chart').getContext('2d');
            this.chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Living Area', 'Bedrooms', 'Kitchen', 'Bathrooms', 'Circulation'],
                    datasets: [{
                        data: [30, 40, 15, 10, 5],
                        backgroundColor: [
                            '#3498db',
                            '#2ecc71',
                            '#e74c3c',
                            '#9b59b6',
                            '#f39c12'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        } catch (e) {
            console.log("Chart.js not available:", e);
        }
    }

    async generateFloorPlan() {
        const specs = this.getInputSpecifications();
        console.log("Generating floor plan with specs:", JSON.stringify(specs, null, 2));
        
        // Show loading
        const generateBtn = document.getElementById('generate-btn');
        generateBtn.innerHTML = '⏳ Generating...';
        generateBtn.disabled = true;

        try {
            console.log("Sending request to backend...");
            const response = await fetch('http://localhost:5000/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(specs)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log("Received response from backend:", data);
            
            if (data.success) {
                this.floorPlanData = data;
                console.log("Floor data received:", data.floors);
                
                this.totalFloors = data.floors ? data.floors.length : 1;
                this.currentFloor = 1;
                
                // Render the floor plan
                this.renderFloorPlan();
                
                // Update analysis if metrics exist
                if (data.metrics) {
                    this.updateAnalysis(data.metrics);
                    if (this.chart) {
                        this.updateChart(data.metrics);
                    }
                }
                
                // Update 3D view if available
                if (typeof THREE !== 'undefined' && data.floors) {
                    this.update3DView(data.floors);
                }
                
                console.log("Floor plan generated successfully!");
            } else {
                throw new Error(data.error || "Unknown error from backend");
            }
        } catch (error) {
            console.error('Error generating floor plan:', error);
            alert(`Error generating floor plan: ${error.message}\n\nPlease check:\n1. Backend is running (localhost:5000)\n2. Browser console for details`);
        } finally {
            generateBtn.innerHTML = 'Generate Floor Plan';
            generateBtn.disabled = false;
        }
    }

    getInputSpecifications() {
        const roomReqs = [];
        document.querySelectorAll('.room-input').forEach(input => {
            const type = input.querySelector('.room-type').value;
            const count = parseInt(input.querySelector('.room-count').value) || 1;
            roomReqs.push({ type, count });
        });

        // Default values if inputs are empty
        return {
            width: parseInt(document.getElementById('width').value) || 12,
            length: parseInt(document.getElementById('length').value) || 10,
            floors: parseInt(document.getElementById('floors').value) || 1,
            rooms: roomReqs.length > 0 ? roomReqs : [{ type: 'bedroom', count: 2 }, { type: 'living', count: 1 }],
            style: document.getElementById('style').value || 'modern',
            include_furniture: document.getElementById('include-furniture').checked,
            include_windows: document.getElementById('include-windows').checked
        };
    }

    renderFloorPlan() {
        console.log("renderFloorPlan called, currentFloor:", this.currentFloor);
        
        if (!this.floorPlanData || !this.floorPlanData.floors || this.floorPlanData.floors.length === 0) {
            console.error("No floor plan data available");
            this.showErrorMessage("No floor plan data available. Please generate a floor plan first.");
            return;
        }

        const floorIndex = this.currentFloor - 1;
        if (floorIndex >= this.floorPlanData.floors.length) {
            console.error("Floor index out of bounds");
            this.showErrorMessage("Invalid floor number");
            return;
        }

        const floorData = this.floorPlanData.floors[floorIndex];
        console.log("Rendering floor data:", floorData);

        const svgContainer = document.getElementById('svg-container');
        if (!svgContainer) {
            console.error("SVG container not found!");
            return;
        }

        // Clear container
        svgContainer.innerHTML = '';
        
        // Create SVG element
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("width", "100%");
        svg.setAttribute("height", "100%");
        svg.setAttribute("viewBox", `0 0 ${floorData.width * 50} ${floorData.length * 50}`);
        svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
        svg.style.backgroundColor = "#ffffff";
        svg.style.border = "1px solid #ddd";

        // Add grid
        this.addGrid(svg, floorData.width * 50, floorData.length * 50);

        // Render rooms
        if (floorData.rooms && floorData.rooms.length > 0) {
            console.log(`Rendering ${floorData.rooms.length} rooms`);
            floorData.rooms.forEach((room, index) => {
                console.log(`Room ${index}:`, room);
                this.renderRoom(svg, room);
            });
        } else {
            console.warn("No rooms to render");
            this.renderNoRoomsMessage(svg, floorData.width * 50, floorData.length * 50);
        }

        // Render walls if they exist
        if (floorData.walls && floorData.walls.length > 0) {
            floorData.walls.forEach(wall => {
                this.renderWall(svg, wall);
            });
        }

        // Render windows if they exist
        if (floorData.windows && floorData.windows.length > 0) {
            floorData.windows.forEach(window => {
                this.renderWindow(svg, window);
            });
        }

        // Render doors if they exist
        if (floorData.doors && floorData.doors.length > 0) {
            floorData.doors.forEach(door => {
                this.renderDoor(svg, door);
            });
        }

        // Add to container
        svgContainer.appendChild(svg);
        console.log("SVG rendering complete");
    }

    addGrid(svg, width, height) {
        const gridSize = 50; // 1 meter = 50 pixels
        
        // Create grid pattern
        const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
        const pattern = document.createElementNS("http://www.w3.org/2000/svg", "pattern");
        pattern.setAttribute("id", "grid");
        pattern.setAttribute("width", gridSize);
        pattern.setAttribute("height", gridSize);
        pattern.setAttribute("patternUnits", "userSpaceOnUse");

        // Horizontal line
        const hLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
        hLine.setAttribute("x1", "0");
        hLine.setAttribute("y1", "0");
        hLine.setAttribute("x2", gridSize);
        hLine.setAttribute("y2", "0");
        hLine.setAttribute("stroke", "#e0e0e0");
        hLine.setAttribute("stroke-width", "1");

        // Vertical line
        const vLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
        vLine.setAttribute("x1", "0");
        vLine.setAttribute("y1", "0");
        vLine.setAttribute("x2", "0");
        vLine.setAttribute("y2", gridSize);
        vLine.setAttribute("stroke", "#e0e0e0");
        vLine.setAttribute("stroke-width", "1");

        pattern.appendChild(hLine);
        pattern.appendChild(vLine);
        defs.appendChild(pattern);
        svg.appendChild(defs);

        // Apply grid to entire area
        const gridRect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        gridRect.setAttribute("width", "100%");
        gridRect.setAttribute("height", "100%");
        gridRect.setAttribute("fill", "url(#grid)");
        svg.appendChild(gridRect);
    }

    renderRoom(svg, room) {
        const scale = 50; // pixels per meter
        
        // Create room group
        const roomGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        
        // Room rectangle
        const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        const x = (room.x || 1) * scale;
        const y = (room.y || 1) * scale;
        const width = (room.width || 3) * scale;
        const height = (room.length || 3) * scale;
        
        rect.setAttribute("x", x);
        rect.setAttribute("y", y);
        rect.setAttribute("width", width);
        rect.setAttribute("height", height);
        rect.setAttribute("fill", this.getRoomColor(room.type));
        rect.setAttribute("stroke", "#2c3e50");
        rect.setAttribute("stroke-width", "2");
        rect.setAttribute("opacity", "0.8");
        
        // Room label
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        const centerX = x + width / 2;
        const centerY = y + height / 2;
        
        text.setAttribute("x", centerX);
        text.setAttribute("y", centerY);
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("dominant-baseline", "middle");
        text.setAttribute("fill", "white");
        text.setAttribute("font-weight", "bold");
        text.setAttribute("font-size", "12");
        text.setAttribute("style", "user-select: none;");

        // Create text content with multiple lines
        const roomType = document.createElementNS("http://www.w3.org/2000/svg", "tspan");
        roomType.setAttribute("x", centerX);
        roomType.setAttribute("dy", "-0.6em");
        roomType.textContent = room.type.charAt(0).toUpperCase() + room.type.slice(1);
        
        const roomArea = document.createElementNS("http://www.w3.org/2000/svg", "tspan");
        roomArea.setAttribute("x", centerX);
        roomArea.setAttribute("dy", "1.2em");
        const area = room.area || ((room.width || 3) * (room.length || 3)).toFixed(1);
        roomArea.textContent = `${area}m²`;

        text.appendChild(roomType);
        text.appendChild(roomArea);
        
        roomGroup.appendChild(rect);
        roomGroup.appendChild(text);
        svg.appendChild(roomGroup);
    }

    renderWall(svg, wall) {
        const scale = 50;
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", wall.x1 * scale);
        line.setAttribute("y1", wall.y1 * scale);
        line.setAttribute("x2", wall.x2 * scale);
        line.setAttribute("y2", wall.y2 * scale);
        line.setAttribute("stroke", "#2c3e50");
        line.setAttribute("stroke-width", "4");
        line.setAttribute("stroke-linecap", "round");
        svg.appendChild(line);
    }

    renderWindow(svg, window) {
        const scale = 50;
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", window.x1 * scale);
        line.setAttribute("y1", window.y1 * scale);
        line.setAttribute("x2", window.x2 * scale);
        line.setAttribute("y2", window.y2 * scale);
        line.setAttribute("stroke", "#3498db");
        line.setAttribute("stroke-width", "3");
        line.setAttribute("stroke-dasharray", "5,5");
        svg.appendChild(line);
    }

    renderDoor(svg, door) {
        const scale = 50;
        const x = door.x * scale;
        const y = door.y * scale;
        const width = 0.9 * scale; // Standard door width
        
        // Door rectangle
        const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        rect.setAttribute("x", x);
        rect.setAttribute("y", y);
        rect.setAttribute("width", width);
        rect.setAttribute("height", "3");
        rect.setAttribute("fill", "none");
        rect.setAttribute("stroke", "#e74c3c");
        rect.setAttribute("stroke-width", "2");
        svg.appendChild(rect);
        
        // Door swing arc (simplified)
        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        const radius = width * 0.8;
        path.setAttribute("d", `M ${x} ${y} A ${radius} ${radius} 0 0 1 ${x + width} ${y + 3}`);
        path.setAttribute("fill", "none");
        path.setAttribute("stroke", "#e74c3c");
        path.setAttribute("stroke-width", "1");
        path.setAttribute("stroke-dasharray", "2,2");
        svg.appendChild(path);
    }

    renderNoRoomsMessage(svg, width, height) {
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", width / 2);
        text.setAttribute("y", height / 2);
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("fill", "#666");
        text.setAttribute("font-size", "16");
        text.textContent = "No rooms generated";
        svg.appendChild(text);
    }

    showErrorMessage(message) {
        const svgContainer = document.getElementById('svg-container');
        svgContainer.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 20px; text-align: center; color: #666;">
                <div style="font-size: 48px; margin-bottom: 20px;">🏗️</div>
                <div style="font-size: 18px; margin-bottom: 10px; font-weight: bold;">${message}</div>
                <div style="font-size: 14px;">Click "Generate Floor Plan" to create a floor plan</div>
            </div>
        `;
    }

    getRoomColor(roomType) {
        const colors = {
            bedroom: '#3498db',
            living: '#2ecc71',
            kitchen: '#e74c3c',
            bathroom: '#9b59b6',
            office: '#f39c12',
            hallway: '#bdc3c7',
            stairs: '#34495e'
        };
        return colors[roomType] || '#95a5a6';
    }

    updateFloorDisplay() {
        const floorDisplay = document.getElementById('current-floor');
        if (floorDisplay) {
            floorDisplay.textContent = `Floor ${this.currentFloor}`;
        }
        this.renderFloorPlan();
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');
    }

    addRoomInput() {
        const container = document.getElementById('room-requirements');
        const div = document.createElement('div');
        div.className = 'room-input';
        div.innerHTML = `
            <select class="room-type">
                <option value="bedroom">Bedroom</option>
                <option value="living">Living Room</option>
                <option value="kitchen">Kitchen</option>
                <option value="bathroom">Bathroom</option>
                <option value="office">Office</option>
            </select>
            <input type="number" class="room-count" value="1" min="1" max="5">
            <button class="remove-room" type="button">×</button>
        `;
        container.appendChild(div);
        
        // Add event listener to remove button
        div.querySelector('.remove-room').addEventListener('click', () => {
            container.removeChild(div);
        });
    }

    updateAnalysis(metrics) {
        const metricsDiv = document.getElementById('metrics');
        if (!metricsDiv) return;
        
        metricsDiv.innerHTML = `
            <div class="metric">
                <h5>Total Area</h5>
                <p>${metrics.total_area || 0}m²</p>
            </div>
            <div class="metric">
                <h5>Room Count</h5>
                <p>${metrics.room_count || 0}</p>
            </div>
            <div class="metric">
                <h5>Efficiency</h5>
                <p>${metrics.efficiency || 0}%</p>
            </div>
            <div class="metric">
                <h5>Circulation Area</h5>
                <p>${metrics.circulation_area || 0}m²</p>
            </div>
        `;
    }

    updateChart(metrics) {
        if (this.chart) {
            // Update chart data with available metrics or defaults
            this.chart.data.datasets[0].data = [
                metrics.living_area || 30,
                metrics.bedroom_area || 40,
                metrics.kitchen_area || 15,
                metrics.bathroom_area || 10,
                metrics.circulation_area || 5
            ];
            this.chart.update();
        }
    }

    initialize3DView() {
        try {
            const canvas = document.getElementById('3d-canvas');
            if (!canvas) return;
            
            this.scene = new THREE.Scene();
            this.camera = new THREE.PerspectiveCamera(75, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
            this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
            
            this.renderer.setSize(canvas.clientWidth, canvas.clientHeight);
            this.renderer.setClearColor(0xf0f0f0);
            
            // Add lights
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            this.scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(10, 20, 5);
            this.scene.add(directionalLight);
            
            // Camera position
            this.camera.position.set(15, 20, 15);
            this.camera.lookAt(0, 0, 0);
            
            // Add grid helper
            const gridHelper = new THREE.GridHelper(50, 50);
            this.scene.add(gridHelper);
            
            // Initial render
            this.animate3D();
        } catch (e) {
            console.log("3D view initialization failed:", e);
        }
    }

    update3DView(floors) {
        if (!this.scene) return;
        
        // Clear existing meshes except lights and helpers
        const objectsToRemove = [];
        this.scene.children.forEach(child => {
            if (child.type === 'Mesh') {
                objectsToRemove.push(child);
            }
        });
        objectsToRemove.forEach(obj => this.scene.remove(obj));
        
        // Create 3D floors
        floors.forEach((floor, floorIndex) => {
            if (floor.rooms && floor.rooms.length > 0) {
                floor.rooms.forEach(room => {
                    try {
                        const geometry = new THREE.BoxGeometry(
                            (room.width || 3) * 3,
                            3, // Height
                            (room.length || 3) * 3
                        );
                        
                        const material = new THREE.MeshPhongMaterial({ 
                            color: this.getRoomColor(room.type),
                            transparent: true,
                            opacity: 0.8
                        });
                        
                        const cube = new THREE.Mesh(geometry, material);
                        cube.position.set(
                            (room.x || 1) * 3 - (floor.width || 12) * 1.5,
                            floorIndex * 4,
                            (room.y || 1) * 3 - (floor.length || 10) * 1.5
                        );
                        
                        this.scene.add(cube);
                    } catch (e) {
                        console.log("Error creating 3D room:", e);
                    }
                });
            }
        });
    }

    animate3D() {
        if (this.renderer && this.scene && this.camera) {
            requestAnimationFrame(() => this.animate3D());
            this.renderer.render(this.scene, this.camera);
        }
    }

    async exportAsPNG() {
        if (!this.floorPlanData) {
            alert('Please generate a floor plan first');
            return;
        }

        try {
            const response = await fetch('http://localhost:5000/export/png', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.floorPlanData)
            });

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `floorplan_${Date.now()}.png`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } catch (error) {
            console.error('Error exporting PNG:', error);
            alert('PNG export not implemented yet');
        }
    }

    async exportAsPDF() {
        if (!this.floorPlanData) {
            alert('Please generate a floor plan first');
            return;
        }

        try {
            const response = await fetch('http://localhost:5000/export/pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.floorPlanData)
            });

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `floorplan_${Date.now()}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } catch (error) {
            console.error('Error exporting PDF:', error);
            alert('PDF export not implemented yet');
        }
    }

    // Debugging functions
    addTestButton() {
        const testBtn = document.createElement('button');
        testBtn.textContent = 'Test Render';
        testBtn.style.position = 'fixed';
        testBtn.style.bottom = '10px';
        testBtn.style.right = '10px';
        testBtn.style.zIndex = '1000';
        testBtn.style.padding = '10px';
        testBtn.style.background = '#3498db';
        testBtn.style.color = 'white';
        testBtn.style.border = 'none';
        testBtn.style.borderRadius = '5px';
        testBtn.style.cursor = 'pointer';
        
        testBtn.addEventListener('click', () => {
            this.testRendering();
        });
        
        document.body.appendChild(testBtn);
    }

    testRendering() {
        console.log("Running test rendering...");
        
        // Create test data that matches backend structure
        const testData = {
            success: true,
            floors: [
                {
                    floor_number: 1,
                    width: 12,
                    length: 10,
                    rooms: [
                        {
                            type: "bedroom",
                            x: 1,
                            y: 1,
                            width: 4,
                            length: 3,
                            area: 12
                        },
                        {
                            type: "living",
                            x: 6,
                            y: 1,
                            width: 5,
                            length: 4,
                            area: 20
                        },
                        {
                            type: "kitchen",
                            x: 1,
                            y: 5,
                            width: 4,
                            length: 3,
                            area: 12
                        },
                        {
                            type: "bathroom",
                            x: 6,
                            y: 6,
                            width: 3,
                            length: 3,
                            area: 9
                        }
                    ],
                    walls: [
                        { x1: 1, y1: 1, x2: 5, y2: 1 },
                        { x1: 5, y1: 1, x2: 5, y2: 4 },
                        { x1: 5, y1: 4, x2: 1, y2: 4 },
                        { x1: 1, y1: 4, x2: 1, y2: 1 },
                        { x1: 6, y1: 1, x2: 11, y2: 1 },
                        { x1: 11, y1: 1, x2: 11, y2: 5 },
                        { x1: 11, y1: 5, x2: 6, y2: 5 },
                        { x1: 6, y1: 5, x2: 6, y2: 1 }
                    ],
                    windows: [
                        { x1: 2, y1: 1, x2: 4, y2: 1 },
                        { x1: 7, y1: 1, x2: 10, y2: 1 }
                    ],
                    doors: [
                        { x: 5, y: 2 },
                        { x: 6, y: 3 }
                    ],
                    metrics: {
                        total_area: 53,
                        room_count: 4,
                        efficiency: 85.5,
                        circulation_area: 8
                    }
                }
            ],
            metrics: {
                total_area: 53,
                total_rooms: 4,
                floors: 1,
                average_efficiency: 85.5
            }
        };
        
        this.floorPlanData = testData;
        this.totalFloors = 1;
        this.currentFloor = 1;
        this.renderFloorPlan();
        
        // Update analysis
        this.updateAnalysis(testData.metrics);
        
        console.log("Test rendering complete! You should see a floor plan now.");
        alert("Test rendering complete! Check the floor plan area.");
    }
}

// Initialize when page loads
window.addEventListener('DOMContentLoaded', () => {
    console.log("DOM loaded, initializing FloorPlanGenerator...");
    window.floorPlanGenerator = new FloorPlanGenerator();
    
    // Show initial message
    const svgContainer = document.getElementById('svg-container');
    if (svgContainer) {
        svgContainer.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 20px; text-align: center; color: #666;">
                <div style="font-size: 64px; margin-bottom: 20px;">🏠</div>
                <div style="font-size: 24px; margin-bottom: 10px; font-weight: bold;">AI Floor Plan Generator</div>
                <div style="font-size: 16px; margin-bottom: 20px;">Configure your building settings and click "Generate Floor Plan"</div>
                <div style="display: flex; gap: 10px; margin-top: 20px;">
                    <div style="width: 15px; height: 15px; background: #3498db; border-radius: 3px;"></div>
                    <span style="font-size: 14px;">Bedroom</span>
                    <div style="width: 15px; height: 15px; background: #2ecc71; border-radius: 3px; margin-left: 15px;"></div>
                    <span style="font-size: 14px;">Living Room</span>
                </div>
            </div>
        `;
    }
});
