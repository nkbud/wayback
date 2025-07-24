# Wayback MCP Server

A Model Context Protocol (MCP) server that provides AI agents with access to historical web pages and digital archives, with a focus on high-authority sources.

## Features

- **Wayback Machine Integration**: Search and retrieve historical web page captures
- **High-Authority Sources**: Prioritized access to authoritative digital collections
- **Library of Congress**: Direct integration with LoC digital collections
- **Extensible Design**: Easy to add new archives and collections
- **Authority Metadata**: Clear indicators of source reliability and authority level

## Installation

### From Source

```bash
git clone https://github.com/edgi-govdata-archiving/wayback.git
cd wayback
pip install -e .[mcp]
```

### Using Docker

```bash
# Build the image
docker build -t wayback-mcp-server .

# Run the container
docker run -p 8000:8000 wayback-mcp-server
```

## Usage

### Running the Server

#### Command Line
```bash
wayback-mcp-server --host 0.0.0.0 --port 8000
```

#### Python Module
```bash
python -m wayback.mcp_server.server
```

#### Docker
```bash
docker run -p 8000:8000 wayback-mcp-server
```

### Available Tools

#### `search_wayback`
Search for historical captures of a URL in the Wayback Machine.

**Parameters:**
- `url` (string): The URL to search for historical captures
- `from_date` (string, optional): Start date for search (YYYY-MM-DD format)
- `to_date` (string, optional): End date for search (YYYY-MM-DD format)
- `limit` (integer, default=10): Maximum number of results to return

**Example:**
```json
{
  "tool": "search_wayback",
  "arguments": {
    "url": "https://nasa.gov",
    "from_date": "2010-01-01",
    "to_date": "2015-12-31",
    "limit": 5
  }
}
```

#### `get_wayback_memento`
Retrieve a specific historical capture (memento) from the Wayback Machine.

**Parameters:**
- `url` (string): The original URL that was captured
- `timestamp` (string): The timestamp of the capture (ISO format: YYYY-MM-DDTHH:MM:SS)
- `mode` (string, default="original"): Playback mode - 'original', 'view', 'javascript', 'css', or 'image'

**Example:**
```json
{
  "tool": "get_wayback_memento",
  "arguments": {
    "url": "https://nasa.gov",
    "timestamp": "2010-06-15T12:00:00",
    "mode": "view"
  }
}
```

#### `search_library_of_congress`
Search the Library of Congress digital collections.

**Parameters:**
- `query` (string): Search query terms
- `limit` (integer, default=10): Maximum number of results to return

**Example:**
```json
{
  "tool": "search_library_of_congress",
  "arguments": {
    "query": "space exploration",
    "limit": 5
  }
}
```

### Available Resources

#### `api_endpoints`
Provides documentation of all available MCP tools and their corresponding API endpoints.

#### `supported_sources`
Lists all supported high-authority digital archive sources with authority ratings.

## API Endpoint Mappings

| MCP Tool | API Endpoint | Authority Level | Source |
|----------|--------------|-----------------|---------|
| `search_wayback` | `https://web.archive.org/cdx/search/cdx` | High | Internet Archive |
| `get_wayback_memento` | `https://web.archive.org/web/{timestamp}/{url}` | High | Internet Archive |
| `search_library_of_congress` | `https://www.loc.gov/search/` | Highest | Library of Congress |

## Authority Levels

- **Highest**: National libraries, government archives (e.g., Library of Congress)
- **High**: Established archives like Internet Archive
- **Medium**: Academic institutions, established organizations
- **Low**: General web archives, smaller collections

## Configuration

The server can be configured using environment variables:

- `MCP_SERVER_HOST`: Host to bind to (default: localhost)
- `MCP_SERVER_PORT`: Port to bind to (default: 8000)
- `PYTHONPATH`: Should include the path to the wayback source code

## Docker Hub

The Docker image is available on Docker Hub:

```bash
docker pull wayback-mcp-server:latest
```

## Adding New Sources

To add a new high-authority source:

1. Create a new tool function in `src/wayback/mcp_server/server.py`
2. Use the `@mcp.tool()` decorator
3. Follow the naming convention: `search_{source_name}`
4. Include authority metadata in the response
5. Update the resources (`api_endpoints` and `supported_sources`)
6. Add documentation to this README

Example:
```python
@mcp.tool()
def search_europeana(query: str, limit: int = 10) -> str:
    """Search Europeana digital collections."""
    # Implementation here
    pass
```

## Development

### Running Tests
```bash
python -m pytest src/wayback/tests/
```

### Building Docker Image
```bash
docker build -t wayback-mcp-server:latest .
```

### Publishing to Docker Hub
```bash
docker tag wayback-mcp-server:latest your-username/wayback-mcp-server:latest
docker push your-username/wayback-mcp-server:latest
```

## License

This project is licensed under the same license as the wayback library - BSD (3-clause).

## Contributing

Please see the main wayback repository's contributing guidelines.