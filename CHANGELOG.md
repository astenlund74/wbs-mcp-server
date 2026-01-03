# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Phase 3: Work item creation tool
- Advanced filtering (logical operators, date ranges)
- Batch operations support
- Enhanced error recovery

## [1.0.0] - 2026-01-03

### Added

- **Phase 1: Read-Only Tools**
  - `list_work_items` - Filter work items by status, type, epic, milestone
  - `get_work_item` - Retrieve single item by WBS ID or issue number
  - `get_hierarchy` - View epic→feature→task tree with progress rollup
  - `validate_sync` - Check work-items.yaml consistency
  - `find_orphans` - Detect items without parent or milestone
  - `get_milestone_coverage` - Track progress by milestone

- **Phase 2: Write Operations & PR Review**
  - `update_work_item` - Modify work item fields with optional GitHub sync
  - `list_pr_review_threads` - Read PR review comments (auto-detects from branch)
  - `reply_to_review_thread` - Reply to review feedback
  - `resolve_review_thread` - Mark review threads as resolved

- **GitHub Integration**
  - `github_sync.py` module with `GitHubProjectSync` class
  - Direct GitHub GraphQL API integration via gh CLI
  - Field mapping and validation with caching
  - Self-contained Python implementation (no shell script dependency)

- **CI/CD & Testing**
  - GitHub Actions workflows for automated testing and releases
  - Automated testing on Python 3.11, 3.12, 3.13
  - Comprehensive test suite (14 passing tests)
  - Test fixture: `tests/fixtures/work-items.yaml`
  - mypy type checking with zero errors

- **Documentation**
  - Installation guide for VS Code and Claude Desktop
  - [GITHUB-INTEGRATION.md](docs/GITHUB-INTEGRATION.md) - Architecture and configuration
  - [RELEASE-PROCESS.md](docs/RELEASE-PROCESS.md) - CI/CD and versioning guide
  - [TOOLS.md](docs/TOOLS.md) - Complete reference for all 10 tools
  - [SETUP.md](docs/SETUP.md) - Comprehensive installation guide

### Technical

- MCP SDK 0.9.0 integration
- Format-preserving YAML updates via ruamel.yaml
- Pydantic validation for data integrity
- GitHub CLI integration for PR operations
- Requires `WBS_WORK_ITEMS_PATH` environment variable
- WBS ID format specification (format-agnostic design)
- Tool usage examples and workflows
- Architecture decision records

### Planned

- Phase 3: Work item creation tool
- Advanced filtering (logical operators, date ranges)
- Batch operations support
- Enhanced error recovery

[1.0.0]: https://github.com/astenlund74/wbs-mcp-server/releases/tag/v1.0.0
