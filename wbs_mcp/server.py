"""MCP server for GitHub Projects with WBS structure."""

import logging
import os
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .data_loader import WorkItemsLoader, find_workspace_root
from .models import WorkItem, WorkItemSummary
from .tools import (
    build_hierarchy,
    calculate_milestone_progress,
    find_orphan_items,
    validate_work_items,
)
from .tools.get_hierarchy import format_hierarchy
from .tools.validate_sync import format_validation_result
from .tools.find_orphans import format_orphans
from .tools.get_milestone_coverage import format_milestone_progress
from .tools.update_work_item import update_work_item, format_update_result
from .tools.pr_review_read import list_pr_review_threads, format_review_threads
from .tools.pr_review_write import (
    reply_to_review_thread,
    resolve_review_thread,
    format_reply_result,
    format_resolve_result,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize server
app = Server("wbs-mcp-server")

# Global loader instance
loader: WorkItemsLoader | None = None


def get_loader() -> WorkItemsLoader:
    """Get or create the work items loader."""
    global loader
    if loader is None:
        # Strategy 1: Check environment variable (WBS_WORK_ITEMS_PATH) to override the default;
        # expected value is an absolute path to the work-items.yaml file.
        yaml_path_str = os.environ.get("WBS_WORK_ITEMS_PATH")
        
        if yaml_path_str:
            yaml_path = Path(yaml_path_str)
            logger.info(f"Using YAML path from environment: {yaml_path}")
        else:
            # Strategy 2: Auto-detect workspace root
            server_file = Path(__file__).resolve()
            workspace_root = find_workspace_root(server_file)
            
            if workspace_root:
                yaml_path = workspace_root / "8-REALIZATION" / "backlog" / "work-items.yaml"
                logger.info(f"Auto-detected workspace root: {workspace_root}")
            else:
                # Strategy 3: Fallback to relative path from server location
                yaml_path = server_file.parent.parent.parent.parent / "8-REALIZATION" / "backlog" / "work-items.yaml"
                logger.warning(f"Could not find workspace root, using relative path")
        
        logger.info(f"Loading work items from: {yaml_path}")
        loader = WorkItemsLoader(yaml_path)
    
    return loader


def format_work_item_summary(item: WorkItem) -> str:
    """Format work item for display."""
    lines = [
        f"**{item.wbs_id}**: {item.title}",
        f"Type: {item.wbs_type} | Status: {item.status} | Priority: {item.priority}",
        f"Effort: {item.effort_days} days | Stream: {item.work_stream}",
    ]
    
    if item.milestone:
        lines.append(f"Milestone: {item.milestone}")
    
    if item.wbs_parent:
        lines.append(f"Parent: {item.wbs_parent}")
    
    if item.responsible_architect:
        lines.append(f"Owner: {item.responsible_architect}")
    
    if item.start_date and item.end_date:
        lines.append(f"Timeline: {item.start_date} → {item.end_date}")
    
    return "\n".join(lines)


def format_work_item_detail(item: WorkItem) -> str:
    """Format work item with full details."""
    lines = [
        f"# {item.wbs_id}: {item.title}",
        "",
        f"**Type**: {item.wbs_type}",
        f"**Status**: {item.status}",
        f"**Priority**: {item.priority}",
        f"**Work Stream**: {item.work_stream}",
        f"**Effort**: {item.effort_days} days",
        "",
    ]
    
    if item.milestone:
        lines.append(f"**Milestone**: {item.milestone}")
    
    if item.wbs_parent:
        lines.append(f"**Parent WBS**: {item.wbs_parent}")
    
    if item.responsible_architect:
        lines.append(f"**Responsible Architect**: {item.responsible_architect}")
    
    if item.start_date and item.end_date:
        lines.extend(["", f"**Timeline**: {item.start_date} → {item.end_date}"])
    
    if item.assignees:
        lines.extend(["", f"**Assignees**: {', '.join(item.assignees)}"])
    
    lines.extend([
        "",
        f"**GitHub Issue**: #{item.issue_number}",
        "",
        "## Description",
        "",
        item.description if item.description else "*No description provided*",
    ])
    
    return "\n".join(lines)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="list_work_items",
            description="List and filter work items from work-items.yaml. Returns items matching the specified criteria. Use this to explore the backlog, find items by status, type, milestone, or work stream.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by status (e.g., 'Todo', 'In Progress', 'Done', 'Blocked')",
                    },
                    "wbs_type": {
                        "type": "string",
                        "description": "Filter by type (e.g., 'Epic', 'Feature', 'Task')",
                    },
                    "milestone": {
                        "type": "string",
                        "description": "Filter by milestone (partial match, e.g., 'M1.1')",
                    },
                    "work_stream": {
                        "type": "string",
                        "description": "Filter by work stream (partial match, e.g., 'WS1', 'Repository')",
                    },
                    "parent_wbs": {
                        "type": "string",
                        "description": "Filter by parent WBS ID (e.g., 'WS-11100' for all features under that epic)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 50)",
                        "default": 50,
                    },
                },
            },
        ),
        Tool(
            name="get_work_item",
            description="Get detailed information about a specific work item by WBS ID or GitHub issue number. Returns full description, relationships, and metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "wbs_id": {
                        "type": "string",
                        "description": "WBS ID of the work item (e.g., 'WS-17101')",
                    },
                    "issue_number": {
                        "type": "integer",
                        "description": "GitHub issue number (alternative to wbs_id)",
                    },
                },
                "oneOf": [
                    {"required": ["wbs_id"]},
                    {"required": ["issue_number"]},
                ],
            },
        ),
        Tool(
            name="get_hierarchy",
            description="Get hierarchical view of work items (epic → features → tasks) with status rollup and progress calculation. Shows parent-child relationships with effort totals.",
            inputSchema={
                "type": "object",
                "properties": {
                    "root_wbs": {
                        "type": "string",
                        "description": "Optional root WBS ID to start from (e.g., 'WS-17001'). If not provided, shows all top-level epics.",
                    },
                },
            },
        ),
        Tool(
            name="validate_sync",
            description="Validate work-items.yaml for consistency issues: missing parents, broken references, orphaned items, invalid statuses. Use this to check data quality.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="find_orphans",
            description="Find orphan work items: features without epics, items without milestones, broken parent references. Use this to identify cleanup tasks.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_milestone_coverage",
            description="Get progress summary by milestone: item counts, effort totals, completion percentage. Use this for milestone tracking and reporting.",
            inputSchema={
                "type": "object",
                "properties": {
                    "milestone_filter": {
                        "type": "string",
                        "description": "Optional milestone filter (partial match, e.g., 'M1')",
                    },
                },
            },
        ),
        Tool(
            name="update_work_item",
            description="Update a work item in work-items.yaml. Can modify status, priority, milestone, assignees, dates, and other fields. Optionally syncs changes to GitHub Project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "wbs_id": {
                        "type": "string",
                        "description": "WBS ID of the work item to update (e.g., 'WS-17101')",
                    },
                    "updates": {
                        "type": "object",
                        "description": "Dictionary of fields to update",
                        "properties": {
                            "status": {"type": "string", "description": "Status (e.g., 'To Do', 'In Progress', 'Done', 'Blocked')"},
                            "priority": {"type": "string", "description": "Priority (🚨 Critical, 🟡 Medium, 🟢 Low)"},
                            "milestone": {"type": "string", "description": "Milestone (e.g., 'M1.2: Logical Layer Integration')"},
                            "assignees": {"type": "array", "items": {"type": "string"}, "description": "List of assignee usernames"},
                            "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                            "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                            "effort_days": {"type": "number", "description": "Effort in days"},
                            "description": {"type": "string", "description": "Full description"},
                            "responsible_architect": {"type": "string", "description": "Responsible architect name"},
                            "allow_yaml_override": {"type": "boolean", "description": "Whether to allow YAML overrides of GitHub data"},
                        },
                    },
                    "push_to_github": {
                        "type": "boolean",
                        "description": "Whether to sync changes to GitHub Project (default: false)",
                        "default": False,
                    },
                },
                "required": ["wbs_id", "updates"],
            },
        ),
        Tool(
            name="list_pr_review_threads",
            description="List unresolved review threads for a pull request. Auto-detects PR from current branch if pr_number not provided. Use this to see what review comments need addressing.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pr_number": {
                        "type": "integer",
                        "description": "PR number (optional - auto-detects from current branch)",
                    },
                },
            },
        ),
        Tool(
            name="reply_to_review_thread",
            description="Add a reply comment to a review thread. Use this to respond to reviewer feedback with explanations of fixes made.",
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_id": {
                        "type": "string",
                        "description": "Review thread ID (from list_pr_review_threads)",
                    },
                    "body": {
                        "type": "string",
                        "description": "Reply text (supports markdown)",
                    },
                },
                "required": ["thread_id", "body"],
            },
        ),
        Tool(
            name="resolve_review_thread",
            description="Mark a review thread as resolved. Use after addressing the feedback and replying to the thread.",
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_id": {
                        "type": "string",
                        "description": "Review thread ID (from list_pr_review_threads)",
                    },
                },
                "required": ["thread_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        data_loader = get_loader()
        
        if name == "list_work_items":
            return await handle_list_work_items(data_loader, arguments)
        elif name == "get_work_item":
            return await handle_get_work_item(data_loader, arguments)
        elif name == "get_hierarchy":
            return await handle_get_hierarchy(data_loader, arguments)
        elif name == "validate_sync":
            return await handle_validate_sync(data_loader, arguments)
        elif name == "find_orphans":
            return await handle_find_orphans(data_loader, arguments)
        elif name == "get_milestone_coverage":
            return await handle_get_milestone_coverage(data_loader, arguments)
        elif name == "update_work_item":
            return await handle_update_work_item(data_loader, arguments)
        elif name == "list_pr_review_threads":
            return await handle_list_pr_review_threads(arguments)
        elif name == "reply_to_review_thread":
            return await handle_reply_to_review_thread(arguments)
        elif name == "resolve_review_thread":
            return await handle_resolve_review_thread(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        logger.error(f"Error handling tool call {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_list_work_items(loader: WorkItemsLoader, args: dict[str, Any]) -> list[TextContent]:
    """Handle list_work_items tool call."""
    status = args.get("status")
    wbs_type = args.get("wbs_type")
    milestone = args.get("milestone")
    work_stream = args.get("work_stream")
    parent_wbs = args.get("parent_wbs")
    limit = args.get("limit", 50)
    
    # Filter items
    items = loader.filter(
        status=status,
        wbs_type=wbs_type,
        milestone=milestone,
        work_stream=work_stream,
        parent_wbs=parent_wbs,
    )
    
    # Apply limit
    items = items[:limit]
    
    if not items:
        return [TextContent(
            type="text",
            text="No work items found matching the specified criteria."
        )]
    
    # Format results
    lines = [
        f"Found {len(items)} work items",
        "",
        "---",
        "",
    ]
    
    for item in items:
        lines.append(format_work_item_summary(item))
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return [TextContent(type="text", text="\n".join(lines))]


async def handle_get_work_item(loader: WorkItemsLoader, args: dict[str, Any]) -> list[TextContent]:
    """Handle get_work_item tool call."""
    wbs_id = args.get("wbs_id")
    issue_number = args.get("issue_number")
    
    if not wbs_id and not issue_number:
        return [TextContent(
            type="text",
            text="Error: Must provide either wbs_id or issue_number"
        )]
    
    # Look up item
    if wbs_id:
        item = loader.get_by_wbs_id(wbs_id)
        if not item:
            return [TextContent(type="text", text=f"Work item not found: {wbs_id}")]
    else:
        item = loader.get_by_issue_number(issue_number)
        if not item:
            return [TextContent(type="text", text=f"Work item not found: #{issue_number}")]
    
    # Format detailed view
    return [TextContent(type="text", text=format_work_item_detail(item))]


async def handle_get_hierarchy(loader: WorkItemsLoader, args: dict[str, Any]) -> list[TextContent]:
    """Handle get_hierarchy tool call."""
    root_wbs = args.get("root_wbs")
    
    items = loader.load()
    hierarchy = build_hierarchy(items, root_wbs)
    
    if not hierarchy:
        return [TextContent(
            type="text",
            text=f"No hierarchy found{f' for root {root_wbs}' if root_wbs else ''}"
        )]
    
    output = format_hierarchy(hierarchy)
    return [TextContent(type="text", text=output)]


async def handle_validate_sync(loader: WorkItemsLoader, args: dict[str, Any]) -> list[TextContent]:
    """Handle validate_sync tool call."""
    items = loader.load()
    result = validate_work_items(items)
    
    output = format_validation_result(result)
    return [TextContent(type="text", text=output)]


async def handle_find_orphans(loader: WorkItemsLoader, args: dict[str, Any]) -> list[TextContent]:
    """Handle find_orphans tool call."""
    items = loader.load()
    orphans = find_orphan_items(items)
    
    output = format_orphans(orphans)
    return [TextContent(type="text", text=output)]


async def handle_get_milestone_coverage(loader: WorkItemsLoader, args: dict[str, Any]) -> list[TextContent]:
    """Handle get_milestone_coverage tool call."""
    milestone_filter = args.get("milestone_filter")
    
    items = loader.load()
    progress_list = calculate_milestone_progress(items, milestone_filter)
    
    output = format_milestone_progress(progress_list)
    return [TextContent(type="text", text=output)]


async def handle_update_work_item(loader: WorkItemsLoader, args: dict[str, Any]) -> list[TextContent]:
    """Handle update_work_item tool call."""
    wbs_id = args.get("wbs_id")
    updates = args.get("updates", {})
    push_to_github = args.get("push_to_github", False)
    
    if not wbs_id:
        return [TextContent(type="text", text="❌ Error: wbs_id is required")]
    
    if not updates:
        return [TextContent(type="text", text="❌ Error: updates dictionary is required")]
    
    result = update_work_item(loader, wbs_id, updates, push_to_github)
    output = format_update_result(result)
    
    return [TextContent(type="text", text=output)]


async def handle_list_pr_review_threads(args: dict[str, Any]) -> list[TextContent]:
    """Handle list_pr_review_threads tool call."""
    pr_number = args.get("pr_number")
    
    result = list_pr_review_threads(pr_number)
    output = format_review_threads(result)
    
    return [TextContent(type="text", text=output)]


async def handle_reply_to_review_thread(args: dict[str, Any]) -> list[TextContent]:
    """Handle reply_to_review_thread tool call."""
    thread_id = args.get("thread_id")
    body = args.get("body")
    
    if not thread_id or not body:
        return [TextContent(type="text", text="❌ Error: thread_id and body are required")]
    
    result = reply_to_review_thread(thread_id, body)
    output = format_reply_result(result)
    
    return [TextContent(type="text", text=output)]


async def handle_resolve_review_thread(args: dict[str, Any]) -> list[TextContent]:
    """Handle resolve_review_thread tool call."""
    thread_id = args.get("thread_id")
    
    if not thread_id:
        return [TextContent(type="text", text="❌ Error: thread_id is required")]
    
    result = resolve_review_thread(thread_id)
    output = format_resolve_result(result)
    
    return [TextContent(type="text", text=output)]


async def async_main():
    """Run the MCP server (async)."""
    logger.info("Starting WBS MCP Server")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main():
    """Entry point for the MCP server (sync wrapper)."""
    import asyncio
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
