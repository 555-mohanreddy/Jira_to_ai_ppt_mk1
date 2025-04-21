#!/usr/bin/env python3
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.ci import Jenkins
from diagrams.onprem.database import MongoDB
from diagrams.onprem.queue import Kafka
from diagrams.programming.language import Python
from diagrams.custom import Custom
from diagrams.aws.storage import SimpleStorageServiceS3
from diagrams.azure.storage import BlobStorage
from diagrams.onprem.analytics import Spark
from diagrams.onprem.network import Nginx
from diagrams.saas.chat import Slack
from diagrams.programming.framework import FastAPI

# Create a diagram with custom styling
with Diagram("Jira to GPT-4o to Beautiful AI Integration", show=True, direction="LR", outformat="png"):
    
    # Data Sources
    with Cluster("Data Sources"):
        jira = Custom("Jira API", "./jira_icon.png")
    
    # Data Processing
    with Cluster("Data Processing"):
        python_extract = Python("Jira Data Extractor")
        python_clean = Python("Data Cleaner")
        azure_blob = BlobStorage("Azure Blob Storage")
    
    # Vector Database
    with Cluster("Vector Database"):
        weaviate = Custom("Weaviate", "./weaviate_icon.png")
    
    # AI Models
    with Cluster("AI Models"):
        gpt4o = Custom("GPT-4o / 4o mini", "./openai_icon.png")
    
    # Presentation Generation
    with Cluster("Presentation Generation"):
        ppt_gen = Python("PPT Generator")
        beautiful_ai = Custom("Beautiful AI", "./beautiful_ai_icon.png")
    
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
