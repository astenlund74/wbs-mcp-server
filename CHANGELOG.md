# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-03

### Added
- **Phase 1: Read-Only Tools** (WS-17101)
  - `list_work_items` - Filter work items by status, type, epic, milestone
  - `get_work_item` - Retrieve single item by WBS ID or issue number
  - `get_hierarchy` - View epic→feature→task tree with progress rollup
  - `validate_sync` - Check work-items.yaml consistency
  - `find_orphans` - Detect items without parent or milestone
  - `get_milestone_coverage` - Track progress by milestone

- **Phase 2: Write Operations & PR Review** (WS-17102)
  - `update_work_item` - Modify work item fields with optional GitHub sync
  - `list_pr_review_threads` - Read PR review comments (auto-detects from branch)
  - `reply_to_review_thread` - Reply to review feedback
  - `resolve_review_thread` - Mark review threads as resolved

### Technical
- MCP SDK 0.9.0 integration
- Format-preserving YAML updates via ruamel.yaml
- Comprehensive test suite (14 passing tests)
- Pydantic validation for data integrity
- GitHub CLI integration for PR operations

### Documentation
- Installation guide for VS Code and Claude Desktop
- WBS ID format specification (format-agnostic design)
- Tool usage examples and workflows
- Architecture decision records

## [Unreleased]

### Planned
- Phase 3: Work item creation tool
- Advanced filtering (logical operators, date ranges)
- Batch operations support
- Enhanced error recovery

[1.0.0]: https://github.com/astenlund74/wbs-mcp-server/releases/tag/v1.0.0
