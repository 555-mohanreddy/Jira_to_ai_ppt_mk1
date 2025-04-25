#!/usr/bin/env python3
"""
Data Processor for Jira Data

This script processes and cleans the data extracted from Jira to prepare it for
integration with Weaviate and GPT-4o.
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import re
import html
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JiraDataProcessor:
    """
    A class to process and clean data extracted from Jira.
    """
    
    def __init__(self, 
                 input_dir: str = "jira_data", 
                 output_dir: str = "processed_data"):
        """
        Initialize the JiraDataProcessor.
        
        Args:
            input_dir: Directory containing the extracted Jira data
            output_dir: Directory to save processed data
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Initialized JiraDataProcessor")
        logger.info(f"Input directory: {input_dir}")
        logger.info(f"Output directory: {output_dir}")
    
    def _load_json_file(self, filename: str) -> Dict:
        """
        Load data from a JSON file.
        
        Args:
            filename: Name of the file to load
            
        Returns:
            Loaded data as dictionary
        """
        filepath = os.path.join(self.input_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Loaded data from {filepath}")
            return data
        
        except Exception as e:
            logger.error(f"Error loading data from {filepath}: {e}")
            return {}
    
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
    
    def _save_to_csv(self, df: pd.DataFrame, filename: str) -> str:
        """
        Save data to a CSV file.
        
        Args:
            df: DataFrame to save
            filename: Name of the file
            
        Returns:
            Path to the saved file
        """
        filepath = os.path.join(self.output_dir, filename)
        
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        logger.info(f"Saved data to {filepath}")
        return filepath
    
    def _clean_html_content(self, html_content: Optional[str]) -> str:
        """
        Clean HTML content by removing tags and converting entities.
        
        Args:
            html_content: HTML content to clean
            
        Returns:
            Cleaned text
        """
        if not html_content:
            return ""
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get text content
        text = soup.get_text(separator=' ', strip=True)
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _parse_jira_date(self, date_str: Optional[str]) -> Optional[str]:
        """
        Parse Jira date string to a standardized format.
        
        Args:
            date_str: Date string from Jira
            
        Returns:
            Standardized date string (YYYY-MM-DD)
        """
        if not date_str:
            return None
        
        try:
            # Jira uses ISO 8601 format with timezone
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d')
        
        except Exception as e:
            logger.warning(f"Error parsing date {date_str}: {e}")
            return None
    
    def _extract_nested_value(self, data: Dict, path: List[str]) -> Any:
        """
        Extract a value from a nested dictionary using a path.
        
        Args:
            data: Dictionary to extract from
            path: List of keys to navigate the dictionary
            
        Returns:
            Extracted value or None if not found
        """
        result = data
        
        for key in path:
            if isinstance(result, dict) and key in result:
                result = result[key]
            else:
                return None
        
        return result
    
    def process_issues(self, filename: str) -> pd.DataFrame:
        """
        Process issues data.
        
        Args:
            filename: Name of the issues JSON file
            
        Returns:
            DataFrame containing processed issues
        """
        logger.info(f"Processing issues from {filename}")
        
        # Load issues data
        issues_data = self._load_json_file(filename)
        
        if not issues_data or "issues" not in issues_data:
            logger.warning(f"No issues found in {filename}")
            return pd.DataFrame()
        
        issues = issues_data["issues"]
        
        # Extract relevant fields
        processed_issues = []
        
        for issue in issues:
            fields = issue.get("fields", {})
            
            processed_issue = {
                "id": issue.get("id"),
                "key": issue.get("key"),
                "summary": fields.get("summary", ""),
                "description": self._clean_html_content(fields.get("description")),
                "status": self._extract_nested_value(fields, ["status", "name"]),
                "priority": self._extract_nested_value(fields, ["priority", "name"]),
                "issue_type": self._extract_nested_value(fields, ["issuetype", "name"]),
                "created_date": self._parse_jira_date(fields.get("created")),
                "updated_date": self._parse_jira_date(fields.get("updated")),
                "assignee": self._extract_nested_value(fields, ["assignee", "displayName"]),
                "reporter": self._extract_nested_value(fields, ["reporter", "displayName"]),
                "labels": ", ".join(fields.get("labels", [])),
                "components": ", ".join([c.get("name", "") for c in fields.get("components", [])]),
                "epic_link": fields.get("epic", {}).get("key") if "epic" in fields else None,
                "sprint": None,  # Will be populated later if sprint data is available
                "story_points": fields.get("customfield_10002")  # Assuming story points are stored in this field
            }
            
            processed_issues.append(processed_issue)
        
        # Convert to DataFrame
        df_issues = pd.DataFrame(processed_issues)
        
        # Save processed issues
        self._save_to_csv(df_issues, "processed_issues.csv")
        self._save_to_json(processed_issues, "processed_issues.json")
        
        return df_issues
    
    def process_comments(self, filename: str) -> pd.DataFrame:
        """
        Process comments data.
        
        Args:
            filename: Name of the comments JSON file
            
        Returns:
            DataFrame containing processed comments
        """
        logger.info(f"Processing comments from {filename}")
        
        # Load comments data
        comments_data = self._load_json_file(filename)
        
        if not comments_data or "comments" not in comments_data:
            logger.warning(f"No comments found in {filename}")
            return pd.DataFrame()
        
        comments = comments_data["comments"]
        
        # Extract relevant fields
        processed_comments = []
        
        for comment in comments:
            processed_comment = {
                "id": comment.get("id"),
                "issue_key": comment.get("issue_key"),
                "author": self._extract_nested_value(comment, ["author", "displayName"]),
                "created_date": self._parse_jira_date(comment.get("created")),
                "updated_date": self._parse_jira_date(comment.get("updated")),
                "content": self._clean_html_content(self._extract_nested_value(comment, ["body", "content"]))
            }
            
            processed_comments.append(processed_comment)
        
        # Convert to DataFrame
        df_comments = pd.DataFrame(processed_comments)
        
        # Save processed comments
        self._save_to_csv(df_comments, "processed_comments.csv")
        self._save_to_json(processed_comments, "processed_comments.json")
        
        return df_comments
    
    def process_sprints(self, filename: str) -> pd.DataFrame:
        """
        Process sprints data.
        
        Args:
            filename: Name of the sprints JSON file
            
        Returns:
            DataFrame containing processed sprints
        """
        logger.info(f"Processing sprints from {filename}")
        
        # Load sprints data
        sprints_data = self._load_json_file(filename)
        
        if not sprints_data or "values" not in sprints_data:
            logger.warning(f"No sprints found in {filename}")
            return pd.DataFrame()
        
        sprints = sprints_data["values"]
        
        # Extract relevant fields
        processed_sprints = []
        
        for sprint in sprints:
            processed_sprint = {
                "id": sprint.get("id"),
                "name": sprint.get("name"),
                "state": sprint.get("state"),
                "start_date": self._parse_jira_date(sprint.get("startDate")),
                "end_date": self._parse_jira_date(sprint.get("endDate")),
                "board_id": sprint.get("originBoardId"),
                "goal": sprint.get("goal")
            }
            
            processed_sprints.append(processed_sprint)
        
        # Convert to DataFrame
        df_sprints = pd.DataFrame(processed_sprints)
        
        # Save processed sprints
        self._save_to_csv(df_sprints, "processed_sprints.csv")
        self._save_to_json(processed_sprints, "processed_sprints.json")
        
        return df_sprints
    
    def process_epics(self, filename: str) -> pd.DataFrame:
        """
        Process epics data.
        
        Args:
            filename: Name of the epics JSON file
            
        Returns:
            DataFrame containing processed epics
        """
        logger.info(f"Processing epics from {filename}")
        
        # Load epics data
        epics_data = self._load_json_file(filename)
        
        if not epics_data or "values" not in epics_data:
            logger.warning(f"No epics found in {filename}")
            return pd.DataFrame()
        
        epics = epics_data["values"]
        
        # Extract relevant fields
        processed_epics = []
        
        for epic in epics:
            fields = epic.get("fields", {})
            
            processed_epic = {
                "id": epic.get("id"),
                "key": epic.get("key"),
                "name": fields.get("name", ""),
                "summary": fields.get("summary", ""),
                "description": self._clean_html_content(fields.get("description")),
                "status": self._extract_nested_value(fields, ["status", "name"]),
                "created_date": self._parse_jira_date(fields.get("created")),
                "updated_date": self._parse_jira_date(fields.get("updated"))
            }
            
            processed_epics.append(processed_epic)
        
        # Convert to DataFrame
        df_epics = pd.DataFrame(processed_epics)
        
        # Save processed epics
        self._save_to_csv(df_epics, "processed_epics.csv")
        self._save_to_json(processed_epics, "processed_epics.json")
        
        return df_epics
    
    def merge_data(self, 
                  df_issues: pd.DataFrame, 
                  df_comments: pd.DataFrame, 
                  df_sprints: pd.DataFrame, 
                  df_epics: pd.DataFrame) -> pd.DataFrame:
        """
        Merge all processed data into a single DataFrame for analysis.
        
        Args:
            df_issues: Processed issues DataFrame
            df_comments: Processed comments DataFrame
            df_sprints: Processed sprints DataFrame
            df_epics: Processed epics DataFrame
            
        Returns:
            Merged DataFrame
        """
        logger.info("Merging all processed data")
        
        # Group comments by issue
        if not df_comments.empty:
            comments_by_issue = df_comments.groupby("issue_key")["content"].apply(lambda x: " | ".join(x)).reset_index()
            comments_by_issue.rename(columns={"content": "comments"}, inplace=True)
            
            # Merge issues with comments
            merged_data = pd.merge(df_issues, comments_by_issue, left_on="key", right_on="issue_key", how="left")
            merged_data.drop("issue_key", axis=1, inplace=True, errors="ignore")
        else:
            merged_data = df_issues.copy()
            merged_data["comments"] = ""
        
        # Merge with epics if available
        if not df_epics.empty and "epic_link" in merged_data.columns:
            merged_data = pd.merge(
                merged_data, 
                df_epics[["key", "name", "summary", "description"]], 
                left_on="epic_link", 
                right_on="key", 
                how="left",
                suffixes=("", "_epic")
            )
        
        # Clean up the merged data
        merged_data.fillna("", inplace=True)
        
        # Save merged data
        self._save_to_csv(merged_data, "merged_jira_data.csv")
        
        # Convert to dictionary for JSON
        merged_data_dict = merged_data.to_dict(orient="records")
        self._save_to_json(merged_data_dict, "merged_jira_data.json")
        
        return merged_data
    
    def create_vector_ready_data(self, merged_data: pd.DataFrame) -> List[Dict]:
        """
        Create data ready for vectorization and storage in Weaviate.
        
        Args:
            merged_data: Merged DataFrame containing all Jira data
            
        Returns:
            List of dictionaries ready for vectorization
        """
        logger.info("Creating vector-ready data")
        
        vector_ready_data = []
        
        for _, row in merged_data.iterrows():
            # Create a comprehensive text representation for vectorization
            text_content = f"""
            Issue: {row['key']}
            Summary: {row['summary']}
            Description: {row['description']}
            Type: {row['issue_type']}
            Status: {row['status']}
            Priority: {row['priority']}
            Assignee: {row['assignee']}
            Reporter: {row['reporter']}
            Created: {row['created_date']}
            Updated: {row['updated_date']}
            Labels: {row['labels']}
            Components: {row['components']}
            Epic: {row.get('name_epic', '')}
            Epic Summary: {row.get('summary_epic', '')}
            Comments: {row['comments']}
            """
            
            # Clean up the text content
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            vector_ready_data.append({
                "id": row['id'],
                "text": text_content,
                "metadata": {
                    "key": row['key'],
                    "summary": row['summary'],
                    "description": row['description'],
                    "type": row['issue_type'],
                    "status": row['status'],
                    "priority": row['priority'],
                    "assignee": row['assignee'],
                    "reporter": row['reporter'],
                    "created": row['created_date'],
                    "updated": row['updated_date'],
                    "labels": row['labels'],
                    "components": row['components'],
                    "epic": row.get('name_epic', ''),
                    "epic_summary": row.get('summary_epic', '')
                }
            })
        
        return vector_ready_data