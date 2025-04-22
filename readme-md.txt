# Jira to GPT-4o to Beautiful AI Integration

A full-stack web application that automatically extracts data from Jira, generates business analyst-level insights using GPT-4o, and creates presentations in PowerPoint and Beautiful AI.

## Overview

This application provides a complete solution for transforming Jira project data into insightful presentations:

1. **Jira Data Extraction**: Extracts tickets, sprints, epics, and comments from Jira using the REST API
2. **Data Processing**: Cleans and processes the extracted data for analysis
3. **Weaviate Vector Database**: Stores processed data in a vector database for semantic search
4. **GPT-4o Integration**: Generates business analyst-level insights from the Jira data
5. **PowerPoint Generation**: Creates PowerPoint presentations from the generated insights
6. **Beautiful AI Integration**: Updates Beautiful AI presentations with the latest insights
7. **Web Interface**: Provides a user-friendly dashboard to manage the entire process

## Installation

### Prerequisites

- Python 3.8 or higher
- Jira account with API access
- OpenAI API key for GPT-4o
- Beautiful AI account with API access

### Setup

1. Clone this repository:
```
git clone https://github.com/yourusername/jira-gpt4o-beautiful-ai.git
cd jira-gpt4o-beautiful-ai
```

2. Create a virtual environment and install dependencies:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Update the configuration file:
```
cp config.json.example config.json
# Edit config.json with your API keys and settings
```

### Directory Structure

Ensure these directories exist:
```
mkdir -p jira_data processed_data insights presentations static/presentations
```

## Usage

### Running the Application

For development:
```
flask run --debug
```

For production (with Gunicorn):
```
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

### Accessing the Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

Default login credentials:
- Username: admin
- Password: admin

> Note: For production use, change the default credentials.

### Running the Pipeline

1. Log in to the dashboard
2. Go to Settings and configure your API credentials
3. Return to the Dashboard and click "Run Full Pipeline"
4. View generated presentations in the Presentations tab

### Setting Up Hourly Updates

To set up automatic hourly updates:
```
chmod +x setup_cron.sh
./setup_cron.sh YOUR_PROJECT_KEY
```

## Components

### 1. Jira Data Extractor

Extracts data from Jira using the REST API:
- Projects
- Issues (tickets)
- Comments
- Sprints
- Epics
- Boards

### 2. Data Processor

Cleans and processes the extracted data:
- HTML content cleaning
- Date standardization
- Field extraction
- Data merging
- Vector-ready data preparation

### 3. Weaviate Vector Database

Stores and queries processed data:
- Schema creation for Jira data
- Vector embedding using OpenAI models
- Natural language querying
- Filtering by priority, status, and type

### 4. GPT-4o Integration

Generates insights from the Jira data:
- General insights
- Sprint insights
- Team insights
- Priority insights

### 5. PowerPoint Generator

Creates PowerPoint presentations:
- Title slides
- Section slides
- Content slides
- Status and priority visualization

### 6. Beautiful AI Integration

Updates Beautiful AI presentations:
- Creating presentations
- Adding slides with insights
- Hourly updates

## API Reference

The application provides a simple API:

### Check Status

```
GET /api/status
```

Returns the current status of the system.

### Run Pipeline

```
POST /api/run
```

Headers:
```
X-API-KEY: your-api-key
```

Body:
```json
{
  "project_key": "PROJECT"
}
```

Runs the full pipeline for the specified project.

## Security Considerations

- API keys are stored in the configuration file
- Authentication is required for accessing the web interface
- HTTPS is recommended for production deployment

## Troubleshooting

Common issues:

1. **Jira API Authentication Errors**
   - Ensure your Jira API token is correct and has necessary permissions
   - Verify the Jira URL includes the protocol (https://)

2. **OpenAI API Errors**
   - Check that your OpenAI API key is valid and has sufficient quota
   - Verify you're using a supported model (gpt-4o or gpt-4o-mini)

3. **Weaviate Connection Issues**
   - If using embedded Weaviate, ensure you have sufficient disk space
   - If using remote Weaviate, check URL and API key

4. **Beautiful AI API Errors**
   - Verify your Beautiful AI API key is correct
   - Check for rate limit errors

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Jira API documentation
- OpenAI API documentation
- Beautiful AI API documentation
- Weaviate documentation
