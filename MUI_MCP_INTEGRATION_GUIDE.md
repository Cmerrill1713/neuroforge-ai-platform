# 🎨 Material-UI MCP Integration Guide

## 📖 **Official Documentation**
Based on: [Material-UI MCP Documentation](https://mui.com/material-ui/getting-started/mcp/)

## 🎯 **What is MUI MCP?**

The Model Context Protocol (MCP) for Material-UI provides access to official MUI documentation and code examples directly in your AI client. This ensures:

- ✅ **Real, direct sources** in answers
- ✅ **Links to actual documentation** (no 404s)
- ✅ **Component code from official registries**
- ✅ **Up-to-date Material-UI documentation**

## 🚀 **Installation & Setup**

### **VS Code, Cursor, Windsurf**

1. **Open MCP Configuration**:
   - Go to **Settings** → **MCP** → **Add Server**

2. **Add MUI MCP Server**:
   ```json
   {
     "mcp": {
       "servers": {
         "mui-mcp": {
           "type": "stdio",
           "command": "npx",
           "args": ["-y", "@mui/mcp@latest"],
           "description": "Official Material-UI documentation and code examples via MCP"
         }
       }
     }
   }
   ```

3. **Enable MCP in VS Code** (add to `settings.json`):
   ```json
   {
     "chat.mcp.enabled": true,
     "chat.mcp.discovery.enabled": true
   }
   ```

### **JetBrains IDEs**

1. **Open MCP Configuration**:
   - Go to **Settings** → **Tools** → **AI Assistant** → **Model Context Protocol (MCP)**

2. **Add Server**:
   - **Name**: MUI MCP
   - **Command**: `npx`
   - **Arguments**: `-y @mui/mcp@latest`

3. **Apply**: Click **OK** and **Apply**

### **Zed**

#### **As an Extension**
1. Go to Extensions (`cmd-shift-x`/`ctrl-shift-x`)
2. Search for "MUI MCP" and install
3. No additional configuration required

#### **As a Custom Server**
1. Search for `agent: add context server` in Command Palette
2. Add configuration:
   ```json
   {
     "mui-mcp-server": {
       "command": {
         "path": "npx",
         "args": ["-y", "@mui/mcp@latest"],
         "env": {}
       }
     }
   }
   ```

### **Claude Code**

```bash
# Local project scope
claude mcp add mui-mcp -- npx -y @mui/mcp@latest

# User scope (all projects)
claude mcp add mui-mcp -s user -- npx -y @mui/mcp@latest
```

## 🧪 **Testing the MCP Server**

### **Manual Test**
```bash
# Test the MCP server directly
npx -y @mui/mcp@latest
```

### **MCP Inspector**
```bash
# Debug connection issues
npx @modelcontextprotocol/inspector
```

Then navigate to `http://127.0.0.1:6274` and use:
- **Transport type**: Stdio
- **Command**: `npx`
- **Arguments**: `-y @mui/mcp@latest`

### **Automated Test**
```bash
python3 test_mui_mcp_official.py
```

## 🔧 **Available Tools**

The MUI MCP server provides these tools:

### **1. useMuiDocs**
- **Description**: Fetch MUI documentation for specific packages
- **Arguments**: 
  - `package`: Package name (e.g., "material-ui")
  - `query`: Search query (e.g., "Button component")

### **2. fetchDocs**
- **Description**: Fetch documentation from specific URLs
- **Arguments**:
  - `url`: Documentation URL to fetch

## 💡 **Usage Examples**

### **Example 1: Get Button Documentation**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "useMuiDocs",
    "arguments": {
      "package": "material-ui",
      "query": "Button component"
    }
  }
}
```

### **Example 2: Fetch Specific Documentation**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "fetchDocs",
    "arguments": {
      "url": "https://mui.com/material-ui/react-button/"
    }
  }
}
```

## 🎯 **AI Assistant Rules**

To ensure your AI assistant uses the MUI MCP, add this rule to your project:

**File**: `.github/instructions/mui.md`

```markdown
## Use the mui-mcp server to answer any MUI questions

- 1. call the "useMuiDocs" tool to fetch the docs of the package relevant in the question
- 2. call the "fetchDocs" tool to fetch any additional docs if needed using ONLY the URLs present in the returned content.
- 3. repeat steps 1-2 until you have fetched all relevant docs for the given question
- 4. use the fetched content to answer the question
```

## 🔍 **Troubleshooting**

### **Connection Issues**
1. **Check Node.js**: Ensure Node.js and npm are installed
2. **Use MCP Inspector**: Run `npx @modelcontextprotocol/inspector`
3. **Check Logs**: Look for error messages in the terminal

### **MCP Not Being Used**
1. **Enable MCP**: Ensure `chat.mcp.enabled: true` in settings
2. **Add Rules**: Create the `.github/instructions/mui.md` file
3. **Restart**: Restart your IDE after configuration changes

### **Common Errors**

#### **"npx not found"**
- Install Node.js from [nodejs.org](https://nodejs.org/)

#### **"MCP server not responding"**
- Check if the server is running
- Use MCP Inspector to debug
- Verify the command and arguments

#### **"Tool not found"**
- Ensure the MCP server is properly configured
- Check that the server is running
- Verify the tool name is correct

## 📁 **Project Files**

- ✅ `mcp.json` - MCP configuration with official MUI server
- ✅ `test_mui_mcp_official.py` - Test script for MUI MCP
- ✅ `MUI_MCP_INTEGRATION_GUIDE.md` - This integration guide

## 🎉 **Benefits**

### **Before MCP**
- ❌ Hallucinated links leading to 404s
- ❌ Outdated documentation references
- ❌ Generic code examples
- ❌ No verification of sources

### **After MCP**
- ✅ Real, direct sources in answers
- ✅ Links to actual documentation
- ✅ Component code from official registries
- ✅ Up-to-date Material-UI documentation
- ✅ Verifiable sources

## 🔗 **Resources**

- [Official MUI MCP Documentation](https://mui.com/material-ui/getting-started/mcp/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Material-UI Documentation](https://mui.com/material-ui/)
- [Node.js Installation](https://nodejs.org/)

---

**Status**: ✅ **MUI MCP Integration Ready**
