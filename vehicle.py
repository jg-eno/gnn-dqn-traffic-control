"""
Vehicle classes for traffic light simulator.
"""

import time
from typing import Optional
from enum import Enum


class VehicleType(Enum):
    NORMAL = "normal"
    SPECIAL = "special"


class Lane(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class Vehicle:
    """Base vehicle class for normal traffic."""
    
    def __init__(self, vehicle_id: str, lane: Lane, speed: float = 1.0):
        self.id = vehicle_id
        self.lane = lane
        self.speed = speed  # vehicles per second
        self.arrival_time = time.time()
        self.wait_time = 0.0
        self.position = 0.0  # Position in queue (0 = front)
        self.has_passed = False
        self.vehicle_type = VehicleType.NORMAL
        self.priority = False
    
    def update_wait_time(self, current_time: float):
        """Update wait time based on current simulation time."""
        self.wait_time = current_time - self.arrival_time
    
    def move(self, can_move: bool) -> bool:
        """
        Move vehicle if possible.
        Returns True if vehicle passed through intersection.
        """
        if can_move:
            self.position += self.speed
            if self.position >= 1.0:  # Vehicle has passed through
                self.has_passed = True
                return True
        return False
    
    def __repr__(self):
        return f"Vehicle(id={self.id}, lane={self.lane.value}, wait={self.wait_time:.1f}s)"


class SpecialVehicle(Vehicle):
    """Special vehicle with priority override capabilities."""
    
    def __init__(self, vehicle_id: str, lane: Lane, speed: float = 1.0):
        super().__init__(vehicle_id, lane, speed)
        self.vehicle_type = VehicleType.SPECIAL
        self.priority = True
    
    def __repr__(self):
        return f"SpecialVehicle(id={self.id}, lane={self.lane.value}, wait={self.wait_time:.1f}s)"
