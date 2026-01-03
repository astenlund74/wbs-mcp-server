# RPDS Project MCP Server - Setup Guide

## Prerequisites

- Python 3.11 or higher
- Access to RPDS architecture repository
- Claude Desktop (for testing integration)

## Installation

### Option 1: Using uv (Recommended)

```bash
cd architecture-work/2026-01-03-mcp-server

# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Option 2: Using pip

```bash
cd architecture-work/2026-01-03-mcp-server

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

## Testing

Run the test suite to verify everything works:

```bash
pytest tests/ -v
```

Expected output:
```
tests/test_data_loader.py::test_load_work_items PASSED
tests/test_data_loader.py::test_get_by_wbs_id PASSED
tests/test_data_loader.py::test_get_by_issue_number PASSED
tests/test_data_loader.py::test_filter_by_status PASSED
tests/test_data_loader.py::test_filter_by_type PASSED
tests/test_data_loader.py::test_filter_by_milestone PASSED
tests/test_data_loader.py::test_filter_by_parent PASSED
tests/test_data_loader.py::test_caching PASSED
```

## Running the Server

### Standalone Testing

Test the server manually:

```bash
python -m wbs_mcp.server
```

The server will start and wait for MCP protocol messages on stdin.

### Claude Desktop Integration

1. **Configure Claude Desktop**

Edit your Claude Desktop config file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the MCP server:

```json
{
  "mcpServers": {
    "rpds-project": {
      "command": "python",
      "args": [
        "-m",
        "wbs_mcp.server"
      ],
      "cwd": "/absolute/path/to/architecture-work/wbs-mcp-server",
      "env": {
        "PYTHONPATH": "/absolute/path/to/architecture-work/wbs-mcp-server"
      }
    }
  }
}
```

**Important**: Replace `/absolute/path/to/` with the actual path to your repo.

2. **Restart Claude Desktop**

Quit and relaunch Claude Desktop to load the new MCP server.

3. **Verify Connection**

In Claude Desktop, you should see the RPDS Project tools available. Try asking:

- "List all work items in progress"
- "Show me details for WS-17101"
- "What epics are in milestone M1.1?"

## VS Code Integration (Copilot)

If using GitHub Copilot with MCP support:

1. Open VS Code settings (`Cmd+,` or `Ctrl+,`)
2. Search for "MCP Servers"
3. Add configuration similar to Claude Desktop setup above

## Available Tools

### 1. list_work_items

Filter and list work items from the backlog.

**Parameters**:
- `status` (optional): Filter by status (e.g., "Todo", "In Progress", "Done")
- `wbs_type` (optional): Filter by type (e.g., "Epic", "Feature")
- `milestone` (optional): Filter by milestone (partial match)
- `work_stream` (optional): Filter by work stream
- `parent_wbs` (optional): Show children of specific epic
- `limit` (optional): Max results (default: 50)

**Example queries**:
- "Show me all epics"
- "List work items in progress"
- "What features are in WS-17001?"

### 2. get_work_item

Get detailed information about a specific work item.

**Parameters**:
- `wbs_id` OR `issue_number`: Identifier for the work item

**Example queries**:
- "Show me WS-17101"
- "Get details for issue #54"

## Troubleshooting

### Server Won't Start

Check that:
1. Virtual environment is activated
2. All dependencies installed (`pip list` should show `mcp`, `pydantic`, `pyyaml`)
3. Path to work-items.yaml is correct

### Claude Desktop Can't Connect

1. Check logs: Claude Desktop → View → Developer Tools → Console
2. Verify JSON config syntax is valid
3. Ensure absolute paths are correct
4. Try restarting Claude Desktop

### "Work items file not found" Error

The server looks for work-items.yaml at:
```
../../8-REALIZATION/backlog/work-items.yaml
```

This assumes you're running from the `architecture-work/wbs-mcp-server/` directory.

If your setup is different, you can set an environment variable:

```bash
export WBS_WORK_ITEMS_PATH="/path/to/work-items.yaml"
python -m wbs_mcp.server
```

## Development

### Code Style

Format code with black and ruff:

```bash
black wbs_mcp/
ruff check wbs_mcp/ --fix
```

### Type Checking

Run mypy for type validation:

```bash
mypy wbs_mcp/
```

### Adding New Tools

See [TOOLS.md](TOOLS.md) for guide on implementing additional tools (Phase 2).

## Support

For issues or questions:
- Check GitHub issues for WS-17101
- Contact Sara (Solution Architect)
