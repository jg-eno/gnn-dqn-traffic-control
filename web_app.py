"""
Flask web application for visual traffic light simulator.
"""

import json
import time
import threading
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from simulation import TrafficSimulation, SimulationConfig
from vehicle import Lane
from traffic_light import SignalPhase


class WebTrafficSimulator:
    """Web-based traffic simulator with real-time updates."""
    
    def __init__(self):
        self.app = Flask(__name__, static_folder='static')
        self.app.config['SECRET_KEY'] = 'traffic_simulator_secret'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Initialize simulation
        self.config = SimulationConfig(
            num_intersections=4,
            cycle_length=60,
            vehicle_spawn_rate=0.3,
            special_vehicle_probability=0.05,
            simulation_speed=1.0
        )
        self.simulation = TrafficSimulation(self.config)
        self.is_running = False
        
        self._setup_routes()
        self._setup_socket_events()
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/static/images/<filename>')
        def serve_image(filename):
            return self.app.send_static_file(f'images/{filename}')
        
        @self.app.route('/api/status')
        def get_status():
            """Get current simulation status."""
            if not self.simulation:
                return jsonify({'error': 'Simulation not initialized'})
            
            intersections_data = self.simulation.get_all_intersections_data()
            metrics = self.simulation.get_simulation_metrics()
            
            return jsonify({
                'intersections': intersections_data,
                'metrics': metrics,
                'is_running': self.simulation.is_running
            })
        
        @self.app.route('/api/start', methods=['POST'])
        def start_simulation():
            """Start the simulation."""
            if not self.simulation.is_running:
                self.simulation.start()
                self.is_running = True
                return jsonify({'status': 'started'})
            return jsonify({'status': 'already_running'})
        
        @self.app.route('/api/stop', methods=['POST'])
        def stop_simulation():
            """Stop the simulation."""
            if self.simulation.is_running:
                self.simulation.stop()
                self.is_running = False
                return jsonify({'status': 'stopped'})
            return jsonify({'status': 'already_stopped'})
        
        @self.app.route('/api/reset', methods=['POST'])
        def reset_simulation():
            """Reset the simulation."""
            self.simulation.reset()
            self.is_running = False
            return jsonify({'status': 'reset'})
        
        @self.app.route('/api/add_special_vehicle', methods=['POST'])
        def add_special_vehicle():
            """Add a special vehicle."""
            data = request.get_json()
            intersection_id = data.get('intersection_id')
            lane = data.get('lane')
            
            if not intersection_id or not lane:
                return jsonify({'error': 'Missing intersection_id or lane'})
            
            try:
                lane_enum = Lane(lane)
                success = self.simulation.add_special_vehicle(intersection_id, lane_enum)
                return jsonify({'success': success})
            except ValueError:
                return jsonify({'error': 'Invalid lane'})
    
    def _setup_socket_events(self):
        """Setup SocketIO events."""
        
        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')
            emit('status', {'message': 'Connected to traffic simulator'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected')
        
        @self.socketio.on('request_update')
        def handle_update_request():
            """Handle real-time update requests."""
            if self.simulation and self.simulation.is_running:
                intersections_data = self.simulation.get_all_intersections_data()
                metrics = self.simulation.get_simulation_metrics()
                
                emit('simulation_update', {
                    'intersections': intersections_data,
                    'metrics': metrics,
                    'timestamp': time.time()
                })
        
        @self.socketio.on('manual_override')
        def handle_manual_override(data):
            """Handle manual signal override."""
            try:
                intersection_id = data.get('intersection_id')
                direction = data.get('direction')
                signal = data.get('signal')
                
                if intersection_id and direction and signal:
                    # Set manual override for the specific signal direction
                    self.simulation.set_manual_override(intersection_id, direction, signal)
                    emit('override_set', {
                        'intersection_id': intersection_id,
                        'direction': direction,
                        'signal': signal
                    })
            except Exception as e:
                print(f"Error setting manual override: {e}")
        
        @self.socketio.on('set_auto_mode')
        def handle_set_auto_mode(data):
            """Handle setting auto mode."""
            try:
                intersection_id = data.get('intersection_id')
                direction = data.get('direction')
                
                if intersection_id and direction:
                    # Set auto mode for the specific signal direction
                    self.simulation.set_auto_mode(intersection_id, direction)
                    emit('auto_mode_set', {
                        'intersection_id': intersection_id,
                        'direction': direction
                    })
            except Exception as e:
                print(f"Error setting auto mode: {e}")
    
    def _broadcast_updates(self):
        """Broadcast simulation updates to all connected clients."""
        while True:
            if self.is_running and self.simulation.is_running:
                intersections_data = self.simulation.get_all_intersections_data()
                metrics = self.simulation.get_simulation_metrics()
                
                self.socketio.emit('simulation_update', {
                    'intersections': intersections_data,
                    'metrics': metrics,
                    'timestamp': time.time()
                })
            
            time.sleep(1)  # Update every second
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the web application."""
        # Start background thread for broadcasting updates
        update_thread = threading.Thread(target=self._broadcast_updates, daemon=True)
        update_thread.start()
        
        print(f"Starting Traffic Light Simulator Web App...")
        print(f"Open your browser to: http://{host}:{port}")
        
        self.socketio.run(self.app, host=host, port=port, debug=debug)


def main():
    """Main function to run the web app."""
    simulator = WebTrafficSimulator()
    simulator.run(debug=True)


if __name__ == "__main__":
    main()
