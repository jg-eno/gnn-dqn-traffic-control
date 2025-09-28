/**
 * Visual Traffic Light Simulator
 * HTML5 Canvas-based traffic simulation with real-time updates and custom images
 */

class VisualTrafficSimulator {
    constructor() {
        this.canvas = document.getElementById('trafficCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.socket = io();
        
        // Simulation state
        this.intersections = [];
        this.vehicles = [];
        this.metrics = {};
        this.isRunning = false;
        
        // Image assets
        this.images = {
            car: null,
            ambulance: null,
            road: null
        };
        
        // Scale factors for responsive design
        this.scale = 1;
        this.baseWidth = 1200;
        this.baseHeight = 800;
        
        this.setupCanvas();
        this.loadImages();
        this.setupEventListeners();
        this.setupSocketEvents();
        this.setupResizeHandler();
        this.setupIntersectionToggles();
        this.draw();
    }
    
    setupCanvas() {
        this.updateCanvasSize();
    }
    
    updateCanvasSize() {
        const container = this.canvas.parentElement;
        const containerWidth = container.clientWidth - 40; // Account for padding
        const containerHeight = Math.min(window.innerHeight - 200, 800); // Much more height, account for controllers
        
        // Use more of the available space, especially vertically
        const targetWidth = Math.min(containerWidth, 1200);
        const targetHeight = Math.min(containerHeight, 800);
        
        // Calculate scale to fit the available space, prioritizing vertical scaling
        this.scale = Math.min(targetWidth / this.baseWidth, targetHeight / this.baseHeight);
        
        // Set canvas size to use more space
        this.canvas.width = this.baseWidth * this.scale;
        this.canvas.height = this.baseHeight * this.scale;
        
        // Update canvas style for crisp rendering
        this.canvas.style.width = this.canvas.width + 'px';
        this.canvas.style.height = this.canvas.height + 'px';
        
        // Scale the context for high DPI displays
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = this.canvas.width * dpr;
        this.canvas.height = this.canvas.height * dpr;
        this.ctx.scale(dpr, dpr);
        
        // Recalculate intersection positions based on scale
        this.updateIntersectionPositions();
    }
    
    updateIntersectionPositions() {
        const scaledWidth = this.baseWidth * this.scale;
        const scaledHeight = this.baseHeight * this.scale;
        
        // 2x2 grid layout for 4 intersections
        this.intersectionPositions = [
            { x: scaledWidth * 0.25, y: scaledHeight * 0.25, id: 'intersection_1' },
            { x: scaledWidth * 0.75, y: scaledHeight * 0.25, id: 'intersection_2' },
            { x: scaledWidth * 0.25, y: scaledHeight * 0.75, id: 'intersection_3' },
            { x: scaledWidth * 0.75, y: scaledHeight * 0.75, id: 'intersection_4' }
        ];
    }
    
    loadImages() {
        const imagePromises = [
            this.loadImage('/static/images/Car.png'),
            this.loadImage('/static/images/Ambulance.png'),
            this.loadImage('/static/images/Road.png')
        ];
        
        Promise.all(imagePromises).then(([car, ambulance, road]) => {
            this.images.car = car;
            this.images.ambulance = ambulance;
            this.images.road = road;
            console.log('All images loaded successfully');
        }).catch(error => {
            console.warn('Some images failed to load, using fallback graphics:', error);
        });
    }
    
    loadImage(src) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = () => reject(new Error(`Failed to load image: ${src}`));
            img.src = src;
        });
    }
    
    setupResizeHandler() {
        window.addEventListener('resize', () => {
            this.updateCanvasSize();
        });
    }
    
    setupEventListeners() {
        // Control buttons
        document.getElementById('startBtn').addEventListener('click', () => this.startSimulation());
        document.getElementById('stopBtn').addEventListener('click', () => this.stopSimulation());
        document.getElementById('resetBtn').addEventListener('click', () => this.resetSimulation());
        document.getElementById('addSpecialBtn').addEventListener('click', () => this.showSpecialVehicleModal());
        
        // Special vehicle modal
        document.getElementById('confirmSpecialBtn').addEventListener('click', () => this.addSpecialVehicle());
        document.getElementById('cancelSpecialBtn').addEventListener('click', () => this.hideSpecialVehicleModal());
    }
    
    setupSocketEvents() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
        });
        
        this.socket.on('simulation_update', (data) => {
            this.updateSimulation(data);
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
        });
    }
    
    async startSimulation() {
        try {
            const response = await fetch('/api/start', { method: 'POST' });
            const result = await response.json();
            
            if (result.status === 'started') {
                this.isRunning = true;
                this.updateButtonStates();
                this.startAnimation();
            }
        } catch (error) {
            console.error('Error starting simulation:', error);
        }
    }
    
    async stopSimulation() {
        try {
            const response = await fetch('/api/stop', { method: 'POST' });
            const result = await response.json();
            
            if (result.status === 'stopped') {
                this.isRunning = false;
                this.updateButtonStates();
            }
        } catch (error) {
            console.error('Error stopping simulation:', error);
        }
    }
    
    async resetSimulation() {
        try {
            const response = await fetch('/api/reset', { method: 'POST' });
            const result = await response.json();
            
            if (result.status === 'reset') {
                this.isRunning = false;
                this.intersections = [];
                this.vehicles = [];
                this.updateButtonStates();
                this.draw();
            }
        } catch (error) {
            console.error('Error resetting simulation:', error);
        }
    }
    
    showSpecialVehicleModal() {
        document.getElementById('specialModal').style.display = 'flex';
    }
    
    hideSpecialVehicleModal() {
        document.getElementById('specialModal').style.display = 'none';
    }
    
    async addSpecialVehicle() {
        const intersectionId = document.getElementById('intersectionSelect').value;
        const lane = document.getElementById('laneSelect').value;
        
        try {
            const response = await fetch('/api/add_special_vehicle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    intersection_id: intersectionId,
                    lane: lane
                })
            });
            
            const result = await response.json();
            if (result.success) {
                this.hideSpecialVehicleModal();
                console.log('Special vehicle added successfully');
            }
        } catch (error) {
            console.error('Error adding special vehicle:', error);
        }
    }
    
    updateButtonStates() {
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        
        startBtn.disabled = this.isRunning;
        stopBtn.disabled = !this.isRunning;
    }
    
    updateSimulation(data) {
        this.intersections = data.intersections || [];
        this.metrics = data.metrics || {};
        
        // Update signal controllers
        this.updateSignalControllers();
        
        // Update vehicles based on intersection data
        this.updateVehicles();
    }
    
    setupIntersectionToggles() {
        // Set up toggle button event listeners
        const toggleButtons = document.querySelectorAll('.toggle-btn');
        toggleButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const intersectionId = e.target.getAttribute('data-intersection');
                this.switchToIntersection(intersectionId);
            });
        });
        
        // Initialize with intersection 1
        this.currentIntersection = 'intersection_1';
        this.updateActiveController();
    }
    
    switchToIntersection(intersectionId) {
        // Update active button
        document.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-intersection="${intersectionId}"]`).classList.add('active');
        
        // Update current intersection
        this.currentIntersection = intersectionId;
        this.updateActiveController();
    }
    
    updateActiveController() {
        const activeController = document.getElementById('active-controller');
        if (!activeController) return;
        
        // Find the intersection data
        const intersection = this.intersections.find(i => i.id === this.currentIntersection);
        if (!intersection) {
            activeController.innerHTML = '<p>No intersection data available</p>';
            return;
        }
        
        // Create and display the controller
        const controller = this.createSignalController(intersection);
        activeController.innerHTML = '';
        activeController.appendChild(controller);
    }
    
    updateSignalControllers() {
        // Update the active controller if it exists
        if (this.currentIntersection) {
            this.updateActiveController();
        }
    }
    
    createSignalController(intersection) {
        const intersectionName = intersection.id.replace('_', ' ').toUpperCase();
        
        // Create a container for all 4 signal controllers for this intersection
        const intersectionContainer = document.createElement('div');
        intersectionContainer.className = 'intersection-controller-group';
        intersectionContainer.id = `intersection-group-${intersection.id}`;
        intersectionContainer.setAttribute('data-intersection', intersection.id);
        
        // Create header for the intersection
        const header = document.createElement('div');
        header.className = 'intersection-header';
        header.innerHTML = `
            <h4>${intersectionName}</h4>
            <div class="intersection-metrics">
                <span class="metric-label">Total Vehicles: </span>
                <span class="metric-value">${Object.values(intersection.queue_lengths).reduce((sum, count) => sum + count, 0)}</span>
            </div>
        `;
        intersectionContainer.appendChild(header);
        
        // Create individual controllers for each direction
        const directions = [
            { name: 'North', key: 'north', icon: '⬆️' },
            { name: 'South', key: 'south', icon: '⬇️' },
            { name: 'East', key: 'east', icon: '➡️' },
            { name: 'West', key: 'west', icon: '⬅️' }
        ];
        
        // Create a container for signal controllers
        const controllersContainer = document.createElement('div');
        controllersContainer.className = 'signal-controllers-container';
        
        directions.forEach(direction => {
            const controller = this.createIndividualSignalController(intersection, direction);
            controllersContainer.appendChild(controller);
        });
        
        intersectionContainer.appendChild(controllersContainer);
        
        return intersectionContainer;
    }
    
    createIndividualSignalController(intersection, direction) {
        const controller = document.createElement('div');
        controller.className = 'signal-controller';
        controller.id = `controller-${intersection.id}-${direction.key}`;
        
        const currentSignal = intersection.signal_colors[direction.key];
        const vehicleCount = intersection.queue_lengths[direction.key] || 0;
        const avgSpeed = this.calculateAverageSpeed(intersection);
        
        controller.innerHTML = `
            <div class="signal-header">
                <span class="signal-direction">${direction.icon} ${direction.name}</span>
                <span class="signal-status ${currentSignal}">●</span>
            </div>
            
            <div class="controller-metrics">
                <div class="metric-item">
                    <span class="metric-label">Vehicles</span>
                    <span class="metric-value" id="vehicles-${intersection.id}-${direction.key}">${vehicleCount}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Speed</span>
                    <span class="metric-value" id="speed-${intersection.id}-${direction.key}">${avgSpeed.toFixed(1)} km/h</span>
                </div>
            </div>
            
            <div class="controller-controls">
                <button class="controller-btn btn-red" data-intersection="${intersection.id}" data-direction="${direction.key}" data-signal="red">🔴</button>
                <button class="controller-btn btn-yellow" data-intersection="${intersection.id}" data-direction="${direction.key}" data-signal="yellow">🟡</button>
                <button class="controller-btn btn-green" data-intersection="${intersection.id}" data-direction="${direction.key}" data-signal="green">🟢</button>
                <button class="controller-btn btn-auto ${intersection.is_override_active ? '' : 'active'}" data-intersection="${intersection.id}" data-direction="${direction.key}" data-signal="auto">⚙️</button>
            </div>
            
            <div class="${intersection.is_override_active ? 'override-mode' : 'auto-mode'}" id="mode-${intersection.id}-${direction.key}">
                ${intersection.is_override_active ? 'MANUAL' : 'AUTO'}
            </div>
        `;
        
        // Add event listeners for manual control
        this.addControllerEventListeners(controller, intersection.id, direction.key);
        
        return controller;
    }
    
    addControllerEventListeners(controller, intersectionId, direction) {
        const buttons = controller.querySelectorAll('.controller-btn');
        const modeIndicator = controller.querySelector(`#mode-${intersectionId}-${direction}`);
        
        buttons.forEach(button => {
            button.addEventListener('click', () => {
                const signal = button.dataset.signal;
                
                if (signal === 'auto') {
                    // Switch to auto mode
                    this.switchToAutoMode(intersectionId, direction);
                } else {
                    // Manual override
                    this.manualSignalOverride(intersectionId, direction, signal);
                }
                
                // Update button states
                buttons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
            });
        });
    }
    
    switchToAutoMode(intersectionId, direction) {
        const modeIndicator = document.querySelector(`#mode-${intersectionId}-${direction}`);
        modeIndicator.textContent = 'AUTO';
        modeIndicator.className = 'auto-mode';
        
        // Send auto mode command to backend
        this.socket.emit('set_auto_mode', { 
            intersection_id: intersectionId,
            direction: direction 
        });
    }
    
    manualSignalOverride(intersectionId, direction, signal) {
        const modeIndicator = document.querySelector(`#mode-${intersectionId}-${direction}`);
        modeIndicator.textContent = 'MANUAL';
        modeIndicator.className = 'override-mode';
        
        // Send manual override command to backend
        this.socket.emit('manual_override', { 
            intersection_id: intersectionId, 
            direction: direction,
            signal: signal 
        });
    }
    
    calculateAverageSpeed(intersection) {
        // Calculate average speed based on queue lengths and signal states
        const totalVehicles = Object.values(intersection.queue_lengths).reduce((sum, count) => sum + count, 0);
        
        if (totalVehicles === 0) return 0;
        
        // Base speed calculation (simplified)
        const baseSpeed = 30; // km/h
        const queueFactor = Math.max(0.1, 1 - (totalVehicles / 20)); // Reduce speed with more vehicles
        
        return baseSpeed * queueFactor;
    }
    
    updateVehicles() {
        // Clear existing vehicles
        this.vehicles = [];
        
        // Create vehicles based on intersection queue data
        this.intersections.forEach(intersection => {
            if (!intersection) return;
            
            const pos = this.intersectionPositions.find(p => p.id === intersection.id);
            if (!pos) return;
            
            // Add vehicles for each lane with queues
            Object.entries(intersection.queue_lengths).forEach(([lane, count]) => {
                for (let i = 0; i < count; i++) {
                    let vehicleX = this.getVehicleX(pos.x, lane, i);
                    let vehicleY = this.getVehicleY(pos.y, lane, i);
                    
                    // Ensure vehicle is on a road
                    if (!this.isVehicleOnRoad(vehicleX, vehicleY)) {
                        // If not on road, move to nearest road position
                        const roadPos = this.getNearestRoadPosition(vehicleX, vehicleY, lane);
                        vehicleX = roadPos.x;
                        vehicleY = roadPos.y;
                    }
                    
                    this.vehicles.push({
                        x: vehicleX,
                        y: vehicleY,
                        lane: lane,
                        intersection: intersection.id,
                        isSpecial: intersection.special_vehicles.some(sv => sv.lane === lane),
                        color: intersection.special_vehicles.some(sv => sv.lane === lane) ? '#ff6b6b' : '#3498db'
                    });
                }
            });
        });
    }
    
    isVehicleOnRoad(x, y) {
        const roadWidth = 56 * this.scale;
        const roadHalfWidth = roadWidth / 2;
        const scaledWidth = this.baseWidth * this.scale;
        const scaledHeight = this.baseHeight * this.scale;
        
        // Check if vehicle is on horizontal roads (y positions)
        const horizontalRoadY1 = scaledHeight * 0.25;
        const horizontalRoadY2 = scaledHeight * 0.75;
        
        if ((Math.abs(y - horizontalRoadY1) <= roadHalfWidth || Math.abs(y - horizontalRoadY2) <= roadHalfWidth) &&
            x >= 50 * this.scale && x <= scaledWidth - 50 * this.scale) {
            return true;
        }
        
        // Check if vehicle is on vertical roads (x positions)
        const verticalRoadX1 = scaledWidth * 0.25;
        const verticalRoadX2 = scaledWidth * 0.75;
        
        if ((Math.abs(x - verticalRoadX1) <= roadHalfWidth || Math.abs(x - verticalRoadX2) <= roadHalfWidth) &&
            y >= 50 * this.scale && y <= scaledHeight - 50 * this.scale) {
            return true;
        }
        
        return false;
    }
    
    getNearestRoadPosition(x, y, lane) {
        const roadWidth = 56 * this.scale;
        const roadHalfWidth = roadWidth / 2;
        const scaledWidth = this.baseWidth * this.scale;
        const scaledHeight = this.baseHeight * this.scale;
        const leftLaneOffset = 14 * this.scale;
        
        // Determine which road the vehicle should be on based on lane
        switch (lane) {
            case 'north':
            case 'south':
                // Vertical roads
                const verticalRoadX1 = scaledWidth * 0.25;
                const verticalRoadX2 = scaledWidth * 0.75;
                const nearestVerticalX = Math.abs(x - verticalRoadX1) < Math.abs(x - verticalRoadX2) ? verticalRoadX1 : verticalRoadX2;
                return {
                    x: nearestVerticalX + (lane === 'south' ? leftLaneOffset : -leftLaneOffset),
                    y: Math.max(50 * this.scale + roadHalfWidth, Math.min(y, scaledHeight - 50 * this.scale - roadHalfWidth))
                };
            case 'east':
            case 'west':
                // Horizontal roads
                const horizontalRoadY1 = scaledHeight * 0.25;
                const horizontalRoadY2 = scaledHeight * 0.75;
                const nearestHorizontalY = Math.abs(y - horizontalRoadY1) < Math.abs(y - horizontalRoadY2) ? horizontalRoadY1 : horizontalRoadY2;
                return {
                    x: Math.max(50 * this.scale + roadHalfWidth, Math.min(x, scaledWidth - 50 * this.scale - roadHalfWidth)),
                    y: nearestHorizontalY + (lane === 'west' ? leftLaneOffset : -leftLaneOffset)
                };
            default:
                return { x: x, y: y };
        }
    }
    
    getVehicleX(intersectionX, lane, index) {
        const offset = index * 50 * this.scale;
        const roadOffset = 60 * this.scale;
        const leftLaneOffset = 14 * this.scale; // Offset to align with left lane
        const roadWidth = 56 * this.scale;
        const roadHalfWidth = roadWidth / 2;
        
        let x;
        switch (lane) {
            case 'north': 
                x = intersectionX - leftLaneOffset;
                // Constrain to road boundaries
                return Math.max(50 * this.scale + roadHalfWidth, Math.min(x, this.baseWidth * this.scale - 50 * this.scale - roadHalfWidth));
            case 'south': 
                x = intersectionX + leftLaneOffset;
                return Math.max(50 * this.scale + roadHalfWidth, Math.min(x, this.baseWidth * this.scale - 50 * this.scale - roadHalfWidth));
            case 'east': 
                x = intersectionX + roadOffset + offset;
                return Math.max(50 * this.scale + roadHalfWidth, Math.min(x, this.baseWidth * this.scale - 50 * this.scale - roadHalfWidth));
            case 'west': 
                x = intersectionX - roadOffset - offset;
                return Math.max(50 * this.scale + roadHalfWidth, Math.min(x, this.baseWidth * this.scale - 50 * this.scale - roadHalfWidth));
            default: 
                return Math.max(50 * this.scale + roadHalfWidth, Math.min(intersectionX, this.baseWidth * this.scale - 50 * this.scale - roadHalfWidth));
        }
    }
    
    getVehicleY(intersectionY, lane, index) {
        const offset = index * 50 * this.scale;
        const roadOffset = 60 * this.scale;
        const leftLaneOffset = 14 * this.scale; // Offset to align with left lane
        const roadWidth = 56 * this.scale;
        const roadHalfWidth = roadWidth / 2;
        
        let y;
        switch (lane) {
            case 'north': 
                y = intersectionY - roadOffset - offset;
                // Constrain to road boundaries
                return Math.max(50 * this.scale + roadHalfWidth, Math.min(y, this.baseHeight * this.scale - 50 * this.scale - roadHalfWidth));
            case 'south': 
                y = intersectionY + roadOffset + offset;
                return Math.max(50 * this.scale + roadHalfWidth, Math.min(y, this.baseHeight * this.scale - 50 * this.scale - roadHalfWidth));
            case 'east': 
                y = intersectionY - leftLaneOffset;
                return Math.max(50 * this.scale + roadHalfWidth, Math.min(y, this.baseHeight * this.scale - 50 * this.scale - roadHalfWidth));
            case 'west': 
                y = intersectionY + leftLaneOffset;
                return Math.max(50 * this.scale + roadHalfWidth, Math.min(y, this.baseHeight * this.scale - 50 * this.scale - roadHalfWidth));
            default: 
                return Math.max(50 * this.scale + roadHalfWidth, Math.min(intersectionY, this.baseHeight * this.scale - 50 * this.scale - roadHalfWidth));
        }
    }
    
    draw() {
        // Clear canvas
        this.ctx.fillStyle = '#2c3e50';
        this.ctx.fillRect(0, 0, this.baseWidth * this.scale, this.baseHeight * this.scale);
        
        // Draw roads
        this.drawRoads();
        
        // Draw intersections
        this.drawIntersections();
        
        // Draw vehicles
        this.drawVehicles();
        
        // Draw traffic lights
        this.drawTrafficLights();
        
        // Request next frame
        requestAnimationFrame(() => this.draw());
    }
    
    drawRoads() {
        const scaledWidth = this.baseWidth * this.scale;
        const scaledHeight = this.baseHeight * this.scale;
        const roadWidth = 56 * this.scale;
        
        // Draw professional roads with black asphalt and yellow markings
        this.drawProfessionalRoad(scaledWidth * 0.25, 50 * this.scale, scaledHeight - 100 * this.scale, roadWidth, 'vertical');
        this.drawProfessionalRoad(scaledWidth * 0.75, 50 * this.scale, scaledHeight - 100 * this.scale, roadWidth, 'vertical');
        this.drawProfessionalRoad(50 * this.scale, scaledHeight * 0.25, scaledWidth - 100 * this.scale, roadWidth, 'horizontal');
        this.drawProfessionalRoad(50 * this.scale, scaledHeight * 0.75, scaledWidth - 100 * this.scale, roadWidth, 'horizontal');
    }
    
    drawProfessionalRoad(x, y, length, width, direction) {
        this.ctx.save();
        
        if (direction === 'vertical') {
            // Draw black asphalt road
            this.ctx.fillStyle = '#2c2c2c';
            this.ctx.fillRect(x - width/2, y, width, length);
            
            // Draw road edges (darker lines)
            this.ctx.strokeStyle = '#1a1a1a';
            this.ctx.lineWidth = 2 * this.scale;
            this.ctx.beginPath();
            this.ctx.moveTo(x - width/2, y);
            this.ctx.lineTo(x - width/2, y + length);
            this.ctx.moveTo(x + width/2, y);
            this.ctx.lineTo(x + width/2, y + length);
            this.ctx.stroke();
            
            // Draw yellow center line
            this.ctx.strokeStyle = '#ffd700';
            this.ctx.lineWidth = 4 * this.scale;
            this.ctx.setLineDash([20 * this.scale, 15 * this.scale]);
            this.ctx.beginPath();
            this.ctx.moveTo(x, y);
            this.ctx.lineTo(x, y + length);
            this.ctx.stroke();
            
            // Draw white lane dividers
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 2 * this.scale;
            this.ctx.setLineDash([15 * this.scale, 10 * this.scale]);
            
            // Left lane divider
            this.ctx.beginPath();
            this.ctx.moveTo(x - width/4, y);
            this.ctx.lineTo(x - width/4, y + length);
            this.ctx.stroke();
            
            // Right lane divider
            this.ctx.beginPath();
            this.ctx.moveTo(x + width/4, y);
            this.ctx.lineTo(x + width/4, y + length);
            this.ctx.stroke();
            
        } else { // horizontal
            // Draw black asphalt road
            this.ctx.fillStyle = '#2c2c2c';
            this.ctx.fillRect(x, y - width/2, length, width);
            
            // Draw road edges (darker lines)
            this.ctx.strokeStyle = '#1a1a1a';
            this.ctx.lineWidth = 2 * this.scale;
            this.ctx.beginPath();
            this.ctx.moveTo(x, y - width/2);
            this.ctx.lineTo(x + length, y - width/2);
            this.ctx.moveTo(x, y + width/2);
            this.ctx.lineTo(x + length, y + width/2);
            this.ctx.stroke();
            
            // Draw yellow center line
            this.ctx.strokeStyle = '#ffd700';
            this.ctx.lineWidth = 4 * this.scale;
            this.ctx.setLineDash([20 * this.scale, 15 * this.scale]);
            this.ctx.beginPath();
            this.ctx.moveTo(x, y);
            this.ctx.lineTo(x + length, y);
            this.ctx.stroke();
            
            // Draw white lane dividers
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 2 * this.scale;
            this.ctx.setLineDash([15 * this.scale, 10 * this.scale]);
            
            // Top lane divider
            this.ctx.beginPath();
            this.ctx.moveTo(x, y - width/4);
            this.ctx.lineTo(x + length, y - width/4);
            this.ctx.stroke();
            
            // Bottom lane divider
            this.ctx.beginPath();
            this.ctx.moveTo(x, y + width/4);
            this.ctx.lineTo(x + length, y + width/4);
            this.ctx.stroke();
        }
        
        this.ctx.setLineDash([]);
        this.ctx.restore();
    }
    
    drawIntersections() {
        this.intersectionPositions.forEach(pos => {
            const intersectionSize = 120 * this.scale;
            
            // Intersection background
            this.ctx.fillStyle = '#34495e';
            this.ctx.fillRect(pos.x - intersectionSize/2, pos.y - intersectionSize/2, intersectionSize, intersectionSize);
            
            // Intersection border
            this.ctx.strokeStyle = '#ecf0f1';
            this.ctx.lineWidth = 2 * this.scale;
            this.ctx.strokeRect(pos.x - intersectionSize/2, pos.y - intersectionSize/2, intersectionSize, intersectionSize);
            
            // Intersection ID label
            this.ctx.fillStyle = '#ecf0f1';
            this.ctx.font = `${12 * this.scale}px Arial`;
            this.ctx.textAlign = 'center';
            this.ctx.fillText(pos.id.replace('intersection_', ''), pos.x, pos.y + 4 * this.scale);
        });
    }
    
    drawVehicles() {
        this.vehicles.forEach(vehicle => {
            const vehicleSize = 32 * this.scale;
            const x = vehicle.x;
            const y = vehicle.y;
            
            this.ctx.save();
            this.ctx.translate(x, y);
            
            // Rotate vehicle based on lane direction
            let rotation = 0;
            switch (vehicle.lane) {
                case 'north': rotation = -Math.PI / 2; break;
                case 'south': rotation = Math.PI / 2; break;
                case 'east': rotation = 0; break;
                case 'west': rotation = Math.PI; break;
            }
            this.ctx.rotate(rotation);
            
            // Draw custom vehicle graphics
            this.drawCustomVehicle(vehicle, vehicleSize);
            
            this.ctx.restore();
        });
    }
    
    drawCustomVehicle(vehicle, size) {
        const width = size;
        const height = size * 0.6;
        
        if (vehicle.isSpecial) {
            // Draw ambulance with custom graphics
            this.drawAmbulance(width, height);
        } else {
            // Draw regular car with custom graphics
            this.drawCar(width, height);
        }
    }
    
    drawCar(width, height) {
        // Car body - rounded rectangle with slightly wider front/back
        const bodyWidth = width;
        const bodyHeight = height;
        const cornerRadius = 6 * this.scale;
        
        // Main car body - solid color (blue)
        this.ctx.fillStyle = '#3498db';
        this.ctx.beginPath();
        this.ctx.roundRect(-bodyWidth/2, -bodyHeight/2, bodyWidth, bodyHeight, cornerRadius);
        this.ctx.fill();
        
        // Car body border
        this.ctx.strokeStyle = '#2c3e50';
        this.ctx.lineWidth = 1 * this.scale;
        this.ctx.stroke();
        
        // Front windshield - dark gray/black rectangle
        const windshieldWidth = bodyWidth * 0.4;
        const windshieldHeight = bodyHeight * 0.25;
        this.ctx.fillStyle = '#2c3e50';
        this.ctx.beginPath();
        this.ctx.roundRect(-windshieldWidth/2, -bodyHeight/2 + 2 * this.scale, windshieldWidth, windshieldHeight, 2 * this.scale);
        this.ctx.fill();
        
        // Rear window - dark gray/black rectangle
        this.ctx.fillStyle = '#2c3e50';
        this.ctx.beginPath();
        this.ctx.roundRect(-windshieldWidth/2, bodyHeight/2 - windshieldHeight - 2 * this.scale, windshieldWidth, windshieldHeight, 2 * this.scale);
        this.ctx.fill();
        
        // Side door lines - thin black lines
        this.ctx.strokeStyle = '#2c3e50';
        this.ctx.lineWidth = 1 * this.scale;
        this.ctx.beginPath();
        this.ctx.moveTo(-bodyWidth/2 + 3 * this.scale, -bodyHeight/2 + 4 * this.scale);
        this.ctx.lineTo(-bodyWidth/2 + 3 * this.scale, bodyHeight/2 - 4 * this.scale);
        this.ctx.moveTo(bodyWidth/2 - 3 * this.scale, -bodyHeight/2 + 4 * this.scale);
        this.ctx.lineTo(bodyWidth/2 - 3 * this.scale, bodyHeight/2 - 4 * this.scale);
        this.ctx.stroke();
        
        // Front lights - small orange/red indicators
        this.ctx.fillStyle = '#f39c12';
        this.ctx.beginPath();
        this.ctx.arc(-bodyWidth/2 + 2 * this.scale, -bodyHeight/2 + 3 * this.scale, 1.5 * this.scale, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.beginPath();
        this.ctx.arc(bodyWidth/2 - 2 * this.scale, -bodyHeight/2 + 3 * this.scale, 1.5 * this.scale, 0, 2 * Math.PI);
        this.ctx.fill();
        
        // Rear lights - small red taillights
        this.ctx.fillStyle = '#e74c3c';
        this.ctx.beginPath();
        this.ctx.arc(-bodyWidth/2 + 2 * this.scale, bodyHeight/2 - 3 * this.scale, 1.5 * this.scale, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.beginPath();
        this.ctx.arc(bodyWidth/2 - 2 * this.scale, bodyHeight/2 - 3 * this.scale, 1.5 * this.scale, 0, 2 * Math.PI);
        this.ctx.fill();
    }
    
    drawAmbulance(width, height) {
        // Ambulance body - rounded rectangle with slightly wider front/back
        const bodyWidth = width;
        const bodyHeight = height;
        const cornerRadius = 6 * this.scale;
        
        // Main ambulance body - solid red color
        this.ctx.fillStyle = '#e74c3c';
        this.ctx.beginPath();
        this.ctx.roundRect(-bodyWidth/2, -bodyHeight/2, bodyWidth, bodyHeight, cornerRadius);
        this.ctx.fill();
        
        // Ambulance body border
        this.ctx.strokeStyle = '#c0392b';
        this.ctx.lineWidth = 1 * this.scale;
        this.ctx.stroke();
        
        // White cross on side - prominent medical symbol
        const crossSize = Math.min(bodyWidth, bodyHeight) * 0.4;
        this.ctx.fillStyle = '#ffffff';
        this.ctx.beginPath();
        this.ctx.roundRect(-crossSize/2, -crossSize/2, crossSize, crossSize, 3 * this.scale);
        this.ctx.fill();
        
        // Red cross in the center
        this.ctx.fillStyle = '#e74c3c';
        this.ctx.beginPath();
        this.ctx.roundRect(-crossSize/6, -crossSize/2, crossSize/3, crossSize, 1 * this.scale);
        this.ctx.fill();
        this.ctx.beginPath();
        this.ctx.roundRect(-crossSize/2, -crossSize/6, crossSize, crossSize/3, 1 * this.scale);
        this.ctx.fill();
        
        // Front windshield - dark gray/black rectangle
        const windshieldWidth = bodyWidth * 0.4;
        const windshieldHeight = bodyHeight * 0.25;
        this.ctx.fillStyle = '#2c3e50';
        this.ctx.beginPath();
        this.ctx.roundRect(-windshieldWidth/2, -bodyHeight/2 + 2 * this.scale, windshieldWidth, windshieldHeight, 2 * this.scale);
        this.ctx.fill();
        
        // Rear window - dark gray/black rectangle
        this.ctx.fillStyle = '#2c3e50';
        this.ctx.beginPath();
        this.ctx.roundRect(-windshieldWidth/2, bodyHeight/2 - windshieldHeight - 2 * this.scale, windshieldWidth, windshieldHeight, 2 * this.scale);
        this.ctx.fill();
        
        // Side door lines - thin black lines
        this.ctx.strokeStyle = '#2c3e50';
        this.ctx.lineWidth = 1 * this.scale;
        this.ctx.beginPath();
        this.ctx.moveTo(-bodyWidth/2 + 3 * this.scale, -bodyHeight/2 + 4 * this.scale);
        this.ctx.lineTo(-bodyWidth/2 + 3 * this.scale, bodyHeight/2 - 4 * this.scale);
        this.ctx.moveTo(bodyWidth/2 - 3 * this.scale, -bodyHeight/2 + 4 * this.scale);
        this.ctx.lineTo(bodyWidth/2 - 3 * this.scale, bodyHeight/2 - 4 * this.scale);
        this.ctx.stroke();
        
        // Emergency lights (flashing effect)
        const time = Date.now() / 200;
        const flash = Math.sin(time) > 0;
        if (flash) {
            this.ctx.fillStyle = '#f1c40f';
            this.ctx.beginPath();
            this.ctx.arc(-bodyWidth/2 + 2 * this.scale, -bodyHeight/2 + 3 * this.scale, 2 * this.scale, 0, 2 * Math.PI);
            this.ctx.fill();
            this.ctx.beginPath();
            this.ctx.arc(bodyWidth/2 - 2 * this.scale, -bodyHeight/2 + 3 * this.scale, 2 * this.scale, 0, 2 * Math.PI);
            this.ctx.fill();
        }
        
        // Rear lights - small red taillights
        this.ctx.fillStyle = '#e74c3c';
        this.ctx.beginPath();
        this.ctx.arc(-bodyWidth/2 + 2 * this.scale, bodyHeight/2 - 3 * this.scale, 1.5 * this.scale, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.beginPath();
        this.ctx.arc(bodyWidth/2 - 2 * this.scale, bodyHeight/2 - 3 * this.scale, 1.5 * this.scale, 0, 2 * Math.PI);
        this.ctx.fill();
    }
    
    drawTrafficLights() {
        this.intersections.forEach(intersection => {
            if (!intersection) return;
            
            const pos = this.intersectionPositions.find(p => p.id === intersection.id);
            if (!pos) return;
            
            const lightDistance = 100 * this.scale;
            const lightSize = 16 * this.scale;
            
            // Draw traffic lights for each direction
            this.drawTrafficLight(pos.x - lightDistance, pos.y - lightDistance/2, intersection.signal_colors.north, 'N');
            this.drawTrafficLight(pos.x + lightDistance/2, pos.y - lightDistance, intersection.signal_colors.east, 'E');
            this.drawTrafficLight(pos.x + lightDistance, pos.y + lightDistance/2, intersection.signal_colors.south, 'S');
            this.drawTrafficLight(pos.x - lightDistance/2, pos.y + lightDistance, intersection.signal_colors.west, 'W');
        });
    }
    
    drawTrafficLight(x, y, color, direction) {
        const poleHeight = 40 * this.scale;
        const lightBoxWidth = 24 * this.scale;
        const lightBoxHeight = 72 * this.scale;
        const lightRadius = 8 * this.scale;
        const lightSpacing = 20 * this.scale;
        
        // Traffic light pole
        this.ctx.strokeStyle = '#2c3e50';
        this.ctx.lineWidth = 4 * this.scale;
        this.ctx.beginPath();
        this.ctx.moveTo(x, y);
        this.ctx.lineTo(x, y + poleHeight);
        this.ctx.stroke();
        
        // Traffic light casing (3D effect)
        const gradient = this.ctx.createLinearGradient(x - lightBoxWidth/2, y - lightBoxHeight/2, x + lightBoxWidth/2, y + lightBoxHeight/2);
        gradient.addColorStop(0, '#4a5568');
        gradient.addColorStop(0.5, '#2d3748');
        gradient.addColorStop(1, '#1a202c');
        
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(x - lightBoxWidth/2, y - lightBoxHeight/2, lightBoxWidth, lightBoxHeight);
        
        // Traffic light border
        this.ctx.strokeStyle = '#1a202c';
        this.ctx.lineWidth = 2 * this.scale;
        this.ctx.strokeRect(x - lightBoxWidth/2, y - lightBoxHeight/2, lightBoxWidth, lightBoxHeight);
        
        // Red light (top)
        const redY = y - lightBoxHeight/2 + lightSpacing;
        this.drawTrafficLightBulb(x, redY, lightRadius, color === 'red' ? '#e53e3e' : '#4a5568', color === 'red');
        
        // Yellow light (middle)
        const yellowY = y;
        this.drawTrafficLightBulb(x, yellowY, lightRadius, color === 'yellow' ? '#d69e2e' : '#4a5568', color === 'yellow');
        
        // Green light (bottom)
        const greenY = y + lightBoxHeight/2 - lightSpacing;
        this.drawTrafficLightBulb(x, greenY, lightRadius, color === 'green' ? '#38a169' : '#4a5568', color === 'green');
        
        // Direction label
        this.ctx.fillStyle = '#ecf0f1';
        this.ctx.font = `${12 * this.scale}px Arial`;
        this.ctx.textAlign = 'center';
        this.ctx.fillText(direction, x, y + poleHeight + 15 * this.scale);
    }
    
    drawTrafficLightBulb(x, y, radius, color, isActive) {
        // Bulb background (darker when off)
        this.ctx.fillStyle = isActive ? color : '#2d3748';
        this.ctx.beginPath();
        this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
        this.ctx.fill();
        
        // Bulb border
        this.ctx.strokeStyle = '#1a202c';
        this.ctx.lineWidth = 1 * this.scale;
        this.ctx.stroke();
        
        // Glow effect for active lights
        if (isActive) {
            const glowGradient = this.ctx.createRadialGradient(x, y, 0, x, y, radius * 1.5);
            glowGradient.addColorStop(0, color + '80');
            glowGradient.addColorStop(0.7, color + '40');
            glowGradient.addColorStop(1, color + '00');
            
            this.ctx.fillStyle = glowGradient;
            this.ctx.beginPath();
            this.ctx.arc(x, y, radius * 1.5, 0, 2 * Math.PI);
            this.ctx.fill();
        }
        
        // Inner highlight
        if (isActive) {
            const highlightGradient = this.ctx.createRadialGradient(x - radius/3, y - radius/3, 0, x - radius/3, y - radius/3, radius/2);
            highlightGradient.addColorStop(0, '#ffffff60');
            highlightGradient.addColorStop(1, '#ffffff00');
            
            this.ctx.fillStyle = highlightGradient;
            this.ctx.beginPath();
            this.ctx.arc(x - radius/3, y - radius/3, radius/2, 0, 2 * Math.PI);
            this.ctx.fill();
        }
    }
    
    getLightColor(signalColor) {
        switch (signalColor) {
            case 'red': return '#e74c3c';
            case 'green': return '#27ae60';
            case 'yellow': return '#f39c12';
            default: return '#95a5a6';
        }
    }
    
    startAnimation() {
        // Animation is handled by the draw() method
        // This method can be used for additional animation logic
    }
}

// Initialize the simulator when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new VisualTrafficSimulator();
});

