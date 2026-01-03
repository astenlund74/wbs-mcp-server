"""GitHub Projects v2 API integration for work item synchronization."""

import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class GitHubProjectSync:
    """Sync work items with GitHub Projects using GraphQL API."""
    
    def __init__(self) -> None:
        """Initialize GitHub sync client."""
        self.token = self._get_token()
        self.org = os.environ.get("GITHUB_ORG", "techseed-codex")
        self.project_number = int(os.environ.get("GITHUB_PROJECT_NUMBER", "2"))
        self._project_id_cache: Optional[str] = None
        self._field_cache: Dict[str, Dict[str, str]] = {}
    
    def _get_token(self) -> str:
        """Get GitHub token from environment or gh CLI."""
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            return token
        
        # Fallback to gh CLI
        try:
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError(
                "No GitHub token found. Set GITHUB_TOKEN or run 'gh auth login'"
            ) from e
    
    def _gh_api(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute GraphQL query using gh CLI.
        
        Args:
            query: GraphQL query string
            variables: Query variables
            
        Returns:
            GraphQL response data
        """
        import json
        
        # Build gh command
        cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
        
        # Add variables
        if variables:
            for key, value in variables.items():
                cmd.extend(["-F", f"{key}={value}"])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            response: Dict[str, Any] = json.loads(result.stdout)
            return response
        except subprocess.CalledProcessError as e:
            logger.error(f"GraphQL query failed: {e.stderr}")
            raise RuntimeError(f"GitHub API error: {e.stderr}") from e
    
    def _get_project_id(self) -> str:
        """Get project global ID (cached)."""
        if self._project_id_cache:
            return self._project_id_cache
        
        query = """
        query($org: String!, $number: Int!) {
          organization(login: $org) {
            projectV2(number: $number) {
              id
            }
          }
        }
        """
        
        result = self._gh_api(query, {"org": self.org, "number": self.project_number})
        self._project_id_cache = result["data"]["organization"]["projectV2"]["id"]
        return self._project_id_cache
    
    def _get_field_config(self, field_name: str) -> Dict[str, str]:
        """Get field ID and options for a project field (cached).
        
        Args:
            field_name: Field name (e.g., "Status", "Priority")
            
        Returns:
            Dict with field_id and options (name -> id mapping)
        """
        if field_name in self._field_cache:
            return self._field_cache[field_name]
        
        query = """
        query($org: String!, $number: Int!) {
          organization(login: $org) {
            projectV2(number: $number) {
              fields(first: 20) {
                nodes {
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                    options {
                      id
                      name
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        result = self._gh_api(query, {"org": self.org, "number": self.project_number})
        fields = result["data"]["organization"]["projectV2"]["fields"]["nodes"]
        
        # Find matching field
        for field in fields:
            if field.get("name") == field_name:
                config = {
                    "field_id": field["id"],
                    "options": {opt["name"]: opt["id"] for opt in field["options"]}
                }
                self._field_cache[field_name] = config
                return config
        
        raise ValueError(f"Field '{field_name}' not found in project")
    
    def _get_project_item_id(self, issue_number: int) -> Optional[str]:
        """Get project item ID for an issue.
        
        Args:
            issue_number: GitHub issue number
            
        Returns:
            Project item ID or None if not in project
        """
        query = """
        query($org: String!, $number: Int!) {
          organization(login: $org) {
            projectV2(number: $number) {
              items(first: 100) {
                nodes {
                  id
                  content {
                    ... on Issue {
                      number
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        result = self._gh_api(query, {"org": self.org, "number": self.project_number})
        items = result["data"]["organization"]["projectV2"]["items"]["nodes"]
        
        for item in items:
            content = item.get("content", {})
            if isinstance(content, dict) and content.get("number") == issue_number:
                return str(item["id"])
        
        return None
    
    def update_item_field(
        self,
        issue_number: int,
        field_name: str,
        value: str
    ) -> bool:
        """Update a single-select field for a work item.
        
        Args:
            issue_number: GitHub issue number
            field_name: Field to update (e.g., "Status", "Priority")
            value: New value (e.g., "In Progress", "High")
            
        Returns:
            True if successful
        """
        # Get project item ID
        item_id = self._get_project_item_id(issue_number)
        if not item_id:
            logger.warning(f"Issue #{issue_number} not found in project")
            return False
        
        # Get field configuration
        field_config = self._get_field_config(field_name)
        field_id = field_config["field_id"]
        
        # Get option ID for value
        options = field_config["options"]
        assert isinstance(options, dict), "Options must be a dict"
        option_id = options.get(value)
        if not option_id:
            raise ValueError(
                f"Invalid {field_name} value '{value}'. "
                f"Valid options: {', '.join(options.keys())}"
            )
        
        # Update field via GraphQL mutation
        mutation = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
          updateProjectV2ItemFieldValue(
            input: {
              projectId: $projectId
              itemId: $itemId
              fieldId: $fieldId
              value: { singleSelectOptionId: $optionId }
            }
          ) {
            projectV2Item {
              id
            }
          }
        }
        """
        
        project_id = self._get_project_id()
        self._gh_api(mutation, {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": field_id,
            "optionId": option_id
        })
        
        logger.info(f"Updated issue #{issue_number} {field_name} to '{value}'")
        return True
    
    def sync_work_item(
        self,
        issue_number: int,
        updates: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Sync multiple fields for a work item to GitHub Project.
        
        Args:
            issue_number: GitHub issue number
            updates: Dictionary of field updates
            
        Returns:
            Dictionary mapping field names to success status
        """
        # Map YAML field names to GitHub field names
        field_mapping = {
            "status": "Status",
            "priority": "Priority",
            # Add more mappings as needed
        }
        
        results = {}
        for yaml_field, value in updates.items():
            github_field = field_mapping.get(yaml_field)
            if not github_field:
                logger.debug(f"Skipping field '{yaml_field}' (no GitHub mapping)")
                continue
            
            try:
                results[yaml_field] = self.update_item_field(
                    issue_number,
                    github_field,
                    value
                )
            except Exception as e:
                logger.error(f"Failed to update {yaml_field}: {e}")
                results[yaml_field] = False
        
        return results
