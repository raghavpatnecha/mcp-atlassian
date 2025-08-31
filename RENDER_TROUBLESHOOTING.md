# Render Deployment Troubleshooting

Your MCP server at `https://mcp-atlassian-eexd.onrender.com` is deployed but returning 404 errors.

## 🔍 Diagnosis

The response shows:
- `HTTP/1.1 404 Not Found`
- `x-render-routing: no-server` 

This suggests the Python application isn't starting correctly.

## 🛠️ Fix Steps

### 1. Check Render Logs

In your Render dashboard:
1. Go to your `mcp-atlassian-eexd` service
2. Click **Logs** tab  
3. Look for error messages during startup

Common errors:
- Python module import failures
- Missing environment variables
- Port binding issues
- uv/pip dependency installation failures

### 2. Update Build & Start Commands

In Render dashboard **Settings**:

#### Build Command:
```bash
pip install uv && uv sync --frozen --no-dev --no-editable
```

#### Start Command (Try one of these):
```bash
# Option 1: Direct uv run
uv run mcp-atlassian --host 0.0.0.0 --port $PORT

# Option 2: With explicit module path
python -m mcp_atlassian --host 0.0.0.0 --port $PORT

# Option 3: Using installed binary
mcp-atlassian --host 0.0.0.0 --port $PORT

# Option 4: Fallback to pip install
pip install . && mcp-atlassian --host 0.0.0.0 --port $PORT
```

### 3. Environment Variables Check

Ensure these are set in Render **Environment** tab:
```
PORT=8000
PYTHON_VERSION=3.10
```

### 4. Alternative: Use Docker

If Python builds are failing, switch to Docker in Render:

#### Settings → Build & Deploy:
- **Runtime**: Docker
- **Dockerfile Path**: Dockerfile
- **Docker Command**: (leave empty, uses ENTRYPOINT)

### 5. Test Build Locally

To test the build process:

```bash
# Clone your fork locally
git clone https://github.com/your-username/mcp-atlassian.git
cd mcp-atlassian

# Test the build commands
pip install uv
uv sync --frozen --no-dev --no-editable

# Test the start command
uv run mcp-atlassian --host 0.0.0.0 --port 8000
```

## 🔧 Quick Fixes to Try

### Fix 1: Simplified Start Command
Change start command to just:
```bash
python -c "import mcp_atlassian; mcp_atlassian.main()" --host 0.0.0.0 --port $PORT
```

### Fix 2: Use Standard pip
Change build command to:
```bash
pip install -e .
```

### Fix 3: Check Python Module Structure
The issue might be that the package structure changed. Try:
```bash
python -m src.mcp_atlassian --host 0.0.0.0 --port $PORT
```

## 📱 Alternative: Quick Deploy Test

If you want to test quickly, you can also try deploying a simple test service first:

### Create test-mcp.py:
```python
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import json

class MCPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_POST(self):
        if self.path == '/mcp/':
            self.send_response(200) 
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "tools": [{"name": "test_tool", "description": "Test tool"}]
                }
            }
            self.wfile.write(json.dumps(response).encode())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), MCPHandler)
    print(f"Test MCP server starting on port {port}")
    server.serve_forever()
```

### Deploy with:
- **Build Command**: `echo "No build needed"`
- **Start Command**: `python test-mcp.py`

This will help confirm Render is working and we can then fix the main MCP server.

## 📞 Next Steps

1. **Check Render logs** - Most important step
2. **Try the simplified start commands** above  
3. **Test locally** to verify the build process
4. **Switch to Docker** if Python builds keep failing
5. **Deploy test service** to isolate the issue

Once we see the Render logs, we can identify the exact issue and fix it quickly!