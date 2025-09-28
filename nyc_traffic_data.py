"""
NYC Traffic Data Processor for Real Traffic Flow Integration
"""

import pandas as pd
import numpy as np
import random
from typing import List, Dict, Tuple
import time

class NYCTrafficDataProcessor:
    """Processes NYC traffic data for integration with traffic simulation."""
    
    def __init__(self, data_file_path: str):
        self.data_file_path = data_file_path
        self.traffic_data = None
        self.selected_intersections = []
        self.current_time_index = 0
        self.time_window_minutes = 2  # 2-minute time window
        self.time_steps_per_minute = 60  # Assuming 1-second time steps
        
        # Load and process the data
        self.load_data()
        self.select_intersections()
    
    def load_data(self):
        """Load the NYC traffic data from CSV file."""
        try:
            # Read the CSV file
            self.traffic_data = pd.read_csv(self.data_file_path, header=None)
            print(f"✅ Loaded NYC traffic data: {self.traffic_data.shape[0]} time steps, {self.traffic_data.shape[1]} intersections")
            
            # Convert to numpy array for faster processing
            self.traffic_data = self.traffic_data.values
            
        except Exception as e:
            print(f"❌ Error loading traffic data: {e}")
            # Fallback to synthetic data
            self.generate_synthetic_data()
    
    def generate_synthetic_data(self):
        """Generate synthetic traffic data as fallback."""
        print("🔄 Generating synthetic traffic data...")
        # Generate 2000 time steps with 128 intersections
        self.traffic_data = np.random.poisson(lam=15, size=(2000, 128))
        print(f"✅ Generated synthetic data: {self.traffic_data.shape}")
    
    def select_intersections(self):
        """Select 4 intersections for our simulation."""
        # Select 4 random intersections from the 128 available
        total_intersections = self.traffic_data.shape[1]
        self.selected_intersections = random.sample(range(total_intersections), 4)
        
        print(f"🎯 Selected intersections: {self.selected_intersections}")
        print(f"📍 Intersection IDs: {[f'intersection_{i+1}' for i in range(4)]}")
    
    def get_traffic_flow_for_timeframe(self, start_time_index: int = None) -> Dict[str, Dict[str, float]]:
        """
        Get traffic flow data for a 2-minute timeframe for the 4 selected intersections.
        
        Args:
            start_time_index: Starting time index (if None, uses current time)
            
        Returns:
            Dictionary with traffic flow data for each intersection and direction
        """
        if start_time_index is None:
            start_time_index = self.current_time_index
        
        # Calculate time window (2 minutes = 120 time steps)
        time_window = self.time_window_minutes * self.time_steps_per_minute
        end_time_index = min(start_time_index + time_window, len(self.traffic_data))
        
        # Extract data for selected intersections
        timeframe_data = self.traffic_data[start_time_index:end_time_index, self.selected_intersections]
        
        # Process data for each intersection
        intersection_data = {}
        
        for i, intersection_idx in enumerate(self.selected_intersections):
            intersection_id = f"intersection_{i+1}"
            intersection_flow = timeframe_data[:, i]
            
            # Calculate average flow rate for each direction
            # Distribute the total flow across 4 directions (North, South, East, West)
            avg_flow = np.mean(intersection_flow)
            
            # Add some variation to make it more realistic
            variation = 0.2  # 20% variation
            
            intersection_data[intersection_id] = {
                'north': max(0, avg_flow * (0.25 + random.uniform(-variation, variation))),
                'south': max(0, avg_flow * (0.25 + random.uniform(-variation, variation))),
                'east': max(0, avg_flow * (0.25 + random.uniform(-variation, variation))),
                'west': max(0, avg_flow * (0.25 + random.uniform(-variation, variation))),
                'total_flow': avg_flow,
                'peak_flow': np.max(intersection_flow),
                'min_flow': np.min(intersection_flow)
            }
        
        return intersection_data
    
    def get_vehicle_spawn_rates(self, intersection_id: str) -> Dict[str, float]:
        """
        Get vehicle spawn rates for a specific intersection based on real data.
        
        Args:
            intersection_id: The intersection ID (e.g., 'intersection_1')
            
        Returns:
            Dictionary with spawn rates for each direction
        """
        # Get current traffic flow data
        traffic_data = self.get_traffic_flow_for_timeframe()
        
        if intersection_id not in traffic_data:
            # Fallback to default rates
            return {
                'north': 0.1,
                'south': 0.1,
                'east': 0.1,
                'west': 0.1
            }
        
        intersection_flow = traffic_data[intersection_id]
        
        # Convert flow rates to spawn probabilities (vehicles per second)
        # Scale down the values to reasonable spawn rates
        scale_factor = 0.01  # Adjust this to control spawn frequency
        
        return {
            'north': min(0.5, intersection_flow['north'] * scale_factor),
            'south': min(0.5, intersection_flow['south'] * scale_factor),
            'east': min(0.5, intersection_flow['east'] * scale_factor),
            'west': min(0.5, intersection_flow['west'] * scale_factor)
        }
    
    def advance_time(self, steps: int = 1):
        """Advance the current time index."""
        self.current_time_index = (self.current_time_index + steps) % len(self.traffic_data)
    
    def get_current_time_info(self) -> Dict:
        """Get information about the current time position in the dataset."""
        total_time_steps = len(self.traffic_data)
        current_time_minutes = self.current_time_index / self.time_steps_per_minute
        
        return {
            'current_time_index': self.current_time_index,
            'current_time_minutes': current_time_minutes,
            'total_time_steps': total_time_steps,
            'total_time_minutes': total_time_steps / self.time_steps_per_minute,
            'progress_percentage': (self.current_time_index / total_time_steps) * 100
        }
    
    def get_traffic_summary(self) -> Dict:
        """Get a summary of current traffic conditions."""
        traffic_data = self.get_traffic_flow_for_timeframe()
        
        summary = {
            'total_intersections': len(traffic_data),
            'average_flow': 0,
            'peak_flow': 0,
            'min_flow': float('inf'),
            'intersections': {}
        }
        
        total_flow = 0
        for intersection_id, data in traffic_data.items():
            total_flow += data['total_flow']
            summary['peak_flow'] = max(summary['peak_flow'], data['peak_flow'])
            summary['min_flow'] = min(summary['min_flow'], data['min_flow'])
            
            summary['intersections'][intersection_id] = {
                'total_flow': data['total_flow'],
                'peak_flow': data['peak_flow'],
                'min_flow': data['min_flow']
            }
        
        summary['average_flow'] = total_flow / len(traffic_data)
        
        return summary

def test_nyc_traffic_data():
    """Test the NYC traffic data processor."""
    print("🧪 Testing NYC Traffic Data Processor")
    print("=" * 50)
    
    # Initialize the processor
    data_file = "/Users/user/Documents/Hackathon/SIH/TrafficSignalAI/data/V-128.csv"
    processor = NYCTrafficDataProcessor(data_file)
    
    # Test getting traffic flow data
    print("\n📊 Current Traffic Flow Data:")
    traffic_data = processor.get_traffic_flow_for_timeframe()
    for intersection_id, data in traffic_data.items():
        print(f"  {intersection_id}:")
        print(f"    Total Flow: {data['total_flow']:.2f}")
        print(f"    North: {data['north']:.2f}, South: {data['south']:.2f}")
        print(f"    East: {data['east']:.2f}, West: {data['west']:.2f}")
        print(f"    Peak: {data['peak_flow']:.2f}, Min: {data['min_flow']:.2f}")
    
    # Test vehicle spawn rates
    print("\n🚗 Vehicle Spawn Rates:")
    for i in range(1, 5):
        intersection_id = f"intersection_{i}"
        spawn_rates = processor.get_vehicle_spawn_rates(intersection_id)
        print(f"  {intersection_id}: {spawn_rates}")
    
    # Test time advancement
    print("\n⏰ Time Information:")
    time_info = processor.get_current_time_info()
    print(f"  Current Time: {time_info['current_time_minutes']:.2f} minutes")
    print(f"  Progress: {time_info['progress_percentage']:.2f}%")
    
    # Test traffic summary
    print("\n📈 Traffic Summary:")
    summary = processor.get_traffic_summary()
    print(f"  Average Flow: {summary['average_flow']:.2f}")
    print(f"  Peak Flow: {summary['peak_flow']:.2f}")
    print(f"  Min Flow: {summary['min_flow']:.2f}")
    
    print("\n✅ NYC Traffic Data Processor test completed!")

if __name__ == "__main__":
    test_nyc_traffic_data()
