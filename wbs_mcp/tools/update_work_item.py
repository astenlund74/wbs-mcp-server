"""Write operations for work items."""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from ..data_loader import WorkItemsLoader, find_workspace_root
from ..yaml_writer import WorkItemWriter

logger = logging.getLogger(__name__)


def update_work_item(
    loader: WorkItemsLoader,
    wbs_id: str,
    updates: Dict[str, Any],
    push_to_github: bool = False
) -> Dict[str, Any]:
    """
    Update a work item in work-items.yaml.
    
    Args:
        loader: Data loader instance
        wbs_id: WBS ID to update
        updates: Dictionary of fields to update
        push_to_github: Whether to sync to GitHub after update
        
    Returns:
        Result dictionary with success status and updated fields
    """
    yaml_path = loader.yaml_path
    writer = WorkItemWriter(yaml_path)
    
    try:
        # Update the work item
        updated_item = writer.update_work_item(wbs_id, updates)
        
        result = {
            "success": True,
            "wbs_id": wbs_id,
            "updated_fields": list(updates.keys()),
            "github_synced": False,
            "issue_number": updated_item.issue_number
        }
        
        # Optionally push to GitHub
        if push_to_github:
            try:
                sync_result = _push_to_github(yaml_path, wbs_id)
                result["github_synced"] = sync_result["success"]
                if not sync_result["success"]:
                    result["github_error"] = sync_result.get("error", "Unknown error")
            except Exception as e:
                logger.error(f"GitHub sync failed: {e}")
                result["github_error"] = str(e)
        
        # Reload data loader cache
        loader.load(force_reload=True)
        
        return result
        
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "wbs_id": wbs_id
        }
    except Exception as e:
        logger.error(f"Unexpected error updating {wbs_id}: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "wbs_id": wbs_id
        }


def _push_to_github(yaml_path: Path, wbs_id: str) -> Dict[str, Any]:
    """Push work item updates to GitHub Project.
    
    Args:
        yaml_path: Path to work-items.yaml
        wbs_id: WBS ID to sync
        
    Returns:
        Dictionary with success status
    """
    repo_root = find_workspace_root(yaml_path)
    if not repo_root:
        return {"success": False, "error": "Could not find repository root (.git)"}
    
    sync_script = repo_root / "tools" / "sync-github-project.sh"
    
    if not sync_script.exists():
        return {
            "success": False,
            "error": f"Sync script not found: {sync_script}"
        }
    
    try:
        result = subprocess.run(
            [str(sync_script), "push", "--wbs-id", wbs_id],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return {"success": True, "output": result.stdout}
        else:
            return {
                "success": False,
                "error": f"Script failed (exit {result.returncode}): {result.stderr}"
            }
            
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Sync script timed out after 30s"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def format_update_result(result: Dict[str, Any]) -> str:
    """Format update result as human-readable text.
    
    Args:
        result: Result dictionary from update_work_item
        
    Returns:
        Formatted text output
    """
    if not result["success"]:
        return f"❌ Update failed: {result['error']}"
    
    lines = [
        f"✅ Successfully updated {result['wbs_id']}",
        f"   Updated fields: {', '.join(result['updated_fields'])}"
    ]
    
    if result.get("github_synced"):
        lines.append(f"   ✓ Synced to GitHub issue #{result['issue_number']}")
    elif "github_error" in result:
        lines.append(f"   ⚠️  GitHub sync failed: {result['github_error']}")
    
    return "\n".join(lines)
