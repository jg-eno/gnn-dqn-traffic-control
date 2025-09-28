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


@dataclass
class SimulationConfig:
    """Configuration for the simulation."""
    num_intersections: int = 6
    cycle_length: int = 60
    vehicle_spawn_rate: float = 0.3  # vehicles per second per intersection
    special_vehicle_probability: float = 0.05  # 5% chance of special vehicle
    simulation_speed: float = 1.0  # 1.0 = real time, 2.0 = 2x speed
    max_vehicles_per_intersection: int = 50


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
        
        self._initialize_intersections()
    
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
        """Spawn new vehicles at intersections."""
        for intersection in self.intersections:
            # Check if we should spawn a vehicle at this intersection
            if random.random() < self.config.vehicle_spawn_rate:
                # Check if intersection has capacity
                if intersection.get_total_queue_length() < self.config.max_vehicles_per_intersection:
                    # Choose random lane
                    lane = random.choice(list(Lane))
                    
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
            
            # Spawn new vehicles
            self._spawn_vehicles(current_time)
            
            # Update all intersections
            for intersection in self.intersections:
                intersection.update_phase(current_time)
                intersection._apply_direction_overrides()
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
            
            return {
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
        with self.lock:
            for intersection in self.intersections:
                if intersection.intersection_id == intersection_id:
                    intersection.set_manual_override(direction, signal)
                    return True
        return False
    
    def set_auto_mode(self, intersection_id: str, direction: str) -> bool:
        """Set auto mode for a specific signal direction at an intersection."""
        with self.lock:
            for intersection in self.intersections:
                if intersection.intersection_id == intersection_id:
                    intersection.set_auto_mode(direction)
                    return True
        return False
    
    def __del__(self):
        """Cleanup when simulation is destroyed."""
        self.stop()
