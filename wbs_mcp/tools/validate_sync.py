"""Validate work items for consistency issues."""

from ..models import ValidationIssue, ValidationResult, WorkItem


def validate_work_items(items: list[WorkItem]) -> ValidationResult:
    """Validate work items for consistency and reference issues.
    
    Args:
        items: List of all work items
        
    Returns:
        Validation result with any issues found
    """
    issues: list[ValidationIssue] = []
    wbs_ids = {item.wbs_id for item in items}
    issue_numbers = {item.issue_number for item in items}
    
    for item in items:
        # Check parent references
        if item.wbs_parent and item.wbs_parent not in wbs_ids:
            issues.append(ValidationIssue(
                severity="error",
                wbs_id=item.wbs_id,
                issue_type="missing_parent",
                message=f"References non-existent parent: {item.wbs_parent}",
            ))
        
        # Check issue parent references
        if item.issue_parent and item.issue_parent not in issue_numbers:
            issues.append(ValidationIssue(
                severity="error",
                wbs_id=item.wbs_id,
                issue_type="missing_issue_parent",
                message=f"References non-existent issue parent: #{item.issue_parent}",
            ))
        
        # Check for features without epic
        if item.wbs_type == "Feature" and not item.wbs_parent:
            issues.append(ValidationIssue(
                severity="warning",
                wbs_id=item.wbs_id,
                issue_type="orphan_feature",
                message="Feature has no parent epic",
            ))
        
        # Check for items without milestone
        if not item.milestone and item.wbs_type in ["Epic", "Feature"]:
            issues.append(ValidationIssue(
                severity="info",
                wbs_id=item.wbs_id,
                issue_type="missing_milestone",
                message=f"{item.wbs_type} has no milestone assigned",
            ))
        
        # Check for invalid status
        valid_statuses = ["Todo", "In Progress", "Done", "Blocked"]
        if item.status not in valid_statuses:
            issues.append(ValidationIssue(
                severity="error",
                wbs_id=item.wbs_id,
                issue_type="invalid_status",
                message=f"Invalid status '{item.status}' (must be one of: {', '.join(valid_statuses)})",
            ))
    
    # Check for duplicate WBS IDs (optimized: O(n) instead of O(n²))
    seen_wbs_ids = set()
    for item in items:
        if item.wbs_id in seen_wbs_ids:
            issues.append(ValidationIssue(
                severity="error",
                wbs_id=item.wbs_id,
                issue_type="duplicate_wbs_id",
                message=f"Duplicate WBS ID: {item.wbs_id}",
            ))
        seen_wbs_ids.add(item.wbs_id)
    
    return ValidationResult(
        is_valid=all(issue.severity != "error" for issue in issues),
        issues=issues,
        total_items=len(items),
    )


def format_validation_result(result: ValidationResult) -> str:
    """Format validation result as text.
    
    Args:
        result: Validation result
        
    Returns:
        Formatted string
    """
    lines = [
        f"# Validation Result",
        "",
        f"**Status**: {'✅ VALID' if result.is_valid else '❌ INVALID'}",
        f"**Total Items**: {result.total_items}",
        f"**Issues Found**: {len(result.issues)}",
        "",
    ]
    
    if not result.issues:
        lines.append("No issues found! All work items are consistent.")
        return "\n".join(lines)
    
    # Group by severity
    errors = [i for i in result.issues if i.severity == "error"]
    warnings = [i for i in result.issues if i.severity == "warning"]
    info = [i for i in result.issues if i.severity == "info"]
    
    if errors:
        lines.extend([
            "## ❌ Errors",
            "",
        ])
        for issue in errors:
            lines.append(f"- **{issue.wbs_id}** [{issue.issue_type}]: {issue.message}")
        lines.append("")
    
    if warnings:
        lines.extend([
            "## ⚠️ Warnings",
            "",
        ])
        for issue in warnings:
            lines.append(f"- **{issue.wbs_id}** [{issue.issue_type}]: {issue.message}")
        lines.append("")
    
    if info:
        lines.extend([
            "## ℹ️ Info",
            "",
        ])
        for issue in info:
            lines.append(f"- **{issue.wbs_id}** [{issue.issue_type}]: {issue.message}")
    
    return "\n".join(lines)
