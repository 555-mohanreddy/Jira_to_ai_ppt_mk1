#!/usr/bin/env python3
"""
GPT-4o Integration with Weaviate

This script integrates GPT-4o with Weaviate to generate business analyst-level insights
from Jira data stored in the vector database.
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union
import openai
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("gpt4o_integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GPT4oIntegration:
    """
    A class to integrate GPT-4o with Weaviate for generating insights from Jira data.
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model: str = "gpt-4o",
                 weaviate_client = None):
        """
        Initialize the GPT4oIntegration.
        
        Args:
            api_key: OpenAI API key
            model: GPT model to use (gpt-4o or gpt-4o-mini)
            weaviate_client: Weaviate client instance
        """
        self.model = model
        self.weaviate_client = weaviate_client
        
        # Set up OpenAI client
        if api_key:
            openai.api_key = api_key
        else:
            # Try to get API key from environment variable
            openai.api_key = os.environ.get("OPENAI_API_KEY")
        
        if not openai.api_key:
            logger.warning("No OpenAI API key provided. Please set OPENAI_API_KEY environment variable or provide api_key parameter.")
        
        logger.info(f"Initialized GPT4oIntegration with model: {model}")
    
    def _save_to_json(self, data: Union[List, Dict], filename: str) -> str:
        """
        Save data to a JSON file.
        
        Args:
            data: Data to save
            filename: Name of the file
            
        Returns:
            Path to the saved file
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved data to {filename}")
        return filename
    
    def generate_insights(self, 
                         jira_data: List[Dict], 
                         insight_type: str = "general",
                         output_file: Optional[str] = None) -> Dict:
        """
        Generate insights from Jira data using GPT-4o.
        
        Args:
            jira_data: List of Jira issues
            insight_type: Type of insights to generate (general, sprint, team, priority)
            output_file: File to save the insights to
            
        Returns:
            Dictionary containing the generated insights
        """
        logger.info(f"Generating {insight_type} insights for {len(jira_data)} Jira issues")
        
        # Prepare the prompt based on insight type
        if insight_type == "general":
            prompt = self._create_general_insights_prompt(jira_data)
        elif insight_type == "sprint":
            prompt = self._create_sprint_insights_prompt(jira_data)
        elif insight_type == "team":
            prompt = self._create_team_insights_prompt(jira_data)
        elif insight_type == "priority":
            prompt = self._create_priority_insights_prompt(jira_data)
        else:
            prompt = self._create_general_insights_prompt(jira_data)
        
        # Call GPT-4o API
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a skilled business analyst who provides insightful analysis of Jira data. Your insights should be data-driven, actionable, and presented in a clear, professional manner suitable for executive presentations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            # Extract the insights from the response
            insights_text = response.choices[0].message.content
            
            # Create a structured insights object
            insights = {
                "type": insight_type,
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "data_count": len(jira_data),
                "insights_text": insights_text,
                "structured_insights": self._parse_insights(insights_text, insight_type)
            }
            
            # Save insights to file if specified
            if output_file:
                self._save_to_json(insights, output_file)
            
            return insights
        
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {
                "type": insight_type,
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "data_count": len(jira_data),
                "error": str(e)
            }
    
    def _create_general_insights_prompt(self, jira_data: List[Dict]) -> str:
        """
        Create a prompt for generating general insights from Jira data.
        
        Args:
            jira_data: List of Jira issues
            
        Returns:
            Prompt for GPT-4o
        """
        # Create a summary of the data
        issue_types = {}
        statuses = {}
        priorities = {}
        
        for issue in jira_data:
            # Count issue types
            issue_type = issue.get("issue_type", "Unknown")
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
            
            # Count statuses
            status = issue.get("status", "Unknown")
            statuses[status] = statuses.get(status, 0) + 1
            
            # Count priorities
            priority = issue.get("priority", "Unknown")
            priorities[priority] = priorities.get(priority, 0) + 1
        
        # Format the data summary
        data_summary = f"""
        Data Summary:
        - Total Issues: {len(jira_data)}
        - Issue Types: {', '.join([f"{k}: {v}" for k, v in issue_types.items()])}
        - Statuses: {', '.join([f"{k}: {v}" for k, v in statuses.items()])}
        - Priorities: {', '.join([f"{k}: {v}" for k, v in priorities.items()])}
        """
        
        # Create the prompt
        prompt = f"""
        Please analyze the following Jira data and provide business analyst-level insights:
        
        {data_summary}
        
        Here are the first 5 issues for reference:
        
        {json.dumps(jira_data[:5], indent=2)}
        
        Please provide the following insights:
        1. Executive Summary: A brief overview of the project status based on the Jira data.
        2. Key Metrics: Important metrics derived from the data.
        3. Issue Distribution Analysis: Analysis of how issues are distributed across types, statuses, and priorities.
        4. Bottlenecks and Blockers: Identification of any bottlenecks or blockers in the project.
        5. Recommendations: Actionable recommendations based on the analysis.
        
        Format your response as a structured report with clear sections and bullet points where appropriate.
        """
        
        return prompt
    
    def _create_sprint_insights_prompt(self, jira_data: List[Dict]) -> str:
        """
        Create a prompt for generating sprint-specific insights from Jira data.
        
        Args:
            jira_data: List of Jira issues
            
        Returns:
            Prompt for GPT-4o
        """
        # Create a summary of the sprint data
        sprint_issues = {}
        
        for issue in jira_data:
            sprint = issue.get("sprint", "No Sprint")
            if sprint not in sprint_issues:
                sprint_issues[sprint] = []
            sprint_issues[sprint].append(issue)
        
        # Format the sprint summary
        sprint_summary = "Sprint Summary:\n"
        for sprint, issues in sprint_issues.items():
            sprint_summary += f"- {sprint}: {len(issues)} issues\n"
        
        # Create the prompt
        prompt = f"""
        Please analyze the following Jira sprint data and provide business analyst-level insights:
        
        {sprint_summary}
        
        Here are the first 5 issues for reference:
        
        {json.dumps(jira_data[:5], indent=2)}
        
        Please provide the following insights:
        1. Sprint Performance: Analysis of sprint velocity, completion rate, and scope changes.
        2. Sprint Comparison: Comparison of current sprint with previous sprints (if data available).
        3. Sprint Health: Assessment of sprint health based on issue distribution and progress.
        4. Risk Assessment: Identification of risks that might affect sprint completion.
        5. Recommendations: Actionable recommendations for improving sprint performance.
        
        Format your response as a structured report with clear sections and bullet points where appropriate.
        """
        
        return prompt
    
    def _create_team_insights_prompt(self, jira_data: List[Dict]) -> str:
        """
        Create a prompt for generating team-specific insights from Jira data.
        
        Args:
            jira_data: List of Jira issues
            
        Returns:
            Prompt for GPT-4o
        """
        # Create a summary of the team data
        assignee_issues = {}
        
        for issue in jira_data:
            assignee = issue.get("assignee", "Unassigned")
            if assignee not in assignee_issues:
                assignee_issues[assignee] = []
            assignee_issues[assignee].append(issue)
        
        # Format the team summary
        team_summary = "Team Summary:\n"
        for assignee, issues in assignee_issues.items():
            team_summary += f"- {assignee}: {len(issues)} issues\n"
        
        # Create the prompt
        prompt = f"""
        Please analyze the following Jira team data and provide business analyst-level insights:
        
        {team_summary}
        
        Here are the first 5 issues for reference:
        
        {json.dumps(jira_data[:5], indent=2)}
        
        Please provide the following insights:
        1. Team Workload: Analysis of workload distribution across team members.
        2. Team Performance: Assessment of team performance based on issue completion and velocity.
        3. Skill Distribution: Identification of skill distribution based on issue types assigned.
        4. Collaboration Patterns: Analysis of collaboration patterns based on issue assignments and comments.
        5. Recommendations: Actionable recommendations for improving team performance and collaboration.
        
        Format your response as a structured report with clear sections and bullet points where appropriate.
        """
        
        return prompt
    
    def _create_priority_insights_prompt(self, jira_data: List[Dict]) -> str:
        """
        Create a prompt for generating priority-specific insights from Jira data.
        
        Args:
            jira_data: List of Jira issues
            
        Returns:
            Prompt for GPT-4o
        """
        # Create a summary of the priority data
        priority_issues = {}
        
        for issue in jira_data:
            priority = issue.get("priority", "No Priority")
            if priority not in priority_issues:
                priority_issues[priority] = []
            priority_issues[priority].append(issue)
        
        # Format the priority summary
        priority_summary = "Priority Summary:\n"
        for priority, issues in priority_issues.items():
            priority_summary += f"- {priority}: {len(issues)} issues\n"
        
        # Create the prompt
        prompt = f"""
        Please analyze the following Jira priority data and provide business analyst-level insights:
        
        {priority_summary}
        
        Here are the first 5 issues for reference:
        
        {json.dumps(jira_data[:5], indent=2)}
        
        Please provide the following insights:
        1. Priority Distribution: Analysis of how issues are distributed across priority levels.
        2. High Priority Issues: Detailed analysis of high priority issues, their status, and progress.
        3. Priority Alignment: Assessment of whether priority assignments align with business objectives.
        4. Priority Trends: Identification of trends in priority assignments over time.
        5. Recommendations: Actionable recommendations for better priority management.
        
        Format your response as a structured report with clear sections and bullet points where appropriate.
        """
        
        return prompt
    
    def _parse_insights(self, insights_text: str, insight_type: str) -> Dict:
        """
        Parse the insights text into a structured format.
        
        Args:
            insights_text: Raw insights text from GPT-4o
            insight_type: Type of insights
            
        Returns:
            Structured insights dictionary
        """
        # Simple parsing based on section headers
        sections = {}
        current_section = "general"
        
        for line in insights_text.split('\n'):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check if this is a section header
            if line.endswith(':') or line.startswith('#') or line.startswith('##'):
                # Clean up the section name
                section_name = line.replace('#', '').replace(':', '').strip().lower()
                current_section = section_name
                sections[current_section] = []
            else:
                # Add the line to the current section
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].append(line)
        
        # Convert lists of lines to strings
        for section, lines in sections.items():
            sections[section] = '\n'.join(lines)
        
        return sections
    
    def generate_all_insights(self, 
                             output_dir: str = "insights",
                             use_weaviate: bool = True) -> Dict:
        """
        Generate all types of insights from Jira data.
        
        Args:
            output_dir: Directory to save the insights to
            use_weaviate: Whether to use Weaviate to get the data
            
        Returns:
            Dictionary containing all generated insights
        """
        logger.info("Generating all insights")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        all_insights = {}
        
        # Get all issues from Weaviate if available
        if use_weaviate and self.weaviate_client:
            try:
                all_issues = self.weaviate_client.get_all_issues(limit=1000)
                logger.info(f"Retrieved {len(all_issues)} issues from Weaviate")
            except Exception as e:
                logger.error(f"Error retrieving issues from Weaviate: {e}")
                all_issues = []
        else:
            # Load from a file if Weaviate is not available
            try:
                with open("processed_data/merged_jira_data.json", 'r', encoding='utf-8') as f:
                    all_issues = json.load(f)
                logger.info(f"Loaded {len(all_issues)} issues from file")
            except Exception as e:
                logger.error(f"Error loading issues from file: {e}")
                all_issues = []
        

(Content truncated due to size limit. Use line ranges to read in chunks)