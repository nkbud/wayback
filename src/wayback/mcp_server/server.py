"""
MCP Server for Wayback Machine and Digital Archive Access

This server provides tools for accessing historical web pages and digital
archives, with a focus on high-authority sources.
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
import json

try:
    from fastmcp import FastMCP
except ImportError:
    raise ImportError(
        "FastMCP is not installed. Please install with: pip install fastmcp"
    )

from .. import WaybackClient, CdxRecord, Memento
from ..exceptions import WaybackException


# Initialize the MCP server
mcp = FastMCP("Wayback Archive Server")


@mcp.tool()
def search_wayback(
    url: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    Search for historical captures of a URL in the Wayback Machine.
    
    Args:
        url: The URL to search for historical captures
        from_date: Start date for search (YYYY-MM-DD format, optional)
        to_date: End date for search (YYYY-MM-DD format, optional)
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        JSON string containing list of historical captures with metadata
    """
    try:
        client = WaybackClient()
        
        # Parse dates if provided
        from_dt = None
        to_dt = None
        if from_date:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d").date()
        if to_date:
            to_dt = datetime.strptime(to_date, "%Y-%m-%d").date()
        
        # Search for captures
        results = []
        count = 0
        for record in client.search(url, from_date=from_dt, to_date=to_dt):
            if count >= limit:
                break
            
            result = {
                "timestamp": record.timestamp.isoformat() if record.timestamp else None,
                "url": record.url,
                "urlkey": record.urlkey,
                "status_code": record.status_code,
                "mime_type": record.mime_type,
                "length": record.length,
                "digest": record.digest,
                "authority": "Internet Archive Wayback Machine",
                "source_type": "web_archive"
            }
            results.append(result)
            count += 1
        
        return json.dumps({
            "query_url": url,
            "results": results,
            "total_found": len(results),
            "authority_level": "high",
            "source_authority": "Internet Archive"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "query_url": url,
            "results": []
        }, indent=2)


@mcp.tool()
def get_wayback_memento(
    url: str,
    timestamp: str,
    mode: str = "original"
) -> str:
    """
    Retrieve a specific historical capture (memento) from the Wayback Machine.
    
    Args:
        url: The original URL that was captured
        timestamp: The timestamp of the capture (ISO format: YYYY-MM-DDTHH:MM:SS)
        mode: Playback mode - 'original', 'view', 'javascript', 'css', or 'image'
    
    Returns:
        JSON string with memento details and content information
    """
    try:
        client = WaybackClient()
        
        # Parse timestamp
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        # Map mode string to Mode enum
        from .. import Mode
        mode_map = {
            'original': Mode.original,
            'view': Mode.view,
            'javascript': Mode.javascript,
            'css': Mode.css,
            'image': Mode.image
        }
        
        playback_mode = mode_map.get(mode, Mode.original)
        
        # Get the memento
        memento = client.get_memento(url, timestamp=dt, mode=playback_mode)
        
        result = {
            "url": memento.url,
            "timestamp": memento.timestamp.isoformat() if memento.timestamp else None,
            "mode": mode,
            "status_code": memento.status_code,
            "headers": dict(memento.headers) if memento.headers else {},
            "content_length": len(memento.text) if memento.text else 0,
            "content_preview": (memento.text[:500] + "..." if len(memento.text) > 500 else memento.text) if memento.text else None,
            "authority": "Internet Archive Wayback Machine",
            "source_type": "web_archive"
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "url": url,
            "timestamp": timestamp
        }, indent=2)


@mcp.tool()
def search_library_of_congress(
    query: str,
    limit: int = 10
) -> str:
    """
    Search the Library of Congress digital collections.
    
    Args:
        query: Search query terms
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        JSON string with search results from Library of Congress
    """
    try:
        import requests
        
        # Library of Congress API endpoint
        url = "https://www.loc.gov/search/"
        params = {
            "q": query,
            "fo": "json",
            "c": limit
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        results = []
        for item in data.get("results", [])[:limit]:
            result = {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
                "date": item.get("date", ""),
                "format": item.get("format", []),
                "subject": item.get("subject", []),
                "authority": "Library of Congress",
                "source_type": "digital_library",
                "authority_level": "highest"
            }
            results.append(result)
        
        return json.dumps({
            "query": query,
            "results": results,
            "total_found": len(results),
            "authority_level": "highest",
            "source_authority": "Library of Congress"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "query": query,
            "results": []
        }, indent=2)


@mcp.resource("api_endpoints")
def get_api_endpoints() -> str:
    """
    Provides documentation of all available MCP tools and their corresponding API endpoints.
    
    Returns:
        JSON documentation of tool-to-endpoint mappings
    """
    endpoints = {
        "wayback_tools": {
            "search_wayback": {
                "description": "Search Wayback Machine for historical captures",
                "api_endpoint": "https://web.archive.org/cdx/search/cdx",
                "authority_level": "high",
                "source": "Internet Archive Wayback Machine"
            },
            "get_wayback_memento": {
                "description": "Retrieve specific historical capture",
                "api_endpoint": "https://web.archive.org/web/{timestamp}/{url}",
                "authority_level": "high",
                "source": "Internet Archive Wayback Machine"
            }
        },
        "high_authority_sources": {
            "search_library_of_congress": {
                "description": "Search Library of Congress digital collections",
                "api_endpoint": "https://www.loc.gov/search/",
                "authority_level": "highest",
                "source": "Library of Congress"
            }
        },
        "authority_levels": {
            "highest": "National libraries, government archives",
            "high": "Established archives like Internet Archive",
            "medium": "Academic institutions, established organizations",
            "low": "General web archives, smaller collections"
        }
    }
    
    return json.dumps(endpoints, indent=2)


@mcp.resource("supported_sources")
def get_supported_sources() -> str:
    """
    Lists all supported high-authority digital archive sources.
    
    Returns:
        JSON list of supported sources with authority ratings
    """
    sources = {
        "internet_archive": {
            "name": "Internet Archive Wayback Machine",
            "authority_level": "high",
            "description": "Comprehensive web archive with historical captures",
            "tools": ["search_wayback", "get_wayback_memento"],
            "base_url": "https://web.archive.org/"
        },
        "library_of_congress": {
            "name": "Library of Congress",
            "authority_level": "highest",
            "description": "National library of the United States",
            "tools": ["search_library_of_congress"],
            "base_url": "https://www.loc.gov/"
        }
    }
    
    return json.dumps(sources, indent=2)


def run_server():
    """Run the MCP server"""
    mcp.run()


if __name__ == "__main__":
    run_server()