# Phase 2 Requirements: Write Operations & PR Review Tools

**Target Work Item**: WS-17102
**Status**: Requirements Capture
**Created**: 2026-01-03

---

## Overview

Phase 2 extends the WBS MCP Server with **write operations** and **PR review comment handling** - two critical pain points in the AI agent workflow identified in `.github/AI_CONTRIBUTING.md`.

## Scope

### 1. Work Item Write Operations
Enable agents to update work items programmatically without manual YAML editing.

### 2. PR Review Comment Tools
Automate the tedious GraphQL-based PR review comment workflow.

---

## Feature Set 1: Work Item Write Operations

### Tool: `update_work_item`

**Purpose**: Update work item status, milestone, description, etc.

**Input Schema**:
```json
{
  "wbs_id": "WS-17101",
  "updates": {
    "status": "In Progress",
    "milestone": "M1.2: Logical Layer Integration",
    "description": "Updated implementation details...",
    "allow_yaml_override": true
  },
  "push_to_github": true
}
```

**Output Schema**:
```json
{
  "success": true,
  "wbs_id": "WS-17101",
  "updated_fields": ["status", "milestone", "description"],
  "github_synced": true,
  "issue_number": 54
}
```

**Implementation Notes**:
- Load existing work-items.yaml
- Apply updates (preserve other fields)
- Validate against Pydantic models
- Write back to YAML with formatting preservation
- Optionally call `sync-github-project.sh push --wbs-id <ID>`

**Error Handling**:
- WBS ID not found → 404 error
- Invalid status value → validation error
- GitHub sync fails → return local success + warning

---

### Tool: `create_work_item`

**Purpose**: Create new work items (e.g., agent discovers missing task)

**Input Schema**:
```json
{
  "wbs_type": "Task",
  "title": "Add error handling for IFC import",
  "parent_wbs": "WS-17101",
  "milestone": "M1.2: Logical Layer Integration",
  "work_stream": "WS1: Repository Operations",
  "status": "Todo",
  "effort_estimate": 3
}
```

**Output Schema**:
```json
{
  "success": true,
  "wbs_id": "WS-17103",
  "issue_number": 56,
  "github_url": "https://github.com/org/repo/issues/56"
}
```

**Implementation Notes**:
- Auto-assign next WBS ID in sequence (read max ID from YAML)
- Create GitHub issue via `gh issue create`
- Add to work-items.yaml
- Link parent/child relationships

---

## Feature Set 2: PR Review Comment Tools

**Context**: Current workflow from `.github/AI_CONTRIBUTING.md` requires manual GraphQL mutations. Agents should handle this autonomously.

### Tool: `list_pr_review_threads` (Read-Only)

**Purpose**: Get all unresolved review threads for current PR

**Input Schema**:
```json
{
  "pr_number": null  // null = auto-detect from current branch
}
```

**Output Schema**:
```json
{
  "pr_number": 42,
  "unresolved_threads": [
    {
      "thread_id": "PRRT_kwDOABCDEF...",
      "file_path": "wbs_mcp/server.py",
      "line": 45,
      "comments": [
        {
          "author": "reviewer-username",
          "body": "Consider caching this result",
          "created_at": "2026-01-03T10:30:00Z"
        }
      ],
      "is_resolved": false
    }
  ],
  "total_unresolved": 3
}
```

**GitHub CLI Implementation**:
```bash
gh pr view <PR_NUM> --json reviewThreads --jq '.reviewThreads[] | select(.isResolved==false)'
```

---

### Tool: `get_pr_review_thread` (Read-Only)

**Purpose**: Get detailed info on specific review thread

**Input Schema**:
```json
{
  "thread_id": "PRRT_kwDOABCDEF..."
}
```

**Output Schema**:
```json
{
  "thread_id": "PRRT_kwDOABCDEF...",
  "file_path": "wbs_mcp/server.py",
  "start_line": 45,
  "end_line": 47,
  "diff_hunk": "@@ -45,3 +45,5 @@ ...",
  "comments": [
    {
      "id": "PRRC_abc123",
      "author": "reviewer",
      "body": "This could be optimized",
      "created_at": "2026-01-03T10:30:00Z"
    }
  ],
  "is_resolved": false
}
```

---

### Tool: `reply_to_review_thread` (Write)

**Purpose**: Add comment to review thread

**Input Schema**:
```json
{
  "thread_id": "PRRT_kwDOABCDEF...",
  "body": "✅ Fixed in abc1234 - added caching with LRU eviction"
}
```

**Output Schema**:
```json
{
  "success": true,
  "comment_id": "PRRC_xyz789",
  "thread_id": "PRRT_kwDOABCDEF...",
  "url": "https://github.com/org/repo/pull/42#discussion_r123456"
}
```

**GraphQL Mutation** (from AI_CONTRIBUTING.md):
```graphql
mutation($thread:ID!, $body:String!) { 
  addPullRequestReviewThreadReply(input: {
    pullRequestReviewThreadId: $thread, 
    body: $body
  }) { 
    comment { id } 
  } 
}
```

**Implementation**:
```python
gh api graphql -f query='...' -f thread="$THREAD_ID" -f body="$BODY"
```

---

### Tool: `resolve_review_thread` (Write)

**Purpose**: Mark review thread as resolved

**Input Schema**:
```json
{
  "thread_id": "PRRT_kwDOABCDEF..."
}
```

**Output Schema**:
```json
{
  "success": true,
  "thread_id": "PRRT_kwDOABCDEF...",
  "is_resolved": true
}
```

**GraphQL Mutation** (from AI_CONTRIBUTING.md):
```graphql
mutation($id:ID!) { 
  resolveReviewThread(input: {threadId: $id}) { 
    thread { isResolved } 
  } 
}
```

---

### Tool: `handle_pr_review_workflow` (Orchestrator)

**Purpose**: Execute full review response workflow autonomously

**Input Schema**:
```json
{
  "pr_number": null,  // auto-detect
  "auto_resolve": true,  // resolve after reply
  "commit_reference": "abc1234"  // current commit SHA
}
```

**Workflow Steps**:
1. List unresolved threads (`list_pr_review_threads`)
2. For each thread:
   - Present to agent/user for response
   - Agent implements fix
   - Call `reply_to_review_thread` with fix description
   - If `auto_resolve=true`: call `resolve_review_thread`
3. Add PR summary comment: "All review comments addressed in commit {SHA}"

**Output Schema**:
```json
{
  "success": true,
  "threads_processed": 3,
  "threads_resolved": 3,
  "summary_comment_url": "https://github.com/org/repo/pull/42#issuecomment-123456"
}
```

---

## Technical Implementation

### GitHub CLI Integration

All tools use `gh` CLI for GitHub API access:
- **Read operations**: `gh pr view --json <fields>`
- **Write operations**: `gh api graphql -f query='...'`

**Error Handling**:
- Authentication failure → Clear error message with setup instructions
- Rate limiting → Exponential backoff with retry
- Invalid thread ID → 404 with helpful message

### YAML Manipulation

**Requirements**:
- Preserve comments in work-items.yaml
- Maintain formatting (indentation, line breaks)
- Atomic writes (temp file + rename)

**Library Options**:
- `ruamel.yaml` (preserves comments, formatting)
- File locking for concurrent access safety

### Testing Strategy

**Unit Tests**:
- YAML round-trip (read → modify → write → verify unchanged formatting)
- Work item validation (invalid status values, missing required fields)
- GitHub CLI command construction

**Integration Tests**:
- Mock `gh` CLI responses
- Test full workflow: create item → update status → push to GitHub

**E2E Tests** (requires test GitHub repo):
- Create real work item
- Create real PR with review comments
- Execute review workflow

---

## User Experience Flow

### Scenario 1: Agent Updates Work Item Status

**Before** (manual):
```bash
# Agent manually edits YAML
vim 8-REALIZATION/backlog/work-items.yaml
# Change status: Todo → In Progress
./tools/sync-github-project.sh push --wbs-id WS-17101
```

**After** (MCP tool):
```
Agent uses MCP tool: update_work_item
Input: {wbs_id: "WS-17101", updates: {status: "In Progress"}, push_to_github: true}
Result: ✅ WS-17101 updated locally and synced to GitHub issue #54
```

---

### Scenario 2: Agent Handles PR Review Comments

**Before** (manual):
```bash
# Agent manually runs GraphQL queries
PR_NUM=$(gh pr view --json number --jq '.number')
gh pr view $PR_NUM --json reviewThreads --jq '...'
# Copy thread ID
gh api graphql -f query='mutation...' -f thread="$THREAD_ID" -f body="..."
gh api graphql -f query='mutation...' -f id="$THREAD_ID"
```

**After** (MCP tool):
```
Agent uses MCP tool: handle_pr_review_workflow
Input: {auto_resolve: true, commit_reference: "abc1234"}
Result: 
  ✅ Thread 1: Fixed caching issue - replied and resolved
  ✅ Thread 2: Updated error handling - replied and resolved
  ✅ Thread 3: Added documentation - replied and resolved
  ✅ Summary comment added to PR
```

---

## Security Considerations

**GitHub Token Access**:
- Tools use `gh` CLI → requires `GH_TOKEN` or `gh auth login`
- No token storage in MCP server
- Rate limiting: Respect GitHub API limits (5,000/hour authenticated)

**YAML Write Safety**:
- Validate all inputs before writing
- Atomic writes (prevent partial updates)
- Backup original file before modification
- Rollback on validation failure

**Permissions**:
- Work item updates: Local file write + GitHub issue write
- PR review comments: GitHub PR review API access
- Clear error if user lacks permissions

---

## Documentation Requirements

**User Guide**:
- Setup instructions (GitHub authentication)
- Tool reference (inputs, outputs, examples)
- Workflow guides (common scenarios)

**Developer Guide**:
- Architecture (how tools interact with GitHub API)
- Adding new tools (template, testing)
- Error handling patterns

**Migration Guide**:
- Updating from Phase 1 (read-only) to Phase 2 (read-write)
- New configuration requirements
- Breaking changes (if any)

---

## Acceptance Criteria

### Work Item Write Operations
- [ ] `update_work_item` updates YAML and syncs to GitHub
- [ ] `create_work_item` assigns next WBS ID and creates issue
- [ ] YAML formatting preserved (comments, indentation)
- [ ] Atomic writes prevent data corruption
- [ ] Error handling for all failure modes

### PR Review Tools
- [ ] `list_pr_review_threads` returns unresolved threads
- [ ] `reply_to_review_thread` adds comment via GraphQL
- [ ] `resolve_review_thread` marks thread resolved
- [ ] `handle_pr_review_workflow` orchestrates full flow
- [ ] Auto-detection of current PR from branch

### Testing
- [ ] Unit tests cover YAML manipulation
- [ ] Integration tests mock GitHub CLI
- [ ] E2E tests (optional, requires test repo)
- [ ] Error scenarios tested (auth failure, rate limits)

### Documentation
- [ ] User guide with setup + examples
- [ ] Tool reference (complete API docs)
- [ ] Migration guide from Phase 1

### Performance
- [ ] Response time <1s for write operations
- [ ] Batch operations supported (update multiple items)
- [ ] Graceful degradation if GitHub API slow

---

## Open Questions

1. **Concurrency**: How to handle multiple agents updating same work item simultaneously?
   - Option A: File locking (simple, may cause delays)
   - Option B: Optimistic locking (version field in YAML)
   - Recommendation: Start with file locking, add optimistic locking if needed

2. **Undo/Rollback**: Should agents be able to undo work item updates?
   - Option A: Keep YAML history (git-like)
   - Option B: Rely on git commits for rollback
   - Recommendation: Git-based (no custom history)

3. **Bulk Operations**: Support updating multiple work items in one call?
   - Use case: "Mark all tasks in epic WS-17100 as In Progress"
   - Recommendation: Add `update_work_items` (plural) in Phase 2.1

4. **PR Review AI Suggestions**: Should tools integrate AI code review?
   - Use case: Agent analyzes review comment + suggests fix
   - Recommendation: Separate feature (Phase 3), keep Phase 2 focused on workflow automation

---

## Implementation Phases

### Phase 2.1: Work Item Writes (Sprint 1)
- `update_work_item`
- `create_work_item`
- YAML manipulation with formatting preservation
- Unit tests

### Phase 2.2: PR Review Reads (Sprint 1-2)
- `list_pr_review_threads`
- `get_pr_review_thread`
- GitHub CLI integration
- Integration tests

### Phase 2.3: PR Review Writes (Sprint 2)
- `reply_to_review_thread`
- `resolve_review_thread`
- `handle_pr_review_workflow` (orchestrator)
- E2E testing

### Phase 2.4: Documentation & Polish (Sprint 2)
- User guide
- Developer guide
- Migration guide from Phase 1
- Performance optimization

---

## References

- `.github/AI_CONTRIBUTING.md` - Current manual workflow
- `tools/sync-github-project.sh` - Existing GitHub sync script
- GitHub GraphQL API docs: https://docs.github.com/en/graphql
- MCP SDK Python: https://github.com/modelcontextprotocol/python-sdk

---

**Next Steps**:
1. Create work item WS-17102 in backlog
2. Prioritize sub-features (work items vs PR review?)
3. Spike: Test `ruamel.yaml` for formatting preservation
4. Design tool API schemas (finalize input/output contracts)

**Estimated Effort**: 12-15 days (2-3 sprints)
**Dependencies**: None (Phase 1 complete and merged)
**Risk**: GitHub API rate limiting for heavy PR review usage → Add caching/batching
