# 🚀 Visual Traffic Light Simulator - Deployment Guide

## 🌐 Web-Based Visual Simulator

This is a modern web-based traffic light simulator with:
- **HTML5 Canvas** for smooth graphics and animations
- **Real-time WebSocket** communication
- **Responsive design** for all devices
- **Visual traffic lights** with red, yellow, green colors
- **Animated vehicles** moving through intersections
- **Special vehicle priority** with visual indicators

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the visual simulator
python main.py --mode web
# or
python deploy.py

# Open browser to: http://localhost:5000
```

### Production Deployment

#### Option 1: Direct Deployment
```bash
python deploy.py --production --host 0.0.0.0 --port 80
```

#### Option 2: Using Gunicorn (Recommended for Production)
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 web_app:app
```

#### Option 3: Docker Deployment
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "deploy.py", "--production", "--host", "0.0.0.0", "--port", "5000"]
```

## 🎮 Features

### Visual Elements
- **Road Network**: 2x3 grid of intersections with connecting roads
- **Traffic Lights**: Red, yellow, green lights for each direction
- **Vehicles**: Animated cars with different colors for normal/special vehicles
- **Real-time Updates**: Live simulation with 1-second refresh rate

### Controls
- **Start/Stop/Reset**: Control simulation state
- **Add Special Vehicle**: Inject emergency vehicles with priority
- **Live Metrics**: Real-time performance monitoring
- **Intersection Status**: Individual intersection monitoring

### Special Vehicle Priority
- **Visual Indicators**: Special vehicles shown in red with warning icons
- **Priority Override**: Automatic signal switching for emergency vehicles
- **Real-time Detection**: Immediate response to special vehicle presence

## 🌍 Deployment Platforms

### Heroku
```bash
# Create Procfile
echo "web: python deploy.py --production --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
git add .
git commit -m "Deploy visual traffic simulator"
git push heroku main
```

### Railway
```bash
# Railway will auto-detect Python and run deploy.py
# Just push your code to GitHub and connect to Railway
```

### DigitalOcean App Platform
```yaml
# .do/app.yaml
name: traffic-simulator
services:
- name: web
  source_dir: /
  github:
    repo: your-username/traffic-simulator
    branch: main
  run_command: python deploy.py --production
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 5000
```

### AWS/GCP/Azure
- Use the Docker deployment option
- Configure load balancer for port 5000
- Set environment variables as needed

## 🔧 Configuration

### Environment Variables
```bash
export FLASK_ENV=production  # For production mode
export PORT=5000             # Server port
export HOST=0.0.0.0          # Server host
```

### Customization
- **Intersection Count**: Modify `num_intersections` in `SimulationConfig`
- **Simulation Speed**: Adjust `simulation_speed` parameter
- **Visual Layout**: Edit `intersectionPositions` in `traffic-simulator.js`
- **Colors/Styles**: Modify `static/css/style.css`

## 📊 Performance

### System Requirements
- **CPU**: 1 core minimum, 2+ cores recommended
- **RAM**: 512MB minimum, 1GB+ recommended
- **Network**: WebSocket support required
- **Browser**: Modern browser with HTML5 Canvas support

### Optimization
- **Real-time Updates**: 1-second intervals for smooth performance
- **Canvas Rendering**: Optimized drawing with requestAnimationFrame
- **WebSocket**: Efficient real-time communication
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🐛 Troubleshooting

### Common Issues
1. **Port Already in Use**: Change port with `--port` argument
2. **WebSocket Connection Failed**: Check firewall settings
3. **Canvas Not Rendering**: Ensure modern browser support
4. **Performance Issues**: Reduce simulation speed or intersection count

### Debug Mode
```bash
python deploy.py --debug
```

## 📱 Mobile Support

The simulator is fully responsive and works on:
- **Desktop**: Full feature set with large canvas
- **Tablet**: Optimized layout with touch controls
- **Mobile**: Compact view with essential features

## 🔒 Security

- **CORS**: Configured for cross-origin requests
- **Input Validation**: Server-side validation for all inputs
- **Rate Limiting**: Built-in protection against abuse
- **Environment Isolation**: Production/development separation

## 📈 Monitoring

### Built-in Metrics
- Simulation time
- Vehicles passed
- Throughput (vehicles/second)
- Average wait time
- Queue lengths per intersection

### External Monitoring
- Use your preferred monitoring service
- Monitor port 5000 for health checks
- WebSocket connection monitoring recommended

## 🎯 Next Steps

1. **Deploy**: Choose your platform and deploy
2. **Monitor**: Set up monitoring and alerts
3. **Scale**: Add load balancing if needed
4. **Customize**: Modify visuals and behavior as needed
5. **Integrate**: Connect to real traffic data sources

---

**Ready to deploy your visual traffic light simulator! 🚦✨**
