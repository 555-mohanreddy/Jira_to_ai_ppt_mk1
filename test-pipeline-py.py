#!/usr/bin/env python3
"""
Unit tests for the Jira to GPT-4o to Beautiful AI pipeline.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules for testing
from jira_data_extractor import JiraDataExtractor
from data_processor import JiraDataProcessor
from weaviate_setup import WeaviateSetup
from gpt4o_integration import GPT4oIntegration
from ppt_generator import PowerPointGenerator
from beautiful_ai_integration import BeautifulAIIntegration

class TestJiraDataExtractor(unittest.TestCase):
    """Tests for the JiraDataExtractor class"""
    
    @patch('requests.get')
    def test_extract_projects(self, mock_get):
        """Test extracting projects"""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"key": "TEST", "name": "Test Project"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Create extractor with mock credentials
        extractor = JiraDataExtractor(
            jira_url="https://example.atlassian.net",
            username="test",
            api_token="test",
            output_dir="test_output"
        )
        
        # Run the test
        with patch.object(extractor, '_save_to_json') as mock_save:
            mock_save.return_value = "test_output/projects.json"
            projects = extractor.extract_projects()
            
            # Verify
            self.assertEqual(len(projects), 1)
            self.assertEqual(projects[0]["key"], "TEST")
            mock_save.assert_called_once()

class TestDataProcessor(unittest.TestCase):
    """Tests for the JiraDataProcessor class"""
    
    def test_clean_html_content(self):
        """Test cleaning HTML content"""
        processor = JiraDataProcessor(
            input_dir="test_input",
            output_dir="test_output"
        )
        
        # Test with simple HTML
        html_content = "<p>This is a <strong>test</strong> paragraph.</p>"
        cleaned = processor._clean_html_content(html_content)
        
        self.assertEqual(cleaned, "This is a test paragraph.")
        
        # Test with None
        cleaned = processor._clean_html_content(None)
        self.assertEqual(cleaned, "")

class TestWeaviateSetup(unittest.TestCase):
    """Tests for the WeaviateSetup class"""
    
    @patch('weaviate.Client')
    def test_create_schema(self, mock_client):
        """Test creating the Weaviate schema"""
        # Mock weaviate client
        mock_weaviate = MagicMock()
        mock_client.return_value = mock_weaviate
        
        # Mock schema.get method
        mock_weaviate.schema.get.return_value = {"classes": []}
        
        # Create WeaviateSetup with embedded option
        weaviate_setup = WeaviateSetup(
            input_dir="test_input",
            use_embedded=True
        )
        
        # Run the test
        weaviate_setup.create_schema()
        
        # Verify
        mock_weaviate.schema.create_class.assert_called_once()

class TestGPT4oIntegration(unittest.TestCase):
    """Tests for the GPT4oIntegration class"""
    
    @patch('openai.ChatCompletion.create')
    def test_generate_insights(self, mock_create):
        """Test generating insights"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test insights text"
        mock_create.return_value = mock_response
        
        # Create GPT4oIntegration
        gpt4o = GPT4oIntegration(
            api_key="test_key",
            model="gpt-4o"
        )
        
        # Mock saving to JSON
        with patch.object(gpt4o, '_save_to_json') as mock_save:
            mock_save.return_value = "test_output/insights.json"
            
            # Run the test
            jira_data = [{"key": "TEST-1", "summary": "Test issue"}]
            insights = gpt4o.generate_insights(
                jira_data=jira_data,
                insight_type="general",
                output_file="test_output/general_insights.json"
            )
            
            # Verify
            self.assertEqual(insights["type"], "general")
            self.assertEqual(insights["insights_text"], "Test insights text")
            mock_save.assert_called_once()

class TestPowerPointGenerator(unittest.TestCase):
    """Tests for the PowerPointGenerator class"""
    
    @patch('pptx.Presentation')
    def test_generate_general_presentation(self, mock_presentation):
        """Test generating a PowerPoint presentation"""
        # Mock presentation
        mock_pres = MagicMock()
        mock_presentation.return_value = mock_pres
        
        # Mock slides
        mock_pres.slides = MagicMock()
        mock_pres.slides.add_slide.return_value = MagicMock()
        
        # Create PowerPointGenerator
        ppt_gen = PowerPointGenerator(
            insights_dir="test_insights",
            output_dir="test_output"
        )
        
        # Mock loading JSON file
        with patch.object(ppt_gen, '_load_json_file') as mock_load:
            mock_load.return_value = {
                "structured_insights": {
                    "executive summary": "Test executive summary",
                    "key metrics": "Test key metrics"
                }
            }
            
            # Run the test
            output_file = ppt_gen.generate_general_presentation()
            
            # Verify
            self.assertIsNotNone(output_file)
            mock_pres.save.assert_called_once()

if __name__ == '__main__':
    unittest.main()
