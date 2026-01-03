"""Data loader for work-items.yaml with caching and file monitoring."""

import logging
import os
from pathlib import Path
from typing import Optional

import yaml

from .models import WorkItem

logger = logging.getLogger(__name__)


def find_workspace_root(start_path: Path) -> Optional[Path]:
    """Find workspace root by looking for .git directory.
    
    Args:
        start_path: Path to start searching from
        
    Returns:
        Path to workspace root or None if not found
    """
    current = start_path.resolve()
    
    # Walk up directories looking for .git
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    
    return None


class WorkItemsLoader:
    """Loads and caches work items from YAML file."""

    def __init__(self, yaml_path: Path):
        """Initialize loader.

        Args:
            yaml_path: Path to work-items.yaml file
        """
        self.yaml_path = yaml_path
        self._cache: Optional[list[WorkItem]] = None
        self._last_mtime: Optional[float] = None

    def _needs_reload(self) -> bool:
        """Check if file has been modified since last load."""
        if not self.yaml_path.exists():
            logger.error(f"Work items file not found: {self.yaml_path}")
            return False

        current_mtime = self.yaml_path.stat().st_mtime

        if self._last_mtime is None:
            return True

        return current_mtime > self._last_mtime

    def load(self, force_reload: bool = False) -> list[WorkItem]:
        """Load work items from YAML file.

        Args:
            force_reload: Force reload even if file hasn't changed

        Returns:
            List of work items

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            ValueError: If YAML is invalid
        """
        if not force_reload and self._cache is not None and not self._needs_reload():
            logger.debug("Using cached work items")
            return self._cache

        if not self.yaml_path.exists():
            raise FileNotFoundError(f"Work items file not found: {self.yaml_path}")

        logger.info(f"Loading work items from {self.yaml_path}")

        try:
            with open(self.yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict) or "work_items" not in data:
                raise ValueError("Invalid work-items.yaml structure: missing 'work_items' key")

            raw_items = data["work_items"]
            if not isinstance(raw_items, list):
                raise ValueError("Invalid work-items.yaml structure: 'work_items' must be a list")

            # Parse and validate each work item
            work_items = []
            for idx, item in enumerate(raw_items):
                try:
                    work_item = WorkItem(**item)
                    work_items.append(work_item)
                except Exception as e:
                    logger.warning(f"Skipping invalid work item at index {idx}: {e}")

            self._cache = work_items
            self._last_mtime = self.yaml_path.stat().st_mtime

            logger.info(f"Loaded {len(work_items)} work items")
            return work_items

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax: {e}")
        except Exception as e:
            logger.error(f"Error loading work items: {e}")
            raise

    def get_by_wbs_id(self, wbs_id: str) -> Optional[WorkItem]:
        """Get work item by WBS ID.

        Args:
            wbs_id: WBS ID (e.g., 'WS-17101')

        Returns:
            Work item or None if not found
        """
        items = self.load()
        for item in items:
            if item.wbs_id == wbs_id:
                return item
        return None

    def get_by_issue_number(self, issue_number: int) -> Optional[WorkItem]:
        """Get work item by GitHub issue number.

        Args:
            issue_number: GitHub issue number

        Returns:
            Work item or None if not found
        """
        items = self.load()
        for item in items:
            if item.issue_number == issue_number:
                return item
        return None

    def filter(
        self,
        status: Optional[str] = None,
        wbs_type: Optional[str] = None,
        milestone: Optional[str] = None,
        work_stream: Optional[str] = None,
        parent_wbs: Optional[str] = None,
    ) -> list[WorkItem]:
        """Filter work items by criteria.

        Args:
            status: Filter by status (e.g., 'Todo', 'In Progress')
            wbs_type: Filter by type (e.g., 'Epic', 'Feature')
            milestone: Filter by milestone
            work_stream: Filter by work stream
            parent_wbs: Filter by parent WBS ID

        Returns:
            Filtered list of work items
        """
        items = self.load()
        filtered = items

        if status:
            filtered = [i for i in filtered if i.status.lower() == status.lower()]

        if wbs_type:
            filtered = [i for i in filtered if i.wbs_type.lower() == wbs_type.lower()]

        if milestone:
            filtered = [i for i in filtered if i.milestone and milestone.lower() in i.milestone.lower()]

        if work_stream:
            filtered = [i for i in filtered if work_stream.lower() in i.work_stream.lower()]

        if parent_wbs:
            filtered = [i for i in filtered if i.wbs_parent == parent_wbs]

        return filtered
