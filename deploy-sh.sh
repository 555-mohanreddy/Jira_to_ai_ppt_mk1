#!/bin/bash
# Deployment script for Jira to GPT-4o to Beautiful AI Integration

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Jira to GPT-4o to Beautiful AI Integration - Deployment Script${NC}"
echo ""

# Check if .env file exists, create from example if not
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit the .env file with your credentials before continuing.${NC}"
    read -p "Press Enter to continue after editing .env..."
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${GREEN}Creating necessary directories...${NC}"
mkdir -p jira_data processed_data insights presentations static/presentations

# Build and start the containers
echo -e "${GREEN}Building and starting Docker containers...${NC}"
docker-compose up -d --build

# Check if containers are running
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Deployment successful!${NC}"
    echo -e "The application is now running at ${YELLOW}http://localhost:5000${NC}"
    echo -e "Default login: ${YELLOW}username: admin, password: admin${NC}"
    echo -e "${RED}IMPORTANT: Change the default login credentials for production use.${NC}"
else
    echo -e "${RED}Deployment failed. Please check the error messages above.${NC}"
    exit 1
fi

# Setup cron job for hourly updates if requested
read -p "Do you want to set up hourly updates? (y/n) " setup_cron
if [[ $setup_cron == "y" || $setup_cron == "Y" ]]; then
    # Source the .env file to get the project key
    source .env
    echo -e "${GREEN}Setting up hourly updates for project ${JIRA_PROJECT_KEY}...${NC}"
    chmod +x setup_cron.sh
    ./setup_cron.sh $JIRA_PROJECT_KEY
    echo -e "${GREEN}Hourly updates configured.${NC}"
fi

echo ""
echo -e "${GREEN}Deployment complete!${NC}"
