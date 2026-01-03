"""Find orphan work items (missing parent or milestone)."""

from typing import Optional

from ..models import WorkItem


def find_orphan_items(items: list[WorkItem]) -> dict[str, list[WorkItem]]:
    """Find work items with missing relationships.
    
    Args:
        items: List of all work items
        
    Returns:
        Dictionary with orphan categories
    """
    orphans: dict[str, list[WorkItem]] = {
        "features_without_epic": [],
        "items_without_milestone": [],
        "broken_parent_refs": [],
    }
    
    wbs_ids = {item.wbs_id for item in items}
    
    for item in items:
        # Features without parent epic
        if item.wbs_type == "Feature" and not item.wbs_parent:
            orphans["features_without_epic"].append(item)
        
        # Items without milestone (epics and features)
        if not item.milestone and item.wbs_type in ["Epic", "Feature"]:
            orphans["items_without_milestone"].append(item)
        
        # Broken parent references
        if item.wbs_parent and item.wbs_parent not in wbs_ids:
            orphans["broken_parent_refs"].append(item)
    
    return orphans


def format_orphans(orphans: dict[str, list[WorkItem]]) -> str:
    """Format orphan items as text.
    
    Args:
        orphans: Dictionary of orphan categories
        
    Returns:
        Formatted string
    """
    lines = [
        "# Orphan Work Items",
        "",
    ]
    
    total_orphans = sum(len(items) for items in orphans.values())
    
    if total_orphans == 0:
        lines.append("✅ No orphan items found! All work items have proper relationships.")
        return "\n".join(lines)
    
    lines.append(f"Found {total_orphans} orphan items across {len([k for k, v in orphans.items() if v])} categories:")
    lines.append("")
    
    # Features without epic
    if orphans["features_without_epic"]:
        lines.extend([
            f"## 🔴 Features Without Parent Epic ({len(orphans['features_without_epic'])})",
            "",
            "These features should be assigned to an epic:",
            "",
        ])
        for item in orphans["features_without_epic"]:
            lines.append(f"- **{item.wbs_id}**: {item.title}")
            lines.append(f"  Status: {item.status} | Stream: {item.work_stream}")
        lines.append("")
    
    # Items without milestone
    if orphans["items_without_milestone"]:
        lines.extend([
            f"## 🟡 Items Without Milestone ({len(orphans['items_without_milestone'])})",
            "",
            "These items should be assigned to a milestone:",
            "",
        ])
        for item in orphans["items_without_milestone"]:
            lines.append(f"- **{item.wbs_id}**: {item.title}")
            lines.append(f"  Type: {item.wbs_type} | Status: {item.status}")
        lines.append("")
    
    # Broken parent references
    if orphans["broken_parent_refs"]:
        lines.extend([
            f"## 🚨 Broken Parent References ({len(orphans['broken_parent_refs'])})",
            "",
            "These items reference non-existent parents:",
            "",
        ])
        for item in orphans["broken_parent_refs"]:
            lines.append(f"- **{item.wbs_id}**: {item.title}")
            lines.append(f"  References missing parent: {item.wbs_parent}")
        lines.append("")
    
    return "\n".join(lines)
