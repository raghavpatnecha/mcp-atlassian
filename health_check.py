#!/usr/bin/env python3
"""
Simple health check script for the Atlassian MCP server
Tests if the server is responding on the expected endpoints
"""
import os
import sys
import json
import urllib.request
import urllib.error

def check_health(base_url="http://localhost:10000"):
    """Check if the MCP server is healthy"""
    endpoints_to_check = [
        f"{base_url}/mcp",
        f"{base_url}/health", 
        f"{base_url}/"
    ]
    
    print(f"🏥 Health check for Atlassian MCP server")
    print(f"🌐 Base URL: {base_url}")
    print("=" * 50)
    
    results = {}
    
    for endpoint in endpoints_to_check:
        try:
            print(f"📡 Testing {endpoint}...")
            
            req = urllib.request.Request(endpoint)
            req.add_header('User-Agent', 'MCP-Health-Check/1.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                status = response.status
                content_type = response.headers.get('Content-Type', 'unknown')
                content = response.read().decode('utf-8')
                
                print(f"   ✅ {status} - {content_type}")
                
                # Try to parse JSON if content type suggests it
                if 'json' in content_type.lower():
                    try:
                        parsed = json.loads(content)
                        print(f"   📄 Response: {json.dumps(parsed, indent=2)[:200]}")
                    except json.JSONDecodeError:
                        print(f"   📄 Response: {content[:100]}...")
                else:
                    print(f"   📄 Response: {content[:100]}...")
                
                results[endpoint] = {"status": status, "success": True}
                
        except urllib.error.HTTPError as e:
            print(f"   ❌ HTTP {e.code} - {e.reason}")
            results[endpoint] = {"status": e.code, "success": False, "error": str(e)}
            
        except urllib.error.URLError as e:
            print(f"   ❌ Connection error: {e.reason}")
            results[endpoint] = {"status": 0, "success": False, "error": str(e)}
            
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            results[endpoint] = {"status": 0, "success": False, "error": str(e)}
        
        print()
    
    # Summary
    successful = sum(1 for r in results.values() if r["success"])
    total = len(results)
    
    print("=" * 50)
    print(f"🎯 Results: {successful}/{total} endpoints responding")
    
    if successful > 0:
        print("✅ Server appears to be running!")
        return True
    else:
        print("❌ Server appears to be down or not accessible")
        return False

if __name__ == "__main__":
    # Get base URL from environment or use default
    port = os.environ.get("PORT", "10000")
    host = os.environ.get("HOST", "localhost")
    base_url = f"http://{host}:{port}"
    
    # Allow override from command line
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    success = check_health(base_url)
    sys.exit(0 if success else 1)