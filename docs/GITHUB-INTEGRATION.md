# GitHub Integration Refactoring

## Overview

As of v0.2.0, the WBS MCP Server uses **direct GitHub API integration** instead of shell scripts for work item synchronization.

## Architecture Change

### Before (v0.1.x)
```
MCP Tool → Shell Script (sync-github-project.sh) → gh CLI → GitHub GraphQL API
```

**Problems:**
- Required `SYNC_SCRIPT_PATH` environment variable
- Script must exist in target repository
- Hard to test and debug
- Subprocess overhead

### After (v0.2.0)
```
MCP Tool → GitHubProjectSync (Python) → gh CLI → GitHub GraphQL API
```

**Benefits:**
- ✅ No external scripts required
- ✅ Self-contained Python implementation
- ✅ Easier testing (mock GitHubProjectSync)
- ✅ Better error handling
- ✅ Cached field/project lookups

## Configuration

### Required Environment Variables

```jsonc
{
  "env": {
    // Work items file path (required)
    "WBS_WORK_ITEMS_PATH": "${workspaceFolder}/8-REALIZATION/backlog/work-items.yaml",
    
    // GitHub org/project (required for sync)
    "GITHUB_ORG": "techseed-codex",
    "GITHUB_PROJECT_NUMBER": "2",
    
    // GitHub token (optional - falls back to gh CLI)
    "GITHUB_TOKEN": "ghp_..."
  }
}
```

### Removed Variables

- ❌ `SYNC_SCRIPT_PATH` - No longer needed!

## Implementation Details

### GitHubProjectSync Class

Located in `wbs_mcp/github_sync.py`:

```python
from wbs_mcp.github_sync import GitHubProjectSync

# Initialize sync client
sync = GitHubProjectSync()

# Update single field
sync.update_item_field(
    issue_number=123,
    field_name="Status",
    value="In Progress"
)

# Sync multiple fields
sync.sync_work_item(
    issue_number=123,
    updates={
        "status": "In Progress",
        "priority": "🔴 High"
    }
)
```

### Features

1. **Field Mapping**
   - YAML fields automatically mapped to GitHub Project fields
   - Validates field values against project configuration
   - Clear error messages for invalid values

2. **Caching**
   - Project ID cached after first lookup
   - Field configurations cached per field name
   - Reduces API calls significantly

3. **Error Handling**
   - Graceful fallback if item not in project
   - Clear validation errors for invalid fields/values
   - Timeout protection (30s)

4. **Token Management**
   - Prefers `GITHUB_TOKEN` environment variable
   - Falls back to `gh auth token` command
   - Fails with clear message if neither available

## Migration Guide

### For Repository Owners

If you have a repository using the old version:

1. **Update `.vscode/mcp.json`:**
   ```diff
   {
     "env": {
       "WBS_WORK_ITEMS_PATH": "...",
-      "SYNC_SCRIPT_PATH": "${workspaceFolder}/tools/sync-github-project.sh"
   +   "GITHUB_ORG": "your-org",
   +   "GITHUB_PROJECT_NUMBER": "2"
     }
   }
   ```

2. **Optional: Remove sync script**
   ```bash
   rm tools/sync-github-project.sh  # No longer needed
   ```

3. **Reload MCP server**
   - In VS Code: Reload window or restart Copilot

### Backwards Compatibility

The `update_work_item` tool API remains unchanged:

```python
# Still works the same way
update_work_item(
    wbs_id="WS-17101",
    updates={"status": "In Progress"},
    push_to_github=True  # Now uses GitHubProjectSync instead of script
)
```

## Testing

Test the GitHub sync without MCP:

```python
from wbs_mcp.github_sync import GitHubProjectSync

sync = GitHubProjectSync()

# Test field update
result = sync.update_item_field(
    issue_number=123,
    field_name="Status",
    value="In Progress"
)
print(f"Success: {result}")
```

## Troubleshooting

### "No GitHub token found"

**Solution:** Either:
1. Set `GITHUB_TOKEN` environment variable
2. Run `gh auth login` to authenticate gh CLI

### "Field 'X' not found in project"

**Solution:** Check GitHub Project configuration. Field names must match exactly (case-sensitive).

### "Invalid Status value 'X'"

**Solution:** Value must match a project field option. Check project settings for valid values.

### API Rate Limiting

The `gh` CLI automatically handles rate limiting. If you hit limits:
- Caching reduces API calls (project ID, field configs)
- Consider batching updates instead of updating individual items

## Future Improvements

Possible enhancements for future versions:

1. **Pure Python GraphQL** - Replace `gh` CLI with direct HTTP requests (requires token management, more complex)
2. **Batch Updates** - Update multiple items in single GraphQL mutation
3. **Webhook Integration** - Listen for GitHub Project updates, sync back to YAML
4. **Offline Mode** - Queue updates, sync when online

## Related Documentation

- [QUICKSTART.md](../QUICKSTART.md) - Getting started guide
- [TOOLS.md](../docs/TOOLS.md) - Tool reference
- [GitHub Projects GraphQL API](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects)
