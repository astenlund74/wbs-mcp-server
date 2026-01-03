# WBS MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-0.9.0-green.svg)](https://modelcontextprotocol.io)

Model Context Protocol (MCP) server enabling AI agents to interact with GitHub Projects managed using Work Breakdown Structure (WBS) methodology via `work-items.yaml`.

## Features

### Read Operations

- **list_work_items** - Filter by status, type, epic, milestone, parent
- **get_work_item** - Retrieve single item by WBS ID or issue number
- **get_hierarchy** - View epic→feature→task tree with progress rollup
- **validate_sync** - Check work-items.yaml consistency
- **find_orphans** - Detect items without parent or milestone
- **get_milestone_coverage** - Track progress by milestone

### Write Operations

- **update_work_item** - Modify work item fields with optional GitHub sync
- **list_pr_review_threads** - Read PR review comments (auto-detects from branch)
- **reply_to_review_thread** - Reply to review feedback
- **resolve_review_thread** - Mark review threads as resolved

## Quick Start

### Installation

\`\`\`bash

# Using uv (recommended)

uv pip install git+<https://github.com/astenlund74/wbs-mcp-server.git@v2.0.1>

# Using pip

pip install git+<https://github.com/astenlund74/wbs-mcp-server.git@v2.0.1>
\`\`\`

### Configuration

**VS Code** - Add to \`.vscode/mcp.json\`:

\`\`\`json
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
\`\`\`

**Claude Desktop** - Add to config file:

- macOS: \`~/Library/Application Support/Claude/claude_desktop_config.json\`
- Windows: \`%APPDATA%\\Claude\\claude_desktop_config.json\`

\`\`\`json
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
\`\`\`

Restart your IDE or Claude Desktop after configuration.

## Usage Examples

### List Work Items

\`\`\`
AI: "Show me all tasks in Todo status for Milestone M1.1"
\`\`\`

### View Progress

\`\`\`
AI: "What's the status of Epic WS-11000?"
\`\`\`

### Update Status

\`\`\`
AI: "Move WS-17101 to Done and sync to GitHub"
\`\`\`

### PR Review

\`\`\`
AI: "List unresolved review comments on my PR"
AI: "Reply to thread abc123 with 'Fixed in latest commit'"
\`\`\`

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[docs/SETUP.md](docs/SETUP.md)** - Detailed installation and configuration
- **[docs/TOOLS.md](docs/TOOLS.md)** - Complete tool reference with examples
- **[docs/GITHUB-INTEGRATION.md](docs/GITHUB-INTEGRATION.md)** - GitHub Projects sync configuration
- **[docs/RELEASE-PROCESS.md](docs/RELEASE-PROCESS.md)** - CI/CD and versioning
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

## Requirements

- Python 3.11+
- Git repository with \`work-items.yaml\` following WBS structure
- GitHub CLI (\`gh\`) for write operations
- GitHub token with \`project\` scope (for sync operations)

## Development

\`\`\`bash
git clone <https://github.com/astenlund74/wbs-mcp-server.git>
cd wbs-mcp-server
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest tests/  # All 14 tests should pass
\`\`\`

## Architecture

The server uses:

- **MCP SDK 0.9.0** for protocol implementation
- **Pydantic** for data validation
- **ruamel.yaml** for format-preserving YAML updates
- **GitHub CLI** for GraphQL API access

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Issues and pull requests welcome at <https://github.com/astenlund74/wbs-mcp-server>

## Support

- **Documentation**: See [docs/](docs/) folder
- **Issues**: <https://github.com/astenlund74/wbs-mcp-server/issues>
- **Discussions**: <https://github.com/astenlund74/wbs-mcp-server/discussions>
