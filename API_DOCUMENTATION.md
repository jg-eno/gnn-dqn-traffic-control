# 🚦 Traffic Simulator API Documentation

## Overview

This document describes the API endpoints and WebSocket events for the NYC Traffic Light Simulator.

## WebSocket Events

### Client to Server Events

#### `start_simulation`
Start the traffic simulation.
```javascript
socket.emit('start_simulation');
```

#### `stop_simulation`
Stop the traffic simulation.
```javascript
socket.emit('stop_simulation');
```

#### `reset_simulation`
Reset the simulation to initial state.
```javascript
socket.emit('reset_simulation');
```

#### `add_special_vehicle`
Add a special vehicle to a specific intersection and lane.
```javascript
socket.emit('add_special_vehicle', {
    intersection_id: 'intersection_1',
    lane: 'north'
});
```

#### `set_signal_override`
Manually override a traffic signal using the centralized signal controller.
```javascript
socket.emit('set_signal_override', {
    intersection_id: 'intersection_1',
    direction: 'north',
    signal: 'green'  // 'red', 'yellow', 'green'
});
```

#### `set_auto_mode`
Set a signal back to automatic mode.
```javascript
socket.emit('set_auto_mode', {
    intersection_id: 'intersection_1',
    direction: 'north'
});
```

#### `emergency_override`
Set emergency override (green light) for a specific direction.
```javascript
socket.emit('emergency_override', {
    intersection_id: 'intersection_1',
    direction: 'north',
    duration: 30.0  // Duration in seconds
});
```

#### `set_ai_control`
Set AI control for a specific signal.
```javascript
socket.emit('set_ai_control', {
    intersection_id: 'intersection_1',
    direction: 'north',
    signal: 'green',
    duration: 60.0  // Optional duration in seconds
});
```

#### `get_signal_states`
Get all current signal states and control summary.
```javascript
socket.emit('get_signal_states');
```

### Server to Client Events

#### `simulation_update`
Real-time simulation data updates.
```javascript
socket.on('simulation_update', (data) => {
    console.log('Simulation data:', data);
    // data contains:
    // - intersections: Array of intersection data
    // - metrics: Simulation metrics
    // - traffic_data: NYC traffic data information
});
```

#### `simulation_started`
Confirmation that simulation has started.
```javascript
socket.on('simulation_started', () => {
    console.log('Simulation started');
});
```

#### `simulation_stopped`
Confirmation that simulation has stopped.
```javascript
socket.on('simulation_stopped', () => {
    console.log('Simulation stopped');
});
```

#### `override_set`
Confirmation that signal override has been set.
```javascript
socket.on('override_set', (data) => {
    console.log('Signal override set:', data);
    // data contains: intersection_id, direction, signal, success
});
```

#### `auto_mode_set`
Confirmation that auto mode has been set.
```javascript
socket.on('auto_mode_set', (data) => {
    console.log('Auto mode set:', data);
    // data contains: intersection_id, direction, success
});
```

#### `emergency_override_set`
Confirmation that emergency override has been set.
```javascript
socket.on('emergency_override_set', (data) => {
    console.log('Emergency override set:', data);
    // data contains: intersection_id, direction, duration, success
});
```

#### `ai_control_set`
Confirmation that AI control has been set.
```javascript
socket.on('ai_control_set', (data) => {
    console.log('AI control set:', data);
    // data contains: intersection_id, direction, signal, duration, success
});
```

#### `signal_states`
Response with all signal states and control summary.
```javascript
socket.on('signal_states', (data) => {
    console.log('Signal states:', data);
    // data contains: signal_states, control_summary
});
```

## Data Structures

### Intersection Data
```javascript
{
    intersection_id: 'intersection_1',
    current_phase: 'north_south_green',
    phase_elapsed: 15.5,
    queue_lengths: {
        north: 5,
        south: 3,
        east: 8,
        west: 2
    },
    signal_colors: {
        north: 'green',
        south: 'green',
        east: 'red',
        west: 'red'
    }
}
```

### Simulation Metrics
```javascript
{
    simulation_time: 120.5,
    total_vehicles_spawned: 150,
    total_vehicles_passed: 120,
    total_special_vehicles_spawned: 8,
    total_wait_time: 450.2,
    average_wait_time: 3.75,
    throughput: 1.0,
    is_running: true,
    traffic_data: {
        using_real_data: true,
        current_time_minutes: 2.0,
        progress_percentage: 5.7,
        average_flow: 142.6,
        peak_flow: 485.0,
        min_flow: 12.0
    }
}
```

### NYC Traffic Data
```javascript
{
    using_real_data: true,
    current_time_minutes: 2.0,
    progress_percentage: 5.7,
    average_flow: 142.6,
    peak_flow: 485.0,
    min_flow: 12.0
}
```

## HTTP Endpoints

### GET `/`
Serves the main web interface.

### GET `/static/<path>`
Serves static files (CSS, JS, images).

## Error Handling

### WebSocket Errors
```javascript
socket.on('error', (error) => {
    console.error('WebSocket error:', error);
});
```

### Connection Events
```javascript
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
});
```

## Usage Examples

### Basic Simulation Control
```javascript
// Connect to the server
const socket = io();

// Start simulation
socket.emit('start_simulation');

// Listen for updates
socket.on('simulation_update', (data) => {
    // Update UI with new data
    updateSimulationDisplay(data);
});

// Stop simulation
socket.emit('stop_simulation');
```

### Manual Signal Control
```javascript
// Override a signal to green
socket.emit('set_signal_override', {
    intersection_id: 'intersection_1',
    direction: 'north',
    signal: 'green'
});

// Set back to automatic
socket.emit('set_auto_mode', {
    intersection_id: 'intersection_1',
    direction: 'north'
});
```

### Special Vehicle Management
```javascript
// Add emergency vehicle
socket.emit('add_special_vehicle', {
    intersection_id: 'intersection_2',
    lane: 'east'
});
```

## Configuration

### Server Configuration
```python
# In web_app.py
app.config.update(
    DEBUG=True,
    SECRET_KEY='your-secret-key'
)

# WebSocket configuration
socketio = SocketIO(app, cors_allowed_origins="*")
```

### Client Configuration
```javascript
// Socket.IO client configuration
const socket = io({
    transports: ['websocket'],
    upgrade: true,
    rememberUpgrade: true
});
```

## Performance Considerations

### Update Frequency
- Simulation updates are sent at 1-second intervals
- WebSocket events are optimized for real-time performance
- Data structures are minimized for efficient transmission

### Scalability
- Supports multiple concurrent clients
- Efficient data serialization
- Optimized WebSocket event handling

## Security

### CORS Configuration
```python
# Allow cross-origin requests for development
socketio = SocketIO(app, cors_allowed_origins="*")
```

### Input Validation
- All WebSocket events are validated on the server
- Malformed requests are rejected with error messages
- Rate limiting prevents abuse

---

This API documentation provides comprehensive information for integrating with the NYC Traffic Light Simulator system.
