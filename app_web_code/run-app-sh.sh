#!/bin/bash
# Script to run the Flask application with error handling

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 first.${NC}"
    exit 1
fi

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Running setup script...${NC}"
    ./setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Check if environment is production or development
if [ "$1" == "prod" ] || [ "$1" == "production" ]; then
    # Production mode
    echo -e "${GREEN}Starting application in production mode...${NC}"
    
    # Check if gunicorn is installed
    if ! python -c "import gunicorn" &> /dev/null; then
        echo -e "${YELLOW}Gunicorn not found. Installing...${NC}"
        pip install gunicorn
    fi
    
    # Run with gunicorn
    gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
else
    # Development mode
    echo -e "${GREEN}Starting application in development mode...${NC}"
    export FLASK_ENV=development
    flask run --debug
fi
