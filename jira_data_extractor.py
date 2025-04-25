#!/usr/bin/env python3
"""
Jira Data Extractor

This script extracts data from Jira including tickets, sprints, epics, and comments.
It uses the Jira REST API to fetch the data and saves it to JSON files.
"""

import os
import json
import time
import logging
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("jira_extractor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JiraDataExtractor:
    """
    A class to extract data from Jira using the REST API.
    """
    
    def __init__(self, 
                 jira_url: str, 
                 username: str, 
                 api_token: str, 
                 output_dir: str = "jira_data"):
        """
        Initialize the JiraDataExtractor with Jira credentials and settings.
        
        Args:
            jira_url: Base URL of the Jira instance (e.g., https://your-domain.atlassian.net)
            username: Jira username (usually email)
            api_token: Jira API token
            output_dir: Directory to save extracted data
        """
        self.jira_url = jira_url.rstrip('/')
        self.auth = HTTPBasicAuth(username, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Initialized JiraDataExtractor for {jira_url}")
    
    def _make_request(self, endpoint: str, method: str = "GET", 
                     params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Jira API.
        
        Args:
            endpoint: API endpoint to call
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            data: Request body for POST requests
            
        Returns:
            Response JSON as dictionary
        """
        url = f"{self.jira_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(
                    url,
                    auth=self.auth,
                    headers=self.headers,
                    params=params
                )
            elif method == "POST":
                response = requests.post(
                    url,
                    auth=self.auth,
                    headers=self.headers,
                    params=params,
                    json=data
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise
    
    def _save_to_json(self, data: Union[List, Dict], filename: str) -> str:
        """
        Save data to a JSON file.
        
        Args:
            data: Data to save
            filename: Name of the file
            
        Returns:
            Path to the saved file
        """
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved data to {filepath}")
        return filepath
    
    def extract_projects(self) -> List[Dict]:
        """
        Extract all projects from Jira.
        
        Returns:
            List of projects
        """
        logger.info("Extracting projects")
        
        projects = self._make_request("/rest/api/3/project")
        self._save_to_json(projects, "projects.json")
        
        return projects
    
    def extract_issues(self, 
                      project_key: Optional[str] = None, 
                      max_results: int = 100,
                      include_fields: Optional[List[str]] = None) -> List[Dict]:
        """
        Extract issues (tickets) from Jira.
        
        Args:
            project_key: Filter by project key
            max_results: Maximum number of results to return
            include_fields: Fields to include in the response
            
        Returns:
            List of issues
        """
        logger.info(f"Extracting issues for project: {project_key or 'all'}")
        
        if include_fields is None:
            include_fields = ["summary", "description", "status", "priority", 
                             "issuetype", "created", "updated", "assignee", 
                             "reporter", "labels", "components"]
        
        jql = f"project = {project_key}" if project_key else ""
        
        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": ",".join(include_fields)
        }
        
        issues_data = self._make_request("/rest/api/3/search", params=params)
        
        # Save all issues
        self._save_to_json(
            issues_data, 
            f"issues_{project_key or 'all'}.json"
        )
        
        return issues_data.get("issues", [])
    
    def extract_issue_details(self, issue_key: str) -> Dict:
        """
        Extract detailed information about a specific issue.
        
        Args:
            issue_key: Issue key (e.g., PROJECT-123)
            
        Returns:
            Issue details
        """
        logger.info(f"Extracting details for issue: {issue_key}")
        
        issue = self._make_request(f"/rest/api/3/issue/{issue_key}")
        self._save_to_json(issue, f"issue_{issue_key}.json")
        
        return issue
    
    def extract_comments(self, issue_key: str) -> List[Dict]:
        """
        Extract comments for a specific issue.
        
        Args:
            issue_key: Issue key (e.g., PROJECT-123)
            
        Returns:
            List of comments
        """
        logger.info(f"Extracting comments for issue: {issue_key}")
        
        comments_data = self._make_request(f"/rest/api/3/issue/{issue_key}/comment")
        self._save_to_json(
            comments_data, 
            f"comments_{issue_key}.json"
        )
        
        return comments_data.get("comments", [])
    
    def extract_sprints(self, board_id: int) -> List[Dict]:
        """
        Extract sprints for a specific board.
        
        Args:
            board_id: Board ID
            
        Returns:
            List of sprints
        """
        logger.info(f"Extracting sprints for board: {board_id}")
        
        sprints_data = self._make_request(f"/rest/agile/1.0/board/{board_id}/sprint")
        self._save_to_json(
            sprints_data, 
            f"sprints_board_{board_id}.json"
        )
        
        return sprints_data.get("values", [])
    
    def extract_epics(self, board_id: int) -> List[Dict]:
        """
        Extract epics for a specific board.
        
        Args:
            board_id: Board ID
            
        Returns:
            List of epics
        """
        logger.info(f"Extracting epics for board: {board_id}")
        
        epics_data = self._make_request(f"/rest/agile/1.0/board/{board_id}/epic")
        self._save_to_json(
            epics_data, 
            f"epics_board_{board_id}.json"
        )
        
        return epics_data.get("values", [])
    
    def extract_boards(self, project_key: Optional[str] = None) -> List[Dict]:
        """
        Extract boards from Jira.
        
        Args:
            project_key: Filter by project key
            
        Returns:
            List of boards
        """
        logger.info(f"Extracting boards for project: {project_key or 'all'}")
        
        params = {"projectKeyOrId": project_key} if project_key else {}
        
        boards_data = self._make_request("/rest/agile/1.0/board", params=params)
        self._save_to_json(
            boards_data, 
            f"boards_{project_key or 'all'}.json"
        )
        
        return boards_data.get("values", [])
    
    def extract_all_data(self, project_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract all data from Jira for a specific project.
        
        Args:
            project_key: Project key to extract data for
            
        Returns:
            Dictionary containing all extracted data
        """
        logger.info(f"Extracting all data for project: {project_key or 'all'}")
        
        # Create a timestamp for this extraction
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Extract projects
        projects = self.extract_projects()
        
        # Filter projects if project_key is provided
        if project_key:
            projects = [p for p in projects if p.get("key") == project_key]
        
        all_data = {
            "metadata": {
                "timestamp": timestamp,
                "project_key": project_key
            },
            "projects": projects,
            "boards": [],
            "sprints": [],
            "epics": [],
            "issues": [],
            "comments": []
        }
        
        # Extract boards for each project
        for project in projects:
            project_key = project.get("key")
            boards = self.extract_boards(project_key)
            all_data["boards"].extend(boards)
            
            # Extract sprints and epics for each board
            for board in boards:
                board_id = board.get("id")
                
                sprints = self.extract_sprints(board_id)
                all_data["sprints"].extend(sprints)
                
                epics = self.extract_epics(board_id)
                all_data["epics"].extend(epics)
            
            # Extract issues for the project
            issues = self.extract_issues(project_key)
            all_data["issues"].extend(issues)
            
            # Extract comments for each issue
            for issue in issues:
                issue_key = issue.get("key")
                comments = self.extract_comments(issue_key)
                
                # Add issue key to each comment for reference
                for comment in comments:
                    comment["issue_key"] = issue_key
                
                all_data["comments"].extend(comments)
            
            # Add a small delay to avoid rate limiting
            time.sleep(1)
        
        # Save the complete dataset
        self._save_to_json(
            all_data, 
            f"jira_complete_data_{project_key or 'all'}_{timestamp}.json"
        )
        
        return all_data


def main():
    """
    Main function to demonstrate the usage of JiraDataExtractor.
    """
    # These would be provided by the user or environment variables
    jira_url = "https://dubbamohan55.atlassian.net"
    username = "dubbamohan55@gmail.com"
    api_token = "TATT3xFfGF0AMktQCEKwMlAjbDVRjHv1qmhit7JJKy5PsRHgGEbxoPXF-gmfdFhAY6XvLjlSwTLLMgOVJvRE5tfCDyO9oPpb27mw54IP4dq7pBJIOzxMjhX20i-2JPYt4O6XtqVF9yBu-D0Lla1BPFwzKZO_IyD9LV5xh6q7yYWs-tK2BR3c-k=C4278333"
    
    # Create the extractor
    extractor = JiraDataExtractor(jira_url, username, api_token)
    
    # Extract all data for a specific project
    # Replace "PROJECT" with your project key, or set to None for all projects
    project_key = "SJA"
    
    try:
        all_data = extractor.extract_all_data(project_key)
        logger.info(f"Successfully extracted all data for {project_key or 'all projects'}")
        
        # Print some statistics
        print(f"Extracted {len(all_data['projects'])} projects")
        print(f"Extracted {len(all_data['boards'])} boards")
        print(f"Extracted {len(all_data['sprints'])} sprints")
        print(f"Extracted {len(all_data['epics'])} epics")
        print(f"Extracted {len(all_data['issues'])} issues")
        print(f"Extracted {len(all_data['comments'])} comments")
        
    except Exception as e:
        logger.error(f"Error extracting data: {e}")


if __name__ == "__main__":
    main()

