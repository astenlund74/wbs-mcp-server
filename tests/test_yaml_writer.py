"""Tests for YAML writer functionality."""

import tempfile
from pathlib import Path
import pytest
from wbs_mcp.yaml_writer import WorkItemWriter


def create_test_yaml():
    """Create a temporary YAML file for testing."""
    content = """work_items:
- issue_number: 1
  wbs_id: WS-TEST-001
  wbs_type: Feature
  title: Test Item
  status: Todo
  priority: 🟡 Medium
  effort_days: 5.0
  work_stream: WS-TEST
  milestone: Test Milestone
  description: Test description
"""
    temp = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    temp.write(content)
    temp.close()
    return Path(temp.name)


def test_update_work_item_status():
    """Test updating work item status."""
    yaml_path = create_test_yaml()
    writer = WorkItemWriter(yaml_path)
    
    try:
        # Update status
        updated = writer.update_work_item(
            "WS-TEST-001",
            {"status": "In Progress"},
            create_backup=False
        )
        
        assert updated.wbs_id == "WS-TEST-001"
        assert updated.status == "In Progress"
        
        # Verify persistence
        writer2 = WorkItemWriter(yaml_path)
        with open(yaml_path, 'r') as f:
            content = f.read()
            assert "In Progress" in content
            
    finally:
        yaml_path.unlink()


def test_update_multiple_fields():
    """Test updating multiple fields at once."""
    yaml_path = create_test_yaml()
    writer = WorkItemWriter(yaml_path)
    
    try:
        updated = writer.update_work_item(
            "WS-TEST-001",
            {
                "status": "Done",
                "priority": "🚨 Critical",
                "effort_days": 8.0
            },
            create_backup=False
        )
        
        assert updated.status == "Done"
        assert updated.priority == "🚨 Critical"
        assert updated.effort_days == 8.0
        
    finally:
        yaml_path.unlink()


def test_update_invalid_wbs_id():
    """Test error handling for non-existent WBS ID."""
    yaml_path = create_test_yaml()
    writer = WorkItemWriter(yaml_path)
    
    try:
        with pytest.raises(ValueError, match="Work item not found"):
            writer.update_work_item(
                "WS-INVALID-999",
                {"status": "Done"},
                create_backup=False
            )
    finally:
        yaml_path.unlink()


def test_update_invalid_field():
    """Test error handling for invalid field names."""
    yaml_path = create_test_yaml()
    writer = WorkItemWriter(yaml_path)
    
    try:
        with pytest.raises(ValueError, match="Invalid fields"):
            writer.update_work_item(
                "WS-TEST-001",
                {"invalid_field": "value"},
                create_backup=False
            )
    finally:
        yaml_path.unlink()


def test_backup_creation():
    """Test that backup is created before updates."""
    yaml_path = create_test_yaml()
    writer = WorkItemWriter(yaml_path)
    backup_path = yaml_path.with_suffix('.yaml.bak')
    
    try:
        writer.update_work_item(
            "WS-TEST-001",
            {"status": "Done"},
            create_backup=True
        )
        
        assert backup_path.exists()
        
    finally:
        yaml_path.unlink()
        if backup_path.exists():
            backup_path.unlink()


def test_formatting_preservation():
    """Test that YAML formatting is preserved."""
    yaml_path = create_test_yaml()
    
    # Read original content
    with open(yaml_path, 'r') as f:
        original = f.read()
    
    writer = WorkItemWriter(yaml_path)
    
    try:
        writer.update_work_item(
            "WS-TEST-001",
            {"status": "In Progress"},
            create_backup=False
        )
        
        # Read updated content
        with open(yaml_path, 'r') as f:
            updated = f.read()
        
        # Should preserve structure (work_items key, indentation)
        assert "work_items:" in updated
        assert "- issue_number:" in updated
        # Indentation should be preserved (2 spaces)
        assert "\n  wbs_id:" in updated or "\n  title:" in updated
        
    finally:
        yaml_path.unlink()
