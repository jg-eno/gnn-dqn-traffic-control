"""
Centralized Signal Controller for Traffic Light Management

This module provides a centralized interface for controlling all traffic signals,
making it easy to integrate AI algorithms and other control strategies.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import time
from dataclasses import dataclass

class SignalState(Enum):
    """Traffic signal states."""
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"

class ControlMode(Enum):
    """Signal control modes."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    AI_CONTROLLED = "ai_controlled"

@dataclass
class SignalCommand:
    """Command for controlling a traffic signal."""
    intersection_id: str
    direction: str  # 'north', 'south', 'east', 'west'
    signal: SignalState
    mode: ControlMode = ControlMode.MANUAL
    timestamp: float = None
    duration: Optional[float] = None  # Duration in seconds (None for indefinite)
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class SignalStatus:
    """Current status of a traffic signal."""
    intersection_id: str
    direction: str
    current_signal: SignalState
    mode: ControlMode
    last_updated: float
    override_active: bool = False
    override_duration: Optional[float] = None

class CentralizedSignalController:
    """
    Centralized controller for all traffic signals.
    
    This class provides a unified interface for controlling traffic signals,
    making it easy to implement different control strategies including AI algorithms.
    """
    
    def __init__(self, simulation):
        self.simulation = simulation
        self.signal_states: Dict[str, Dict[str, SignalStatus]] = {}
        self.override_commands: Dict[str, Dict[str, SignalCommand]] = {}
        self.control_mode: ControlMode = ControlMode.AUTOMATIC
        
        # Initialize signal states for all intersections
        self._initialize_signal_states()
    
    def _initialize_signal_states(self):
        """Initialize signal states for all intersections."""
        for intersection in self.simulation.intersections:
            intersection_id = intersection.intersection_id
            self.signal_states[intersection_id] = {}
            self.override_commands[intersection_id] = {}
            
            for direction in ['north', 'south', 'east', 'west']:
                self.signal_states[intersection_id][direction] = SignalStatus(
                    intersection_id=intersection_id,
                    direction=direction,
                    current_signal=SignalState.RED,
                    mode=ControlMode.AUTOMATIC,
                    last_updated=time.time()
                )
    
    def set_signal_state(self, intersection_id: str, direction: str, signal: SignalState, 
                        mode: ControlMode = ControlMode.MANUAL, duration: Optional[float] = None) -> bool:
        """
        Set the state of a specific traffic signal.
        
        Args:
            intersection_id: ID of the intersection
            direction: Direction ('north', 'south', 'east', 'west')
            signal: Signal state to set
            mode: Control mode
            duration: Duration in seconds (None for indefinite)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate inputs
            if intersection_id not in self.signal_states:
                print(f"❌ Invalid intersection ID: {intersection_id}")
                return False
            
            if direction not in self.signal_states[intersection_id]:
                print(f"❌ Invalid direction: {direction}")
                return False
            
            # Create command
            command = SignalCommand(
                intersection_id=intersection_id,
                direction=direction,
                signal=signal,
                mode=mode,
                duration=duration
            )
            
            # Store override command
            self.override_commands[intersection_id][direction] = command
            
            # Update signal state
            self.signal_states[intersection_id][direction].current_signal = signal
            self.signal_states[intersection_id][direction].mode = mode
            self.signal_states[intersection_id][direction].last_updated = time.time()
            self.signal_states[intersection_id][direction].override_active = True
            self.signal_states[intersection_id][direction].override_duration = duration
            
            # Apply to simulation
            self._apply_signal_to_simulation(intersection_id, direction, signal)
            
            print(f"✅ Signal set: {intersection_id} {direction} -> {signal.value} ({mode.value})")
            return True
            
        except Exception as e:
            print(f"❌ Error setting signal state: {e}")
            return False
    
    def set_automatic_mode(self, intersection_id: str, direction: str) -> bool:
        """
        Set a signal back to automatic mode.
        
        Args:
            intersection_id: ID of the intersection
            direction: Direction to set to automatic
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if intersection_id in self.override_commands and direction in self.override_commands[intersection_id]:
                del self.override_commands[intersection_id][direction]
            
            self.signal_states[intersection_id][direction].mode = ControlMode.AUTOMATIC
            self.signal_states[intersection_id][direction].override_active = False
            self.signal_states[intersection_id][direction].last_updated = time.time()
            
            print(f"✅ Signal set to automatic: {intersection_id} {direction}")
            return True
            
        except Exception as e:
            print(f"❌ Error setting automatic mode: {e}")
            return False
    
    def set_all_automatic(self, intersection_id: str) -> bool:
        """
        Set all signals in an intersection to automatic mode.
        
        Args:
            intersection_id: ID of the intersection
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            for direction in ['north', 'south', 'east', 'west']:
                self.set_automatic_mode(intersection_id, direction)
            return True
        except Exception as e:
            print(f"❌ Error setting all automatic: {e}")
            return False
    
    def get_signal_state(self, intersection_id: str, direction: str) -> Optional[SignalStatus]:
        """
        Get the current state of a specific signal.
        
        Args:
            intersection_id: ID of the intersection
            direction: Direction
            
        Returns:
            SignalStatus or None if not found
        """
        try:
            return self.signal_states.get(intersection_id, {}).get(direction)
        except Exception as e:
            print(f"❌ Error getting signal state: {e}")
            return None
    
    def get_all_signal_states(self) -> Dict[str, Dict[str, SignalStatus]]:
        """
        Get all signal states.
        
        Returns:
            Dictionary of all signal states
        """
        return self.signal_states
    
    def get_intersection_states(self, intersection_id: str) -> Dict[str, SignalStatus]:
        """
        Get all signal states for a specific intersection.
        
        Args:
            intersection_id: ID of the intersection
            
        Returns:
            Dictionary of signal states for the intersection
        """
        return self.signal_states.get(intersection_id, {})
    
    def _apply_signal_to_simulation(self, intersection_id: str, direction: str, signal: SignalState):
        """Apply signal state to the simulation."""
        try:
            # Find the intersection in the simulation
            for intersection in self.simulation.intersections:
                if intersection.intersection_id == intersection_id:
                    # Apply the signal override
                    intersection.set_manual_override(direction, signal.value)
                    break
        except Exception as e:
            print(f"❌ Error applying signal to simulation: {e}")
    
    def update_automatic_signals(self, current_time: float):
        """
        Update signals that are in automatic mode.
        This should be called regularly to ensure automatic signals work correctly.
        
        Args:
            current_time: Current simulation time
        """
        try:
            for intersection in self.simulation.intersections:
                intersection_id = intersection.intersection_id
                
                # Check if any signals are in automatic mode
                has_automatic = any(
                    state.mode == ControlMode.AUTOMATIC 
                    for state in self.signal_states[intersection_id].values()
                )
                
                if has_automatic:
                    # Store current manual overrides to protect them
                    manual_overrides = {}
                    for direction, state in self.signal_states[intersection_id].items():
                        if state.mode in [ControlMode.MANUAL, ControlMode.AI_CONTROLLED]:
                            manual_overrides[direction] = state.current_signal.value
                    
                    # Let the intersection handle automatic signals
                    intersection.update_phase(current_time)
                    
                    # Restore manual overrides to protect them from automatic updates
                    for direction, signal_value in manual_overrides.items():
                        intersection.set_manual_override(direction, signal_value)
                    
                    # Update our signal states to match the intersection (only for automatic signals)
                    for direction, state in self.signal_states[intersection_id].items():
                        if state.mode == ControlMode.AUTOMATIC:
                            # Get current signal from intersection
                            from vehicle import Lane
                            direction_map = {
                                'north': Lane.NORTH,
                                'south': Lane.SOUTH,
                                'east': Lane.EAST,
                                'west': Lane.WEST
                            }
                            
                            if direction in direction_map:
                                current_signal = intersection.get_signal_color(direction_map[direction])
                                state.current_signal = SignalState(current_signal)
                                state.last_updated = current_time
                                
        except Exception as e:
            print(f"❌ Error updating automatic signals: {e}")
    
    def check_override_timeouts(self, current_time: float):
        """
        Check for override timeouts and reset expired overrides.
        
        Args:
            current_time: Current simulation time
        """
        try:
            for intersection_id, directions in self.override_commands.items():
                for direction, command in list(directions.items()):
                    if command.duration is not None:
                        elapsed = current_time - command.timestamp
                        if elapsed >= command.duration:
                            # Timeout reached, set back to automatic
                            self.set_automatic_mode(intersection_id, direction)
                            print(f"⏰ Override timeout: {intersection_id} {direction}")
                            
        except Exception as e:
            print(f"❌ Error checking override timeouts: {e}")
    
    def verify_signal_integrity(self):
        """
        Verify that manual signals are still properly set and haven't been overridden.
        This is a safety check to ensure signal persistence.
        """
        try:
            integrity_issues = []
            
            for intersection_id, directions in self.override_commands.items():
                for direction, command in directions.items():
                    # Check if the signal state matches the command
                    if intersection_id in self.signal_states and direction in self.signal_states[intersection_id]:
                        current_state = self.signal_states[intersection_id][direction]
                        
                        # If it's a manual or AI command, verify the signal matches
                        if command.mode in [ControlMode.MANUAL, ControlMode.AI_CONTROLLED]:
                            if current_state.current_signal != command.signal:
                                integrity_issues.append({
                                    'intersection_id': intersection_id,
                                    'direction': direction,
                                    'expected': command.signal.value,
                                    'actual': current_state.current_signal.value,
                                    'mode': command.mode.value
                                })
            
            if integrity_issues:
                print(f"⚠️ Signal integrity issues detected: {len(integrity_issues)}")
                for issue in integrity_issues:
                    print(f"   {issue['intersection_id']} {issue['direction']}: Expected {issue['expected']}, got {issue['actual']} ({issue['mode']})")
                    
                    # Fix the issue by reapplying the command
                    self._apply_signal_to_simulation(
                        issue['intersection_id'], 
                        issue['direction'], 
                        SignalState(issue['expected'])
                    )
                    print(f"   🔧 Fixed: {issue['intersection_id']} {issue['direction']} -> {issue['expected']}")
            
            return len(integrity_issues) == 0
            
        except Exception as e:
            print(f"❌ Error verifying signal integrity: {e}")
            return False
    
    def get_control_summary(self) -> Dict:
        """
        Get a summary of the current control state.
        
        Returns:
            Dictionary with control summary
        """
        try:
            total_signals = 0
            manual_signals = 0
            automatic_signals = 0
            ai_signals = 0
            
            for intersection_id, directions in self.signal_states.items():
                for direction, state in directions.items():
                    total_signals += 1
                    if state.mode == ControlMode.MANUAL:
                        manual_signals += 1
                    elif state.mode == ControlMode.AUTOMATIC:
                        automatic_signals += 1
                    elif state.mode == ControlMode.AI_CONTROLLED:
                        ai_signals += 1
            
            return {
                'total_signals': total_signals,
                'manual_signals': manual_signals,
                'automatic_signals': automatic_signals,
                'ai_signals': ai_signals,
                'control_mode': self.control_mode.value
            }
            
        except Exception as e:
            print(f"❌ Error getting control summary: {e}")
            return {}
    
    def set_ai_control(self, intersection_id: str, direction: str, signal: SignalState, 
                      duration: Optional[float] = None) -> bool:
        """
        Set a signal to AI control mode.
        
        Args:
            intersection_id: ID of the intersection
            direction: Direction
            signal: Signal state
            duration: Duration in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.set_signal_state(intersection_id, direction, signal, 
                                   ControlMode.AI_CONTROLLED, duration)
    
    def emergency_override(self, intersection_id: str, direction: str, duration: float = 30.0) -> bool:
        """
        Set emergency override (green light) for a specific direction.
        
        Args:
            intersection_id: ID of the intersection
            direction: Direction
            duration: Duration in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.set_signal_state(intersection_id, direction, SignalState.GREEN, 
                                   ControlMode.MANUAL, duration)

def test_signal_controller():
    """Test the centralized signal controller."""
    print("🧪 Testing Centralized Signal Controller")
    print("=" * 50)
    
    # This would normally be called with a real simulation instance
    # For testing, we'll just demonstrate the interface
    
    print("✅ Signal Controller interface ready")
    print("📋 Available methods:")
    print("  - set_signal_state(intersection_id, direction, signal, mode, duration)")
    print("  - set_automatic_mode(intersection_id, direction)")
    print("  - set_all_automatic(intersection_id)")
    print("  - get_signal_state(intersection_id, direction)")
    print("  - get_all_signal_states()")
    print("  - set_ai_control(intersection_id, direction, signal, duration)")
    print("  - emergency_override(intersection_id, direction, duration)")
    print("  - get_control_summary()")
    
    print("\n🎯 Ready for AI integration!")

if __name__ == "__main__":
    test_signal_controller()
