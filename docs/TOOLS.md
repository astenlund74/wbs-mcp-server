# MCP Tools Reference

Complete reference for all 6 read-only tools provided by the RPDS Project MCP Server.

## Tool 1: list_work_items

**Purpose**: Filter and list work items from the backlog

**Parameters**:
- `status` (string, optional): Filter by status
  - Valid values: `"Todo"`, `"In Progress"`, `"Done"`, `"Blocked"`
- `wbs_type` (string, optional): Filter by type
  - Valid values: `"Epic"`, `"Feature"`, `"Task"`
- `milestone` (string, optional): Filter by milestone (partial match)
  - Example: `"M1.1"`, `"M1"`, `"Logical Layer"`
- `work_stream` (string, optional): Filter by work stream (partial match)
  - Example: `"WS1"`, `"Repository"`, `"Information Modeling"`
- `parent_wbs` (string, optional): Filter by parent WBS ID
  - Example: `"WS-17001"` (shows all children of that epic)
- `limit` (integer, optional): Maximum results (default: 50)

**Returns**: List of matching work items with summary information

**Example Queries** (natural language for Claude):
- "List all work items in progress"
- "Show me all epics"
- "What features are under WS-17001?"
- "List all work items in milestone M1.1"
- "Show me blocked items"

**Sample Output**:
```
Found 3 work items

---

**WS-17101**: MCP Server Phase 1: Read-Only Tools
Type: Feature | Status: In Progress | Priority: 🟡 Medium
Effort: 5.0 days | Stream: WS7: Documentation & Tooling
Milestone: null
Parent: WS-17001
Owner: Sara

---
```

---

## Tool 2: get_work_item

**Purpose**: Get detailed information about a specific work item

**Parameters**:
- `wbs_id` (string): WBS ID of the work item
  - Example: `"WS-17101"`
- `issue_number` (integer): GitHub issue number (alternative to wbs_id)
  - Example: `54`

**Note**: Must provide either `wbs_id` OR `issue_number`, not both.

**Returns**: Full work item details including description, relationships, timeline

**Example Queries**:
- "Show me WS-17101"
- "Get details for issue #54"
- "What is WS-11100 about?"

**Sample Output**:
```
# WS-17101: MCP Server Phase 1: Read-Only Tools

**Type**: Feature
**Status**: In Progress
**Priority**: 🟡 Medium
**Work Stream**: WS7: Documentation & Tooling
**Effort**: 5.0 days

**Parent WBS**: WS-17001
**Responsible Architect**: Sara

**GitHub Issue**: #54

## Description

Create MCP (Model Context Protocol) server for read-only project management queries and analysis.

**Objective**: Replace inline Python scripts with structured MCP protocol for safe, read-only work item operations.

**Scope - 6 Query/Analysis Tools**:
1. **list_work_items**: Filter by status/type/epic/milestone...
...
```

---

## Tool 3: get_hierarchy

**Purpose**: View work item hierarchy (epic → features → tasks) with progress rollup

**Parameters**:
- `root_wbs` (string, optional): Root WBS ID to start from
  - If not provided: Shows all top-level epics
  - If provided: Shows hierarchy starting from that item

**Returns**: Hierarchical tree with effort totals and progress percentages

**Example Queries**:
- "Show me the work hierarchy"
- "What's the hierarchy under WS-17001?"
- "Show all epics with their features"

**Sample Output**:
```
✅ **WS-17001**: Documentation Toolchain [Done] (100.0% complete)
   Effort: 5.0d | Total w/ children: 15.0d
  🔄 **WS-17101**: MCP Server Phase 1: Read-Only Tools [In Progress] (40.0% complete)
     Effort: 5.0d | Total w/ children: 5.0d
  📋 **WS-17102**: MCP Server Phase 2: Mutation Tools [Todo] (0.0% complete)
     Effort: 5.0d | Total w/ children: 5.0d
```

---

## Tool 4: validate_sync

**Purpose**: Validate work-items.yaml for consistency issues

**Parameters**: None

**Returns**: Validation report with errors, warnings, and info messages

**Checks Performed**:
- Missing parent references (broken WBS parent links)
- Missing issue parent references (broken GitHub issue links)
- Features without parent epic (orphaned features)
- Items without milestone assignment
- Invalid status values
- Duplicate WBS IDs

**Example Queries**:
- "Validate the work items"
- "Check for consistency issues"
- "Are there any data quality problems?"

**Sample Output**:
```
# Validation Result

**Status**: ✅ VALID
**Total Items**: 56
**Issues Found**: 3

## ⚠️ Warnings

- **WS-17103** [orphan_feature]: Feature has no parent epic

## ℹ️ Info

- **WS-17001** [missing_milestone]: Epic has no milestone assigned
- **WS-17101** [missing_milestone]: Feature has no milestone assigned
```

---

## Tool 5: find_orphans

**Purpose**: Find orphan work items (missing relationships)

**Parameters**: None

**Returns**: List of orphan items grouped by category

**Orphan Categories**:
1. **Features without parent epic**: Features that should be assigned to an epic
2. **Items without milestone**: Epics/features missing milestone assignment
3. **Broken parent references**: Items referencing non-existent parents

**Example Queries**:
- "Find orphan work items"
- "What items are missing relationships?"
- "Show me cleanup tasks"

**Sample Output**:
```
# Orphan Work Items

Found 2 orphan items across 2 categories:

## 🟡 Items Without Milestone (2)

These items should be assigned to a milestone:

- **WS-17001**: Documentation Toolchain
  Type: Epic | Status: Done
- **WS-17101**: MCP Server Phase 1: Read-Only Tools
  Type: Feature | Status: In Progress

---
```

---

## Tool 6: get_milestone_coverage

**Purpose**: Get progress summary by milestone

**Parameters**:
- `milestone_filter` (string, optional): Filter by milestone (partial match)
  - Example: `"M1"` (shows M1.1, M1.2, etc.)
  - If not provided: Shows all milestones

**Returns**: Progress report with item counts, effort totals, completion percentage

**Example Queries**:
- "Show milestone progress"
- "How far along is M1.1?"
- "What's the status of Phase 1 milestones?"

**Sample Output**:
```
# Milestone Progress Report

Tracking 2 milestone(s)

## M1.1: Program Management Spine

**Progress**: 83.3% | ████████████████████░░

**Item Status**:
- ✅ Done: 5
- 🔄 In Progress: 1
- 🚫 Blocked: 0
- 📋 Todo: 0
- **Total**: 6 items

**Effort**:
- Completed: 25.0 days
- Total: 30.0 days

**Epics**: WS-11001

---

## M1.2: Logical Layer Integration

**Progress**: 20.0% | ████░░░░░░░░░░░░░░░░

**Item Status**:
- ✅ Done: 1
- 🔄 In Progress: 2
- 🚫 Blocked: 0
- 📋 Todo: 2
- **Total**: 5 items

**Effort**:
- Completed: 3.0 days
- Total: 15.0 days

**Epics**: WS-11100

---
```

---

## Usage Tips

### Combining Tools for Analysis

**Workflow 1: Milestone Review**
```
1. get_milestone_coverage(milestone_filter="M1.1")  # Get overview
2. list_work_items(milestone="M1.1", status="In Progress")  # See active items
3. get_work_item(wbs_id="WS-11102")  # Drill into specific item
```

**Workflow 2: Epic Planning**
```
1. list_work_items(wbs_type="Epic")  # See all epics
2. get_hierarchy(root_wbs="WS-17001")  # View epic breakdown
3. list_work_items(parent_wbs="WS-17001", status="Todo")  # Plan next work
```

**Workflow 3: Data Quality Audit**
```
1. validate_sync()  # Check for errors
2. find_orphans()  # Find missing relationships
3. list_work_items(milestone=null)  # Find unassigned items
```

### Performance Notes

- All tools execute in < 500ms on typical work-items.yaml (< 100 items)
- Data is cached in memory, reload only when file changes
- Safe for concurrent access (read-only, no file locking needed)

### Error Handling

Tools return user-friendly error messages:
- Missing WBS ID: `"Work item not found: WS-99999"`
- No results: `"No work items found matching the specified criteria."`
- Invalid input: `"Error: Must provide either wbs_id or issue_number"`

---

## Phase 2 Tools (Not Yet Implemented)

WS-17102 will add write operations:
- `update_work_item`: Modify single field
- `assign_milestone`: Bulk milestone assignment
- `push_to_github`: Sync to GitHub
- `pull_from_github`: Refresh from GitHub
- `set_issue_parent`: Update relationships
- `batch_update`: Multiple updates in transaction
- `create_work_item`: Add new items

See [WS-17102 specification](../8-REALIZATION/backlog/work-items.yaml) for details.
