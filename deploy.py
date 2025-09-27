#!/usr/bin/env python3
"""
Deployment script for the visual traffic simulator.
Supports both local development and production deployment.
"""

import os
import sys
import argparse
from web_app import WebTrafficSimulator


def main():
    parser = argparse.ArgumentParser(description='Deploy Visual Traffic Simulator')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--production', action='store_true', help='Production mode')
    
    args = parser.parse_args()
    
    # Production configuration
    if args.production:
        os.environ['FLASK_ENV'] = 'production'
        args.debug = False
        print("🚀 Starting in PRODUCTION mode")
    else:
        print("🔧 Starting in DEVELOPMENT mode")
    
    # Create and run the simulator
    simulator = WebTrafficSimulator()
    
    print(f"🌐 Visual Traffic Light Simulator")
    print(f"📍 Server: http://{args.host}:{args.port}")
    print(f"🎮 Controls: Start/Stop/Reset simulation")
    print(f"🚨 Features: Special vehicle priority override")
    print(f"📊 Real-time: Live metrics and visualization")
    print("-" * 50)
    
    simulator.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
