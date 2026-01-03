# WBS ID Format Specification

## MCP Server Design: Format-Agnostic

**Key Design Principle**: The MCP server is **agnostic to WBS ID format**. It treats WBS IDs as opaque unique identifiers.

### Why Format-Agnostic?

The MCP server only **reads and updates** work items - it never creates them. Work item creation happens through:
- GitHub Issues (synced via `sync-github-project.sh`)
- Manual YAML editing
- External tools/workflows

Therefore, the server **makes no assumptions** about ID format, structure, or numbering scheme.

### ✅ **REQUIRED by MCP Server & Sync Tools**

These are **hard requirements** - the system will break without them:

1. **Unique String Identifier**
   - Must be unique across all work items
   - Used for: HashMap lookups, parent-child relationships, GitHub Project custom field
   - Code: `item.wbs_id == wbs_id` (exact string equality)
   - **Format**: Any string format that's unique

2. **Stable/Immutable**
   - Cannot change once created (used as foreign key in parent relationships)
   - GitHub Project tracks by issue number, but WBS ID used for human-readable linking
   - **Format**: Any string that won't be edited later

3. **YAML-Safe String**
   - Must be valid YAML string (no special escaping needed)
   - **Format**: Alphanumeric + hyphens work fine

4. **Non-Empty**
   - Code checks: `if wbs_id:` in multiple places
   - Validation: `seen_wbs_ids.add(item.wbs_id)` would fail with None
   - **Format**: Any non-empty string

### ⚠️ **NOT IMPLEMENTED** (Future Consideration)

These would only be needed **IF** we add a `create_work_item` tool in the future:

5. **Auto-generation Logic**
   - Would need to know: What format? What numbering scheme?
   - Current codebase: **No auto-generation exists**
   - Removed in Phase 2: `get_next_wbs_id()` method (YAGNI violation)

## MCP Server Implementation

These are **domain-specific patterns** - the system doesn't use them:

10. **Hierarchical Structure** (`WS-XXYYZ`)
    - Pattern: XX=work stream, YY=level (0=Epic), Z=sequence
    - Used by: RPDS program managers (human interpretation)
    - Code: **Ignores hierarchy completely** - just increments max number
    - Examples: `WS-11100` (epic), `WS-11101` (feature) - code doesn't care

11. **Work Stream Ranges** (11xxx, 12xxx, etc.)
    - Convention: WS-11xxx = Repository Foundation
    - Used by: Human organization of backlog
    - Code: **Doesn't validate or enforce ranges**

12. **Five-Digit Format**
    - Current: All IDs are 5 digits (11100, 17101, etc.)
    - Code: **Preserves whatever format exists** (zero-padding logic)
    - Could be: 3 digits, 6 digits, mixed - code adapts

13. **Epic/Feature Level Indicators**
    - Pattern: XX-YY where YY=0 means Epic, YY=1 means Feature
    - Used by: Human interpretation
    - Code: **Has separate `wbs_type` field** (Epic/Feature/Task) - not parsed from ID

## MCP Server Implementation

**Current Tools** (10 total):
- **6 Read-only**: list_work_items, get_work_item, get_hierarchy, validate_sync, find_orphans, get_milestone_coverage
- **1 Update**: update_work_item (requires existing wbs_id as input)
- **3 PR Review**: list_pr_review_threads, reply_to_review_thread, resolve_review_thread

**None of these create new work items** → No auto-generation needed → Format-agnostic!

### RPDS Domain Conventions (Not Enforced)

The RPDS program uses this convention for organizing work items:

**Pattern**: `WS-XXYYZ` (5-digit hierarchical coding)

Where:
- `WS` = Work Stream prefix (fixed literal)
- `XX` = Work stream number (2 digits: 11-19 observed)
- `YY` = Hierarchy level (1 digit: 0=Epic, 1=Feature, 2-9=Tasks)
- `Z` = Sequence number within level (1-9 single digit, extendable to 00-99)

**Examples from actual data**:
- Epics: `WS-11100`, `WS-12100`, `WS-17001`
- Features: `WS-11101`, `WS-12101`, `WS-17101`, `WS-17102`
- Tasks: `WS-11002`, `WS-12002`, `WS-11003`

**Work Stream Allocation** (RPDS convention only):
- **WS-11xxx**: Repository Foundation work stream
- **WS-12xxx**: Information Modeling work stream  
- **WS-13xxx**: Logical Architecture work stream
- **WS-14xxx**: Technology Architecture work stream
- **WS-15xxx**: Operations Architecture work stream
- **WS-16xxx**: Testing & Quality work stream
- **WS-17xxx**: Tooling & Automation work stream (MCP server, etc.)

**Important**: MCP server doesn't validate or enforce this convention - it's organizational guidance for humans.

## How the MCP Server Uses WBS IDs

### Read Operations (Format-Agnostic)
```python
# Only needs: String equality
item.wbs_id == "WS-17101"  # Could be "TASK-123" or "uuid-abc"
item.wbs_parent == "WS-17001"  # Parent relationship by ID equality
```
**Requirement**: Unique string for matching

### Update Operations (Format-Agnostic)
```python
# update_work_item uses wbs_id as lookup key
writer.update_work_item(wbs_id, updates)  # wbs_id itself is immutable
```
**Requirement**: Existing valid WBS ID (no format constraints)

### GitHub Sync
```python
# Stores as text field in GitHub Project
fields["wbs_id"] = field_value.get("text", "")
```
**Requirement**: String that fits in GitHub text field (no length limit observed)

### Validation Tools
```python
# Duplicate detection
seen_wbs_ids = {item.wbs_id for item in items}  # Set membership
if item.wbs_id in seen_wbs_ids: ...
```
**Requirement**: Hashable unique string

### Display/Formatting
```python
# Used in markdown output
f"**{item.wbs_id}**: {item.title}"
```
**Requirement**: String that renders in markdown (no special chars needed)

### RPDS Domain Conventions (Not Enforced)

The RPDS program uses this convention for organizing work items:

**Pattern**: `WS-XXYYZ` (5-digit hierarchical coding)

Where:
- `WS` = Work Stream prefix (fixed literal)
- `XX` = Work stream number (2 digits: 11-19 observed)
- `YY` = Hierarchy level (1 digit: 0=Epic, 1=Feature, 2-9=Tasks)
- `Z` = Sequence number within level (1-9 single digit, extendable to 00-99)

**Examples from actual data**:
- Epics: `WS-11100`, `WS-12100`, `WS-17001`
- Features: `WS-11101`, `WS-12101`, `WS-17101`, `WS-17102`
- Tasks: `WS-11002`, `WS-12002`, `WS-11003`

**Special Cases**:
- `WS-11103-DUP` - Has text suffix (currently handled by split('-')[-1])

**Important**: The hierarchical format is **RPDS program management convention**, not enforced by code!

### Work Stream Allocation (RPDS Convention Only)

From work-items.yaml analysis:
- **WS-11xxx**: Repository Foundation work stream
- **WS-12xxx**: Information Modeling work stream  
- **WS-13xxx**: Logical Architecture work stream
- **WS-14xxx**: Technology Architecture work stream
- **WS-15xxx**: Operations Architecture work stream
- **WS-16xxx**: Testing & Quality work stream
- **WS-17xxx**: Tooling & Automation work stream (MCP server, etc.)

**Note**: Code doesn't validate these ranges - humans assign them when creating work items.

## Why the Convention Exists (But Isn't Enforced)

The hierarchical format (`WS-XXYYZ`) serves **human organization**:

1. **Program Management**
   - Visually groups work items (WS-12xxx = all info modeling work)
   - Milestones map to work streams
   - Enables board/roadmap organization in GitHub Project

2. **Audit Trail**
   - ID format encodes historical context (which work stream, when created)
   - Hierarchical structure visible in ID itself

**But**: MCP server doesn't need or use this structure. It treats IDs as opaque strings.

**But**: MCP server doesn't need or use this structure. It treats IDs as opaque strings.

## Alternative Formats That Work

Since the MCP server is format-agnostic, any of these would work:

### UUID Format
```yaml
wbs_id: "550e8400-e29b-41d4-a716-446655440000"
```
- ✅ Unique, stable, YAML-safe, no collisions
- ❌ Not human-readable
- ✅ **MCP server would work unchanged**

### Semantic Slugs
```yaml
wbs_id: "repo-foundation-epic-001"
wbs_id: "info-modeling-tenant-domain-002"
```
- ✅ Human-readable, self-documenting
- ⚠️ Long
- ✅ **MCP server would work unchanged**

### GitHub Issue Numbers
```yaml
wbs_id: "GH-123"  # Maps to issue #123
```
- ✅ Direct 1:1 mapping
- ❌ Couples to GitHub (bad for export)
- ✅ **MCP server would work unchanged**

### Simple Sequential
```yaml
wbs_id: "TASK-001"
wbs_id: "TASK-002"
```
- ✅ Simple, clean
- ❌ No hierarchy encoding (but `work_stream` field provides grouping)
- ✅ **MCP server would work unchanged**

**Key point**: All format decisions are upstream (GitHub, YAML creation) - MCP server just consumes them.

## Code Changes Needed (Addressing Review Comments)
```python
def get_next_wbs_id(self, wbs_prefix: str = "WS") -> str:
```
- Hardcoded default: `"WS"`
- Configurable via parameter (good!)
- Assumption: Prefix is alphanumeric without hyphens

#### 2. **Starting ID**
```python
return f"{wbs_prefix}-10001"  # Line 120 & 142
```
- Hardcoded: `10001` (appears twice)
- Assumption: New work streams start at 10xxx range
- **Issue**: Magic number, not configurable

#### 3. **Delimiter**
```python
if wbs_id.startswith(f"{wbs_prefix}-"):
    num_str = wbs_id.split('-')[-1]
```
- Hardcoded: Single hyphen `-`
- Assumption: Last part after last hyphen is numeric
- Handles `WS-11103-DUP` correctly (takes "DUP" but int() will fail → caught)

#### 4. **Numeric Extraction**
```python
num_str = wbs_id.split('-')[-1]
num = int(num_str)
```
- Assumption: Numeric part is at the end after last hyphen
- Catches non-numeric with try/except (robust)

#### 5. **Zero-Padding Preservation**
```python
num_digits = len(max_id_str)
return f"{wbs_prefix}-{str(max_id + 1).zfill(num_digits)}"
```
- Preserves existing format (WS-00001 → WS-00002)
- Works for any digit count (3, 4, 5 digits)
- Good for flexibility!

#### 6. **Directory Structure**
```python
# update_work_item.py line 88
repo_root = yaml_path.parents[2]  # Assumes: repo/8-REALIZATION/backlog/work-items.yaml
```
- **Brittle**: Hardcoded `[2]` index
- Assumption: YAML is always at `8-REALIZATION/backlog/work-items.yaml`
- Breaks if: YAML moved, different structure, symbolic links

## What We DON'T Assume

✅ **Good - Flexible**:
- Prefix can be anything (via parameter)
- Numeric part can be any length (preserves existing format)
- Non-numeric IDs are gracefully skipped (try/except)
- Multiple hyphens in ID are handled (takes last part)

❌ **Bad - Rigid**:
- Starting ID hardcoded to 10001
- Repository structure hardcoded
- Hyphen delimiter not configurable (though unlikely to change)

## Potential Issues

### Issue 1: Work Stream Collision
If someone creates `WS-10001` manually, then next auto-generated ID would be `WS-10002`, potentially conflicting with hierarchical scheme (should be `WS-10100` for Epic?).

**Current behavior**: Code just increments, doesn't validate hierarchy rules.

### Issue 2: Cross-Prefix Pollution
If YAML contains both `WS-17101` and `TEST-001`, calling:
```python
writer.get_next_wbs_id("WS")  # Returns WS-17102 (correct)
writer.get_next_wbs_id("TEST")  # Returns TEST-002 (correct - filters by prefix)
```
Actually works fine! Prefix filtering prevents pollution.

### Issue 3: Non-Sequential IDs
Current IDs are not fully sequential:
- Epic range: WS-11100, WS-12100, WS-17001 (gaps in XX and YY)
- Feature range: WS-11101, WS-12101 (different XX values)

**Current behavior**: Finds max across ALL matching prefix, increments by 1.
**Result**: `get_next_wbs_id("WS")` would return `WS-17103` (max is 17102), ignoring hierarchy.

### Issue 4: Format Drift
If someone manually adds `WS-NEW-ITEM-001`, code will:
1. Try `int("001")` → succeeds
2. Compare 1 vs max (e.g., 17102)
3. Ignore this ID (not the max)
4. But format preservation uses last 5-digit ID found

**Edge case**: Mixed formats could cause confusion.

**Key point**: All format decisions are upstream (GitHub, YAML creation) - MCP server just consumes them.

## Future: If We Add create_work_item Tool

If we ever need to create work items through MCP, we should **require caller to provide WBS_ID**:

```python
Tool(
    name="create_work_item",
    inputSchema={
        "properties": {
            "wbs_id": {"type": "string", "description": "Unique WBS ID (required)"},
            "title": {"type": "string"},
            "wbs_type": {"type": "string"},
            # ...
        },
        "required": ["wbs_id", "title", "wbs_type"]
    }
)
```

**Why require caller to provide ID:**
- ✅ Caller knows their ID scheme (hierarchical, sequential, UUID, etc.)
- ✅ MCP server stays format-agnostic
- ✅ No hardcoded assumptions about format
- ✅ Validation only checks uniqueness (no format rules)

**Alternative approaches** (if auto-generation needed):
1. **UUID generation** - Format-agnostic but not human-readable
2. **External ID service** - Call GitHub API or dedicated microservice
3. **Configurable format** - Complex, many edge cases, high maintenance

**Recommendation**: Don't implement create until there's a clear use case. Current workflow (GitHub Issues → sync) works well.

## Summary

**Technical Requirements** (4 things):
1. Unique string
2. Stable/immutable  
3. YAML-safe
4. Non-empty

**Everything else is RPDS convention**, not technical requirement!

The `WS-XXYYZ` hierarchical format is:
- ✅ Used by humans for organization
- ✅ Supported by code (preserves format)
- ❌ NOT validated or enforced by code
- ❌ NOT required for sync/processing

**Code only needs**: A way to generate unique IDs (currently uses max+1 on numeric suffix).

---

## Appendix: RPDS Artifact ID Scheme (Separate System)

The repository also has architecture artifact IDs defined in [1-FOUNDATIONS/ARTIFACT-ID-SCHEME.md](../../../1-FOUNDATIONS/ARTIFACT-ID-SCHEME.md):

- `IO-XX`: Information Objects (e.g., IO-01-Tenant)
- `OG-XX`: Object Groups  
- `ABB-XXX`: Architecture Building Blocks
- `PAT-XXX`: Patterns
- `ADR-XXX`: Architecture Decision Records

**These are COMPLETELY SEPARATE** from WBS work item IDs:
- Different namespace (IO- vs WS-)
- Different purpose (architecture artifacts vs work tracking)
- Different numbering (2-3 digits vs 5 digits)
- No code relationship (not processed by MCP server)

**WBS IDs** (`WS-XXXXX`) are for **project management** (GitHub Project tracking).
**Artifact IDs** (`IO-XX`, etc.) are for **architecture documentation** (design artifacts).

---
**Last Updated**: 2026-01-03  
**Author**: Solutions-Sara  
**Context**: PR #58 review feedback - clarifying technical requirements vs. domain conventions
