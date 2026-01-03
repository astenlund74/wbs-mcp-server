# Quick Start Guide

Get the WBS MCP Server running in 5 minutes.

## Installation (2 minutes)

```bash
# From repository root
cd architecture-work/wbs-mcp-server

# Option A: Using uv (fast!)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv && uv pip install -e ".[dev]"

# Option B: Using pip
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
```

## Verify Installation (30 seconds)

```bash
# Run tests
.venv/bin/pytest tests/ -v

# Should show:
# ✅ 8 passed
```

## Configure Claude Desktop (2 minutes)

### Step 1: Find your config file

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Step 2: Add MCP server configuration

**Important**: Replace `/ABSOLUTE/PATH/TO/REPO` with your actual path!

```json
{
  "mcpServers": {
    "rpds-project": {
      "command": "/ABSOLUTE/PATH/TO/REPO/architecture-work/wbs-mcp-server/.venv/bin/python",
      "args": ["-m", "wbs_mcp.server"]
    }
  }
}
```

**Example** (macOS):
```json
{
  "mcpServers": {
    "wbs-project": {
      "command": "/Users/yourname/repos/architecture-repo/architecture-work/wbs-mcp-server/.venv/bin/python",
      "args": ["-m", "wbs_mcp.server"]
    }
  }
}
```

### Step 3: Restart Claude Desktop

Quit Claude Desktop completely (Cmd+Q on Mac) and relaunch.

## Test It Works (1 minute)

In Claude Desktop, try these queries:

### Query 1: List work items
```
List all work items in progress
```

Expected: You should see items with status "In Progress"

### Query 2: Get specific item
```
Show me details for WS-17101
```

Expected: Full description of the MCP server work item

### Query 3: View hierarchy
```
Show me the hierarchy under WS-17001
```

Expected: Tree view of Documentation Toolchain epic with features

## Troubleshooting

### "No tools available" in Claude

1. Check Claude Desktop logs: View → Developer Tools → Console
2. Look for errors like "Failed to connect to MCP server"
3. Common fixes:
   - Verify absolute path is correct (no `~` shorthand)
   - Verify `.venv/bin/python` exists
   - Try full path: `which python` inside activated venv

### "Work items file not found"

The server looks for: `../../8-REALIZATION/backlog/work-items.yaml`

This path works when running from `architecture-work/wbs-mcp-server/`.

If your structure is different, set environment variable:

```json
{
  "mcpServers": {
    "wbs-project": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "wbs_mcp.server"],
      "env": {
        "WBS_WORK_ITEMS_PATH": "/absolute/path/to/work-items.yaml"
      }
    }
  }
}
```

### Server crashes on startup

Check Python version:
```bash
.venv/bin/python --version
# Should be 3.11 or higher
```

If Python is too old:
```bash
# Recreate venv with newer Python
rm -rf .venv
python3.11 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## What Can I Ask?

### Project Status
- "What milestones are we tracking?"
- "Show me milestone M1.1 progress"
- "List all blocked work items"

### Work Item Details
- "Show me WS-17101"
- "What epics are in the backlog?"
- "List features under WS-11100"

### Data Quality
- "Validate the work items"
- "Find orphan items"
- "Check for consistency issues"

### Planning
- "Show hierarchy for WS-17001"
- "What work is in progress?"
- "List all Todo items in WS1 work stream"

## Next Steps

- Read [TOOLS.md](docs/TOOLS.md) for complete tool reference
- See [SETUP.md](docs/SETUP.md) for advanced configuration
- Try combining tools for analysis workflows

## Getting Help

- Check tool documentation: [docs/TOOLS.md](docs/TOOLS.md)
- Review test examples: [tests/test_data_loader.py](tests/test_data_loader.py)
- Contact Sara (Solution Architect) for issues

---

**Happy querying! 🚀**
