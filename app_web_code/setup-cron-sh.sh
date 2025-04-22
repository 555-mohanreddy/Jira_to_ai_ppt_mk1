#!/bin/bash
# Setup cron job for hourly updates

# Get absolute path to the project directory
PROJECT_DIR=$(pwd)

# Create a temporary file for the cron job
cat > /tmp/jira_cron << EOL
# Run the Jira to GPT-4o to Beautiful AI pipeline every hour
0 * * * * cd $PROJECT_DIR && python3 -c "from app import run_full_pipeline; run_full_pipeline('${1:-PROJECT}')" >> $PROJECT_DIR/cron.log 2>&1
EOL

# Install the cron job
crontab -l | grep -v "jira_cron" | cat - /tmp/jira_cron > /tmp/crontab_new
crontab /tmp/crontab_new
rm /tmp/jira_cron /tmp/crontab_new

echo "Cron job installed to run the pipeline every hour for project ${1:-PROJECT}"
echo "Logs will be written to $PROJECT_DIR/cron.log"
