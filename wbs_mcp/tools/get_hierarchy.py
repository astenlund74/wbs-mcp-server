"""Build work item hierarchy with status rollup."""

from typing import Optional

from ..models import HierarchyNode, WorkItem, WorkItemSummary


def build_hierarchy(items: list[WorkItem], root_wbs: Optional[str] = None) -> list[HierarchyNode]:
    """Build hierarchical tree of work items.
    
    Args:
        items: List of all work items
        root_wbs: Optional root WBS ID to start from (if None, shows all top-level items)
        
    Returns:
        List of hierarchy nodes with children
    """
    # Create lookup dict
    item_dict = {item.wbs_id: item for item in items}
    
    # Build children map
    children_map: dict[str, list[WorkItem]] = {}
    for item in items:
        if item.wbs_parent:
            if item.wbs_parent not in children_map:
                children_map[item.wbs_parent] = []
            children_map[item.wbs_parent].append(item)
    
    def build_node(item: WorkItem) -> HierarchyNode:
        """Recursively build hierarchy node."""
        children = children_map.get(item.wbs_id, [])
        child_nodes = [build_node(child) for child in children]
        
        # Calculate totals
        total_effort = item.effort_days
        completed_effort = item.effort_days if item.status == "Done" else 0.0
        
        for child_node in child_nodes:
            total_effort += child_node.total_effort
            completed_effort += child_node.completed_effort
        
        progress = (completed_effort / total_effort * 100) if total_effort > 0 else 0.0
        
        return HierarchyNode(
            work_item=WorkItemSummary(
                wbs_id=item.wbs_id,
                title=item.title,
                wbs_type=item.wbs_type,
                status=item.status,
                priority=item.priority,
                milestone=item.milestone,
                effort_days=item.effort_days,
            ),
            children=child_nodes,
            total_effort=total_effort,
            completed_effort=completed_effort,
            progress_percent=round(progress, 1),
        )
    
    # Find root items
    if root_wbs:
        # Start from specific root
        if root_wbs not in item_dict:
            return []
        return [build_node(item_dict[root_wbs])]
    else:
        # Show all epics (items without parents)
        roots = [item for item in items if not item.wbs_parent and item.wbs_type == "Epic"]
        return [build_node(item) for item in roots]


def format_hierarchy(nodes: list[HierarchyNode], indent: int = 0) -> str:
    """Format hierarchy nodes as text with indentation.
    
    Args:
        nodes: List of hierarchy nodes
        indent: Current indentation level
        
    Returns:
        Formatted string
    """
    lines = []
    prefix = "  " * indent
    
    for node in nodes:
        item = node.work_item
        status_icon = {
            "Done": "✅",
            "In Progress": "🔄",
            "Todo": "📋",
            "Blocked": "🚫",
        }.get(item.status, "❓")
        
        lines.append(
            f"{prefix}{status_icon} **{item.wbs_id}**: {item.title} "
            f"[{item.status}] ({node.progress_percent}% complete)"
        )
        lines.append(f"{prefix}   Effort: {item.effort_days}d | Total w/ children: {node.total_effort}d")
        
        if node.children:
            child_block = format_hierarchy(node.children, indent + 1)
            lines.extend(child_block.splitlines())
    
    return "\n".join(lines)
