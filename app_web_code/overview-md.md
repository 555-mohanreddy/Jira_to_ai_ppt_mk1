# Jira to GPT-4o to Beautiful AI Integration

I've created a complete web application that integrates Jira with GPT-4o and Beautiful AI. This application provides a seamless pipeline for extracting data from Jira, processing it, generating insights using GPT-4o, and creating presentations in both PowerPoint and Beautiful AI formats.

## Key Components

### 1. Flask Web Application
* User authentication system
* Dashboard for monitoring pipeline status
* Settings management for API credentials
* Presentation viewer

### 2. Data Pipeline
* Jira data extraction (using existing `jira_data_extractor.py`)
* Data processing (using existing `data_processor.py`)
* Weaviate vector database integration (using existing `weaviate_setup.py`)
* GPT-4o insights generation (using existing `gpt4o_integration.py`)
* PowerPoint generation (using existing `ppt_generator.py`)
* Beautiful AI integration (using existing `beautiful_ai_integration.py`)

### 3. API Layer
* RESTful API for triggering the pipeline
* Status monitoring endpoints

### 4. Deployment System
* Docker container support
* Docker Compose configuration for easy deployment
* Environment variable configuration

## How to Use

### 1. Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/jira-gpt4o-beautiful-ai.git
cd jira-gpt4o-beautiful-ai

# Run the setup script
chmod +x setup.sh
./setup.sh
```

### 2. Configure
* Edit `config.json` with your API credentials
* Or use environment variables in `.env` file

### 3. Run the Application

```bash
# Development mode
./run_app.sh

# Production mode
./run_app.sh prod
```

### 4. Access the Web Interface
* Open your browser and navigate to `http://localhost:5000`
* Login with default credentials (username: admin, password: admin)
* Configure your API credentials in the Settings page
* Run the pipeline from the Dashboard

### 5. Docker Deployment

```bash
# Deploy with Docker
./deploy.sh
```

### 6. Scheduled Updates

```bash
# Set up hourly updates
./setup_cron.sh YOUR_PROJECT_KEY
```

## Directory Structure

```
jira-gpt4o-beautiful-ai/
├── app.py                  # Main Flask application
├── wsgi.py                 # WSGI entry point
├── config.json             # Configuration file
├── config.json.example     # Configuration template
├── .env                    # Environment variables
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── run_app.sh              # Script to run the application
├── run_pipeline.py         # Script to run the pipeline
├── setup.sh                # Setup script
├── setup_cron.sh           # Cron job setup script
├── deploy.sh               # Deployment script
├── run_tests.sh            # Test runner script
├── update_modules.py       # Module updater script
├── jira_data_extractor.py  # Jira data extraction
├── data_processor.py       # Data processing
├── weaviate_setup.py       # Weaviate integration
├── gpt4o_integration.py    # GPT-4o integration
├── ppt_generator.py        # PowerPoint generation
├── beautiful_ai_integration.py # Beautiful AI integration
├── templates/              # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── settings.html
│   └── presentations.html
├── static/                 # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── jira_data/              # Extracted Jira data
├── processed_data/         # Processed data
├── insights/               # Generated insights
├── presentations/          # Generated presentations
└── tests/                  # Unit tests
    ├── __init__.py
    └── test_pipeline.py
```
