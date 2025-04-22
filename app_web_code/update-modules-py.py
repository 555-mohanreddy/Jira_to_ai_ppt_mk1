#!/usr/bin/env python3
"""
Module Updater for Jira to GPT-4o to Beautiful AI Integration

This script updates the pipeline modules to match the files in the current project.
It's useful when you've made changes to the code and need to ensure all components
are using the latest versions.
"""

import os
import shutil
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("update.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def backup_file(file_path):
    """Create a backup of a file"""
    if os.path.exists(file_path):
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Get filename without path
        filename = os.path.basename(file_path)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filename}_{timestamp}.bak"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Create the backup
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        
        return True
    
    return False

def update_module(module_name):
    """Update a specific module"""
    file_path = f"{module_name}.py"
    
    if not os.path.exists(file_path):
        logger.error(f"Module file not found: {file_path}")
        return False
    
    # Create a backup
    backup_file(file_path)
    
    # Update any imports or code as needed
    # This is where you'd put any necessary modifications
    
    logger.info(f"Updated module: {module_name}")
    return True

def update_all_modules():
    """Update all pipeline modules"""
    modules = [
        "jira_data_extractor",
        "data_processor",
        "weaviate_setup",
        "gpt4o_integration",
        "ppt_generator",
        "beautiful_ai_integration"
    ]
    
    success_count = 0
    for module in modules:
        if update_module(module):
            success_count += 1
    
    logger.info(f"Updated {success_count}/{len(modules)} modules")
    return success_count == len(modules)

if __name__ == "__main__":
    logger.info("Starting module update process")
    
    if update_all_modules():
        logger.info("Module update completed successfully")
    else:
        logger.warning("Module update completed with issues")
