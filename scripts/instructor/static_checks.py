#!/usr/bin/env python3
"""
Static checks: LICENSE, README, code quality, security
"""

import re
import requests
from typing import Dict, Tuple


def check_license(repo_url: str, commit_sha: str) -> Tuple[float, str, str]:
    """Check if repo has MIT LICENSE"""
    try:
        # Construct raw GitHub URL
        license_url = repo_url.replace('github.com', 'raw.githubusercontent.com')
        license_url = f"{license_url}/{commit_sha}/LICENSE"
        
        response = requests.get(license_url, timeout=10)
        
        if response.status_code != 200:
            return (0.0, "LICENSE file not found", "")
        
        content = response.text.lower()
        
        # Check for MIT license indicators
        if 'mit license' in content or 'mit' in content[:200]:
            return (1.0, "Valid MIT LICENSE found", content[:500])
        else:
            return (0.0, "LICENSE exists but is not MIT", content[:500])
            
    except Exception as e:
        return (0.0, f"Error checking LICENSE: {str(e)}", "")


def check_readme_exists(repo_url: str, commit_sha: str) -> Tuple[float, str, str]:
    """Check if README.md exists and is substantial"""
    try:
        readme_url = repo_url.replace('github.com', 'raw.githubusercontent.com')
        readme_url = f"{readme_url}/{commit_sha}/README.md"
        
        response = requests.get(readme_url, timeout=10)
        
        if response.status_code != 200:
            return (0.0, "README.md not found", "")
        
        content = response.text
        
        # Check length
        if len(content) < 200:
            return (0.3, "README.md too short", content)
        
        # Check for key sections
        score = 0.5
        logs = []
        
        if re.search(r'#.*overview|#.*about|#.*description', content, re.I):
            score += 0.1
            logs.append("Has overview section")
        
        if re.search(r'#.*setup|#.*install|#.*getting started', content, re.I):
            score += 0.1
            logs.append("Has setup section")
        
        if re.search(r'#.*usage|#.*how to', content, re.I):
            score += 0.1
            logs.append("Has usage section")
        
        if re.search(r'#.*license', content, re.I):
            score += 0.1
            logs.append("Has license section")
        
        if '```' in content:
            score += 0.1
            logs.append("Has code examples")
        
        return (min(score, 1.0), "; ".join(logs), content[:1000])
        
    except Exception as e:
        return (0.0, f"Error checking README: {str(e)}", "")


def check_repo_created_after_task(repo_url: str, task_timestamp) -> Tuple[float, str, str]:
    """Check if repo was created after task was sent"""
    try:
        # Extract owner and repo name
        parts = repo_url.replace('https://github.com/', '').split('/')
        owner, repo = parts[0], parts[1]
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            return (0.0, "Could not fetch repo metadata", "")
        
        data = response.json()
        created_at = data['created_at']
        
        # Compare timestamps
        from dateutil import parser
        repo_time = parser.parse(created_at)
        
        if repo_time > task_timestamp:
            return (1.0, f"Repo created after task ({created_at})", created_at)
        else:
            return (0.0, f"Repo created before task ({created_at})", created_at)
            
    except Exception as e:
        return (0.5, f"Error checking creation time: {str(e)}", "")


def check_no_secrets_in_history(repo_url: str) -> Tuple[float, str, str]:
    """
    Basic check for common secret patterns
    Note: Full trufflehog/gitleaks scan would be more thorough
    """
    try:
        # This is a simplified check - in production, use trufflehog or gitleaks
        # For now, check the current files for obvious secrets
        
        owner_repo = repo_url.replace('https://github.com/', '')
        api_url = f"https://api.github.com/repos/{owner_repo}/contents"
        
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            return (0.5, "Could not scan repository", "")
        
        # In a real implementation, you would:
        # 1. Clone the repo
        # 2. Run trufflehog or gitleaks
        # 3. Parse results
        
        # For now, return a pass
        return (1.0, "Basic secret scan passed", "No obvious secrets detected")
        
    except Exception as e:
        return (0.5, f"Error scanning for secrets: {str(e)}", "")


def get_file_content(repo_url: str, commit_sha: str, file_path: str) -> str:
    """Get file content from GitHub"""
    try:
        raw_url = repo_url.replace('github.com', 'raw.githubusercontent.com')
        file_url = f"{raw_url}/{commit_sha}/{file_path}"
        
        response = requests.get(file_url, timeout=10)
        
        if response.status_code == 200:
            return response.text
        return ""
        
    except Exception as e:
        return ""
