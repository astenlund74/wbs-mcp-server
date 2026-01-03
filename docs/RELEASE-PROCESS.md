# Release Process

## Overview

WBS MCP Server uses GitHub Actions for automated testing and releases. This ensures quality and provides versioned, stable releases for users.

## Workflows

### 1. Test Workflow (`test.yml`)

**Triggers:** Push to main, pull requests

**What it does:**
- Runs tests on Python 3.11, 3.12, 3.13
- Checks code with ruff and black
- Runs type checking with mypy
- Generates coverage reports

**Status:** [![Test](https://github.com/astenlund74/wbs-mcp-server/actions/workflows/test.yml/badge.svg)](https://github.com/astenlund74/wbs-mcp-server/actions/workflows/test.yml)

### 2. Release Workflow (`release.yml`)

**Triggers:** Push tags matching `v*.*.*` (e.g., v2.0.0)

**What it does:**
- Extracts version from tag
- Generates release notes from CHANGELOG.md
- Creates GitHub Release with:
  - Installation instructions
  - Configuration examples
  - Changelog excerpt

**Future:** Can publish to PyPI (currently commented out)

## Creating a Release

### Step 1: Update Version Numbers

Update version in these files:

```bash
# pyproject.toml
version = "2.0.0"

# CHANGELOG.md (move Unreleased to versioned section)
## [2.0.0] - 2026-01-03
```

### Step 2: Update CHANGELOG.md

Move `## [Unreleased]` content to versioned section:

```markdown
## [Unreleased]

(Empty or new unreleased changes)

## [2.0.0] - 2026-01-03

### Added
- Feature A
- Feature B

### Changed
- Update C

### Fixed
- Bug D
```

### Step 3: Commit and Tag

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: Prepare release v2.0.0"
git push origin main

# Create and push tag
git tag v2.0.0 -m "Release v2.0.0: Self-contained GitHub integration"
git push origin v2.0.0
```

### Step 4: Verify Release

1. Check GitHub Actions: https://github.com/astenlund74/wbs-mcp-server/actions
2. Verify release created: https://github.com/astenlund74/wbs-mcp-server/releases
3. Test installation from release:

```bash
uv pip install git+https://github.com/astenlund74/wbs-mcp-server.git@v2.0.0
```

## Version Pinning for Users

### Why Pin Versions?

**Benefits:**
- ✅ Stability - No surprise breaking changes
- ✅ Reproducibility - Same version across environments
- ✅ Control - Upgrade on your schedule
- ✅ Rollback - Easy to revert if issues

**Without pinning (not recommended):**
```json
"git+https://github.com/astenlund74/wbs-mcp-server.git"
```
👎 Always pulls latest main - may break without warning

**With pinning (recommended):**
```json
"git+https://github.com/astenlund74/wbs-mcp-server.git@v2.0.0"
```
👍 Locked to v2.0.0 - predictable behavior

### Upgrade Process

When a new version releases:

1. **Review changelog:**
   - Check release notes: https://github.com/astenlund74/wbs-mcp-server/releases
   - Look for breaking changes

2. **Update configuration:**
   ```diff
   - "git+...@v2.0.0",
   + "git+...@v2.1.0",
   ```

3. **Test in development:**
   - Reload MCP server in VS Code/Claude
   - Test read operations
   - Test write operations with GitHub sync

4. **Deploy to production:**
   - Commit updated `.vscode/mcp.json`
   - Push to repository

## Versioning Strategy

We follow [Semantic Versioning](https://semver.org/):

- **Major (X.0.0)**: Breaking changes
  - Example: v2.0.0 removed SYNC_SCRIPT_PATH
  - Users must update configuration

- **Minor (0.X.0)**: New features, backward compatible
  - Example: v2.1.0 adds batch update tool
  - Users can upgrade without changes

- **Patch (0.0.X)**: Bug fixes
  - Example: v2.0.1 fixes error message
  - Safe to upgrade immediately

## CI/CD Pipeline

```
┌─────────────────────────────────────────────────────────┐
│ Developer Workflow                                      │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│ 1. git push origin feature-branch                       │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│ 2. GitHub Actions: Test Workflow                       │
│    - Run pytest on Python 3.11, 3.12, 3.13             │
│    - Check code with ruff/black                         │
│    - Type check with mypy                               │
│    - Status reported on PR                              │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Code Review & Merge to main                          │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Update version in pyproject.toml & CHANGELOG.md     │
│    git tag v2.1.0 && git push origin v2.1.0            │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│ 5. GitHub Actions: Release Workflow                    │
│    - Create GitHub Release                              │
│    - Generate release notes                             │
│    - Attach installation instructions                   │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│ 6. Users Update Their Configurations                    │
│    - Pin to new version in mcp.json                     │
│    - Test and deploy                                    │
└─────────────────────────────────────────────────────────┘
```

## Hotfix Process

For critical bugs in production:

```bash
# Create hotfix branch from tag
git checkout v2.0.0
git checkout -b hotfix/v2.0.1

# Fix bug, update tests
git add .
git commit -m "fix: Critical bug in GitHub sync"

# Update version
# pyproject.toml: version = "2.0.1"
# CHANGELOG.md: Add [2.0.1] section

# Tag and push
git tag v2.0.1 -m "Hotfix: Critical bug fix"
git push origin v2.0.1

# Merge back to main
git checkout main
git merge hotfix/v2.0.1
git push origin main
```

## Future: PyPI Publishing

Currently commented out in `release.yml`. To enable:

1. **Create PyPI account:**
   - https://pypi.org/account/register/

2. **Set up trusted publishing:**
   - PyPI → Account Settings → Publishing
   - Add GitHub repository

3. **Uncomment workflow section:**
   ```yaml
   publish-pypi:
     needs: create-release
     runs-on: ubuntu-latest
     permissions:
       id-token: write
     
     steps:
       - uses: actions/checkout@v4
       - name: Install uv
         uses: astral-sh/setup-uv@v4
       - name: Build package
         run: uv build
       - name: Publish to PyPI
         uses: pypa/gh-action-pypi-publish@release/v1
   ```

4. **Update installation:**
   ```bash
   # Simple PyPI install
   uv pip install wbs-mcp-server==2.0.0
   ```

## Monitoring Releases

**GitHub Releases:** https://github.com/astenlund74/wbs-mcp-server/releases

**Watch for updates:**
- Click "Watch" → "Releases only" on GitHub
- Get notifications for new versions

**Changelog:** [CHANGELOG.md](../CHANGELOG.md)

## Questions?

- GitHub Issues: https://github.com/astenlund74/wbs-mcp-server/issues
- Discussions: https://github.com/astenlund74/wbs-mcp-server/discussions
