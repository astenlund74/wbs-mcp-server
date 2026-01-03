"""PR review thread tools - read operations."""

import json
import logging
import subprocess
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Maximum comment length to display before truncating
MAX_COMMENT_DISPLAY_LENGTH = 500


def list_pr_review_threads(pr_number: Optional[int] = None) -> Dict[str, Any]:
    """
    List unresolved review threads for a PR.
    
    Args:
        pr_number: PR number (if None, auto-detect from current branch)
        
    Returns:
        Dictionary with PR number and list of unresolved threads
    """
    try:
        # Auto-detect PR number if not provided
        if pr_number is None:
            pr_number = _get_current_pr_number()
            if pr_number is None:
                return {
                    "success": False,
                    "error": "Could not determine PR number from current branch"
                }
        
        # GraphQL query to get review threads
        query = '''
        query($owner: String!, $repo: String!, $pr: Int!) {
            repository(owner: $owner, name: $repo) {
                pullRequest(number: $pr) {
                    reviewThreads(first: 50) {
                        nodes {
                            id
                            isResolved
                            comments(first: 10) {
                                nodes {
                                    author { login }
                                    body
                                    path
                                    line
                                    createdAt
                                }
                            }
                        }
                    }
                }
            }
        }
        '''
        
        # Get repo info
        repo_info = _get_repo_info()
        if not repo_info:
            return {"success": False, "error": "Could not determine repository info"}
        
        # Execute query
        result = subprocess.run(
            [
                "gh", "api", "graphql",
                "-f", f"query={query}",
                "-f", f"owner={repo_info['owner']}",
                "-f", f"repo={repo_info['repo']}",
                "-F", f"pr={pr_number}"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"GraphQL query failed: {result.stderr}"
            }
        
        data = json.loads(result.stdout)
        threads = data["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"]
        
        # Filter to unresolved threads
        unresolved = []
        for thread in threads:
            if not thread["isResolved"] and thread["comments"]["nodes"]:
                first_comment = thread["comments"]["nodes"][0]
                unresolved.append({
                    "thread_id": thread["id"],
                    "file_path": first_comment.get("path"),
                    "line": first_comment.get("line"),
                    "author": first_comment["author"]["login"],
                    "body": first_comment["body"],
                    "created_at": first_comment["createdAt"],
                    "comment_count": len(thread["comments"]["nodes"])
                })
        
        return {
            "success": True,
            "pr_number": pr_number,
            "unresolved_threads": unresolved,
            "total_unresolved": len(unresolved)
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Request timed out after 30s"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Failed to parse response: {e}"}
    except Exception as e:
        logger.error(f"Unexpected error listing review threads: {e}")
        return {"success": False, "error": str(e)}


def _get_current_pr_number() -> Optional[int]:
    """Get PR number for current branch."""
    try:
        result = subprocess.run(
            ["gh", "pr", "view", "--json", "number"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            number = data.get("number")
            return int(number) if number is not None else None
    except Exception as e:
        logger.error(f"Failed to get PR number: {e}")
    return None


def _get_repo_info() -> Optional[Dict[str, str]]:
    """Get current repository owner and name."""
    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "owner,name"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                "owner": data["owner"]["login"],
                "repo": data["name"]
            }
    except Exception as e:
        logger.error(f"Failed to get repo info: {e}")
    return None


def format_review_threads(result: Dict[str, Any]) -> str:
    """Format review threads as human-readable text.
    
    Args:
        result: Result from list_pr_review_threads
        
    Returns:
        Formatted text output
    """
    if not result["success"]:
        return f"❌ Failed to get review threads: {result['error']}"
    
    pr_num = result["pr_number"]
    threads = result["unresolved_threads"]
    
    if not threads:
        return f"✅ PR #{pr_num}: No unresolved review threads"
    
    lines = [
        f"📋 PR #{pr_num}: {result['total_unresolved']} unresolved review thread(s)",
        ""
    ]
    
    for i, thread in enumerate(threads, 1):
        file_path = thread.get('file_path', 'unknown')
        line = thread.get('line', 'N/A')
        lines.append(f"{i}. {file_path}:{line}")
        lines.append(f"   Author: @{thread['author']}")
        lines.append(f"   Thread ID: {thread['thread_id']}")
        
        # Truncate long comments
        body = thread['body']
        if len(body) > MAX_COMMENT_DISPLAY_LENGTH:
            body = body[:MAX_COMMENT_DISPLAY_LENGTH] + "..."
        lines.append(f"   Comment: {body}")
        lines.append("")
    
    return "\n".join(lines)
