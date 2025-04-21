#!/usr/bin/env python3
"""
Beautiful AI Integration

This script integrates with Beautiful AI to automatically update presentations
with insights generated from Jira data.
"""

import os
import json
import logging
import requests
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("beautiful_ai_integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BeautifulAIIntegration:
    """
    A class to integrate with Beautiful AI for updating presentations.
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 insights_dir: str = "insights",
                 presentations_dir: str = "presentations"):
        """
        Initialize the BeautifulAIIntegration.
        
        Args:
            api_key: Beautiful AI API key
            insights_dir: Directory containing the insights JSON files
            presentations_dir: Directory containing the generated PowerPoint presentations
        """
        self.api_key = api_key
        self.insights_dir = insights_dir
        self.presentations_dir = presentations_dir
        
        # Beautiful AI API base URL
        self.base_url = "https://api.beautiful.ai/v1"
        
        # Headers for API requests
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Initialized BeautifulAIIntegration")
        logger.info(f"Insights directory: {insights_dir}")
        logger.info(f"Presentations directory: {presentations_dir}")
    
    def _load_json_file(self, filename: str) -> Dict:
        """
        Load data from a JSON file.
        
        Args:
            filename: Path to the JSON file
            
        Returns:
            Loaded data as dictionary
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Loaded data from {filename}")
            return data
        
        except Exception as e:
            logger.error(f"Error loading data from {filename}: {e}")
            return {}
    
    def _save_to_json(self, data: Union[List, Dict], filename: str) -> str:
        """
        Save data to a JSON file.
        
        Args:
            data: Data to save
            filename: Path to the file
            
        Returns:
            Path to the saved file
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved data to {filename}")
        return filename
    
    def get_presentations(self) -> List[Dict]:
        """
        Get all presentations from Beautiful AI.
        
        Returns:
            List of presentations
        """
        logger.info("Getting all presentations from Beautiful AI")
        
        try:
            response = requests.get(
                f"{self.base_url}/presentations",
                headers=self.headers
            )
            
            response.raise_for_status()
            
            presentations = response.json()
            
            logger.info(f"Retrieved {len(presentations)} presentations")
            
            return presentations
        
        except Exception as e:
            logger.error(f"Error getting presentations: {e}")
            return []
    
    def create_presentation(self, title: str, description: str = "") -> Dict:
        """
        Create a new presentation in Beautiful AI.
        
        Args:
            title: Presentation title
            description: Presentation description
            
        Returns:
            Created presentation data
        """
        logger.info(f"Creating presentation: {title}")
        
        try:
            payload = {
                "title": title,
                "description": description
            }
            
            response = requests.post(
                f"{self.base_url}/presentations",
                headers=self.headers,
                json=payload
            )
            
            response.raise_for_status()
            
            presentation = response.json()
            
            logger.info(f"Created presentation: {presentation.get('id')}")
            
            return presentation
        
        except Exception as e:
            logger.error(f"Error creating presentation: {e}")
            return {}
    
    def get_presentation(self, presentation_id: str) -> Dict:
        """
        Get a presentation from Beautiful AI.
        
        Args:
            presentation_id: ID of the presentation
            
        Returns:
            Presentation data
        """
        logger.info(f"Getting presentation: {presentation_id}")
        
        try:
            response = requests.get(
                f"{self.base_url}/presentations/{presentation_id}",
                headers=self.headers
            )
            
            response.raise_for_status()
            
            presentation = response.json()
            
            logger.info(f"Retrieved presentation: {presentation.get('id')}")
            
            return presentation
        
        except Exception as e:
            logger.error(f"Error getting presentation: {e}")
            return {}
    
    def add_slide(self, 
                 presentation_id: str, 
                 slide_type: str, 
                 title: str, 
                 content: Dict) -> Dict:
        """
        Add a slide to a presentation.
        
        Args:
            presentation_id: ID of the presentation
            slide_type: Type of slide (e.g., "title", "bullets", "chart")
            title: Slide title
            content: Slide content
            
        Returns:
            Added slide data
        """
        logger.info(f"Adding {slide_type} slide to presentation: {presentation_id}")
        
        try:
            payload = {
                "type": slide_type,
                "title": title,
                "content": content
            }
            
            response = requests.post(
                f"{self.base_url}/presentations/{presentation_id}/slides",
                headers=self.headers,
                json=payload
            )
            
            response.raise_for_status()
            
            slide = response.json()
            
            logger.info(f"Added slide: {slide.get('id')}")
            
            return slide
        
        except Exception as e:
            logger.error(f"Error adding slide: {e}")
            return {}
    
    def update_slide(self, 
                    presentation_id: str, 
                    slide_id: str, 
                    title: str, 
                    content: Dict) -> Dict:
        """
        Update a slide in a presentation.
        
        Args:
            presentation_id: ID of the presentation
            slide_id: ID of the slide
            title: New slide title
            content: New slide content
            
        Returns:
            Updated slide data
        """
        logger.info(f"Updating slide {slide_id} in presentation: {presentation_id}")
        
        try:
            payload = {
                "title": title,
                "content": content
            }
            
            response = requests.put(
                f"{self.base_url}/presentations/{presentation_id}/slides/{slide_id}",
                headers=self.headers,
                json=payload
            )
            
            response.raise_for_status()
            
            slide = response.json()
            
            logger.info(f"Updated slide: {slide.get('id')}")
            
            return slide
        
        except Exception as e:
            logger.error(f"Error updating slide: {e}")
            return {}
    
    def delete_slide(self, presentation_id: str, slide_id: str) -> bool:
        """
        Delete a slide from a presentation.
        
        Args:
            presentation_id: ID of the presentation
            slide_id: ID of the slide
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Deleting slide {slide_id} from presentation: {presentation_id}")
        
        try:
            response = requests.delete(
                f"{self.base_url}/presentations/{presentation_id}/slides/{slide_id}",
                headers=self.headers
            )
            
            response.raise_for_status()
            
            logger.info(f"Deleted slide: {slide_id}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error deleting slide: {e}")
            return False
    
    def upload_image(self, image_path: str) -> str:
        """
        Upload an image to Beautiful AI.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            URL of the uploaded image
        """
        logger.info(f"Uploading image: {image_path}")
        
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Encode image data as base64
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "image": encoded_image,
                "filename": os.path.basename(image_path)
            }
            
            response = requests.post(
                f"{self.base_url}/images",
                headers=self.headers,
                json=payload
            )
            
            response.raise_for_status()
            
            image_url = response.json().get('url')
            
            logger.info(f"Uploaded image: {image_url}")
            
            return image_url
        
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return ""
    
    def create_general_presentation(self, insights_file: str = "general_insights.json") -> str:
        """
        Create a general insights presentation in Beautiful AI.
        
        Args:
            insights_file: Name of the insights JSON file
            
        Returns:
            ID of the created presentation
        """
        logger.info(f"Creating general presentation from {insights_file}")
        
        # Load insights
        insights = self._load_json_file(os.path.join(self.insights_dir, insights_file))
        
        if not insights:
            logger.error(f"No insights found in {insights_file}")
            return ""
        
        # Create presentation
        presentation = self.create_presentation(
            "Jira Project Analysis",
            f"Generated on {datetime.now().strftime('%Y-%m-%d')}"
        )
        
        if not presentation:
            logger.error("Failed to create presentation")
            return ""
        
        presentation_id = presentation.get('id')
        
        # Extract structured insights
        structured_insights = insights.get("structured_insights", {})
        
        # Add title slide
        self.add_slide(
            presentation_id,
            "title",
            "Jira Project Analysis",
            {
                "subtitle": f"Generated on {datetime.now().strftime('%Y-%m-%d')}"
            }
        )
        
        # Add executive summary
        if "executive summary" in structured_insights:
            self.add_slide(
                presentation_id,
                "section",
                "Executive Summary",
                {}
            )
            
            # Split content into bullet points
            bullets = structured_insights["executive summary"].split('\n')
            bullets = [b.strip() for b in bullets if b.strip()]
            
            self.add_slide(
                presentation_id,
                "bullets",
                "Executive Summary",
                {
                    "bullets": bullets
                }
            )
        
        # Add key metrics
        if "key metrics" in structured_insights:
            self.add_slide(
                presentation_id,
                "section",
                "Key Metrics",
                {}
            )
            
            # Split content into bullet points
            bullets = structured_insights["key metrics"].split('\n')
            bullets = [b.strip() for b in bullets if b.strip()]
            
            self.add_slide(
                presentation_id,
                "bullets",
                "Key Metrics",
                {
                    "bullets": bullets
                }
            )
        
        # Add issue distribution analysis
        if "issue distribution analysis" in structured_insights:
            self.add_slide(
                presentation_id,
                "section",
                "Issue Distribution",
                {}
            )
            
            # Split content into bullet points
            bullets = structured_insights["issue distribution analysis"].split('\n')
            bullets = [b.strip() for b in bullets if b.strip()]
            
            self.add_slide(
                presentation_id,
                "bullets",
                "Issue Distribution Analysis",
                {
                    "bullets": bullets
                }
            )
        
        # Add bottlenecks and blockers
        if "bottlenecks and blockers" in structured_insights:
            self.add_slide(
                presentation_id,
                "section",
                "Bottlenecks & Blockers",
                {}
            )
            
            # Split content into bullet points
            bullets = structured_insights["bottlenecks and blockers"].split('\n')
            bullets = [b.strip() for b in bullets if b.strip()]
            
            self.add_slide(
                presentation_id,
                "bullets",
                "Bottlenecks and Blockers",
                {
                    "bullets": bullets
                }
            )
        
        # Add recommendations
        if "recommendations" in structured_insights:
            self.add_slide(
                presentation_id,
                "section",
                "Recommendations",
                {}
            )
            
            # Split content into bullet points
            bullets = structured_insights["recommendations"].split('\n')
            bullets = [b.strip() for b in bullets if b.strip()]
            
            self.add_slide(
                presentation_id,
                "bullets",
                "Recommendations",
                {
                    "bullets": bullets
                }
            )
        
        logger.info(f"Created general presentation: {presentation_id}")
        
        return presentation_id
    
    def create_priority_presentation(self, insights_file: str = "priority_insights.json") -> str:
        """
        Create a priority insights presentation in Beautiful AI.
        
        Args:
            insights_file: Name of the insights JSON file
            
        Returns:
            ID of the created presentation
        """
        logger.info(f"Creating priority presentation from {insights_file}")
        
        # Load insights
        insights = self._load_json_file(os.path.join(self.insights_dir, insights_file))
        
        if not insights:
            logger.error(f"No insights found in {insights_file
(Content truncated due to size limit. Use line ranges to read in chunks)