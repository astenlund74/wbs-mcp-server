# Quick Start Guide

Get the WBS MCP Server running in 5 minutes.

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- Git repository with `work-items.yaml`

## Installation

### Option 1: Direct Install (Recommended)

```bash
# Using uv
uv pip install git+https://github.com/astenlund74/wbs-mcp-server.git@v2.0.1

# Using pip
pip install git+https://github.com/astenlund74/wbs-mcp-server.git@v2.0.1
```

### Option 2: Local Development

```bash
git clone https://github.com/astenlund74/wbs-mcp-server.git
cd wbs-mcp-server
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest tests/  # Verify installation: should show 14 passed
```

## Configuration

### VS Code

Create `.vscode/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "wbs-project": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "git+https://github.com/astenlund74/wbs-mcp-server.git@v2.0.1",
        "wbs-mcp"
      ],
      "env": {
        "WBS_WORK_ITEMS_PATH": "${workspaceFolder}/backlog/work-items.yaml",
        "GITHUB_ORG": "your-org",
        "GITHUB_PROJECT_NUMBER": "2"
      }
    }
  }
}
```

**Important**: Replace `your-org` and project number with your actual values.

Reload VS Code window: `Cmd+Shift+P` → "Reload Window"

### Claude Desktop

**macOS**: Edit `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: Edit `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "wbs-project": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "git+https://github.com/astenlund74/wbs-mcp-server.git@v2.0.1",
        "wbs-mcp"
      ],
      "env": {
        "WBS_WORK_ITEMS_PATH": "/absolute/path/to/work-items.yaml",
        "GITHUB_ORG": "your-org",
        "GITHUB_PROJECT_NUMBER": "2"
      }
    }
  }
}
```

Restart Claude Desktop completely (Quit and relaunch).

## Test It Works

### In VS Code Copilot

Try these queries:

```
List all work items in progress
```

```
Show me details for WS-17101
```

```
What's the status of milestone M1.1?
```

### In Claude Desktop

```
List all tasks in Todo status
```

```
Show me the hierarchy under epic WS-11000
```

## Troubleshooting

### "No tools available"

1. Check logs (VS Code: Output panel, Claude: View → Developer Tools)
2. Verify `WBS_WORK_ITEMS_PATH` points to existing file
3. Ensure `work-items.yaml` has correct structure

### "Work items file not found"

Update environment variable to absolute path:

```json
{
  "env": {
    "WBS_WORK_ITEMS_PATH": "/Users/yourname/projects/repo/backlog/work-items.yaml"
  }
}
```

### GitHub sync not working

Ensure you have:
1. GitHub CLI installed: `gh --version`
2. Authenticated: `gh auth login`
3. Token has `project` scope
4. Set `GITHUB_ORG` and `GITHUB_PROJECT_NUMBER` correctly

## Example Queries

**Project Status:**
- "What milestones are we tracking?"
- "Show me milestone M1.1 progress"
- "List all blocked work items"

**Work Item Details:**
- "Show me WS-17101"
- "What epics are in the backlog?"
- "List features under epic WS-11100"

**Data Quality:**
- "Validate the work items"
- "Find orphan items"
- "Check for consistency issues"

**Updates:**
- "Move WS-17101 to Done"
- "Update WS-17102 priority to High and sync to GitHub"

**PR Reviews:**
- "List unresolved review comments"
- "Reply to thread abc123"
- "Resolve all my review threads"

## Next Steps

- Review [docs/TOOLS.md](docs/TOOLS.md) for complete tool reference
- See [docs/SETUP.md](docs/SETUP.md) for advanced configuration
- Read [docs/GITHUB-INTEGRATION.md](docs/GITHUB-INTEGRATION.md) for sync setup

## Getting Help

- **Documentation**: [docs/](docs/) folder
- **Issues**: https://github.com/astenlund74/wbs-mcp-server/issues
- **Discussions**: https://github.com/astenlund74/wbs-mcp-server/discussions
