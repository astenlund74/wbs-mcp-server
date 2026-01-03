# WBS MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-0.9.0-green.svg)](https://modelcontextprotocol.io)

Model Context Protocol (MCP) server for AI agents to interact with GitHub Projects managed using Work Breakdown Structure (WBS) methodology via `work-items.yaml`.

## Features

### 📖 Read Operations (Phase 1)
- **list_work_items** - Filter by status, type, epic, milestone, parent
- **get_work_item** - Retrieve single item by WBS ID or issue number
- **get_hierarchy** - View epic→feature→task tree with progress rollup
- **validate_sync** - Check work-items.yaml consistency
- **find_orphans** - Detect items without parent or milestone
- **get_milestone_coverage** - Track progress by milestone

### ✏️ Write Operations (Phase 2)
- **update_work_item** - Modify work item fields with optional GitHub sync
- **list_pr_review_threads** - Read PR review comments (auto-detects from branch)
- **reply_to_review_thread** - Reply to review feedback
- **resolve_review_thread** - Mark review threads as resolved

## Why This Tool?

Managing architecture backlogs requires structured work breakdown, progress tracking, and AI agent integration. This server bridges GitHub Projects with AI assistants (Claude Desktop, VS Code Copilot) using the Model Context Protocol.

**Use Cases**:
- Architecture teams tracking epics, features, tasks
- Project managers monitoring milestone progress
- AI agents autonomously replying to PR reviews
- Automated work item updates with audit trails

## Installation

### Prerequisites
- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- Git repository with `work-items.yaml` in `8-REALIZATION/backlog/`

### Install from GitHub

```bash
# Using uv (recommended)
uv pip install git+https://github.com/astenlund74/wbs-mcp-server.git

# Using pip
pip install git+https://github.com/astenlund74/wbs-mcp-server.git
```

### Local Development

```bash
git clone https://github.com/astenlund74/wbs-mcp-server.git
cd wbs-mcp-server
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
pytest tests/  # Run tests
```

## Quick Start

### VS Code Copilot Integration

Add to your `.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "wbs-project": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/wbs-mcp-server",
        "run",
        "wbs_mcp"
      ],
      "env": {
        "WORK_ITEMS_FILE": "${workspaceFolder}/8-REALIZATION/backlog/work-items.yaml",
        "SYNC_SCRIPT_PATH": "${workspaceFolder}/tools/sync-github-project.sh"
      }
    }
  }
}
```

### Claude Desktop Integration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "wbs-project": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/wbs-mcp-server",
        "run",
        "wbs_mcp"
      ],
      "env": {
        "WORK_ITEMS_FILE": "/path/to/your-repo/8-REALIZATION/backlog/work-items.yaml",
        "SYNC_SCRIPT_PATH": "/path/to/your-repo/tools/sync-github-project.sh"
      }
    }
  }
}
```

**Restart Claude Desktop** after updating configuration.

## Usage Examples

### List Active Tasks
```
AI Agent: "Show me all tasks in Todo status for Milestone M1.1"
→ Calls: list_work_items(status="Todo", milestone="M1.1", wbs_type="Task")
```

### View Progress Hierarchy
```
AI Agent: "What's the status of Epic WS-11000?"
→ Calls: get_hierarchy(root_wbs="WS-11000")
→ Returns: Tree with all features/tasks under epic with progress %
```

### Update Work Item
```
AI Agent: "Move WS-17101 to Done and set effort to 8 days"
→ Calls: update_work_item(wbs_id="WS-17101", updates={status: "Done", effort_days: 8})
```

### PR Review Workflow
```
AI Agent: "Review and respond to PR feedback"
→ Calls: list_pr_review_threads() [auto-detects current PR]
→ Calls: reply_to_review_thread(thread_id, "Fixed in commit abc123")
→ Calls: resolve_review_thread(thread_id)
```

## Project Structure

```
wbs-mcp-server/
├── README.md                    # This file
├── pyproject.toml              # Python project config (Poetry/uv)
├── wbs_mcp/                    # Python package
│   ├── __init__.py
│   ├── server.py               # MCP server main
│   ├── models.py               # Pydantic models for WorkItem
│   ├── tools/                  # Tool implementations
│   │   ├── __init__.py
│   │   ├── list_work_items.py
│   │   ├── get_work_item.py
│   │   ├── get_hierarchy.py
│   │   ├── validate_sync.py
│   │   ├── find_orphans.py
│   │   └── get_milestone_coverage.py
│   └── data_loader.py          # YAML loading & caching
├── tests/                      # Unit tests
│   ├── test_tools.py
│   └── test_data_loader.py
└── docs/
    ├── SETUP.md                # Installation guide
    ├── TOOLS.md                # Tool reference
    └── INTEGRATION.md          # Claude Desktop config
```

## Development Approach

**Vertical Slice Delivery**: Implement tools one-by-one with full testing, not all at once.

### Sprint Plan

- **Day 1**: Server scaffold + `list_work_items` (working end-to-end)
- **Day 2**: `get_work_item` + `get_hierarchy` 
- **Day 3**: `validate_sync` + `find_orphans`
- **Day 4**: `get_milestone_coverage` + polish
- **Day 5**: Documentation + Claude Desktop integration guide

## Success Criteria

- [x] All 6 tools implemented and tested
- [x] Response time < 500ms per query
- [x] Zero writes to work-items.yaml (read-only guarantee)
- [ ] Works with Claude Desktop (config provided)
- [x] Clear documentation for setup and usage

## Implementation Status

✅ **PHASE 1 COMPLETE** - All 6 read-only tools implemented:

1. ✅ `list_work_items` - Filter and list work items
2. ✅ `get_work_item` - Get detailed item information
3. ✅ `get_hierarchy` - View epic→feature tree with progress
4. ✅ `validate_sync` - Check data consistency
5. ✅ `find_orphans` - Find items missing relationships
6. ✅ `get_milestone_coverage` - Track milestone progress

**Tests**: 8/8 passing  
**Documentation**: Complete (SETUP.md, TOOLS.md)  
**Ready for**: Claude Desktop integration testing

## Next Steps

1. Set up Python project structure with Poetry/uv
2. Implement MCP server scaffold
3. Implement first tool (`list_work_items`) with full testing
4. Test integration with Claude Desktop
5. Iterate through remaining tools

---

**Note**: This is a generic WBS MCP server. Can be used with any architecture repository following the Work Breakdown Structure pattern, not specific to RPDS.
