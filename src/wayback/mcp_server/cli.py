#!/usr/bin/env python3
"""
Command-line interface for the Wayback MCP Server
"""

import argparse
import sys
from wayback.mcp_server.server import run_server


def main():
    parser = argparse.ArgumentParser(
        description="Wayback MCP Server - Model Context Protocol server for digital archives"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Wayback MCP Server 1.0.0"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind the server to (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    
    args = parser.parse_args()
    
    print(f"Starting Wayback MCP Server on {args.host}:{args.port}")
    print("Available tools:")
    print("  - search_wayback: Search Wayback Machine for historical captures")
    print("  - get_wayback_memento: Retrieve specific historical capture")
    print("  - search_library_of_congress: Search Library of Congress collections")
    print("\nAvailable resources:")
    print("  - api_endpoints: Documentation of tool-to-endpoint mappings")
    print("  - supported_sources: List of supported high-authority sources")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        # Set host and port for the server (if supported by FastMCP)
        run_server()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()