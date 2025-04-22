#!/usr/bin/env python3
"""
Run Jira to GPT-4o to Beautiful AI Pipeline

This script runs the full pipeline from the command line.
"""

import os
import json
import logging
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import modules from the app
from jira_data_extractor import JiraDataExtractor
from data_processor import JiraDataProcessor
from weaviate_setup import WeaviateSetup
from gpt4o_integration import GPT4oIntegration
from ppt_generator import PowerPointGenerator
from beautiful_ai_integration import BeautifulAIIntegration

def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {
            "jira": {
                "url": os.environ.get("JIRA_URL", ""),
                "username": os.environ.get("JIRA_USERNAME", ""),
                "api_token": os.environ.get("JIRA_API_TOKEN", ""),
                "project_key": os.environ.get("JIRA_PROJECT_KEY", "")
            },
            "openai": {
                "api_key": os.environ.get("OPENAI_API_KEY", ""),
                "model": os.environ.get("OPENAI_MODEL", "gpt-4o")
            },
            "beautiful_ai": {
                "api_key": os.environ.get("BEAUTIFUL_AI_API_KEY", "")
            },
            "weaviate": {
                "use_embedded": True,
                "url": os.environ.get("WEAVIATE_URL", ""),
                "api_key": os.environ.get("WEAVIATE_API_KEY", "")
            },
            "update_interval": 3600
        }

def run_pipeline(project_key, skip_steps=None):
    """Run the full pipeline"""
    if skip_steps is None:
        skip_steps = []
    
    config = load_config()
    
    logger.info(f"Starting pipeline for project: {project_key}")
    start_time = datetime.now()
    
    # Create necessary directories
    for directory in ['jira_data', 'processed_data', 'insights', 'presentations']:
        os.makedirs(directory, exist_ok=True)
    
    # 1. Extract data from Jira
    if 'extract' not in skip_steps:
        logger.info("Step 1: Extracting data from Jira")
        jira_extractor = JiraDataExtractor(
            jira_url=config['jira']['url'],
            username=config['jira']['username'],
            api_token=config['jira']['api_token'],
            output_dir="jira_data"
        )
        jira_extractor.extract_all_data(project_key)
    else:
        logger.info("Skipping step 1: Jira data extraction")
    
    # Get the latest data file
    jira_files = os.listdir('jira_data')
    jira_files = [f for f in jira_files if f.startswith(f'jira_complete_data_{project_key}')]
    jira_files.sort(reverse=True)  # Latest first
    
    if not jira_files:
        logger.error("No Jira data files found")
        return False
    
    latest_jira_file = jira_files[0]
    logger.info(f"Using latest Jira data file: {latest_jira_file}")
    
    # 2. Process the data
    if 'process' not in skip_steps:
        logger.info("Step 2: Processing data")
        data_processor = JiraDataProcessor(
            input_dir="jira_data",
            output_dir="processed_data"
        )
        data_processor.process_all_data(os.path.join('jira_data', latest_jira_file))
    else:
        logger.info("Skipping step 2: Data processing")
    
    # 3. Set up Weaviate
    if 'weaviate' not in skip_steps:
        logger.info("Step 3: Setting up Weaviate")
        weaviate_client = WeaviateSetup(
            input_dir="processed_data",
            weaviate_url=config['weaviate']['url'],
            api_key=config['weaviate']['api_key'],
            use_embedded=config['weaviate']['use_embedded']
        )
        weaviate_client.create_schema()
        weaviate_client.import_data("vector_ready_data.json")
    else:
        logger.info("Skipping step 3: Weaviate setup")
        weaviate_client = WeaviateSetup(
            input_dir="processed_data",
            weaviate_url=config['weaviate']['url'],
            api_key=config['weaviate']['api_key'],
            use_embedded=config['weaviate']['use_embedded']
        )
    
    # 4. Generate insights with GPT-4o
    if 'insights' not in skip_steps:
        logger.info("Step 4: Generating insights with GPT-4o")
        gpt4o_integration = GPT4oIntegration(
            api_key=config['openai']['api_key'],
            model=config['openai']['model'],
            weaviate_client=weaviate_client
        )
        gpt4o_integration.generate_all_insights(output_dir="insights", use_weaviate=True)
    else:
        logger.info("Skipping step 4: Insights generation")
    
    # 5. Generate PowerPoint presentations
    if 'ppt' not in skip_steps:
        logger.info("Step 5: Generating PowerPoint presentations")
        ppt_generator = PowerPointGenerator(
            insights_dir="insights",
            output_dir="presentations"
        )
        ppt_generator.generate_all_presentations()
    else:
        logger.info("Skipping step 5: PowerPoint generation")
    
    # 6. Update Beautiful AI presentations
    if 'beautiful_ai' not in skip_steps:
        logger.info("Step 6: Updating Beautiful AI presentations")
        beautiful_ai_integration = BeautifulAIIntegration(
            api_key=config['beautiful_ai']['api_key'],
            insights_dir="insights",
            presentations_dir="presentations"
        )
        beautiful_ai_integration.create_all_presentations()
    else:
        logger.info("Skipping step 6: Beautiful AI integration")
    
    # Save timestamp of last run
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('last_run_timestamp.txt', 'w') as f:
        f.write(timestamp)
    
    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"Pipeline completed in {duration}. Timestamp: {timestamp}")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Jira to GPT-4o to Beautiful AI pipeline')
    parser.add_argument('--project', type=str, help='Jira project key')
    parser.add_argument('--skip', type=str, nargs='+', choices=['extract', 'process', 'weaviate', 'insights', 'ppt', 'beautiful_ai'], 
                        help='Skip specific steps of the pipeline')
    
    args = parser.parse_args()
    
    # Load config to get default project key if not specified
    config = load_config()
    project_key = args.project or config['jira']['project_key']
    
    if not project_key:
        parser.error("Project key must be specified either with --project or in config.json")
    
    success = run_pipeline(project_key, args.skip)
    
    if success:
        logger.info("Pipeline execution completed successfully")
    else:
        logger.error("Pipeline execution failed")
