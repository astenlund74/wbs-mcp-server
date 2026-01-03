"""Pydantic models for RPDS work items."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class WorkItem(BaseModel):
    """Work item from work-items.yaml."""

    model_config = ConfigDict(populate_by_name=True)

    issue_number: int
    wbs_id: str
    wbs_type: str  # Epic, Feature, Task
    wbs_parent: Optional[str] = None
    issue_parent: Optional[int] = None
    milestone: Optional[str] = None
    title: str
    priority: str  # 🚨 Critical, 🔥 High, 🟡 Medium, 🟢 Low
    effort_days: float
    work_stream: str
    status: str  # Todo, In Progress, Done, Blocked
    assignees: list[str] = Field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    responsible_architect: str = ""
    github_type: str = ""
    github_created_at: Optional[str] = None
    github_updated_at: Optional[str] = None
    last_synced_at: Optional[str] = None
    allow_yaml_override: bool = False
    description: str = ""


class WorkItemSummary(BaseModel):
    """Lightweight work item summary for listings."""

    wbs_id: str
    title: str
    wbs_type: str
    status: str
    priority: str
    milestone: Optional[str] = None
    effort_days: float


class HierarchyNode(BaseModel):
    """Work item with children for hierarchy view."""

    work_item: WorkItemSummary
    children: list["HierarchyNode"] = Field(default_factory=list)
    total_effort: float = 0.0
    completed_effort: float = 0.0
    progress_percent: float = 0.0


class MilestoneProgress(BaseModel):
    """Progress summary for a milestone."""

    milestone: str
    total_items: int
    completed_items: int
    in_progress_items: int
    blocked_items: int
    total_effort_days: float
    completed_effort_days: float
    progress_percent: float
    epics: list[str] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    """Issue found during validation."""

    severity: str  # error, warning, info
    wbs_id: str
    issue_type: str
    message: str


class ValidationResult(BaseModel):
    """Result of validate_sync operation."""

    is_valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
    total_items: int
    checked_at: datetime = Field(default_factory=lambda: datetime.now())


# Allow forward references for recursive models
HierarchyNode.model_rebuild()
