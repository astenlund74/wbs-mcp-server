"""Calculate milestone progress and coverage."""

from collections import defaultdict
from typing import Optional

from ..models import MilestoneProgress, WorkItem


def calculate_milestone_progress(
    items: list[WorkItem],
    milestone_filter: Optional[str] = None,
) -> list[MilestoneProgress]:
    """Calculate progress for each milestone.
    
    Args:
        items: List of all work items
        milestone_filter: Optional milestone to filter by (partial match)
        
    Returns:
        List of milestone progress summaries
    """
    # Group by milestone
    milestone_items: dict[str, list[WorkItem]] = defaultdict(list)
    
    for item in items:
        if item.milestone:
            # Apply filter if provided
            if milestone_filter and milestone_filter.lower() not in item.milestone.lower():
                continue
            milestone_items[item.milestone].append(item)
    
    # Calculate progress for each milestone
    progress_list: list[MilestoneProgress] = []
    
    for milestone, milestone_work_items in sorted(milestone_items.items()):
        total_items = len(milestone_work_items)
        completed = sum(1 for i in milestone_work_items if i.status == "Done")
        in_progress = sum(1 for i in milestone_work_items if i.status == "In Progress")
        blocked = sum(1 for i in milestone_work_items if i.status == "Blocked")
        
        total_effort = sum(i.effort_days for i in milestone_work_items)
        completed_effort = sum(i.effort_days for i in milestone_work_items if i.status == "Done")
        
        progress_percent = (completed_effort / total_effort * 100) if total_effort > 0 else 0.0
        
        # Find epics in this milestone
        epics = sorted(set(
            i.wbs_id for i in milestone_work_items
            if i.wbs_type == "Epic"
        ))
        
        progress_list.append(MilestoneProgress(
            milestone=milestone,
            total_items=total_items,
            completed_items=completed,
            in_progress_items=in_progress,
            blocked_items=blocked,
            total_effort_days=total_effort,
            completed_effort_days=completed_effort,
            progress_percent=round(progress_percent, 1),
            epics=epics,
        ))
    
    return progress_list


def format_milestone_progress(progress_list: list[MilestoneProgress]) -> str:
    """Format milestone progress as text.
    
    Args:
        progress_list: List of milestone progress summaries
        
    Returns:
        Formatted string
    """
    if not progress_list:
        return "No milestones found with assigned work items."
    
    lines = [
        "# Milestone Progress Report",
        "",
        f"Tracking {len(progress_list)} milestone(s)",
        "",
    ]
    
    for progress in progress_list:
        # Progress bar
        bar_length = 20
        filled = int(progress.progress_percent / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        lines.extend([
            f"## {progress.milestone}",
            "",
            f"**Progress**: {progress.progress_percent}% | {bar}",
            "",
            "**Item Status**:",
            f"- ✅ Done: {progress.completed_items}",
            f"- 🔄 In Progress: {progress.in_progress_items}",
            f"- 🚫 Blocked: {progress.blocked_items}",
            f"- 📋 Todo: {progress.total_items - progress.completed_items - progress.in_progress_items - progress.blocked_items}",
            f"- **Total**: {progress.total_items} items",
            "",
            "**Effort**:",
            f"- Completed: {progress.completed_effort_days} days",
            f"- Total: {progress.total_effort_days} days",
            "",
        ])
        
        if progress.epics:
            lines.append(f"**Epics**: {', '.join(progress.epics)}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)
