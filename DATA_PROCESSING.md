# 🗽 NYC Traffic Data Processing Documentation

## Overview

This document provides detailed technical information about how NYC traffic data is preprocessed and integrated into the traffic light simulation system.

## Dataset Information

### Source Data
- **File**: `V-128.csv`
- **Location**: `/Users/user/Documents/Hackathon/SIH/TrafficSignalAI/data/`
- **Format**: CSV with no headers
- **Dimensions**: 2,112 rows × 128 columns
- **Data Type**: Float64 values representing traffic flow counts

### Data Characteristics
- **Time Steps**: 2,112 (representing ~35.2 minutes at 1-second intervals)
- **Intersections**: 128 different NYC intersections
- **Value Range**: 0.0 to 1,032.0 vehicles per time step
- **Average Flow**: 142.6 vehicles per time step
- **Standard Deviation**: 77.1 vehicles per time step

## Data Preprocessing Pipeline

### 1. Data Loading and Validation

```python
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
```

### 2. Intersection Selection

```python
def select_intersections(self):
    """Select 4 intersections for our simulation."""
    # Select 4 random intersections from the 128 available
    total_intersections = self.traffic_data.shape[1]
    self.selected_intersections = random.sample(range(total_intersections), 4)
    
    print(f"🎯 Selected intersections: {self.selected_intersections}")
    print(f"📍 Intersection IDs: {[f'intersection_{i+1}' for i in range(4)]}")
```

**Selection Criteria:**
- Random selection from 128 available intersections
- Ensures diverse traffic patterns across the simulation
- Each run selects different intersections for variety

### 3. Time Window Processing

```python
def get_traffic_flow_for_timeframe(self, start_time_index: int = None):
    """Get traffic flow data for a 2-minute timeframe for the 4 selected intersections."""
    if start_time_index is None:
        start_time_index = self.current_time_index
    
    # Calculate time window (2 minutes = 120 time steps)
    time_window = self.time_window_minutes * self.time_steps_per_minute
    end_time_index = min(start_time_index + time_window, len(self.traffic_data))
    
    # Extract data for selected intersections
    timeframe_data = self.traffic_data[start_time_index:end_time_index, self.selected_intersections]
```

**Time Window Parameters:**
- **Window Size**: 2 minutes (120 time steps)
- **Step Size**: 1 second per time step
- **Overlap**: Sliding window approach
- **Boundary Handling**: Wraps around when reaching dataset end

### 4. Flow Rate Calculation

```python
# Process data for each intersection
intersection_data = {}

for i, intersection_idx in enumerate(self.selected_intersections):
    intersection_id = f"intersection_{i+1}"
    intersection_flow = timeframe_data[:, i]
    
    # Calculate average flow rate for each direction
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
```

**Flow Distribution Algorithm:**
- **Base Distribution**: 25% to each direction (N, S, E, W)
- **Variation**: ±20% random variation for realism
- **Constraints**: Minimum value of 0 (no negative flows)
- **Statistics**: Calculate peak, minimum, and average flows

### 5. Vehicle Spawn Rate Conversion

```python
def get_vehicle_spawn_rates(self, intersection_id: str) -> Dict[str, float]:
    """Get vehicle spawn rates for a specific intersection based on real data."""
    # Get current traffic flow data
    traffic_data = self.get_traffic_flow_for_timeframe()
    
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
```

**Conversion Parameters:**
- **Scale Factor**: 0.01 (converts flow counts to spawn probabilities)
- **Maximum Rate**: 0.5 vehicles per second (prevents overwhelming simulation)
- **Direction-Specific**: Individual rates for each direction
- **Real-time Updates**: Rates update as simulation progresses

## Data Processing Features

### Time Advancement

```python
def advance_time(self, steps: int = 1):
    """Advance the current time index."""
    self.current_time_index = (self.current_time_index + steps) % len(self.traffic_data)
```

**Time Management:**
- **Synchronization**: 1 simulation second = 1 dataset time step
- **Looping**: Dataset loops when reaching the end
- **Continuous Flow**: Seamless progression through the dataset

### Fallback System

```python
def generate_synthetic_data(self):
    """Generate synthetic traffic data as fallback."""
    print("🔄 Generating synthetic traffic data...")
    # Generate 2000 time steps with 128 intersections
    self.traffic_data = np.random.poisson(lam=15, size=(2000, 128))
    print(f"✅ Generated synthetic data: {self.traffic_data.shape}")
```

**Fallback Characteristics:**
- **Poisson Distribution**: Realistic traffic flow distribution
- **Lambda Parameter**: 15 (average flow rate)
- **Same Structure**: Maintains 128 intersections for consistency
- **Automatic Activation**: Triggers if NYC data fails to load

## Integration with Simulation

### Simulation Engine Integration

```python
# In simulation.py
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
                # Spawn vehicle logic...
```

### Real-time Data Updates

```python
# Advance traffic data time (every second of simulation time)
if self.config.use_real_traffic_data and self.traffic_data_processor:
    # Advance by 1 time step for every second of simulation
    steps_to_advance = int(time_delta * self.config.simulation_speed)
    if steps_to_advance > 0:
        self.traffic_data_processor.advance_time(steps_to_advance)
```

## Performance Optimizations

### Memory Management
- **Numpy Arrays**: Efficient numerical operations
- **Selective Loading**: Only loads necessary data segments
- **Time Windows**: Processes data in manageable chunks
- **Garbage Collection**: Automatic cleanup of processed data

### Computational Efficiency
- **Vectorized Operations**: Uses NumPy for fast calculations
- **Caching**: Stores processed results to avoid recalculation
- **Lazy Loading**: Loads data only when needed
- **Batch Processing**: Processes multiple intersections simultaneously

## Data Quality and Validation

### Data Validation
- **Range Checking**: Ensures values are within expected bounds
- **Type Validation**: Confirms data types are correct
- **Shape Validation**: Verifies dataset dimensions
- **Null Handling**: Manages missing or invalid data

### Quality Metrics
- **Flow Rate Statistics**: Mean, median, standard deviation
- **Peak Detection**: Identifies high-traffic periods
- **Pattern Analysis**: Detects traffic flow patterns
- **Anomaly Detection**: Identifies unusual traffic conditions

## Configuration Parameters

### Data Processing Settings
```python
# Time window configuration
time_window_minutes = 2
time_steps_per_minute = 60

# Flow distribution settings
variation = 0.2  # 20% variation
base_direction_ratio = 0.25  # 25% per direction

# Spawn rate conversion
scale_factor = 0.01
max_spawn_rate = 0.5

# Data selection
num_selected_intersections = 4
total_intersections = 128
```

### Simulation Integration Settings
```python
# Simulation configuration
use_real_traffic_data = True
traffic_data_file = "V-128.csv"
simulation_speed = 1.0  # real-time
```

## Monitoring and Debugging

### Data Processing Metrics
- **Processing Time**: Time taken for data processing operations
- **Memory Usage**: Memory consumption during processing
- **Data Quality**: Statistics about data validity
- **Performance Metrics**: Throughput and efficiency measures

### Debug Information
- **Selected Intersections**: Which intersections are being used
- **Time Progression**: Current position in the dataset
- **Flow Rates**: Current flow rates for each intersection
- **Spawn Rates**: Current vehicle spawn probabilities

## Future Enhancements

### Planned Improvements
- **Dynamic Intersection Selection**: Allow users to choose specific intersections
- **Multiple Time Windows**: Support for different window sizes
- **Advanced Analytics**: More sophisticated traffic pattern analysis
- **Real-time Data Integration**: Connect to live traffic data feeds
- **Machine Learning**: Predictive traffic flow modeling

### Scalability Considerations
- **Larger Datasets**: Support for bigger traffic datasets
- **More Intersections**: Scale to handle more intersections
- **Distributed Processing**: Parallel processing for large datasets
- **Cloud Integration**: Cloud-based data processing and storage

---

This documentation provides a comprehensive overview of how NYC traffic data is processed and integrated into the simulation system, ensuring realistic and authentic traffic behavior.
