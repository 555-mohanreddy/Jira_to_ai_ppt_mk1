I'll create a README file for this project:

```markdown
# Jira to GPT-4o to Beautiful AI Integration

## Overview

This project integrates Jira with GPT-4o and Beautiful AI to automatically generate insightful presentations from Jira project data. The system extracts data from Jira, processes it, stores it in a Weaviate vector database, generates business analyst-level insights using GPT-4o, creates PowerPoint presentations, and updates Beautiful AI presentations on an hourly basis.

## Features

- Automated extraction of Jira data (issues, epics, sprints, comments)
- Data cleaning and processing
- Vector database storage with Weaviate
- AI-generated insights using GPT-4o
- Automatic PowerPoint generation
- Beautiful AI presentation creation and updating
- Scheduled hourly updates

## System Architecture

The system follows a data pipeline architecture that processes Jira data through multiple stages:

1. Data is extracted from Jira using the REST API
2. The data is processed and cleaned
3. Processed data is stored in Weaviate vector database
4. GPT-4o queries Weaviate to generate insights
5. PowerPoint presentations are generated from insights
6. Beautiful AI presentations are updated with the latest insights hourly

## Prerequisites

- Python 3.8 or higher
- Jira account with API access
- OpenAI API key for GPT-4o
- Beautiful AI account with API access
- Weaviate (embedded or remote instance)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/jira-gpt4o-beautiful-ai.git
cd jira-gpt4o-beautiful-ai
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export JIRA_URL="https://your-domain.atlassian.net"
export JIRA_USERNAME="your-email@example.com"
export JIRA_API_TOKEN="your-jira-api-token"
export OPENAI_API_KEY="your-openai-api-key"
export BEAUTIFUL_AI_API_KEY="your-beautiful-ai-api-key"
```

## Configuration

Create a configuration file `config.json`:
```json
{
  "jira": {
    "url": "https://your-domain.atlassian.net",
    "username": "your-email@example.com",
    "api_token": "your-jira-api-token",
    "project_key": "PROJECT"
  },
  "openai": {
    "api_key": "your-openai-api-key",
    "model": "gpt-4o"
  },
  "beautiful_ai": {
    "api_key": "your-beautiful-ai-api-key"
  },
  "weaviate": {
    "use_embedded": true,
    "url": null,
    "api_key": null
  },
  "update_interval": 3600
}
```

## Usage

### Running the Complete Pipeline

To run the complete pipeline, use the main script:

```bash
python main.py
```

This will:
1. Extract data from Jira
2. Process and clean the data
3. Store the data in Weaviate
4. Generate insights using GPT-4o
5. Create PowerPoint presentations
6. Update Beautiful AI presentations

### Setting Up Hourly Updates

To set up hourly updates, add the following to your crontab:

```bash
0 * * * * cd /path/to/jira-gpt4o-beautiful-ai && python main.py --update-only
```

This will run the update process every hour, extracting new data from Jira, generating new insights, and updating the Beautiful AI presentations.

## Project Structure

- `jira_data_extractor.py`: Extracts data from Jira
- `data_processor.py`: Cleans and processes the extracted data
- `weaviate_setup.py`: Sets up and manages the Weaviate vector database
- `gpt4o_integration.py`: Integrates with GPT-4o for insight generation
- `ppt_generator.py`: Generates PowerPoint presentations
- `beautiful_ai_integration.py`: Integrates with Beautiful AI
- `main.py`: Main script to run the complete pipeline

## Troubleshooting

### Common Issues

1. **Jira API Authentication Errors**
   - Ensure your Jira API token is correct and has the necessary permissions
   - Check that your Jira URL is correct and includes the protocol (https://)

2. **OpenAI API Errors**
   - Verify your OpenAI API key is correct and has sufficient quota
   - Check that you're using a supported model (gpt-4o or gpt-4o-mini)

3. **Weaviate Connection Issues**
   - If using a remote Weaviate instance, ensure the URL and API key are correct
   - If using embedded Weaviate, ensure you have sufficient disk space and memory

4. **Beautiful AI API Errors**
   - Verify your Beautiful AI API key is correct and has the necessary permissions
   - Check that you're not exceeding API rate limits

## License

MIT

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
```
