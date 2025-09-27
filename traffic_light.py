"""
Traffic light controller with 4-phase cycle and special vehicle override.
"""

import time
from typing import List, Optional, Dict
from enum import Enum
from vehicle import Vehicle, SpecialVehicle, Lane


class SignalPhase(Enum):
    NORTH_SOUTH_GREEN = "north_south_green"
    EAST_WEST_GREEN = "east_west_green"
    LEFT_TURNS = "left_turns"
    ALL_RED = "all_red"


class TrafficLight:
    """Traffic light controller for a single intersection."""
    
    def __init__(self, intersection_id: str, cycle_length: int = 60):
        self.intersection_id = intersection_id
        self.cycle_length = cycle_length
        
        # Phase durations (in seconds)
        self.phase_durations = {
            SignalPhase.NORTH_SOUTH_GREEN: 20,
            SignalPhase.EAST_WEST_GREEN: 20,
            SignalPhase.LEFT_TURNS: 15,
            SignalPhase.ALL_RED: 5
        }
        
        # Current state
        self.current_phase = SignalPhase.NORTH_SOUTH_GREEN
        self.phase_start_time = time.time()
        self.phase_elapsed = 0.0
        self.is_override_active = False
        self.override_phase = None
        
        # Vehicle queues for each lane
        self.vehicle_queues: Dict[Lane, List[Vehicle]] = {
            Lane.NORTH: [],
            Lane.SOUTH: [],
            Lane.EAST: [],
            Lane.WEST: []
        }
        
        # Metrics
        self.total_vehicles_passed = 0
        self.total_wait_time = 0.0
    
    def add_vehicle(self, vehicle: Vehicle):
        """Add a vehicle to the appropriate queue."""
        self.vehicle_queues[vehicle.lane].append(vehicle)
    
    def remove_vehicle(self, vehicle: Vehicle):
        """Remove a vehicle from its queue."""
        if vehicle in self.vehicle_queues[vehicle.lane]:
            self.vehicle_queues[vehicle.lane].remove(vehicle)
    
    def get_special_vehicles(self) -> List[SpecialVehicle]:
        """Get all special vehicles currently in queues."""
        special_vehicles = []
        for queue in self.vehicle_queues.values():
            for vehicle in queue:
                if isinstance(vehicle, SpecialVehicle):
                    special_vehicles.append(vehicle)
        return special_vehicles
    
    def check_special_vehicle_override(self) -> Optional[SignalPhase]:
        """
        Check if special vehicle override should be activated.
        Returns the required phase or None.
        """
        special_vehicles = self.get_special_vehicles()
        if not special_vehicles:
            return None
        
        # Get the lane of the first special vehicle
        special_lane = special_vehicles[0].lane
        
        # Determine required phase based on lane
        if special_lane in [Lane.NORTH, Lane.SOUTH]:
            return SignalPhase.NORTH_SOUTH_GREEN
        elif special_lane in [Lane.EAST, Lane.WEST]:
            return SignalPhase.EAST_WEST_GREEN
        
        return None
    
    def update_phase(self, current_time: float):
        """Update traffic light phase based on time and special vehicle priority."""
        self.phase_elapsed = current_time - self.phase_start_time
        
        # Check for special vehicle override
        required_phase = self.check_special_vehicle_override()
        
        if required_phase and not self.is_override_active:
            # Activate override
            self.is_override_active = True
            self.override_phase = required_phase
            self.current_phase = required_phase
            self.phase_start_time = current_time
            self.phase_elapsed = 0.0
        elif self.is_override_active:
            # Check if special vehicles are still present
            if not self.get_special_vehicles():
                # Deactivate override and return to normal cycle
                self.is_override_active = False
                self.override_phase = None
                self.phase_start_time = current_time
                self.phase_elapsed = 0.0
        else:
            # Normal phase progression
            current_duration = self.phase_durations[self.current_phase]
            if self.phase_elapsed >= current_duration:
                self._advance_to_next_phase(current_time)
    
    def _advance_to_next_phase(self, current_time: float):
        """Advance to the next phase in the cycle."""
        phase_order = [
            SignalPhase.NORTH_SOUTH_GREEN,
            SignalPhase.EAST_WEST_GREEN,
            SignalPhase.LEFT_TURNS,
            SignalPhase.ALL_RED
        ]
        
        current_index = phase_order.index(self.current_phase)
        next_index = (current_index + 1) % len(phase_order)
        
        self.current_phase = phase_order[next_index]
        self.phase_start_time = current_time
        self.phase_elapsed = 0.0
    
    def can_vehicle_move(self, vehicle: Vehicle) -> bool:
        """Check if a vehicle can move based on current signal phase."""
        if self.current_phase == SignalPhase.ALL_RED:
            return False
        
        if self.current_phase == SignalPhase.NORTH_SOUTH_GREEN:
            return vehicle.lane in [Lane.NORTH, Lane.SOUTH]
        elif self.current_phase == SignalPhase.EAST_WEST_GREEN:
            return vehicle.lane in [Lane.EAST, Lane.WEST]
        elif self.current_phase == SignalPhase.LEFT_TURNS:
            # Allow all vehicles during left turn phase
            return True
        
        return False
    
    def update_vehicles(self, current_time: float):
        """Update all vehicles in queues and handle movement."""
        for lane, queue in self.vehicle_queues.items():
            if not queue:
                continue
            
            # Update wait times
            for vehicle in queue:
                vehicle.update_wait_time(current_time)
            
            # Move vehicles that can move
            vehicles_to_remove = []
            for vehicle in queue:
                can_move = self.can_vehicle_move(vehicle)
                if vehicle.move(can_move):
                    vehicles_to_remove.append(vehicle)
                    self.total_vehicles_passed += 1
                    self.total_wait_time += vehicle.wait_time
            
            # Remove vehicles that have passed
            for vehicle in vehicles_to_remove:
                self.remove_vehicle(vehicle)
    
    def get_queue_length(self, lane: Lane) -> int:
        """Get the number of vehicles waiting in a specific lane."""
        return len(self.vehicle_queues[lane])
    
    def get_total_queue_length(self) -> int:
        """Get total number of vehicles waiting at this intersection."""
        return sum(len(queue) for queue in self.vehicle_queues.values())
    
    def get_average_wait_time(self) -> float:
        """Get average wait time for vehicles currently in queues."""
        total_wait = 0.0
        total_vehicles = 0
        
        for queue in self.vehicle_queues.values():
            for vehicle in queue:
                total_wait += vehicle.wait_time
                total_vehicles += 1
        
        return total_wait / total_vehicles if total_vehicles > 0 else 0.0
    
    def get_signal_color(self, lane: Lane) -> str:
        """Get the current signal color for a specific lane."""
        if self.current_phase == SignalPhase.ALL_RED:
            return "red"
        
        if self.current_phase == SignalPhase.NORTH_SOUTH_GREEN:
            return "green" if lane in [Lane.NORTH, Lane.SOUTH] else "red"
        elif self.current_phase == SignalPhase.EAST_WEST_GREEN:
            return "green" if lane in [Lane.EAST, Lane.WEST] else "red"
        elif self.current_phase == SignalPhase.LEFT_TURNS:
            return "green"  # All lanes green during left turns
        
        return "red"
    
    def get_phase_progress(self) -> float:
        """Get the progress of the current phase (0.0 to 1.0)."""
        current_duration = self.phase_durations[self.current_phase]
        return min(self.phase_elapsed / current_duration, 1.0)
    
    def __repr__(self):
        return f"TrafficLight(id={self.intersection_id}, phase={self.current_phase.value}, override={self.is_override_active})"
