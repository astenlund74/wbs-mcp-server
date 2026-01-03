"""PR review thread tools - write operations."""

import json
import logging
import subprocess
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def reply_to_review_thread(thread_id: str, body: str) -> Dict[str, Any]:
    """
    Reply to a review thread.
    
    Args:
        thread_id: GitHub review thread ID (e.g., "PRRT_...")
        body: Reply text
        
    Returns:
        Success status and comment ID
    """
    try:
        mutation = '''
        mutation($thread: ID!, $body: String!) {
            addPullRequestReviewThreadReply(input: {
                pullRequestReviewThreadId: $thread,
                body: $body
            }) {
                comment { id }
            }
        }
        '''
        
        result = subprocess.run(
            [
                "gh", "api", "graphql",
                "-f", f"query={mutation}",
                "-f", f"thread={thread_id}",
                "-f", f"body={body}"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"GraphQL mutation failed: {result.stderr}"
            }
        
        data = json.loads(result.stdout)
        comment_id = data["data"]["addPullRequestReviewThreadReply"]["comment"]["id"]
        
        return {
            "success": True,
            "thread_id": thread_id,
            "comment_id": comment_id
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Request timed out after 30s"}
    except Exception as e:
        logger.error(f"Failed to reply to thread: {e}")
        return {"success": False, "error": str(e)}


def resolve_review_thread(thread_id: str) -> Dict[str, Any]:
    """
    Mark a review thread as resolved.
    
    Args:
        thread_id: GitHub review thread ID
        
    Returns:
        Success status
    """
    try:
        mutation = '''
        mutation($id: ID!) {
            resolveReviewThread(input: {threadId: $id}) {
                thread { isResolved }
            }
        }
        '''
        
        result = subprocess.run(
            [
                "gh", "api", "graphql",
                "-f", f"query={mutation}",
                "-f", f"id={thread_id}"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"GraphQL mutation failed: {result.stderr}"
            }
        
        data = json.loads(result.stdout)
        is_resolved = data["data"]["resolveReviewThread"]["thread"]["isResolved"]
        
        return {
            "success": True,
            "thread_id": thread_id,
            "is_resolved": is_resolved
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Request timed out after 30s"}
    except Exception as e:
        logger.error(f"Failed to resolve thread: {e}")
        return {"success": False, "error": str(e)}


def format_reply_result(result: Dict[str, Any]) -> str:
    """Format reply result as text."""
    if not result["success"]:
        return f"❌ Failed to reply: {result['error']}"
    
    return f"✅ Replied to thread {result['thread_id'][:12]}..."


def format_resolve_result(result: Dict[str, Any]) -> str:
    """Format resolve result as text."""
    if not result["success"]:
        return f"❌ Failed to resolve: {result['error']}"
    
    return f"✅ Resolved thread {result['thread_id'][:12]}..."
