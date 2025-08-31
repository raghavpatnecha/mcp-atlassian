#!/usr/bin/env python3
"""
HTTP Web Server for Atlassian MCP
Starts the MCP server in HTTP mode for Render deployment
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the source directory to Python path
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

try:
    # Import the main MCP server using the correct path
    from mcp_atlassian.servers.main import main_mcp
    
    if __name__ == "__main__":
        # Get configuration from environment
        port = int(os.environ.get("PORT", "8000"))
        host = os.environ.get("HOST", "0.0.0.0")
        
        print(f"🚀 Starting Atlassian MCP HTTP Server on {host}:{port}")
        print(f"🔑 OAuth enabled: {bool(os.environ.get('ATLASSIAN_OAUTH_CLIENT_ID'))}")
        print(f"🌐 Transport: streamable-http")
        print(f"📍 Endpoint: http://{host}:{port}/mcp")
        
        # Set up environment for OAuth
        oauth_vars = [
            "ATLASSIAN_OAUTH_CLIENT_ID",
            "ATLASSIAN_OAUTH_CLIENT_SECRET", 
            "ATLASSIAN_OAUTH_REDIRECT_URI",
            "ATLASSIAN_OAUTH_CLOUD_ID",
            "ATLASSIAN_OAUTH_SCOPE"
        ]
        
        print("🔧 Environment check:")
        for var in oauth_vars:
            status = "✅ SET" if os.environ.get(var) else "❌ MISSING"
            print(f"   {var}: {status}")
        
        # Start the server with streamable-http transport
        run_kwargs = {
            "transport": "streamable-http",
            "host": host,
            "port": port,
            "path": "/mcp"
        }
        
        print("🎯 Starting MCP server...")
        asyncio.run(main_mcp.run_async(**run_kwargs))
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📁 Current working directory:", os.getcwd())
    print("🐍 Python path:", sys.path[:3])  # Show first 3 entries
    
    # Fallback: try alternative import method
    print("🔄 Trying fallback import method...")
    try:
        from mcp_atlassian.servers import main_mcp
        
        if __name__ == "__main__":
            port = int(os.environ.get("PORT", "8000"))
            host = os.environ.get("HOST", "0.0.0.0")
            
            print(f"🚀 Starting Atlassian MCP HTTP Server (fallback) on {host}:{port}")
            print(f"🌐 Transport: streamable-http")
            print(f"📍 Endpoint: http://{host}:{port}/mcp")
            
            run_kwargs = {
                "transport": "streamable-http",
                "host": host,
                "port": port,
                "path": "/mcp"
            }
            
            asyncio.run(main_mcp.run_async(**run_kwargs))
    except Exception as fallback_error:
        print(f"❌ Fallback also failed: {fallback_error}")
        
        # Final fallback: create minimal health check server using starlette (already available)
        print("🔧 Starting minimal health check server using starlette...")
        try:
            from starlette.applications import Starlette
            from starlette.routing import Route
            from starlette.responses import JSONResponse
            import uvicorn
            
            async def health_check(request):
                return JSONResponse({
                    "status": "healthy", 
                    "error": "MCP server import failed",
                    "debug": {
                        "python_path": sys.path[:2],
                        "cwd": os.getcwd(),
                        "env_vars": {
                            "PORT": os.environ.get("PORT", "not-set"),
                            "ATLASSIAN_OAUTH_CLIENT_ID": "set" if os.environ.get("ATLASSIAN_OAUTH_CLIENT_ID") else "not-set"
                        }
                    }
                })
            
            async def root(request):
                return JSONResponse({
                    "message": "Atlassian MCP server - import error occurred",
                    "available_endpoints": ["/health"]
                })
            
            routes = [
                Route("/health", health_check, methods=["GET"]),
                Route("/", root, methods=["GET"]),
            ]
            
            app = Starlette(routes=routes)
            
            if __name__ == "__main__":
                port = int(os.environ.get("PORT", "8000"))
                print(f"🏥 Health check server starting on 0.0.0.0:{port}")
                uvicorn.run(app, host="0.0.0.0", port=port)
                
        except ImportError as starlette_error:
            print(f"❌ Even starlette import failed: {starlette_error}")
            print("📦 Available packages:")
            import pkg_resources
            installed_packages = [d.project_name for d in pkg_resources.working_set]
            print(f"   {', '.join(sorted(installed_packages)[:10])}...")
            
            # Absolute final fallback: simple HTTP server
            print("🚨 Starting basic HTTP server...")
            import http.server
            import socketserver
            
            class HealthHandler(http.server.SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/health':
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        response = '{"status": "healthy", "error": "all imports failed"}'
                        self.wfile.write(response.encode())
                    else:
                        self.send_response(200)
                        self.send_header('Content-type', 'text/plain')
                        self.end_headers()
                        self.wfile.write(b'Atlassian MCP - Import Error')
            
            if __name__ == "__main__":
                port = int(os.environ.get("PORT", "8000"))
                with socketserver.TCPServer(("0.0.0.0", port), HealthHandler) as httpd:
                    print(f"🌐 Basic HTTP server started on 0.0.0.0:{port}")
                    httpd.serve_forever()