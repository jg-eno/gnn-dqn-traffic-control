# 🚦 Visual Traffic Light Simulator

A modern web-based traffic light simulation system with **visual roads, animated traffic lights, and moving vehicles**. Features real-time simulation of 4 intersections with special vehicle priority override.

## 🌟 Features

- **🎨 Visual Simulation**: HTML5 Canvas with roads, traffic lights, and animated vehicles
- **🚦 Traffic Lights**: Red, yellow, green lights for each direction (North, South, East, West)
- **🚗 Custom Vehicle Images**: Real car and ambulance sprites with proper rotation
- **🛣️ Custom Road Graphics**: Realistic road textures with transparent backgrounds
- **📱 Fully Responsive**: Scales perfectly on desktop, tablet, and mobile devices
- **🚨 Special Vehicle Priority**: Emergency vehicles get immediate green lights
- **📊 Real-time Metrics**: Live performance monitoring and statistics
- **🌐 Web-based**: Runs in any modern browser with high DPI support
- **⚡ Real-time Updates**: WebSocket communication for live simulation
- **🔄 Auto-scaling**: Canvas automatically adjusts to window size

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Modern web browser

### Installation
```bash
# Clone or download the project
cd gnn-dqn-traffic-control

# Install dependencies
pip install -r requirements.txt

# Run the visual simulator
python main.py
```

### Access the Simulator
Open your browser to: **http://localhost:5000**

## 🎮 How to Use

1. **Start Simulation**: Click the "▶️ Start" button
2. **Watch Traffic**: See vehicles moving through intersections
3. **Add Special Vehicle**: Click "🚨 Add Special Vehicle" to test priority override
4. **Monitor Metrics**: View real-time statistics in the sidebar
5. **Control Simulation**: Use Start/Stop/Reset buttons as needed

## 🏗️ Architecture

### Core Components
- **`web_app.py`**: Flask web server with WebSocket support
- **`simulation.py`**: Traffic simulation engine with 4-phase cycles
- **`traffic_light.py`**: Individual intersection controller
- **`vehicle.py`**: Vehicle classes (normal and special)

### Frontend
- **`templates/index.html`**: Main web interface
- **`static/css/style.css`**: Visual styling and responsive design
- **`static/js/traffic-simulator.js`**: Canvas animations and WebSocket client

## 🎯 Traffic Light Phases

Each intersection cycles through 4 phases:
1. **North-South Green** (20s): Allows northbound and southbound traffic
2. **East-West Green** (20s): Allows eastbound and westbound traffic
3. **Left Turns** (15s): Permits left turns from all directions
4. **All Red** (5s): Clearing phase for intersection safety

## 🚨 Special Vehicle Priority

When a special vehicle is detected:
- Normal cycle is immediately interrupted
- Signal switches to green for the special vehicle's direction
- Override remains active until special vehicle passes through
- Normal cycle resumes after override ends

## 🌐 Deployment

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

### Cloud Platforms
- **Heroku**: Push to GitHub and deploy
- **Railway**: Auto-detects and deploys
- **AWS/GCP/Azure**: Use Docker deployment

## 📊 Performance Metrics

- **Simulation Time**: Current simulation duration
- **Vehicles Passed**: Total vehicles that completed their journey
- **Throughput**: Vehicles passing per second
- **Average Wait Time**: Mean waiting time for vehicles
- **Queue Lengths**: Real-time queue monitoring per intersection

## 🎨 Visual Elements

- **Road Network**: 2x2 grid of intersections with connecting roads
- **Traffic Lights**: Color-coded signals (red/yellow/green) that scale with screen size
- **Custom Vehicle Sprites**: Real car and ambulance images with proper directional rotation
- **Custom Road Textures**: Realistic road graphics with transparent backgrounds
- **Responsive Design**: Automatically scales from mobile to desktop screens
- **High DPI Support**: Crisp graphics on retina and high-resolution displays
- **Special Vehicle Alerts**: Ambulance sprites for emergency vehicles
- **Real-time Updates**: Live simulation with smooth visual feedback

## 📱 Scalability Features

- **Responsive Canvas**: Automatically adjusts size based on screen dimensions
- **Proportional Scaling**: All elements scale together maintaining visual consistency
- **Mobile Optimization**: Touch-friendly controls and compact layout
- **High DPI Support**: Sharp graphics on all display types
- **Window Resize**: Real-time adjustment when browser window is resized
- **Fallback Graphics**: Graceful degradation if custom images fail to load

## 🖼️ Image Processing

The simulator includes automatic image processing to remove white backgrounds:

```bash
# Process images to remove white backgrounds
python process_images.py
```

This script:
- Removes white/light backgrounds from vehicle and road images
- Makes backgrounds transparent for seamless integration
- Processes Car.png, Ambulance.png, and Road.png
- Saves processed images to `static/images/`

## 🔧 Configuration

Key parameters can be adjusted in `web_app.py`:
- **Number of Intersections**: Default 4 (2x2 grid)
- **Cycle Length**: Total signal cycle duration (default: 60s)
- **Vehicle Spawn Rate**: Vehicles per second per intersection
- **Special Vehicle Probability**: Chance of emergency vehicle
- **Simulation Speed**: Real-time multiplier

## 📱 Browser Support

- **Desktop**: Full feature set with large canvas
- **Tablet**: Optimized layout with touch controls
- **Mobile**: Compact view with essential features
- **Requirements**: Modern browser with HTML5 Canvas and WebSocket support

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

## 🎯 Use Cases

- **Traffic Engineering**: Study intersection efficiency
- **Education**: Learn about traffic management systems
- **Research**: Test traffic control algorithms
- **Demonstration**: Show traffic light behavior
- **Prototyping**: Develop new traffic management solutions

## 📈 Future Enhancements

- Machine learning-based traffic prediction
- Dynamic signal timing optimization
- Integration with real traffic data
- Advanced vehicle routing algorithms
- Multi-modal transportation support
- 3D visualization
- VR/AR support

## 📄 License

This project is part of a Smart India Hackathon submission for intelligent traffic management systems.

---

**Ready to simulate traffic! 🚦✨**

Open your browser to **http://localhost:5000** and start the simulation!
