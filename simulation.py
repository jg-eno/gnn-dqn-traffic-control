"""
Main simulation engine for the traffic light system.
"""

import time
import random
import threading
from typing import List, Dict, Optional
from dataclasses import dataclass
from vehicle import Vehicle, SpecialVehicle, Lane, VehicleType
from traffic_light import TrafficLight, SignalPhase
from nyc_traffic_data import NYCTrafficDataProcessor
from signal_controller import CentralizedSignalController, SignalState, ControlMode


@dataclass
class SimulationConfig:
    """Configuration for the simulation."""
    num_intersections: int = 4  # Updated to 4 intersections
    cycle_length: int = 60
    vehicle_spawn_rate: float = 0.3  # vehicles per second per intersection (fallback)
    special_vehicle_probability: float = 0.05  # 5% chance of special vehicle
    simulation_speed: float = 1.0  # 1.0 = real time, 2.0 = 2x speed
    max_vehicles_per_intersection: int = 50
    use_real_traffic_data: bool = True  # Use NYC traffic data
    traffic_data_file: str = "V-128.csv"


class TrafficSimulation:
    """Main simulation controller for the traffic light system."""
    
    def __init__(self, config: SimulationConfig = None):
        self.config = config or SimulationConfig()
        self.intersections: List[TrafficLight] = []
        self.vehicle_counter = 0
        self.special_vehicle_counter = 0
        
        # Simulation state
        self.is_running = False
        self.simulation_time = 0.0
        self.start_time = None
        self.last_update_time = None
        
        # Metrics
        self.total_vehicles_spawned = 0
        self.total_vehicles_passed = 0
        self.total_special_vehicles_spawned = 0
        
        # Threading
        self.simulation_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        # NYC Traffic Data Integration
        self.traffic_data_processor = None
        if self.config.use_real_traffic_data:
            try:
                self.traffic_data_processor = NYCTrafficDataProcessor(self.config.traffic_data_file)
                print("✅ NYC Traffic Data integrated successfully")
            except Exception as e:
                print(f"⚠️ Failed to load NYC traffic data: {e}")
                print("🔄 Falling back to synthetic data")
                self.config.use_real_traffic_data = False
        
        self._initialize_intersections()
        
        # Initialize centralized signal controller
        self.signal_controller = CentralizedSignalController(self)
        print("✅ Centralized Signal Controller initialized")
    
    def _initialize_intersections(self):
        """Initialize the traffic light intersections."""
        for i in range(self.config.num_intersections):
            intersection = TrafficLight(
                intersection_id=f"intersection_{i+1}",
                cycle_length=self.config.cycle_length
            )
            self.intersections.append(intersection)
    
    def _generate_vehicle_id(self, is_special: bool = False) -> str:
        """Generate a unique vehicle ID."""
        if is_special:
            self.special_vehicle_counter += 1
            return f"special_{self.special_vehicle_counter}"
        else:
            self.vehicle_counter += 1
            return f"vehicle_{self.vehicle_counter}"
    
    def _spawn_vehicles(self, current_time: float):
        """Spawn new vehicles at intersections using real traffic data."""
        for i, intersection in enumerate(self.intersections):
            intersection_id = f"intersection_{i+1}"
            
            # Get spawn rates from real traffic data or use fallback
            if self.config.use_real_traffic_data and self.traffic_data_processor:
                spawn_rates = self.traffic_data_processor.get_vehicle_spawn_rates(intersection_id)
            else:
                # Fallback to uniform spawn rates
                spawn_rates = {
                    'north': self.config.vehicle_spawn_rate / 4,
                    'south': self.config.vehicle_spawn_rate / 4,
                    'east': self.config.vehicle_spawn_rate / 4,
                    'west': self.config.vehicle_spawn_rate / 4
                }
            
            # Spawn vehicles for each direction
            for direction, spawn_rate in spawn_rates.items():
                if random.random() < spawn_rate:
                    # Check if intersection has capacity
                    if intersection.get_total_queue_length() < self.config.max_vehicles_per_intersection:
                        # Map direction to Lane enum
                        lane_map = {
                            'north': Lane.NORTH,
                            'south': Lane.SOUTH,
                            'east': Lane.EAST,
                            'west': Lane.WEST
                        }
                        lane = lane_map[direction]
                        
                        # Determine if this should be a special vehicle
                        is_special = random.random() < self.config.special_vehicle_probability
                        
                        if is_special:
                            vehicle = SpecialVehicle(
                                vehicle_id=self._generate_vehicle_id(is_special=True),
                                lane=lane
                            )
                            self.total_special_vehicles_spawned += 1
                        else:
                            vehicle = Vehicle(
                                vehicle_id=self._generate_vehicle_id(),
                                lane=lane,
                                speed=random.uniform(0.8, 1.2)  # Random speed variation
                            )
                        
                        intersection.add_vehicle(vehicle)
                        self.total_vehicles_spawned += 1
    
    def _update_simulation(self, current_time: float):
        """Update the simulation state."""
        with self.lock:
            # Update simulation time
            if self.last_update_time is not None:
                time_delta = current_time - self.last_update_time
                self.simulation_time += time_delta * self.config.simulation_speed
                
                # Advance traffic data time (every second of simulation time)
                if self.config.use_real_traffic_data and self.traffic_data_processor:
                    # Advance by 1 time step for every second of simulation
                    steps_to_advance = int(time_delta * self.config.simulation_speed)
                    if steps_to_advance > 0:
                        self.traffic_data_processor.advance_time(steps_to_advance)
            
            # Spawn new vehicles
            self._spawn_vehicles(current_time)
            
            # Update signal controller
            self.signal_controller.update_automatic_signals(current_time)
            self.signal_controller.check_override_timeouts(current_time)
            
            # Verify signal integrity (safety check)
            self.signal_controller.verify_signal_integrity()
            
            # Update all intersections
            for intersection in self.intersections:
                intersection.update_phase(current_time)
                # Note: _apply_direction_overrides() is now handled by the signal controller
                intersection.update_vehicles(current_time)
            
            # Update metrics
            self.total_vehicles_passed = sum(
                intersection.total_vehicles_passed 
                for intersection in self.intersections
            )
            
            self.last_update_time = current_time
    
    def _simulation_loop(self):
        """Main simulation loop running in a separate thread."""
        self.start_time = time.time()
        self.last_update_time = self.start_time
        
        while self.is_running:
            current_time = time.time()
            self._update_simulation(current_time)
            
            # Sleep for a short time to prevent excessive CPU usage
            time.sleep(0.1)
    
    def start(self):
        """Start the simulation."""
        if not self.is_running:
            self.is_running = True
            self.simulation_thread = threading.Thread(target=self._simulation_loop)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()
    
    def stop(self):
        """Stop the simulation."""
        self.is_running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=1.0)
    
    def pause(self):
        """Pause the simulation."""
        self.is_running = False
    
    def resume(self):
        """Resume the simulation."""
        if not self.is_running:
            self.start()
    
    def reset(self):
        """Reset the simulation to initial state."""
        self.stop()
        
        # Reset state
        self.simulation_time = 0.0
        self.start_time = None
        self.last_update_time = None
        self.vehicle_counter = 0
        self.special_vehicle_counter = 0
        self.total_vehicles_spawned = 0
        self.total_vehicles_passed = 0
        self.total_special_vehicles_spawned = 0
        
        # Reset intersections
        for intersection in self.intersections:
            intersection.current_phase = SignalPhase.NORTH_SOUTH_GREEN
            intersection.phase_start_time = time.time()
            intersection.phase_elapsed = 0.0
            intersection.is_override_active = False
            intersection.override_phase = None
            intersection.vehicle_queues = {lane: [] for lane in Lane}
            intersection.total_vehicles_passed = 0
            intersection.total_wait_time = 0.0
    
    def get_intersection_data(self, intersection_id: str) -> Optional[Dict]:
        """Get current data for a specific intersection."""
        with self.lock:
            for intersection in self.intersections:
                if intersection.intersection_id == intersection_id:
                    return {
                        'id': intersection.intersection_id,
                        'current_phase': intersection.current_phase.value,
                        'phase_progress': intersection.get_phase_progress(),
                        'is_override_active': intersection.is_override_active,
                        'queue_lengths': {
                            lane.value: intersection.get_queue_length(lane)
                            for lane in Lane
                        },
                        'total_queue_length': intersection.get_total_queue_length(),
                        'average_wait_time': intersection.get_average_wait_time(),
                        'vehicles_passed': intersection.total_vehicles_passed,
                        'special_vehicles': [
                            {
                                'id': vehicle.id,
                                'lane': vehicle.lane.value,
                                'wait_time': vehicle.wait_time
                            }
                            for vehicle in intersection.get_special_vehicles()
                        ],
                        'signal_colors': {
                            lane.value: intersection.get_signal_color(lane)
                            for lane in Lane
                        }
                    }
        return None
    
    def get_all_intersections_data(self) -> List[Dict]:
        """Get current data for all intersections."""
        return [
            self.get_intersection_data(intersection.intersection_id)
            for intersection in self.intersections
        ]
    
    def get_simulation_metrics(self) -> Dict:
        """Get overall simulation metrics."""
        with self.lock:
            total_wait_time = sum(
                intersection.total_wait_time 
                for intersection in self.intersections
            )
            
            metrics = {
                'simulation_time': self.simulation_time,
                'total_vehicles_spawned': self.total_vehicles_spawned,
                'total_vehicles_passed': self.total_vehicles_passed,
                'total_special_vehicles_spawned': self.total_special_vehicles_spawned,
                'total_wait_time': total_wait_time,
                'average_wait_time': (
                    total_wait_time / self.total_vehicles_passed 
                    if self.total_vehicles_passed > 0 else 0.0
                ),
                'throughput': (
                    self.total_vehicles_passed / max(self.simulation_time, 1.0)
                ),
                'is_running': self.is_running
            }
            
            # Add traffic data information if available
            if self.config.use_real_traffic_data and self.traffic_data_processor:
                time_info = self.traffic_data_processor.get_current_time_info()
                traffic_summary = self.traffic_data_processor.get_traffic_summary()
                
                metrics.update({
                    'traffic_data': {
                        'using_real_data': True,
                        'current_time_minutes': time_info['current_time_minutes'],
                        'progress_percentage': time_info['progress_percentage'],
                        'average_flow': traffic_summary['average_flow'],
                        'peak_flow': traffic_summary['peak_flow'],
                        'min_flow': traffic_summary['min_flow']
                    }
                })
            else:
                metrics['traffic_data'] = {'using_real_data': False}
            
            return metrics
    
    def add_special_vehicle(self, intersection_id: str, lane: Lane) -> bool:
        """Manually add a special vehicle to a specific intersection and lane."""
        with self.lock:
            for intersection in self.intersections:
                if intersection.intersection_id == intersection_id:
                    vehicle = SpecialVehicle(
                        vehicle_id=self._generate_vehicle_id(is_special=True),
                        lane=lane
                    )
                    intersection.add_vehicle(vehicle)
                    self.total_special_vehicles_spawned += 1
                    return True
        return False
    
    def set_manual_override(self, intersection_id: str, direction: str, signal: str) -> bool:
        """Set manual override for a specific signal direction at an intersection."""
        try:
            signal_state = SignalState(signal)
            return self.signal_controller.set_signal_state(
                intersection_id, direction, signal_state, ControlMode.MANUAL
            )
        except ValueError:
            print(f"❌ Invalid signal state: {signal}")
            return False
    
    def set_auto_mode(self, intersection_id: str, direction: str) -> bool:
        """Set auto mode for a specific signal direction at an intersection."""
        return self.signal_controller.set_automatic_mode(intersection_id, direction)
    
    def get_signal_control_summary(self) -> Dict:
        """Get signal control summary."""
        return self.signal_controller.get_control_summary()
    
    def get_all_signal_states(self) -> Dict:
        """Get all signal states."""
        return self.signal_controller.get_all_signal_states()
    
    def emergency_override(self, intersection_id: str, direction: str, duration: float = 30.0) -> bool:
        """Set emergency override for a specific direction."""
        return self.signal_controller.emergency_override(intersection_id, direction, duration)
    
    def set_ai_control(self, intersection_id: str, direction: str, signal: str, duration: Optional[float] = None) -> bool:
        """Set AI control for a specific signal."""
        try:
            signal_state = SignalState(signal)
            return self.signal_controller.set_ai_control(intersection_id, direction, signal_state, duration)
        except ValueError:
            print(f"❌ Invalid signal state: {signal}")
            return False
    
    def verify_signal_integrity(self) -> bool:
        """Verify that all manual signals are properly maintained."""
        return self.signal_controller.verify_signal_integrity()
    
    def __del__(self):
        """Cleanup when simulation is destroyed."""
        self.stop()
