# 🗽 NYC Traffic Light Simulator

A **real-time traffic light simulation system** powered by **actual NYC traffic data**. Features 4 intersections with authentic traffic patterns, visual simulation, and intelligent traffic management.

## 🌟 Key Features

- **🗽 Real NYC Data**: Uses actual traffic flow data from 128 NYC intersections
- **🎨 Visual Simulation**: HTML5 Canvas with roads, traffic lights, and animated vehicles
- **🚦 Smart Traffic Lights**: 4-phase cycle with special vehicle priority override
- **📊 Real-time Metrics**: Live performance monitoring and traffic data visualization
- **🌐 Web-based Interface**: Modern dark-themed UI with responsive design
- **⚡ Real-time Updates**: WebSocket communication for live simulation
- **🎛️ Manual Controls**: Individual signal controllers for each intersection

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Modern web browser

### Installation
```bash
# Clone the repository
cd gnn-dqn-traffic-control

# Install dependencies
pip install -r requirements.txt

# Run the simulator
python main.py
```

### Access the Simulator
Open your browser to: **http://localhost:5000**

## 🗽 NYC Traffic Data Integration

### Dataset Overview
- **Source**: Real NYC traffic flow data
- **Size**: 2,112 time steps × 128 intersections
- **Time Span**: ~35.2 minutes of actual traffic data
- **Data Type**: Traffic flow counts (vehicles per time step)
- **Value Range**: 0 to 1,032 vehicles per time step

### Data Preprocessing Pipeline

#### 1. **Data Selection**
```python
# Select 4 random intersections from 128 available
selected_intersections = random.sample(range(128), 4)
# Example: [104, 71, 124, 119]
```

#### 2. **Time Window Processing**
```python
# Extract 2-minute time windows (120 time steps)
time_window = 2 minutes × 60 steps/minute = 120 time steps
timeframe_data = data[start:start+120, selected_intersections]
```

#### 3. **Flow Rate Calculation**
```python
# Calculate average flow for each intersection
avg_flow = np.mean(intersection_flow)

# Distribute across 4 directions with variation
directions = {
    'north': avg_flow * (0.25 + random.uniform(-0.2, 0.2)),
    'south': avg_flow * (0.25 + random.uniform(-0.2, 0.2)),
    'east': avg_flow * (0.25 + random.uniform(-0.2, 0.2)),
    'west': avg_flow * (0.25 + random.uniform(-0.2, 0.2))
}
```

#### 4. **Vehicle Spawn Rate Conversion**
```python
# Convert flow counts to spawn probabilities
scale_factor = 0.01
spawn_rate = min(0.5, flow_rate * scale_factor)
```

### Data Processing Features

- **Real-time Advancement**: Dataset progresses with simulation time
- **Sliding Windows**: 2-minute windows slide through the dataset
- **Direction Distribution**: Traffic flow distributed across N/S/E/W with 20% variation
- **Peak/Min Tracking**: Monitors peak and minimum flow rates
- **Looping**: Dataset loops when reaching the end

## 🏗️ System Architecture

### Core Components

#### **Backend (Python)**
- **`simulation.py`**: Main simulation engine with NYC data integration
- **`nyc_traffic_data.py`**: NYC traffic data processor and preprocessor
- **`traffic_light.py`**: Individual intersection controller with 4-phase cycles
- **`vehicle.py`**: Vehicle classes (normal and special vehicles)
- **`web_app.py`**: Flask web server with WebSocket support

#### **Frontend (HTML/CSS/JavaScript)**
- **`templates/index.html`**: Main web interface with dark theme
- **`static/css/style.css`**: Responsive styling and visual design
- **`static/js/traffic-simulator.js`**: Canvas animations and real-time updates

### Data Flow

```
NYC Dataset → Data Processor → Simulation Engine → Web Interface
     ↓              ↓              ↓              ↓
Raw Traffic → Flow Rates → Vehicle Spawning → Visual Display
```

## 🚦 Traffic Light System

### 4-Phase Cycle
Each intersection cycles through 4 phases:

1. **North-South Green** (20s): Allows northbound and southbound traffic
2. **East-West Green** (20s): Allows eastbound and westbound traffic  
3. **Left Turns** (15s): Permits left turns from all directions
4. **All Red** (5s): Clearing phase for intersection safety

### Special Vehicle Priority
- **Immediate Override**: Normal cycle interrupted when special vehicle detected
- **Direction-Specific**: Signal switches to green for special vehicle's direction
- **Auto-Resume**: Normal cycle resumes after special vehicle passes

## 🎛️ User Interface

### Main Features
- **Visual Simulation**: Real-time traffic animation on HTML5 Canvas
- **Intersection Controllers**: Individual control for each of the 4 intersections
- **NYC Data Panel**: Live display of traffic data status and metrics
- **Manual Override**: Manual signal control for each direction
- **Real-time Metrics**: Live performance monitoring

### Controller Layout
- **Left Side**: Visual simulation canvas
- **Right Side**: Intersection controllers with toggle buttons
- **NYC Data Panel**: Traffic data status and progression metrics

## 📊 Real-time Metrics

### Simulation Metrics
- **Simulation Time**: Current simulation duration
- **Vehicles Spawned**: Total vehicles created
- **Vehicles Passed**: Total vehicles that completed their journey
- **Throughput**: Vehicles passing per second
- **Average Wait Time**: Mean waiting time for vehicles

### NYC Data Metrics
- **Data Time**: Current position in NYC dataset (minutes)
- **Progress**: Percentage through the dataset
- **Average Flow**: Mean traffic flow across all intersections
- **Peak Flow**: Maximum traffic flow observed
- **Min Flow**: Minimum traffic flow observed

## 🔧 Configuration

### Key Parameters
```python
# In simulation.py
num_intersections = 4
cycle_length = 60  # seconds
vehicle_spawn_rate = 0.3  # fallback rate
special_vehicle_probability = 0.05  # 5%
simulation_speed = 1.0  # real-time
use_real_traffic_data = True
```

### NYC Data Settings
```python
# In nyc_traffic_data.py
time_window_minutes = 2
time_steps_per_minute = 60
scale_factor = 0.01  # flow to spawn rate conversion
variation = 0.2  # 20% direction variation
```

## 🚀 Deployment

### Local Development
```bash
python main.py --debug
```

### Production
```bash
python main.py --production --host 0.0.0.0 --port 80
```

### Docker
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "main.py", "--production"]
```

## 📈 Performance Features

### Scalability
- **Responsive Design**: Automatically scales from mobile to desktop
- **High DPI Support**: Crisp graphics on retina displays
- **Real-time Updates**: WebSocket communication for live data
- **Efficient Processing**: Optimized data processing pipeline

### Data Efficiency
- **Selective Loading**: Uses only 4 out of 128 intersections (3.1% of data)
- **Time Windows**: Processes 2-minute segments for memory efficiency
- **Real-time Processing**: Dynamic flow rate calculation
- **Fallback System**: Graceful degradation to synthetic data if needed

## 🎯 Use Cases

- **Traffic Engineering**: Study intersection efficiency with real data
- **Education**: Learn about traffic management systems
- **Research**: Test traffic control algorithms with authentic patterns
- **Demonstration**: Show real-world traffic light behavior
- **Prototyping**: Develop new traffic management solutions

## 🔬 Technical Details

### Data Processing Algorithm
1. **Load Dataset**: Read 2,112 × 128 traffic flow matrix
2. **Select Intersections**: Randomly choose 4 intersections
3. **Extract Windows**: Get 2-minute time windows (120 steps)
4. **Calculate Flows**: Compute average, peak, and min flow rates
5. **Distribute Directions**: Split flow across N/S/E/W with variation
6. **Convert Rates**: Transform flow counts to spawn probabilities
7. **Advance Time**: Progress through dataset with simulation time

### Simulation Engine
- **Discrete Time Steps**: 1-second simulation intervals
- **Vehicle Spawning**: Probability-based spawning using real data
- **Signal Control**: 4-phase cycle with special vehicle override
- **Queue Management**: Realistic vehicle queuing and movement
- **Metrics Collection**: Real-time performance monitoring

## 🐛 Troubleshooting

### Common Issues
1. **Port Already in Use**: Use `--port` argument to change port
2. **WebSocket Connection Failed**: Check firewall settings
3. **Canvas Not Rendering**: Ensure modern browser support
4. **Performance Issues**: Reduce simulation speed or intersection count

### Debug Mode
```bash
python main.py --debug
```

## 📄 License

This project is part of a Smart India Hackathon submission for intelligent traffic management systems.

---

**Ready to simulate real NYC traffic! 🗽🚦✨**

Open your browser to **http://localhost:5000** and experience authentic NYC traffic patterns!