# Tool Reference

Complete documentation for all 10 MCP tools provided by the WBS MCP Server.

## Overview

The WBS MCP Server provides tools organized into three categories:

**Read Operations (6 tools)**:

- Work item queries and filtering
- Hierarchy visualization
- Data validation
- Progress tracking

**Write Operations (2 tools)**:

- Work item updates with GitHub sync
- PR review thread management

**PR Review Operations (2 tools)**:

- List unresolved review threads
- Reply to and resolve threads

---

## Read Operations

### Tool 1: list_work_items

Filter and list work items from the backlog.

**Parameters**:

- `status` (string, optional): Filter by status
  - Valid values: `"Todo"`, `"In Progress"`, `"Done"`, `"Blocked"`
- `wbs_type` (string, optional): Filter by type
  - Valid values: `"Epic"`, `"Feature"`, `"Task"`
- `milestone` (string, optional): Filter by milestone (partial match)
  - Example: `"M1.1"`, `"M1"`, `"Foundation"`
- `work_stream` (string, optional): Filter by work stream (partial match)
  - Example: `"WS1"`, `"Repository"`, `"Backend"`
- `parent_wbs` (string, optional): Filter by parent WBS ID
  - Example: `"WS-11000"` (shows all children of that epic)
- `limit` (integer, optional): Maximum results (default: 50)

**Returns**: List of matching work items with summary information (title, status, type, milestone, etc.)

**Example Queries**:

```
List all work items in progress
Show me all epics
What features are under WS-11000?
List all work items in milestone M1.1
Show me blocked items
```

**Sample Output**:

```
Found 3 work items

---

**WS-11101**: Tenant Administration Feature
Type: Feature | Status: In Progress | Priority: 🟡 Medium
Effort: 8.0 days | Stream: WS1: Core Backend
Milestone: M1.1: Foundation
Parent: WS-11000
Owner: Alice

Description: Implement tenant CRUD operations with validation
```

---

### Tool 2: get_work_item

Get detailed information about a specific work item.

**Parameters**:

- `wbs_id` (string): WBS ID of the work item (e.g., `"WS-11101"`)
- `issue_number` (integer): GitHub issue number (alternative to wbs_id, e.g., `42`)

**Note**: Must provide either `wbs_id` OR `issue_number`, not both.

**Returns**: Full work item details including:

- Title, description, status, priority
- Relationships (parent, children)
- Timeline (start/end dates, effort)
- GitHub integration (issue number, URL)
- Responsible architect/assignees

**Example Queries**:

```
Show me WS-11101
Get details for issue #42
What is WS-11000 about?
```

**Sample Output**:

```
# WS-11101: Tenant Administration Feature

**Type**: Feature
**Status**: In Progress
**Priority**: 🟡 Medium
**Work Stream**: WS1: Core Backend
**Effort**: 8.0 days

**Parent WBS**: WS-11000
**Responsible Architect**: Alice

**GitHub Issue**: #42
**Issue URL**: https://github.com/your-org/project/issues/42

## Description

Implement tenant CRUD operations with validation and authorization.

**Scope**:
1. Create tenant endpoint with validation
2. Update tenant details
3. Delete tenant (soft delete)
4. List tenants with pagination

**Acceptance Criteria**:
- All endpoints return proper HTTP status codes
- Input validation with detailed error messages
- Unit tests coverage > 90%
```

---

### Tool 3: get_hierarchy

View work item hierarchy (epic → features → tasks) with progress rollup.

**Parameters**:

- `root_wbs` (string, optional): Root WBS ID to start from
  - If omitted, shows all top-level epics
  - Example: `"WS-11000"` (shows that epic and all descendants)

**Returns**: Tree structure showing:

- Parent-child relationships
- Status of each item
- Effort totals and rollups
- Completion percentages

**Example Queries**:

```
Show me the full work hierarchy
What's the structure under epic WS-11000?
Show me the project tree
```

**Sample Output**:

```
Work Item Hierarchy

📦 WS-11000: Backend Core System (Epic) - In Progress
   Effort: 24.0 days total
   
   ├─ 📋 WS-11101: Tenant Administration (Feature) - In Progress
   │  Effort: 8.0 days
   │  
   │  ├─ ✅ WS-11201: Create Tenant Endpoint (Task) - Done
   │  │  Effort: 2.0 days
   │  
   │  └─ 🔄 WS-11202: Update Tenant Endpoint (Task) - In Progress
   │     Effort: 2.0 days
   │
   └─ 📋 WS-11102: Contract Management (Feature) - Todo
      Effort: 10.0 days
```

---

### Tool 4: get_milestone_coverage

Get progress summary by milestone with item counts, effort totals, and completion percentage.

**Parameters**:

- `milestone_filter` (string, optional): Filter to specific milestone (partial match)
  - Example: `"M1"`, `"M1.1"`, `"Foundation"`

**Returns**: Milestone summary showing:

- Total work items per status
- Total effort (days) per status
- Completion percentage
- List of items in milestone

**Example Queries**:

```
What's the status of milestone M1.1?
Show me all milestones
How much work is in M1?
```

**Sample Output**:

```
Milestone Coverage Report

## M1.1: Foundation Phase
**Total Items**: 12
**Total Effort**: 42.0 days

**By Status**:
- Done: 4 items (12.0 days) - 33%
- In Progress: 5 items (20.0 days) - 42%
- Todo: 3 items (10.0 days) - 25%

**Completion**: 33% complete (12.0 / 42.0 days)

**Items**:
- WS-11101: Tenant Administration (In Progress)
- WS-11102: Contract Management (Todo)
- WS-11201: Create Tenant Endpoint (Done)
...
```

---

### Tool 5: validate_sync

Validate work-items.yaml for consistency issues like missing parents, broken references, invalid statuses, orphaned items.

**Parameters**: None

**Returns**: Validation report showing:

- Missing parent references
- Broken WBS ID references
- Invalid status values
- Orphaned items (no parent, not an Epic)
- Duplicate WBS IDs

**Example Queries**:

```
Validate the work items
Check for consistency issues
Are there any data problems?
```

**Sample Output**:

```
Validation Report

✅ No issues found

Total items validated: 24
- Epics: 3
- Features: 8
- Tasks: 13

All parent references valid
All statuses valid
No orphaned items
No duplicate WBS IDs
```

Or if issues found:

```
Validation Report

❌ 3 issues found

**Missing Parent References**:
- WS-11102: Parent WS-11999 does not exist

**Invalid Status**:
- WS-11201: Status "Complete" is not valid (use "Done")

**Orphaned Items**:
- WS-11203: Task has no parent and is not an Epic
```

---

### Tool 6: find_orphans

Find orphan work items: features without epics, items without milestones, broken parent references.

**Parameters**: None

**Returns**: List of orphaned items categorized by issue type:

- Items with missing parent references
- Items without milestones
- Features/Tasks without parent epics

**Example Queries**:

```
Find orphan items
What work items are orphaned?
Check for items without parents
```

**Sample Output**:

```
Orphan Work Items Report

**Items with Missing Parents** (2):
- WS-11102: Contract Management
  Parent WS-11999 does not exist

- WS-11205: Validation Task
  Parent WS-11199 does not exist

**Items without Milestones** (3):
- WS-11103: Search Feature
- WS-11206: Logging Task
- WS-11207: Monitoring Task

**Total Orphans**: 5 items
```

---

## Write Operations

### Tool 7: update_work_item

Update a work item in work-items.yaml and optionally sync to GitHub Projects.

**Parameters**:

- `wbs_id` (string, required): WBS ID to update (e.g., `"WS-11101"`)
- `updates` (object, required): Fields to update
  - `status` (string): New status (`"Todo"`, `"In Progress"`, `"Done"`, `"Blocked"`)
  - `priority` (string): New priority (`"🔴 Critical"`, `"🟡 Medium"`, `"🟢 Low"`)
  - `milestone` (string): New milestone (e.g., `"M1.2: Integration"`)
  - `assignees` (array): List of assignee usernames
  - `effort_days` (number): Effort estimate in days
  - `start_date` (string): Start date (YYYY-MM-DD)
  - `end_date` (string): End date (YYYY-MM-DD)
  - `description` (string): Full description text
  - `responsible_architect` (string): Architect name
  - `allow_yaml_override` (boolean): Allow YAML to override GitHub data
- `push_to_github` (boolean, optional): Whether to sync to GitHub (default: false)

**Returns**: Update confirmation with:

- Success status
- Fields updated
- Whether GitHub sync occurred
- GitHub issue number (if synced)

**Example Queries**:

```
Move WS-11101 to Done
Update WS-11102 priority to High
Set WS-11103 milestone to M1.2 and sync to GitHub
Update assignees for WS-11104
```

**Sample Usage (natural language)**:

```
Update WS-11101:
- Set status to Done
- Set milestone to M1.1: Foundation
- Add assignee alice
- Sync to GitHub
```

**Sample Output**:

```
✅ Updated WS-11101

**Fields Changed**:
- status: In Progress → Done
- milestone: null → M1.1: Foundation
- assignees: [] → [alice]

**GitHub Sync**: ✅ Success
- Issue #42 updated
- Status field set to "Done"
- Milestone field set to "M1.1: Foundation"
```

**Requirements**:

- `WBS_WORK_ITEMS_PATH` must be set
- For GitHub sync: `GITHUB_ORG` and `GITHUB_PROJECT_NUMBER` must be set
- For GitHub sync: `gh` CLI must be authenticated with `project` scope

---

## PR Review Operations

### Tool 8: list_pr_review_threads

List unresolved review threads for a pull request.

**Parameters**:

- `pr_number` (integer, optional): PR number
  - If omitted, auto-detects from current branch

**Returns**: List of unresolved review comment threads:

- Thread ID (for use with reply/resolve tools)
- Comment body
- File path and line number
- Author and timestamp
- Number of replies

**Example Queries**:

```
List unresolved review comments
Show me review threads for PR #15
What review feedback needs addressing?
```

**Sample Output**:

```
Unresolved Review Threads for PR #15

## Thread T_abc123
**File**: wbs_mcp/server.py:42
**Author**: reviewer-bob
**Posted**: 2025-01-05 14:23

> Consider using async/await here for better performance with concurrent requests.

**Replies**: 0

---

## Thread T_def456
**File**: wbs_mcp/tools/update_work_item.py:78
**Author**: reviewer-alice
**Posted**: 2025-01-05 15:10

> This error handling could be more specific. What if the YAML file is malformed?

**Replies**: 1
  - reviewer-alice (2025-01-05 15:30): Actually, yaml_writer handles this.

---

**Total Unresolved**: 2 threads
```

**Requirements**:

- Must be in a Git repository
- `gh` CLI must be authenticated
- Branch must have an associated PR (or provide `pr_number`)

---

### Tool 9: reply_to_review_thread

Add a reply comment to a review thread.

**Parameters**:

- `thread_id` (string, required): Review thread ID (from `list_pr_review_threads`)
  - Example: `"T_abc123"`
- `body` (string, required): Reply text (supports Markdown)

**Returns**: Confirmation with:

- Success status
- Thread ID
- Reply comment ID

**Example Queries**:

```
Reply to thread T_abc123 with "Fixed in latest commit"
Add comment to thread T_def456
```

**Sample Usage (natural language)**:

```
Reply to thread T_abc123:

"Good catch! I've refactored to use async/await as suggested. The performance improvement is ~40% in benchmarks."
```

**Sample Output**:

```
✅ Reply added to thread T_abc123

**Your comment**:
> Good catch! I've refactored to use async/await as suggested. The performance improvement is ~40% in benchmarks.

**Thread**: wbs_mcp/server.py:42
**Comment ID**: C_xyz789
```

**Requirements**:

- Same as `list_pr_review_threads`
- Thread ID must exist and be from current PR

---

### Tool 10: resolve_review_thread

Mark a review thread as resolved.

**Parameters**:

- `thread_id` (string, required): Review thread ID (from `list_pr_review_threads`)

**Returns**: Confirmation with:

- Success status
- Thread ID
- File path and line number

**Example Queries**:

```
Resolve thread T_abc123
Mark thread T_def456 as resolved
Close review thread T_ghi789
```

**Sample Output**:

```
✅ Resolved thread T_abc123

**Thread**: wbs_mcp/server.py:42
**Status**: Resolved

All review comments addressed.
```

**Best Practice**: Reply to thread explaining the fix before resolving:

1. `reply_to_review_thread` - Explain what you changed
2. `resolve_review_thread` - Mark as resolved

**Requirements**:

- Same as `list_pr_review_threads`
- Thread must not already be resolved

---

## Configuration Requirements

### Read-Only Operations (Tools 1-6)

**Required**:

- `WBS_WORK_ITEMS_PATH`: Path to `work-items.yaml`

**Example**:

```json
{
  "env": {
    "WBS_WORK_ITEMS_PATH": "${workspaceFolder}/backlog/work-items.yaml"
  }
}
```

### Write Operations (Tools 7)

**Required**:

- `WBS_WORK_ITEMS_PATH`: Path to `work-items.yaml`

**Optional (for GitHub sync)**:

- `GITHUB_ORG`: GitHub organization/username
- `GITHUB_PROJECT_NUMBER`: GitHub Project number
- `gh` CLI installed and authenticated with `project` scope

**Example**:

```json
{
  "env": {
    "WBS_WORK_ITEMS_PATH": "${workspaceFolder}/backlog/work-items.yaml",
    "GITHUB_ORG": "your-org",
    "GITHUB_PROJECT_NUMBER": "2"
  }
}
```

### PR Review Operations (Tools 8-10)

**Required**:

- Git repository with remote
- `gh` CLI installed and authenticated
- Branch with associated PR (or provide PR number)

No additional environment variables needed.

---

## Common Workflows

### 1. Work Item Status Update

```
List all work items in progress
Show me WS-11101
Update WS-11101 status to Done and sync to GitHub
```

### 2. Milestone Planning

```
Show me milestone M1.1 progress
What features are in M1.1?
List all tasks under feature WS-11101
```

### 3. Data Quality Check

```
Validate the work items
Find orphan items
Show me the full hierarchy
```

### 4. PR Review Workflow

```
List unresolved review comments
Reply to thread T_abc123 with "Fixed in commit abc1234"
Resolve thread T_abc123
List unresolved review comments  # Verify all addressed
```

### 5. Project Dashboard

```
What milestones are we tracking?
Show me milestone M1 progress
List all blocked items
What's critical priority?
```

---

## Error Handling

All tools return structured error messages if something goes wrong:

**File Not Found**:

```
❌ Error: Work items file not found

Path: /path/to/work-items.yaml
Check WBS_WORK_ITEMS_PATH environment variable
```

**Invalid WBS ID**:

```
❌ Error: Work item not found

WBS ID: WS-99999
No work item found with this ID
```

**GitHub Sync Failure**:

```
❌ Error: GitHub sync failed

Reason: GitHub CLI not authenticated
Run: gh auth login
Then: gh auth refresh -h github.com -s project
```

**Invalid Update**:

```
❌ Error: Invalid status

Status: "Complete"
Valid values: Todo, In Progress, Done, Blocked
```

---

## Next Steps

- **Setup Guide**: [SETUP.md](SETUP.md) - Installation and configuration
- **GitHub Integration**: [GITHUB-INTEGRATION.md](GITHUB-INTEGRATION.md) - Sync setup
- **Quick Start**: [QUICKSTART.md](../QUICKSTART.md) - 5-minute setup

## Support

- **Issues**: <https://github.com/astenlund74/wbs-mcp-server/issues>
- **Discussions**: <https://github.com/astenlund74/wbs-mcp-server/discussions>
