"""Write operations for work items."""

import logging
from typing import Any, Dict

from ..data_loader import WorkItemsLoader
from ..github_sync import GitHubProjectSync
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
        if push_to_github and updated_item.issue_number:
            try:
                sync = GitHubProjectSync()
                sync_results = sync.sync_work_item(
                    updated_item.issue_number,
                    updates
                )
                result["github_synced"] = all(sync_results.values())
                result["github_sync_details"] = sync_results
                
                if not result["github_synced"]:
                    failed = [k for k, v in sync_results.items() if not v]
                    result["github_error"] = f"Failed to sync fields: {', '.join(failed)}"
            except Exception as e:
                logger.error(f"GitHub sync failed: {e}")
                result["github_error"] = str(e)
        elif push_to_github and not updated_item.issue_number:
            result["github_error"] = "No GitHub issue linked to work item"
        
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
