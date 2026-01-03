# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Documentation:** Corrected environment variable name from `WORK_ITEMS_FILE` to `WBS_WORK_ITEMS_PATH` in all documentation and examples (thanks Frank!)

### Planned

- Phase 3: Work item creation tool
- Advanced filtering (logical operators, date ranges)
- Batch operations support
- Enhanced error recovery

## [2.0.1] - 2026-01-03

### Fixed

- All mypy type errors resolved (18 errors fixed across 5 files)
- Release workflow now requires tests to pass before creating release
- Added types-PyYAML stub package for proper YAML typing
- Proper type annotations for async_main and main functions
- Type handling in GitHubProjectSync API responses
- Issue number validation in get_work_item tool

### Changed

- CI/CD: Linting made non-blocking (warnings only)
- CI/CD: Removed pytest-cov from test run (not in core dependencies)

## [2.0.0] - 2026-01-03

### Changed

- **BREAKING: Refactored GitHub integration** - Removed shell script dependency
  - `update_work_item` now uses `GitHubProjectSync` class directly
  - No longer requires `SYNC_SCRIPT_PATH` environment variable
  - Now requires `GITHUB_ORG` and `GITHUB_PROJECT_NUMBER` instead
  - Self-contained Python implementation for better testing and portability

### Added

- `github_sync.py` module with `GitHubProjectSync` class
  - Direct GitHub GraphQL API integration via gh CLI
  - Field mapping and validation
  - Caching for project ID and field configurations
  - Better error messages and logging
- Documentation: [GITHUB-INTEGRATION.md](docs/GITHUB-INTEGRATION.md)
- Documentation: [RELEASE-PROCESS.md](docs/RELEASE-PROCESS.md)
- GitHub Actions workflows for CI/CD
  - Automated testing on Python 3.11, 3.12, 3.13
  - Automated releases with changelog extraction
- Test fixture: `tests/fixtures/test-work-items.yaml` for unit testing

### Removed

- Dependency on external sync scripts (`sync-github-project.sh`)
- `SYNC_SCRIPT_PATH` environment variable requirement

### Fixed

- Eliminated subprocess overhead for GitHub sync operations
- Improved error handling for GitHub API failures
- Data loader tests now pass with proper test fixtures

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

### Planned

- Phase 3: Work item creation tool
- Advanced filtering (logical operators, date ranges)
- Batch operations support
- Enhanced error recovery

[1.0.0]: https://github.com/astenlund74/wbs-mcp-server/releases/tag/v1.0.0
