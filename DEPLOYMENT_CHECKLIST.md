# Atlassian MCP Server Deployment Checklist

## ✅ Pre-Deployment (Completed)

- [x] Created Render configuration files (`render.yaml`, `requirements.txt`, `gunicorn.conf.py`)
- [x] Added Atlassian MCP to Xerus database
- [x] Fixed Atlassian icon visibility issue  
- [x] Updated icon mappings and database scripts
- [x] Created comprehensive deployment guides
- [x] Prepared Xerus integration scripts

## 🚀 Deployment Steps (Manual)

### Step 1: Fork Repository & Add Config
- [ ] Fork https://github.com/sooperset/mcp-atlassian to your GitHub
- [ ] Add the configuration files to your fork:
  - `render.yaml`
  - `requirements.txt`  
  - `gunicorn.conf.py`
  - `RENDER_DEPLOY_GUIDE.md`
- [ ] Commit and push changes

### Step 2: Deploy to Render
- [ ] Sign up at https://render.com (free account)
- [ ] Create new Web Service from your GitHub repository
- [ ] Configure build settings:
  ```
  Build Command: pip install uv && uv sync --frozen --no-dev --no-editable
  Start Command: uv run mcp-atlassian --port $PORT --host 0.0.0.0 --oauth-enable
  Plan: Free
  ```

### Step 3: Set Environment Variables in Render
- [ ] `ATLASSIAN_OAUTH_CLIENT_ID` (from Atlassian Developer Console)
- [ ] `ATLASSIAN_OAUTH_CLIENT_SECRET` (from Atlassian Developer Console)
- [ ] `ATLASSIAN_OAUTH_CLOUD_ID` (from Atlassian API)
- [ ] `ATLASSIAN_OAUTH_REDIRECT_URI=https://your-app.onrender.com/oauth2callback`
- [ ] `ATLASSIAN_OAUTH_SCOPE=read:jira-user read:jira-work write:jira-work manage:jira-project read:confluence-content.all write:confluence-content offline_access`

## 🔐 OAuth Configuration

### Step 1: Atlassian Developer Console
- [ ] Go to https://developer.atlassian.com/console/myapps/
- [ ] Create new "OAuth 2.0 (3LO)" app
- [ ] Set app name: "Xerus AI Assistant"
- [ ] Configure required scopes (see deployment guide)
- [ ] Set callback URL: `https://your-app.onrender.com/oauth2callback`
- [ ] Copy Client ID and Secret to Render environment variables

### Step 2: Get Atlassian Cloud ID
- [ ] Use browser console method OR API call (see guide)
- [ ] Add Cloud ID to Render environment variables

## 🔧 Xerus Integration

### Step 1: Update Configuration
- [ ] Run the URL update script:
  ```bash
  cd glass/backend
  node scripts/update-mcp-urls.js
  ```
- [ ] Restart Xerus backend to pick up changes

### Step 2: Database Updates  
- [ ] Verify Atlassian MCP server is in database:
  ```bash
  node scripts/check-schema.js
  ```

## 🧪 Testing

### Step 1: Test Render Deployment
- [ ] Health check: `curl https://your-app.onrender.com/health`
- [ ] MCP capabilities: `curl -X POST https://your-app.onrender.com/mcp/ ...`
- [ ] OAuth flow: Visit callback URL and test authentication

### Step 2: Test Xerus Integration
- [ ] Start Xerus backend: `cd glass/backend && npm run dev`
- [ ] Test MCP registration: `curl localhost:5001/api/v1/tools/mcp-servers`
- [ ] Test via tools page: http://localhost:3000/tools
- [ ] Configure and enable Atlassian MCP server
- [ ] Test AI queries: "Show me my Jira projects"

## 📊 Post-Deployment

### Step 1: Monitor
- [ ] Check Render service logs for errors
- [ ] Monitor free tier usage (750 hours/month)
- [ ] Set up Render notifications for issues

### Step 2: Documentation
- [ ] Update team documentation with new URLs
- [ ] Document OAuth setup process for future reference
- [ ] Create troubleshooting guide for common issues

## 🎯 Success Criteria

- [ ] ✅ Render service shows "Live" status
- [ ] ✅ Health endpoint returns 200 OK
- [ ] ✅ MCP capabilities endpoint works
- [ ] ✅ OAuth flow completes successfully
- [ ] ✅ Xerus shows Atlassian server as "Connected"
- [ ] ✅ AI can successfully query Jira projects
- [ ] ✅ AI can search Confluence pages
- [ ] ✅ Tool execution logs show successful operations

## 🚨 Troubleshooting Quick Reference

### Render Issues
- **Build Fails**: Check logs, verify uv/pip install
- **Service Won't Start**: Check start command and port binding
- **Service Sleeps**: Normal on free tier (15 min inactivity)

### OAuth Issues  
- **Callback Error**: Verify exact URL match in Atlassian app
- **Scope Error**: Ensure all required scopes are configured
- **Token Refresh**: Verify `offline_access` scope is included

### Xerus Integration Issues
- **Server Not Found**: Run URL update script
- **Connection Failed**: Check Render service is live and accessible  
- **Tool Execution Failed**: Check OAuth tokens and permissions

---

**Total Estimated Time**: 30-45 minutes for complete deployment and testing

**Key URLs After Deployment**:
- Render Service: `https://xerus-atlassian-mcp.onrender.com`
- Health Check: `https://xerus-atlassian-mcp.onrender.com/health`
- MCP Endpoint: `https://xerus-atlassian-mcp.onrender.com/mcp/`
- OAuth Callback: `https://xerus-atlassian-mcp.onrender.com/oauth2callback`