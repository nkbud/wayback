# Wayback MCP Server Deployment Guide

This guide covers deployment options for the Wayback MCP Server.

## Quick Start

### Using Docker (Recommended)

```bash
# Pull the latest image
docker pull wayback-mcp-server:latest

# Run the server
docker run -p 8000:8000 wayback-mcp-server:latest
```

### Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/edgi-govdata-archiving/wayback.git
cd wayback

# Start the service
docker-compose up -d
```

### Local Installation

```bash
# Install with MCP dependencies
pip install -e .[mcp]

# Run the server
wayback-mcp-server --host 0.0.0.0 --port 8000
```

## Configuration

### Environment Variables

- `MCP_SERVER_HOST`: Host to bind to (default: localhost)
- `MCP_SERVER_PORT`: Port to bind to (default: 8000)
- `PYTHONPATH`: Path to wayback source code

### Docker Environment

```bash
docker run -p 8000:8000 \
  -e MCP_SERVER_HOST=0.0.0.0 \
  -e MCP_SERVER_PORT=8000 \
  wayback-mcp-server:latest
```

## Production Deployment

### Using Docker Swarm

```yaml
version: '3.8'
services:
  wayback-mcp:
    image: wayback-mcp-server:latest
    ports:
      - "8000:8000"
    environment:
      - MCP_SERVER_HOST=0.0.0.0
      - MCP_SERVER_PORT=8000
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### Using Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wayback-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: wayback-mcp-server
  template:
    metadata:
      labels:
        app: wayback-mcp-server
    spec:
      containers:
      - name: wayback-mcp-server
        image: wayback-mcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: MCP_SERVER_HOST
          value: "0.0.0.0"
        - name: MCP_SERVER_PORT
          value: "8000"
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
---
apiVersion: v1
kind: Service
metadata:
  name: wayback-mcp-service
spec:
  selector:
    app: wayback-mcp-server
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Health Monitoring

The server includes health check endpoints:

```bash
# Check if server is running
curl http://localhost:8000/health

# Check available tools
curl http://localhost:8000/tools

# Check resources
curl http://localhost:8000/resources
```

## Scaling Considerations

- The server is stateless and can be scaled horizontally
- Each instance can handle multiple concurrent requests
- Consider rate limiting for external API calls (Library of Congress, etc.)
- Monitor memory usage for large search results

## Security

- Run containers as non-root user (already configured)
- Use HTTPS in production with a reverse proxy
- Implement rate limiting and authentication as needed
- Monitor for unusual API usage patterns

## Troubleshooting

### Common Issues

1. **FastMCP Import Error**
   ```bash
   pip install fastmcp
   ```

2. **Docker Build Fails**
   ```bash
   # Clear Docker cache
   docker system prune -a
   ```

3. **Port Already in Use**
   ```bash
   # Use different port
   docker run -p 8001:8000 wayback-mcp-server:latest
   ```

### Logs

```bash
# Docker logs
docker logs <container_id>

# Follow logs
docker logs -f <container_id>
```

## Integration Examples

### With Claude/ChatGPT

```python
# Example MCP client integration
import requests

def search_historical_pages(url, from_date=None, to_date=None):
    response = requests.post('http://localhost:8000/tools/search_wayback', 
                           json={
                               'url': url,
                               'from_date': from_date,
                               'to_date': to_date,
                               'limit': 10
                           })
    return response.json()
```

### With LangChain

```python
from langchain.tools import BaseTool

class WaybackSearchTool(BaseTool):
    name = "wayback_search"
    description = "Search for historical versions of web pages"
    
    def _run(self, url: str, from_date: str = None) -> str:
        # Implementation using MCP server
        pass
```

## Performance Optimization

- Use persistent connections for repeated requests
- Implement caching for frequently requested data
- Consider using a CDN for static responses
- Monitor and optimize database queries if added

## Support

For issues and questions:
- GitHub Issues: https://github.com/edgi-govdata-archiving/wayback/issues
- Documentation: See `docs/mcp-server.md`