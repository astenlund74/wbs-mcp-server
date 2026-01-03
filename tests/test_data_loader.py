"""Test data loader functionality."""

from pathlib import Path

import pytest

from wbs_mcp.data_loader import WorkItemsLoader


@pytest.fixture
def yaml_path():
    """Get path to test fixture work-items.yaml."""
    # Path relative to test file
    test_dir = Path(__file__).parent
    return test_dir / "fixtures" / "work-items.yaml"


@pytest.fixture
def loader(yaml_path):
    """Create loader instance."""
    return WorkItemsLoader(yaml_path)


def test_load_work_items(loader):
    """Test loading work items from YAML."""
    items = loader.load()
    
    assert len(items) > 0, "Should load at least one work item"
    
    # Check first item structure
    first_item = items[0]
    assert first_item.wbs_id
    assert first_item.title
    assert first_item.wbs_type in ["Epic", "Feature", "Task"]
    assert first_item.status in ["Todo", "In Progress", "Done", "Blocked"]


def test_get_by_wbs_id(loader):
    """Test getting work item by WBS ID."""
    item = loader.get_by_wbs_id("WS-17101")
    
    assert item is not None, "Should find WS-17101"
    assert item.wbs_id == "WS-17101"
    assert "MCP Server" in item.title


def test_get_by_issue_number(loader):
    """Test getting work item by issue number."""
    item = loader.get_by_issue_number(54)
    
    assert item is not None, "Should find issue #54"
    assert item.issue_number == 54
    assert item.wbs_id == "WS-17101"


def test_filter_by_status(loader):
    """Test filtering by status."""
    in_progress = loader.filter(status="In Progress")
    
    assert all(item.status == "In Progress" for item in in_progress)


def test_filter_by_type(loader):
    """Test filtering by WBS type."""
    epics = loader.filter(wbs_type="Epic")
    
    assert all(item.wbs_type == "Epic" for item in epics)
    assert len(epics) > 0, "Should have at least one epic"


def test_filter_by_milestone(loader):
    """Test filtering by milestone."""
    m11_items = loader.filter(milestone="M1.1")
    
    for item in m11_items:
        assert item.milestone is not None
        assert "M1.1" in item.milestone


def test_filter_by_parent(loader):
    """Test filtering by parent WBS ID."""
    # Get features under WS-17001 epic
    children = loader.filter(parent_wbs="WS-17001")
    
    assert all(item.wbs_parent == "WS-17001" for item in children)
    # Should include WS-17101 and WS-17102
    wbs_ids = [item.wbs_id for item in children]
    assert "WS-17101" in wbs_ids


def test_caching(loader):
    """Test that loader caches results."""
    # First load
    items1 = loader.load()
    
    # Second load should use cache
    items2 = loader.load()
    
    # Should be exact same objects (cached)
    assert items1 is items2
