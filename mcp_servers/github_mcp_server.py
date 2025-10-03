#!/usr/bin/env python3
"""
GitHub MCP Server
Provides GitHub repository management tools via MCP
"""

import asyncio
import json
import sys
import logging
import os
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path
import requests

logger = logging.getLogger(__name__)

class GitHubMCPServer:
    """GitHub MCP Server for repository operations"""

    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_owner = os.getenv("GITHUB_REPO_OWNER")
        self.repo_name = os.getenv("GITHUB_REPO_NAME")

        if not self.github_token:
            logger.warning("GITHUB_TOKEN not set - some operations may fail")
        if not self.repo_owner or not self.repo_name:
            logger.warning("GITHUB_REPO_OWNER or GITHUB_REPO_NAME not set")

    async def initialize_repository(self, repo_name: str, description: str = "", private: bool = False) -> Dict[str, Any]:
        """Initialize a new GitHub repository"""
        if not self.github_token:
            return {
                "success": False,
                "error": "GITHUB_TOKEN not configured"
            }

        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }

            data = {
                "name": repo_name,
                "description": description,
                "private": private,
                "auto_init": True
            }

            response = requests.post(
                "https://api.github.com/user/repos",
                headers=headers,
                json=data
            )

            if response.status_code == 201:
                repo_data = response.json()
                return {
                    "success": True,
                    "repository": {
                        "name": repo_data["name"],
                        "full_name": repo_data["full_name"],
                        "html_url": repo_data["html_url"],
                        "ssh_url": repo_data["ssh_url"],
                        "clone_url": repo_data["clone_url"]
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code} - {response.text}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create repository: {e}"
            }

    async def push_code_to_github(self, repo_url: str, commit_message: str = "Initial commit") -> Dict[str, Any]:
        """Push current code to GitHub repository"""
        try:
            # Initialize git if not already done
            if not Path(".git").exists():
                subprocess.run(["git", "init"], check=True, capture_output=True)
                subprocess.run(["git", "config", "user.name", "NeuroForge AI"], check=True)
                subprocess.run(["git", "config", "user.email", "ai@neuroforge.ai"], check=True)

            # Add remote if not exists
            result = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True)
            if repo_url not in result.stdout:
                subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)

            # Add all files
            subprocess.run(["git", "add", "."], check=True)

            # Commit
            subprocess.run(["git", "commit", "-m", commit_message], check=True)

            # Push
            subprocess.run(["git", "push", "-u", "origin", "main"], check=True)

            return {
                "success": True,
                "message": "Code successfully pushed to GitHub",
                "repo_url": repo_url,
                "commit_message": commit_message
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Git operation failed: {e.stderr.decode()}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to push code: {e}"
            }

    async def create_github_issue(self, title: str, body: str, labels: List[str] = None) -> Dict[str, Any]:
        """Create a GitHub issue"""
        if not all([self.github_token, self.repo_owner, self.repo_name]):
            return {
                "success": False,
                "error": "GitHub credentials not configured"
            }

        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }

            data = {
                "title": title,
                "body": body,
                "labels": labels or []
            }

            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues"
            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 201:
                issue_data = response.json()
                return {
                    "success": True,
                    "issue": {
                        "number": issue_data["number"],
                        "title": issue_data["title"],
                        "html_url": issue_data["html_url"],
                        "state": issue_data["state"]
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code} - {response.text}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create issue: {e}"
            }

    async def get_repository_info(self) -> Dict[str, Any]:
        """Get repository information"""
        if not all([self.github_token, self.repo_owner, self.repo_name]):
            return {
                "success": False,
                "error": "GitHub credentials not configured"
            }

        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }

            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                repo_data = response.json()
                return {
                    "success": True,
                    "repository": {
                        "name": repo_data["name"],
                        "full_name": repo_data["full_name"],
                        "description": repo_data["description"],
                        "html_url": repo_data["html_url"],
                        "language": repo_data["language"],
                        "stars": repo_data["stargazers_count"],
                        "forks": repo_data["forks_count"],
                        "open_issues": repo_data["open_issues_count"],
                        "private": repo_data["private"],
                        "created_at": repo_data["created_at"],
                        "updated_at": repo_data["updated_at"]
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code} - {response.text}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get repository info: {e}"
            }

    async def list_repository_issues(self, state: str = "open", labels: List[str] = None) -> Dict[str, Any]:
        """List repository issues"""
        if not all([self.github_token, self.repo_owner, self.repo_name]):
            return {
                "success": False,
                "error": "GitHub credentials not configured"
            }

        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }

            params = {"state": state, "per_page": 100}
            if labels:
                params["labels"] = ",".join(labels)

            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues"
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                issues_data = response.json()
                issues = []
                for issue in issues_data:
                    if "pull_request" not in issue:  # Skip pull requests
                        issues.append({
                            "number": issue["number"],
                            "title": issue["title"],
                            "state": issue["state"],
                            "html_url": issue["html_url"],
                            "labels": [label["name"] for label in issue["labels"]],
                            "created_at": issue["created_at"],
                            "updated_at": issue["updated_at"]
                        })

                return {
                    "success": True,
                    "issues": issues,
                    "count": len(issues)
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code} - {response.text}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list issues: {e}"
            }

    async def run_workflow_dispatch(self, workflow_id: str, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Trigger a GitHub Actions workflow"""
        if not all([self.github_token, self.repo_owner, self.repo_name]):
            return {
                "success": False,
                "error": "GitHub credentials not configured"
            }

        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }

            data = {
                "ref": "main",
                "inputs": inputs or {}
            }

            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/workflows/{workflow_id}/dispatches"
            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 204:
                return {
                    "success": True,
                    "message": f"Workflow '{workflow_id}' triggered successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code} - {response.text}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to trigger workflow: {e}"
            }

    async def get_workflow_runs(self, workflow_id: str = None, status: str = None) -> Dict[str, Any]:
        """Get workflow run information"""
        if not all([self.github_token, self.repo_owner, self.repo_name]):
            return {
                "success": False,
                "error": "GitHub credentials not configured"
            }

        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }

            params = {"per_page": 10}
            if status:
                params["status"] = status

            if workflow_id:
                url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/workflows/{workflow_id}/runs"
            else:
                url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/runs"

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                runs_data = response.json()
                runs = []
                for run in runs_data.get("workflow_runs", []):
                    runs.append({
                        "id": run["id"],
                        "name": run["name"],
                        "status": run["status"],
                        "conclusion": run.get("conclusion"),
                        "html_url": run["html_url"],
                        "created_at": run["created_at"],
                        "updated_at": run["updated_at"]
                    })

                return {
                    "success": True,
                    "runs": runs,
                    "count": len(runs)
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code} - {response.text}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get workflow runs: {e}"
            }

async def main():
    """Main MCP server loop"""
    server = GitHubMCPServer()

    while True:
        try:
            # Read MCP request
            request = json.loads(sys.stdin.readline())
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            # Route to appropriate method
            if method == "initialize_repository":
                repo_name = params.get("repo_name", "")
                description = params.get("description", "")
                private = params.get("private", False)
                result = await server.initialize_repository(repo_name, description, private)

            elif method == "push_code_to_github":
                repo_url = params.get("repo_url", "")
                commit_message = params.get("commit_message", "Initial commit")
                result = await server.push_code_to_github(repo_url, commit_message)

            elif method == "create_github_issue":
                title = params.get("title", "")
                body = params.get("body", "")
                labels = params.get("labels", [])
                result = await server.create_github_issue(title, body, labels)

            elif method == "get_repository_info":
                result = await server.get_repository_info()

            elif method == "list_repository_issues":
                state = params.get("state", "open")
                labels = params.get("labels", [])
                result = await server.list_repository_issues(state, labels)

            elif method == "run_workflow_dispatch":
                workflow_id = params.get("workflow_id", "")
                inputs = params.get("inputs", {})
                result = await server.run_workflow_dispatch(workflow_id, inputs)

            elif method == "get_workflow_runs":
                workflow_id = params.get("workflow_id")
                status = params.get("status")
                result = await server.get_workflow_runs(workflow_id, status)

            else:
                result = {
                    "success": False,
                    "error": f"Method not found: {method}"
                }

            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }

            print(json.dumps(response))
            sys.stdout.flush()

        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if "request" in locals() else None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
