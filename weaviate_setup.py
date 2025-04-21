#!/usr/bin/env python3
"""
Weaviate Vector Database Setup

This script sets up a Weaviate vector database for storing and querying processed Jira data.
It creates the necessary schema, imports data, and provides functions for querying.
"""

import os
import json
import logging
import weaviate
from weaviate.auth import AuthApiKey
from weaviate.embedded import EmbeddedOptions
from typing import Dict, List, Any, Optional, Union
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("weaviate_setup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WeaviateSetup:
    """
    A class to set up and manage a Weaviate vector database for Jira data.
    """
    
    def __init__(self, 
                 input_dir: str = "processed_data",
                 weaviate_url: Optional[str] = None,
                 api_key: Optional[str] = None,
                 use_embedded: bool = True):
        """
        Initialize the WeaviateSetup.
        
        Args:
            input_dir: Directory containing the processed Jira data
            weaviate_url: URL of the Weaviate instance (if not using embedded)
            api_key: API key for Weaviate authentication (if not using embedded)
            use_embedded: Whether to use embedded Weaviate (for development/testing)
        """
        self.input_dir = input_dir
        self.use_embedded = use_embedded
        
        # Connect to Weaviate
        if use_embedded:
            logger.info("Using embedded Weaviate instance")
            self.client = weaviate.Client(
                embedded_options=EmbeddedOptions()
            )
        else:
            logger.info(f"Connecting to Weaviate at {weaviate_url}")
            auth_config = AuthApiKey(api_key=api_key) if api_key else None
            self.client = weaviate.Client(
                url=weaviate_url,
                auth_client_secret=auth_config
            )
        
        logger.info("Connected to Weaviate")
    
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
    
    def create_schema(self):
        """
        Create the Weaviate schema for Jira data.
        """
        logger.info("Creating Weaviate schema")
        
        # Check if schema already exists
        try:
            schema = self.client.schema.get()
            existing_classes = [c["class"] for c in schema["classes"]] if "classes" in schema else []
            
            if "JiraIssue" in existing_classes:
                logger.info("Schema already exists, skipping creation")
                return
        except Exception as e:
            logger.warning(f"Error checking schema: {e}")
        
        # Define the schema for Jira issues
        jira_issue_class = {
            "class": "JiraIssue",
            "description": "A Jira issue with all related data",
            "vectorizer": "text2vec-openai",  # Using OpenAI's text embeddings
            "moduleConfig": {
                "text2vec-openai": {
                    "model": "text-embedding-3-small",  # Using OpenAI's embedding model
                    "modelVersion": "latest",
                    "type": "text"
                }
            },
            "properties": [
                {
                    "name": "issue_key",
                    "dataType": ["string"],
                    "description": "The key of the Jira issue (e.g., PROJECT-123)"
                },
                {
                    "name": "summary",
                    "dataType": ["text"],
                    "description": "The summary of the Jira issue",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": False,
                            "vectorizePropertyName": False
                        }
                    }
                },
                {
                    "name": "description",
                    "dataType": ["text"],
                    "description": "The description of the Jira issue",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": False,
                            "vectorizePropertyName": False
                        }
                    }
                },
                {
                    "name": "issue_type",
                    "dataType": ["string"],
                    "description": "The type of the Jira issue (e.g., Bug, Story, Task)"
                },
                {
                    "name": "status",
                    "dataType": ["string"],
                    "description": "The status of the Jira issue (e.g., Open, In Progress, Done)"
                },
                {
                    "name": "priority",
                    "dataType": ["string"],
                    "description": "The priority of the Jira issue (e.g., High, Medium, Low)"
                },
                {
                    "name": "assignee",
                    "dataType": ["string"],
                    "description": "The assignee of the Jira issue"
                },
                {
                    "name": "reporter",
                    "dataType": ["string"],
                    "description": "The reporter of the Jira issue"
                },
                {
                    "name": "created_date",
                    "dataType": ["date"],
                    "description": "The creation date of the Jira issue"
                },
                {
                    "name": "updated_date",
                    "dataType": ["date"],
                    "description": "The last update date of the Jira issue"
                },
                {
                    "name": "labels",
                    "dataType": ["string"],
                    "description": "The labels of the Jira issue"
                },
                {
                    "name": "components",
                    "dataType": ["string"],
                    "description": "The components of the Jira issue"
                },
                {
                    "name": "epic_link",
                    "dataType": ["string"],
                    "description": "The key of the epic this issue belongs to"
                },
                {
                    "name": "epic_name",
                    "dataType": ["string"],
                    "description": "The name of the epic this issue belongs to"
                },
                {
                    "name": "epic_summary",
                    "dataType": ["text"],
                    "description": "The summary of the epic this issue belongs to",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": False,
                            "vectorizePropertyName": False
                        }
                    }
                },
                {
                    "name": "comments",
                    "dataType": ["text"],
                    "description": "The comments on the Jira issue",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": False,
                            "vectorizePropertyName": False
                        }
                    }
                },
                {
                    "name": "text_content",
                    "dataType": ["text"],
                    "description": "The full text content of the Jira issue for vectorization",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": False,
                            "vectorizePropertyName": False
                        }
                    }
                }
            ]
        }
        
        # Create the schema
        try:
            self.client.schema.create_class(jira_issue_class)
            logger.info("Created JiraIssue class in Weaviate schema")
        except Exception as e:
            logger.error(f"Error creating schema: {e}")
            raise
    
    def import_data(self, filename: str = "vector_ready_data.json"):
        """
        Import processed Jira data into Weaviate.
        
        Args:
            filename: Name of the vector-ready data JSON file
        """
        logger.info(f"Importing data from {filename}")
        
        # Load vector-ready data
        vector_ready_data = self._load_json_file(filename)
        
        if not vector_ready_data:
            logger.error(f"No data found in {filename}")
            return
        
        # Configure batch import
        with self.client.batch as batch:
            batch.batch_size = 100
            
            # Import each item
            for i, item in enumerate(vector_ready_data):
                # Convert dates to proper format if they exist
                for date_field in ["created_date", "updated_date"]:
                    if date_field in item and item[date_field]:
                        # Ensure date is in ISO format
                        if not item[date_field].endswith("Z"):
                            item[date_field] = f"{item[date_field]}T00:00:00Z"
                
                # Generate a UUID based on the issue key
                uuid = self.client.query.generate_uuid(item["issue_key"])
                
                # Add the item to the batch
                try:
                    batch.add_data_object(
                        data_object=item,
                        class_name="JiraIssue",
                        uuid=uuid
                    )
                    
                    if i % 10 == 0:
                        logger.info(f"Imported {i} items")
                
                except Exception as e:
                    logger.error(f"Error importing item {item['issue_key']}: {e}")
        
        logger.info(f"Imported {len(vector_ready_data)} items into Weaviate")
    
    def query_data(self, query_text: str, limit: int = 5) -> List[Dict]:
        """
        Query the Weaviate database using natural language.
        
        Args:
            query_text: Natural language query
            limit: Maximum number of results to return
            
        Returns:
            List of matching Jira issues
        """
        logger.info(f"Querying Weaviate with: {query_text}")
        
        try:
            result = (
                self.client.query
                .get("JiraIssue", [
                    "issue_key", 
                    "summary", 
                    "description", 
                    "issue_type",
                    "status",
                    "priority",
                    "assignee",
                    "reporter",
                    "created_date",
                    "updated_date",
                    "labels",
                    "components",
                    "epic_link",
                    "epic_name",
                    "epic_summary",
                    "comments"
                ])
                .with_near_text({"concepts": [query_text]})
                .with_limit(limit)
                .do()
            )
            
            if "data" in result and "Get" in result["data"] and "JiraIssue" in result["data"]["Get"]:
                return result["data"]["Get"]["JiraIssue"]
            else:
                logger.warning(f"No results found for query: {query_text}")
                return []
        
        except Exception as e:
            logger.error(f"Error querying Weaviate: {e}")
            return []
    
    def get_issues_by_priority(self, priority: str) -> List[Dict]:
        """
        Get Jira issues by priority.
        
        Args:
            priority: Priority to filter by (e.g., "High", "Medium", "Low")
            
        Returns:
            List of matching Jira issues
        """
        logger.info(f"Getting issues with priority: {priority}")
        
        try:
            result = (
                self.client.query
                .get("JiraIssue", [
                    "issue_key", 
                    "summary", 
                    "description", 
                    "issue_type",
                    "status",
                    "priority",
                    "assignee",
                    "reporter"
                ])
                .with_where({
                    "path": ["priority"],
                    "operator": "Equal",
                    "valueString": priority
                })
                .do()
            )
            
            if "data" in result and "Get" in result["data"] and "JiraIssue" in result["data"]["Get"]:
                return result["data"]["Get"]["JiraIssue"]
            else:
                logger.warning(f"No issues found with priority: {priority}")
                return []
        
        except Exception as e:
            logger.error(f"Error querying Weaviate: {e}")
            return []
    
    def get_issues_by_status(self, status: str) -> List[Dict]:
        """
        Get Jira issues by status.
        
        Args:
            status: Status to filter by (e.g., "Open", "In Progress", "Done")
            
        Returns:
            List of matching Jira issues
        """
        logger.info(f"Getting issues with status: {status}")
        
        try:
            result = (
                self.client.query
                .get("JiraIssue", [
                    "issue_key", 
                    "summary", 
                    "description", 
                    "issue_type",
                    "status",
                    "priority",
                    "assignee",
                    "reporter"
                ])
                .with_where({
                    "path": ["status"],
                    "operator": "Equal",
                    "valueString": status
                })
                .do()
            )
            
            if "data" in result and "Get" in result["data"] and "JiraIssue" in result["data"]["Get"]:
                return result["data"]["Get"]["JiraIssue"]
            else:
                logger.warning(f"No issues found with status: {status}")
                return []
        
        except Exception as e:
            logger.error(f"Error querying Weaviate: {e}")
            return []
    
    def get_issues_by_type(self, issue_type: str) -> List[Dict]:
        """
        Get Jira issues by type.
        
        Args:
            issue_type: Type to filter by (e.g., "Bug", "Story", "Task")
            
        Returns:
            List of matching Jira issues
        """
        logger.info(f"Getting issues with type: {issue_type}")
        
        try:
            result = (
                self.client.query
                .get("JiraIssue", [
                    "issue_key", 
                    "summary", 
                    "description", 
                    "issue_type",
                    "status",
                    "priority",
                    "assignee",
                    "reporter"
                ])
                .with_where({
                    "path": ["issue_type"],
                    "operator": "Equal",
                    "valueString": issue_type
    
(Content truncated due to size limit. Use line ranges to read in chunks)