"""YAML writer with formatting preservation for work items."""

import logging
import shutil
from pathlib import Path
from typing import Any, Dict, Optional
from ruamel.yaml import YAML

from .models import WorkItem

logger = logging.getLogger(__name__)


class WorkItemWriter:
    """Write work items to YAML while preserving formatting and comments."""
    
    def __init__(self, yaml_path: Path):
        """Initialize the writer.
        
        Args:
            yaml_path: Path to work-items.yaml file
        """
        self.yaml_path = yaml_path
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
        self.yaml.indent(mapping=2, sequence=2, offset=0)
    
    def update_work_item(
        self, 
        wbs_id: str, 
        updates: Dict[str, Any],
        create_backup: bool = True
    ) -> WorkItem:
        """Update a work item in the YAML file.
        
        Args:
            wbs_id: WBS ID of the item to update
            updates: Dictionary of fields to update
            create_backup: Whether to create a backup before writing
            
        Returns:
            Updated WorkItem object
            
        Raises:
            ValueError: If WBS ID not found or invalid field values
            FileNotFoundError: If YAML file doesn't exist
        """
        # Create backup
        backup_path = self.yaml_path.with_suffix('.yaml.bak')
        if create_backup:
            shutil.copy2(self.yaml_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        # Load current YAML
        with open(self.yaml_path, 'r') as f:
            data = self.yaml.load(f)
        
        if not data or 'work_items' not in data:
            raise ValueError("Invalid YAML structure: missing 'work_items' key")
        
        # Find the work item
        item_dict = None
        item_index = None
        for idx, item in enumerate(data['work_items']):
            if item.get('wbs_id') == wbs_id:
                item_dict = item
                item_index = idx
                break
        
        if item_dict is None:
            raise ValueError(f"Work item not found: {wbs_id}")
        
        # Validate updates
        valid_fields = {
            'status', 'priority', 'milestone', 'assignees', 
            'start_date', 'end_date', 'effort_days', 'description',
            'title', 'responsible_architect', 'allow_yaml_override'
        }
        
        invalid_fields = set(updates.keys()) - valid_fields
        if invalid_fields:
            raise ValueError(f"Invalid fields for update: {invalid_fields}")
        
        # Apply updates
        original_values = {}
        for key, value in updates.items():
            original_values[key] = item_dict.get(key)
            item_dict[key] = value
            logger.info(f"Updated {wbs_id}.{key}: {original_values[key]} → {value}")
        
        # Write back to file
        try:
            with open(self.yaml_path, 'w') as f:
                self.yaml.dump(data, f)
            logger.info(f"Successfully wrote updates to {self.yaml_path}")
        except Exception as e:
            # Restore backup on write failure
            if create_backup and backup_path.exists():
                shutil.copy2(backup_path, self.yaml_path)
                logger.error(f"Write failed, restored backup: {e}")
            raise
        
        # Return updated WorkItem
        return WorkItem(**item_dict)