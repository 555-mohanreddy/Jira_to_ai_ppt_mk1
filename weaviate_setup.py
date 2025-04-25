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
from weaviate.connect import ConnectionParams
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
                 weaviate_url: Optional[str] = "http://localhost:8080",
                 grpc_port: int = 50051,  # Default gRPC port
                 api_key: Optional[str] = None,
                 use_embedded: bool = False):
        """
        Initialize the WeaviateSetup.
        
        Args:
            input_dir: Directory containing the processed Jira data
            weaviate_url: URL of the Weaviate instance (default Docker URL)
            grpc_port: gRPC port for Weaviate
            api_key: API key for Weaviate authentication (if not using embedded)
            use_embedded: Whether to use embedded Weaviate (not recommended)
        """
        self.input_dir = input_dir
        self.use_embedded = use_embedded
        
        # Connect to Weaviate
        if use_embedded:
            logger.info("Using embedded Weaviate instance (not recommended)")
            embedded = EmbeddedOptions()
            self.client = weaviate.WeaviateClient(embedded_options=embedded)
            try:
                self.client.connect()
            except Exception as e:
                logger.error(f"Error connecting to embedded Weaviate: {e}")
                logger.info("Falling back to Docker Weaviate at http://localhost:8080")
                # Fall back to Docker
                connection_params = ConnectionParams.from_url(
                    url="http://localhost:8080",
                    grpc_port=50051
                )
                self.client = weaviate.WeaviateClient(connection_params=connection_params)
                self.client.connect()
        else:
            logger.info(f"Connecting to Weaviate at {weaviate_url}")
            # Create connection parameters
            if api_key:
                auth_config = AuthApiKey(api_key=api_key)
                connection_params = ConnectionParams.from_url(
                    url=weaviate_url,
                    grpc_port=grpc_port,
                    auth_client_secret=auth_config
                )
            else:
                connection_params = ConnectionParams.from_url(
                    url=weaviate_url,
                    grpc_port=grpc_port
                )
            self.client = weaviate.WeaviateClient(connection_params=connection_params)
            self.client.connect()
        
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
        
        # Make sure client is connected
        self.client.connect()
        
        # Check if collection already exists
        try:
            collections = self.client.collections.list_all()
            if "JiraIssue" in collections:
                logger.info("Schema already exists, skipping creation")
                return
        except Exception as e:
            logger.warning(f"Error checking schema: {e}")
        
        # Define the collection for Jira issues
        try:
            # Create property configurations
            properties = [
                {
                    "name": "issue_key",
                    "dataType": ["text"],
                    "description": "The key of the Jira issue (e.g., PROJECT-123)"
                },
                {
                    "name": "summary",
                    "dataType": ["text"],
                    "description": "The summary of the Jira issue"
                },
                {
                    "name": "description",
                    "dataType": ["text"],
                    "description": "The description of the Jira issue"
                },
                {
                    "name": "issue_type",
                    "dataType": ["text"],
                    "description": "The type of the Jira issue (e.g., Bug, Story, Task)"
                },
                {
                    "name": "status",
                    "dataType": ["text"],
                    "description": "The status of the Jira issue (e.g., Open, In Progress, Done)"
                },
                {
                    "name": "priority",
                    "dataType": ["text"],
                    "description": "The priority of the Jira issue (e.g., High, Medium, Low)"
                },
                {
                    "name": "assignee",
                    "dataType": ["text"],
                    "description": "The assignee of the Jira issue"
                },
                {
                    "name": "reporter",
                    "dataType": ["text"],
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
                    "dataType": ["text"],
                    "description": "The labels of the Jira issue"
                },
                {
                    "name": "components",
                    "dataType": ["text"],
                    "description": "The components of the Jira issue"
                },
                {
                    "name": "epic_link",
                    "dataType": ["text"],
                    "description": "The key of the epic this issue belongs to"
                },
                {
                    "name": "epic_name",
                    "dataType": ["text"],
                    "description": "The name of the epic this issue belongs to"
                },
                {
                    "name": "epic_summary",
                    "dataType": ["text"],
                    "description": "The summary of the epic this issue belongs to"
                },
                {
                    "name": "comments",
                    "dataType": ["text"],
                    "description": "The comments on the Jira issue"
                },
                {
                    "name": "text_content",
                    "dataType": ["text"],
                    "description": "The full text content of the Jira issue for vectorization"
                }
            ]
            
            # Create a new collection with properties
            jira_collection = self.client.collections.create(
                name="JiraIssue",
                description="A Jira issue with all related data",
                properties=properties,  # Pass properties directly
                vectorizer_config=weaviate.classes.config.Configure.Vectorizer.text2vec_openai(
                    model="text-embedding-3-small",
                    model_version="latest",
                    type_="text"
                )
            )
            
            logger.info("Created JiraIssue collection in Weaviate schema")
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
        
        # Get the JiraIssue collection
        jira_collection = self.client.collections.get("JiraIssue")
        
        # Configure batch import
        with jira_collection.batch.dynamic() as batch:
            # Import each item
            for i, item in enumerate(vector_ready_data):
                # Convert dates to proper format if they exist
                for date_field in ["created_date", "updated_date"]:
                    if date_field in item and item[date_field]:
                        # Ensure date is in ISO format
                        if not item[date_field].endswith("Z"):
                            item[date_field] = f"{item[date_field]}T00:00:00Z"
                
                # Add the item to the batch
                try:
                    batch.add_object(
                        properties=item,
                        uuid=item.get("issue_key")  # Use issue_key as UUID for consistency
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
            # Get the JiraIssue collection
            jira_collection = self.client.collections.get("JiraIssue")
            
            # Query the collection
            result = jira_collection.query.near_text(
                query=query_text,
                limit=limit
            ).with_additional(["id"]).objects
            
            # Format the result
            formatted_result = []
            for item in result:
                formatted_item = item.properties
                formatted_item["id"] = item.uuid
                formatted_result.append(formatted_item)
            
            return formatted_result
        
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
            # Get the JiraIssue collection
            jira_collection = self.client.collections.get("JiraIssue")
            
            # Query the collection
            filter_by = {
                "path": ["priority"],
                "operator": "Equal",
                "valueText": priority
            }
            
            result = jira_collection.query.fetch_objects(
                filters=filter_by,
                limit=100
            ).with_additional(["id"]).objects
            
            # Format the result
            formatted_result = []
            for item in result:
                formatted_item = item.properties
                formatted_item["id"] = item.uuid
                formatted_result.append(formatted_item)
            
            return formatted_result
        
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
            # Get the JiraIssue collection
            jira_collection = self.client.collections.get("JiraIssue")
            
            # Query the collection
            filter_by = {
                "path": ["status"],
                "operator": "Equal",
                "valueText": status
            }
            
            result = jira_collection.query.fetch_objects(
                filters=filter_by,
                limit=100
            ).with_additional(["id"]).objects
            
            # Format the result
            formatted_result = []
            for item in result:
                formatted_item = item.properties
                formatted_item["id"] = item.uuid
                formatted_result.append(formatted_item)
            
            return formatted_result
        
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
            # Get the JiraIssue collection
            jira_collection = self.client.collections.get("JiraIssue")
            
            # Query the collection
            filter_by = {
                "path": ["issue_type"],
                "operator": "Equal",
                "valueText": issue_type
            }
            
            result = jira_collection.query.fetch_objects(
                filters=filter_by,
                limit=100
            ).with_additional(["id"]).objects
            
            # Format the result
            formatted_result = []
            for item in result:
                formatted_item = item.properties
                formatted_item["id"] = item.uuid
                formatted_result.append(formatted_item)
            
            return formatted_result
        
        except Exception as e:
            logger.error(f"Error querying Weaviate: {e}")
            return []
    
    def get_all_issues(self, limit: int = 1000) -> List[Dict]:
        """
        Retrieve all Jira issues from Weaviate.
        
        Args:
            limit: Maximum number of issues to retrieve
            
        Returns:
            List of issue dictionaries
        """
        logger.info(f"Retrieving up to {limit} issues from Weaviate")

        try:
            jira_collection = self.client.collections.get("JiraIssue")
            result = jira_collection.query.fetch_objects(limit=limit).objects

            formatted_result = []
            for item in result:
                formatted_item = item.properties
                formatted_item["id"] = item.uuid
                formatted_result.append(formatted_item)

            return formatted_result

        except Exception as e:
            logger.error(f"Error retrieving issues from Weaviate: {e}")
            return []

