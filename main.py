"""
Main entry point for the Visual Traffic Light Simulator.
"""

import sys
import argparse
from web_app import main as web_main


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Visual Traffic Light Simulator")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to bind to (default: 5000)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Production mode"
    )
    
    args = parser.parse_args()
    
    print("🚦 Visual Traffic Light Simulator")
    print("=" * 50)
    print(f"🌐 Server: http://{args.host}:{args.port}")
    print("🎮 Features: Visual roads, traffic lights, animated vehicles")
    print("🚨 Special: Emergency vehicle priority override")
    print("📊 Real-time: Live metrics and visualization")
    print("-" * 50)
    
    # Import and run the web app with custom arguments
    from web_app import WebTrafficSimulator
    simulator = WebTrafficSimulator()
    simulator.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
