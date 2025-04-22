#!/bin/bash
# Setup script for the Jira to GPT-4o to Beautiful AI Integration

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Jira to GPT-4o to Beautiful AI Integration${NC}"
echo ""

# Make scripts executable
echo -e "${YELLOW}Making scripts executable...${NC}"
chmod +x run_pipeline.py
chmod +x run_tests.sh
chmod +x setup_cron.sh
chmod +x deploy.sh
chmod +x update_modules.py

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p jira_data
mkdir -p processed_data
mkdir -p insights
mkdir -p presentations
mkdir -p static/css
mkdir -p static/js
mkdir -p static/presentations
mkdir -p templates
mkdir -p backups
mkdir -p tests

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
else
    source venv/bin/activate
    echo -e "${YELLOW}Updating dependencies...${NC}"
    pip install -r requirements.txt
fi

# Check if config.json exists
if [ ! -f "config.json" ]; then
    echo -e "${YELLOW}Creating config.json from template...${NC}"
    cp config.json.example config.json
    echo -e "${YELLOW}Please edit config.json with your API keys and settings.${NC}"
else
    echo -e "${GREEN}config.json already exists.${NC}"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env with your environment variables.${NC}"
else
    echo -e "${GREEN}.env file already exists.${NC}"
fi

echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo -e "To run the application in development mode:"
echo -e "  ${YELLOW}source venv/bin/activate${NC}"
echo -e "  ${YELLOW}flask run --debug${NC}"
echo ""
echo -e "To run the application in production mode:"
echo -e "  ${YELLOW}source venv/bin/activate${NC}"
echo -e "  ${YELLOW}gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app${NC}"
echo ""
echo -e "To deploy with Docker:"
echo -e "  ${YELLOW}./deploy.sh${NC}"
echo ""
echo -e "To run the pipeline manually:"
echo -e "  ${YELLOW}./run_pipeline.py --project YOUR_PROJECT_KEY${NC}"
echo ""
