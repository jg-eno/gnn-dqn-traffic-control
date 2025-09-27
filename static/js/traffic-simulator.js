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
        this.draw();
    }
    
    setupCanvas() {
        this.updateCanvasSize();
    }
    
    updateCanvasSize() {
        const container = this.canvas.parentElement;
        const containerWidth = container.clientWidth - 40; // Account for padding
        const containerHeight = Math.min(800, window.innerHeight - 200);
        
        // Calculate scale based on container width
        this.scale = Math.min(containerWidth / this.baseWidth, containerHeight / this.baseHeight, 1);
        
        // Set canvas size
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
        
        // Update UI metrics
        this.updateMetrics();
        this.updateIntersectionStatus();
        
        // Update vehicles based on intersection data
        this.updateVehicles();
    }
    
    updateMetrics() {
        document.getElementById('simTime').textContent = `${this.metrics.simulation_time?.toFixed(1) || 0}s`;
        document.getElementById('vehiclesPassed').textContent = this.metrics.total_vehicles_passed || 0;
        document.getElementById('throughput').textContent = `${(this.metrics.throughput || 0).toFixed(2)} veh/s`;
        document.getElementById('avgWaitTime').textContent = `${(this.metrics.average_wait_time || 0).toFixed(1)}s`;
    }
    
    updateIntersectionStatus() {
        const container = document.getElementById('intersectionList');
        container.innerHTML = '';
        
        this.intersections.forEach(intersection => {
            if (!intersection) return;
            
            const item = document.createElement('div');
            item.className = `intersection-item ${intersection.is_override_active ? 'override' : ''}`;
            
            const phase = intersection.current_phase.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            const queues = Object.entries(intersection.queue_lengths)
                .filter(([_, count]) => count > 0)
                .map(([lane, count]) => `${lane}: ${count}`)
                .join(', ');
            
            item.innerHTML = `
                <div class="intersection-title">${intersection.id.replace('_', ' ').toUpperCase()}</div>
                <div class="intersection-phase">${phase} ${intersection.is_override_active ? '🚨 OVERRIDE' : ''}</div>
                <div class="intersection-queues">${queues || 'No queues'}</div>
            `;
            
            container.appendChild(item);
        });
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
                    this.vehicles.push({
                        x: this.getVehicleX(pos.x, lane, i),
                        y: this.getVehicleY(pos.y, lane, i),
                        lane: lane,
                        intersection: intersection.id,
                        isSpecial: intersection.special_vehicles.some(sv => sv.lane === lane),
                        color: intersection.special_vehicles.some(sv => sv.lane === lane) ? '#ff6b6b' : '#3498db'
                    });
                }
            });
        });
    }
    
    getVehicleX(intersectionX, lane, index) {
        const offset = index * 50 * this.scale;
        const roadOffset = 60 * this.scale;
        switch (lane) {
            case 'north': return intersectionX;
            case 'south': return intersectionX;
            case 'east': return intersectionX + roadOffset + offset;
            case 'west': return intersectionX - roadOffset - offset;
            default: return intersectionX;
        }
    }
    
    getVehicleY(intersectionY, lane, index) {
        const offset = index * 50 * this.scale;
        const roadOffset = 60 * this.scale;
        switch (lane) {
            case 'north': return intersectionY - roadOffset - offset;
            case 'south': return intersectionY + roadOffset + offset;
            case 'east': return intersectionY;
            case 'west': return intersectionY;
            default: return intersectionY;
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
        
        if (this.images.road) {
            // Use custom road image if available
            const roadWidth = 350 * this.scale;
            const roadHeight = 56 * this.scale;
            
            // Horizontal roads
            for (let y of [scaledHeight * 0.25, scaledHeight * 0.75]) {
                this.ctx.drawImage(this.images.road, 50 * this.scale, y - roadHeight/2, scaledWidth - 100 * this.scale, roadHeight);
            }
            
            // Vertical roads
            for (let x of [scaledWidth * 0.25, scaledWidth * 0.75]) {
                this.ctx.save();
                this.ctx.translate(x, scaledHeight * 0.5);
                this.ctx.rotate(Math.PI / 2);
                this.ctx.drawImage(this.images.road, -scaledHeight/2, -roadHeight/2, scaledHeight, roadHeight);
                this.ctx.restore();
            }
        } else {
            // Fallback to drawn roads
            this.ctx.strokeStyle = '#34495e';
            this.ctx.lineWidth = 56 * this.scale;
            this.ctx.lineCap = 'round';
            
            // Horizontal roads
            for (let y of [scaledHeight * 0.25, scaledHeight * 0.75]) {
                this.ctx.beginPath();
                this.ctx.moveTo(50 * this.scale, y);
                this.ctx.lineTo(scaledWidth - 50 * this.scale, y);
                this.ctx.stroke();
            }
            
            // Vertical roads
            for (let x of [scaledWidth * 0.25, scaledWidth * 0.75]) {
                this.ctx.beginPath();
                this.ctx.moveTo(x, 50 * this.scale);
                this.ctx.lineTo(x, scaledHeight - 50 * this.scale);
                this.ctx.stroke();
            }
            
            // Road markings
            this.ctx.strokeStyle = '#ecf0f1';
            this.ctx.lineWidth = 8 * this.scale;
            this.ctx.setLineDash([25 * this.scale, 25 * this.scale]);
            
            for (let y of [scaledHeight * 0.25, scaledHeight * 0.75]) {
                this.ctx.beginPath();
                this.ctx.moveTo(50 * this.scale, y);
                this.ctx.lineTo(scaledWidth - 50 * this.scale, y);
                this.ctx.stroke();
            }
            
            for (let x of [scaledWidth * 0.25, scaledWidth * 0.75]) {
                this.ctx.beginPath();
                this.ctx.moveTo(x, 50 * this.scale);
                this.ctx.lineTo(x, scaledHeight - 50 * this.scale);
                this.ctx.stroke();
            }
            
            this.ctx.setLineDash([]);
        }
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
            
            if (vehicle.isSpecial && this.images.ambulance) {
                // Draw ambulance for special vehicles
                this.ctx.drawImage(this.images.ambulance, -vehicleSize/2, -vehicleSize/2, vehicleSize, vehicleSize);
            } else if (this.images.car) {
                // Draw regular car
                this.ctx.drawImage(this.images.car, -vehicleSize/2, -vehicleSize/2, vehicleSize, vehicleSize);
            } else {
                // Fallback to drawn vehicles
                this.ctx.fillStyle = vehicle.color;
                this.ctx.fillRect(-vehicleSize/2, -vehicleSize/2, vehicleSize, vehicleSize * 0.6);
                
                // Vehicle highlight
                this.ctx.fillStyle = '#ecf0f1';
                this.ctx.fillRect(-vehicleSize/2 + 2, -vehicleSize/2 + 2, vehicleSize - 4, 4);
                
                // Special vehicle indicator
                if (vehicle.isSpecial) {
                    this.ctx.fillStyle = '#f39c12';
                    this.ctx.beginPath();
                    this.ctx.arc(0, -vehicleSize/2 - 5, 3 * this.scale, 0, 2 * Math.PI);
                    this.ctx.fill();
                }
            }
            
            this.ctx.restore();
        });
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
