# Setup Guide

Detailed installation and configuration instructions for the WBS MCP Server.

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- Git repository containing `work-items.yaml`
- GitHub CLI (`gh`) for sync functionality
- Claude Desktop or VS Code with GitHub Copilot

## Installation Methods

### Method 1: Direct Install (Recommended for End Users)

Install directly from GitHub:

```bash
# Using uv (faster)
uv pip install git+https://github.com/astenlund74/wbs-mcp-server.git@v2.0.1

# Using pip
pip install git+https://github.com/astenlund74/wbs-mcp-server.git@v2.0.1
```

**Version Pinning**: Pin to specific versions (e.g., `@v2.0.1`) for stability. See [CHANGELOG.md](../CHANGELOG.md) for version history.

### Method 2: Local Development Install

For contributors and local development:

```bash
# Clone repository
git clone https://github.com/astenlund74/wbs-mcp-server.git
cd wbs-mcp-server

# Option A: Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Option B: Using pip
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Verify Installation

Run the test suite:

```bash
pytest tests/ -v
```

Expected: 14 tests passed (8 data loader, 6 yaml writer tests).

## Configuration

### Environment Variables

The server requires one mandatory environment variable:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `WBS_WORK_ITEMS_PATH` | **Yes** | Absolute or relative path to `work-items.yaml` | `/path/to/work-items.yaml` or `${workspaceFolder}/backlog/work-items.yaml` |
| `GITHUB_ORG` | No | GitHub organization/username for sync | `your-org` |
| `GITHUB_PROJECT_NUMBER` | No | GitHub Project number for sync | `2` |

**Important**: The environment variable is `WBS_WORK_ITEMS_PATH` (not `WORK_ITEMS_FILE`).

### VS Code Setup

**File**: `.vscode/mcp.json` in your project root

**Basic Configuration** (read-only):

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
        "WBS_WORK_ITEMS_PATH": "${workspaceFolder}/backlog/work-items.yaml"
      }
    }
  }
}
```

**With GitHub Sync** (read + write):

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

**Local Development**:

```json
{
  "mcpServers": {
    "wbs-project": {
      "command": "uv",
      "args": ["run", "wbs-mcp"],
      "cwd": "/absolute/path/to/wbs-mcp-server",
      "env": {
        "WBS_WORK_ITEMS_PATH": "${workspaceFolder}/backlog/work-items.yaml",
        "GITHUB_ORG": "your-org",
        "GITHUB_PROJECT_NUMBER": "2"
      }
    }
  }
}
```

After editing `.vscode/mcp.json`:
1. Save file
2. Reload VS Code: `Cmd+Shift+P` → "Reload Window"

### Claude Desktop Setup

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Basic Configuration**:

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
        "WBS_WORK_ITEMS_PATH": "/absolute/path/to/work-items.yaml"
      }
    }
  }
}
```

**Important**: Claude Desktop requires **absolute paths** (no `${workspaceFolder}` variable).

**With GitHub Sync**:

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
        "WBS_WORK_ITEMS_PATH": "/Users/yourname/projects/repo/backlog/work-items.yaml",
        "GITHUB_ORG": "your-org",
        "GITHUB_PROJECT_NUMBER": "2"
      }
    }
  }
}
```

After editing config file:
1. Save file
2. **Quit** Claude Desktop completely
3. Relaunch application

## GitHub Integration Setup

For write operations and project sync, configure GitHub CLI:

### 1. Install GitHub CLI

```bash
# macOS
brew install gh

# Windows
winget install GitHub.cli

# Linux
# See https://github.com/cli/cli/blob/trunk/docs/install_linux.md
```

### 2. Authenticate

```bash
gh auth login
```

Select:
- **GitHub.com**
- **HTTPS** protocol
- **Login with a web browser** or paste token

### 3. Grant Project Permissions

The token needs `project` scope. To add:

```bash
gh auth refresh -h github.com -s project
```

### 4. Find Your Project Number

```bash
# List projects for your org
gh project list --owner your-org

# Or view in browser
# URL format: github.com/orgs/YOUR_ORG/projects/NUMBER
```

Set environment variables with your org and project number (see Configuration section above).

### 5. Test Connection

```bash
# Should list your projects
gh project list --owner your-org
```

See [GITHUB-INTEGRATION.md](GITHUB-INTEGRATION.md) for detailed sync documentation.

## Testing the Server

### Standalone Test

```bash
# Direct execution (for debugging)
python -m wbs_mcp.server
```

Server starts and waits for MCP protocol messages on stdin. Press `Ctrl+C` to exit.

### In VS Code

Open Copilot Chat and try:

```
List all work items in progress
```

```
Show me WS-17101
```

Check Output panel (`Cmd+Shift+U`) and select "MCP: wbs-project" for logs.

### In Claude Desktop

Try these queries:

```
What milestones are we tracking?
```

```
Show me the hierarchy under WS-11000
```

Logs: View → Developer Tools → Console tab

## Troubleshooting

### "No tools available" in VS Code/Claude

**Causes**:
1. MCP server failed to start
2. Configuration error in mcp.json / claude_desktop_config.json
3. Python/uv not in PATH

**Solutions**:
1. Check logs (Output panel in VS Code, Developer Tools in Claude)
2. Verify JSON syntax (no trailing commas, quotes correct)
3. Test command manually:
   ```bash
   uv run --with git+https://github.com/astenlund74/wbs-mcp-server.git@v2.0.1 wbs-mcp
   ```
4. Verify uv/python installation: `uv --version`, `python --version`

### "Work items file not found"

**Error message**: `FileNotFoundError: [Errno 2] No such file or directory: '...'`

**Solutions**:
1. Check `WBS_WORK_ITEMS_PATH` points to existing file
2. Use absolute path (especially in Claude Desktop)
3. Verify file name is exactly `work-items.yaml` (case-sensitive)
4. Check file permissions (readable by user running MCP server)

### "GitHub sync failed" / gh CLI errors

**Causes**:
1. GitHub CLI not installed or not authenticated
2. Missing `project` scope on token
3. Wrong `GITHUB_ORG` or `GITHUB_PROJECT_NUMBER`

**Solutions**:
1. Test gh CLI: `gh auth status`
2. Refresh with project scope: `gh auth refresh -h github.com -s project`
3. Verify project number: `gh project list --owner your-org`
4. Check error message for GraphQL errors (field permissions, etc.)

### Type errors during development

**Error**: `mypy` reports errors like `"Module has no attribute X"`

**Solutions**:
1. Install type stubs: `uv pip install types-PyYAML`
2. Run mypy: `mypy wbs_mcp/`
3. Expected: Zero errors

### Tests failing

**Run tests with verbose output**:

```bash
pytest tests/ -v
```

**Expected**: 14 passed tests
- 8 data_loader tests
- 6 yaml_writer tests

If tests fail:
1. Check `tests/fixtures/work-items.yaml` exists
2. Verify `WBS_WORK_ITEMS_PATH` not set in environment (tests use fixture)
3. Update dependencies: `uv pip install -e ".[dev]"`

## Development Setup

### Code Style

Format code:

```bash
black wbs_mcp/ tests/
ruff check wbs_mcp/ tests/ --fix
```

### Type Checking

```bash
mypy wbs_mcp/
```

Should show zero errors.

### Running Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_data_loader.py -v

# With coverage
pytest tests/ --cov=wbs_mcp --cov-report=html
```

### Pre-commit Checks

Before committing:

```bash
# Format
black wbs_mcp/ tests/

# Lint
ruff check wbs_mcp/ tests/ --fix

# Type check
mypy wbs_mcp/

# Test
pytest tests/
```

### CI/CD

GitHub Actions runs automatically on push/PR:
- Tests on Python 3.11, 3.12, 3.13
- Type checking with mypy
- Code formatting checks
- Release automation on version tags

See [.github/workflows/](../.github/workflows/) for workflow definitions.

## Upgrading

### To Latest Release

```bash
# Using uv
uv pip install --upgrade git+https://github.com/astenlund74/wbs-mcp-server.git

# Using pip
pip install --upgrade git+https://github.com/astenlund74/wbs-mcp-server.git
```

**Check changelog first**: [CHANGELOG.md](../CHANGELOG.md)

### To Specific Version

```bash
uv pip install git+https://github.com/astenlund74/wbs-mcp-server.git@v2.0.1
```

**After upgrade**:
1. Update version in configuration (mcp.json / claude_desktop_config.json)
2. Restart VS Code / Claude Desktop
3. Test with simple query: "List all work items"

## Next Steps

- **Tool Reference**: [TOOLS.md](TOOLS.md) - Complete tool documentation
- **GitHub Sync**: [GITHUB-INTEGRATION.md](GITHUB-INTEGRATION.md) - Sync setup and workflows
- **Quick Start**: [QUICKSTART.md](../QUICKSTART.md) - 5-minute setup guide
- **Changelog**: [CHANGELOG.md](../CHANGELOG.md) - Version history

## Support

- **Issues**: https://github.com/astenlund74/wbs-mcp-server/issues
- **Discussions**: https://github.com/astenlund74/wbs-mcp-server/discussions
- **Documentation**: [docs/](.) folder
