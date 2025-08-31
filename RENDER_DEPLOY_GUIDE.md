# Render Deployment Guide - Atlassian MCP Server

Deploy the Atlassian MCP server to Render's **free tier** with automatic HTTPS and continuous deployment.

## 🆓 Why Render?

- **Free Tier**: 750 hours/month (perfect for MCP servers)
- **Automatic HTTPS**: Built-in SSL certificates
- **Zero Configuration**: Automatic deployments from GitHub
- **Python Support**: Excellent Python/uv support
- **Persistent URLs**: Stable URLs that don't change

## 🚀 Step 1: Prepare Repository

### Option A: Fork the Original Repository
1. Go to https://github.com/sooperset/mcp-atlassian
2. Click "Fork" to create your copy
3. Add the Render configuration files (created in this guide)

### Option B: Use This Pre-configured Version
If you have the files locally with Render configs:
```bash
cd mcp-atlassian
git add render.yaml requirements.txt gunicorn.conf.py
git commit -m "Add Render deployment configuration"
git push origin main
```

## 🌐 Step 2: Deploy to Render

### 1. Create Render Account
- Go to https://render.com
- Sign up with GitHub (recommended)
- Connect your GitHub account

### 2. Create New Web Service
1. **Dashboard** → **New** → **Web Service**
2. **Connect Repository**:
   - Select your forked `mcp-atlassian` repository
   - Branch: `main`
3. **Configure Service**:
   ```
   Name: xerus-atlassian-mcp
   Region: Oregon (US West) or nearest to you
   Branch: main
   Runtime: Python 3
   Build Command: pip install uv && uv sync --frozen --no-dev --no-editable
   Start Command: uv run mcp-atlassian --port $PORT --host 0.0.0.0 --oauth-enable
   Plan: Free
   ```

### 3. Environment Variables
Add these in Render dashboard under **Environment**:

#### Required OAuth Variables:
```
ATLASSIAN_OAUTH_CLIENT_ID=your_client_id_here
ATLASSIAN_OAUTH_CLIENT_SECRET=your_client_secret_here  
ATLASSIAN_OAUTH_CLOUD_ID=your_cloud_id_here
ATLASSIAN_OAUTH_REDIRECT_URI=https://xerus-atlassian-mcp.onrender.com/oauth2callback
ATLASSIAN_OAUTH_SCOPE=read:jira-user read:jira-work write:jira-work manage:jira-project read:confluence-content.all write:confluence-content offline_access
```

#### Optional Configuration:
```
PYTHON_VERSION=3.10
PORT=8000
```

### 4. Deploy!
Click **Create Web Service** - Render will:
- Clone your repository
- Install Python dependencies with uv
- Deploy your application
- Provide a free HTTPS URL like: `https://xerus-atlassian-mcp.onrender.com`

## 🔐 Step 3: Atlassian OAuth Setup

### 1. Create Atlassian OAuth App
1. **Go to Atlassian Developer Console:**
   - Visit: https://developer.atlassian.com/console/myapps/
   - Click "Create" → "OAuth 2.0 (3LO)"

2. **Configure App:**
   ```
   App name: Xerus AI Assistant
   Description: AI assistant for Jira and Confluence
   ```

3. **Set Permissions (Scopes):**
   ```
   Jira API:
   ✅ read:jira-user
   ✅ read:jira-work  
   ✅ write:jira-work
   ✅ manage:jira-project
   ✅ offline_access
   
   Confluence API:
   ✅ read:confluence-space.summary
   ✅ read:confluence-props
   ✅ write:confluence-props
   ✅ read:confluence-content.all
   ✅ write:confluence-content
   ✅ offline_access
   ```

4. **Callback URLs:**
   ```
   https://xerus-atlassian-mcp.onrender.com/oauth2callback
   https://xerus-atlassian-mcp.onrender.com/auth/callback
   ```

5. **Copy Credentials:**
   - Client ID → Render environment variables
   - Client Secret → Render environment variables

### 2. Get Atlassian Cloud ID

#### Method 1: Browser Console
1. Go to any page in your Atlassian instance
2. Open browser console (F12)
3. Run:
   ```javascript
   AP.getLocation(function(location) {
       console.log('Cloud ID:', location.cloudId);
   });
   ```

#### Method 2: API Call
```bash
curl -u your-email@domain.com:your-api-token \
  "https://your-domain.atlassian.net/rest/api/3/serverInfo" \
  | jq '.cloudId'
```

## ✅ Step 4: Verify Deployment

### 1. Check Render Logs
- Go to your service dashboard in Render
- Click **Logs** tab
- Look for successful startup messages

### 2. Test Health Endpoint
```bash
curl https://xerus-atlassian-mcp.onrender.com/health
# Should return: {"status": "healthy", "timestamp": "..."}
```

### 3. Test MCP Capabilities
```bash
curl -X POST https://xerus-atlassian-mcp.onrender.com/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

### 4. Test OAuth Flow
1. Visit: `https://xerus-atlassian-mcp.onrender.com/oauth2callback`
2. Should redirect to Atlassian OAuth page
3. Complete authentication
4. Verify successful callback

## 🔧 Step 5: Update Xerus Configuration

Update Xerus to use your deployed Render URL:

### File: `glass/backend/services/mcp/mcpManager.js`
```javascript
// Update Atlassian MCP Server
this.serverRegistry.set('atlassian-remote', {
  name: 'Atlassian',
  description: 'Jira and Confluence integration with issue management, project tracking, and documentation',
  type: 'remote',
  url: 'https://xerus-atlassian-mcp.onrender.com/mcp/',
  category: 'productivity',
  authType: 'oauth',
  oauthCallbackUrl: 'https://xerus-atlassian-mcp.onrender.com/oauth2callback',
  // ... rest of existing configuration
});
```

### Update Database:
```bash
cd glass/backend
node scripts/update-mcp-urls.js atlassian-remote https://xerus-atlassian-mcp.onrender.com/mcp/
```

## 🧪 Step 6: Test Integration

### 1. Start Xerus Backend
```bash
cd glass/backend && npm run dev
```

### 2. Test MCP Registration
```bash
curl http://localhost:5001/api/v1/tools/mcp-servers
# Should show Atlassian server with Render URL
```

### 3. Test via Xerus Tools Page
1. Go to http://localhost:3000/tools
2. Find "Atlassian" MCP server
3. Click "Configure" → Complete OAuth flow
4. Click "Enable" → Server should show as connected

### 4. Test AI Integration
- Ask Xerus: "Show me my Jira projects"  
- Ask Xerus: "Search for API documentation in Confluence"
- Ask Xerus: "Create a test issue in Jira"

## 🚨 Troubleshooting

### Common Issues

1. **Build Failures:**
   - Check Render build logs for Python/uv errors
   - Verify `pyproject.toml` and `uv.lock` are in repository
   - Fallback: Use `requirements.txt` with standard pip

2. **OAuth Errors:**
   - Verify callback URL exactly matches: `https://your-app.onrender.com/oauth2callback`
   - Check all required scopes are configured in Atlassian app
   - Ensure `offline_access` is included for token refresh

3. **MCP Connection Issues:**
   - Test health endpoint: `curl https://your-app.onrender.com/health`
   - Check MCP endpoint: `curl -X POST https://your-app.onrender.com/mcp/ -d '...'`
   - Verify CORS settings if needed

4. **Render Service Issues:**
   - **Sleep Mode**: Free tier services sleep after 15 minutes of inactivity
   - **Cold Starts**: First request after sleep takes ~30 seconds
   - **Memory Limits**: Free tier has 512MB RAM limit

### Monitoring

- **Render Dashboard**: Service metrics and logs
- **Health Checks**: Automatic monitoring via `/health` endpoint
- **Uptime**: Render provides 99.9% uptime for paid plans, 99.0% for free

## 🎯 Production Considerations

### Free Tier Limitations
- **Sleep after 15 min** of inactivity
- **750 hours/month** total runtime
- **512MB RAM** limit
- **Cold starts** after sleep

### Upgrade Benefits ($7/month)
- **Always-on** (no sleeping)
- **Custom domains**
- **More RAM** and CPU
- **Priority support**

## 📈 Next Steps

1. **Monitor Usage**: Track your 750 free hours
2. **Set Alerts**: Configure Render notifications
3. **Custom Domain**: Add your domain (paid plan)  
4. **Backup Strategy**: Export OAuth tokens if needed
5. **Scale Up**: Upgrade to paid plan when ready

## 🎉 Success!

Your Atlassian MCP server is now running on Render with:
- ✅ **Free HTTPS hosting**
- ✅ **Automatic deployments** from GitHub
- ✅ **OAuth 2.0 integration** with Atlassian
- ✅ **MCP protocol compliance**
- ✅ **Xerus AI integration** ready

The server will be available at: `https://xerus-atlassian-mcp.onrender.com` 🚀