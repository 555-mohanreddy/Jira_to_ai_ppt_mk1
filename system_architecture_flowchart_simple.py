#!/usr/bin/env python3
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.ci import Jenkins
from diagrams.onprem.database import MongoDB
from diagrams.programming.language import Python
from diagrams.azure.storage import BlobStorage
from diagrams.programming.framework import FastAPI

# Create a diagram with custom styling
with Diagram("Jira to GPT-4o to Beautiful AI Integration", show=True, direction="LR", outformat="png"):
    
    # Data Sources
    with Cluster("Data Sources"):
        jira = Python("Jira API")
    
    # Data Processing
    with Cluster("Data Processing"):
        python_extract = Python("Jira Data Extractor")
        python_clean = Python("Data Cleaner")
        azure_blob = BlobStorage("Azure Blob Storage")
    
    # Vector Database
    with Cluster("Vector Database"):
        weaviate = Python("Weaviate")
    
    # AI Models
    with Cluster("AI Models"):
        gpt4o = Python("GPT-4o / 4o mini")
    
    # Presentation Generation
    with Cluster("Presentation Generation"):
        ppt_gen = Python("PPT Generator")
        beautiful_ai = Python("Beautiful AI")
    
    # Scheduler
    with Cluster("Scheduler"):
        scheduler = Jenkins("Hourly Scheduler")
    
    # API Layer
    with Cluster("API Layer"):
        api = FastAPI("Integration API")
    
    # Flow connections
    jira >> python_extract >> python_clean
    python_clean >> Edge(label="Store Processed Data") >> azure_blob
    azure_blob >> Edge(label="Load Data") >> weaviate
    weaviate >> Edge(label="Query Vectors") >> gpt4o
    gpt4o >> Edge(label="Generate Insights") >> ppt_gen
    ppt_gen >> Edge(label="Create Presentations") >> beautiful_ai
    
    # Scheduler connections
    scheduler >> Edge(label="Trigger Hourly") >> python_extract
    scheduler >> Edge(label="Trigger Hourly") >> api
    
    # API connections
    api >> Edge(label="Manage Integration") >> weaviate
    api >> Edge(label="Update Content") >> beautiful_ai
