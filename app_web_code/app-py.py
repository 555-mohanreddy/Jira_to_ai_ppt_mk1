#!/usr/bin/env python3
"""
Jira to GPT-4o to Beautiful AI Integration Web Application

This is the main Flask application file that provides a web interface for the integration.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import json
import time
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

# Import our custom modules
from jira_data_extractor import JiraDataExtractor
from data_processor import JiraDataProcessor
from weaviate_setup import WeaviateSetup
from gpt4o_integration import GPT4oIntegration
from ppt_generator import PowerPointGenerator
from beautiful_ai_integration import BeautifulAIIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("flask_app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load configuration
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {
            "jira": {
                "url": os.environ.get("JIRA_URL", ""),
                "username": os.environ.get("JIRA_USERNAME", ""),
                "api_token": os.environ.get("JIRA_API_TOKEN", ""),
                "project_key": os.environ.get("JIRA_PROJECT_KEY", "")
            },
            "openai": {
                "api_key": os.environ.get("OPENAI_API_KEY", ""),
                "model": os.environ.get("OPENAI_MODEL", "gpt-4o")
            },
            "beautiful_ai": {
                "api_key": os.environ.get("BEAUTIFUL_AI_API_KEY", "")
            },
            "weaviate": {
                "use_embedded": True,
                "url": os.environ.get("WEAVIATE_URL", ""),
                "api_key": os.environ.get("WEAVIATE_API_KEY", "")
            },
            "update_interval": 3600
        }

config = load_config()

# Simple user database (replace with actual database in production)
users = {
    'admin': {
        'password': generate_password_hash('admin'),
        'name': 'Administrator'
    }
}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, name):
        self.id = id
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id, users[user_id]['name'])
    return None

# Initialize components
def init_jira_extractor():
    return JiraDataExtractor(
        jira_url=config['jira']['url'],
        username=config['jira']['username'],
        api_token=config['jira']['api_token'],
        output_dir="jira_data"
    )

def init_data_processor():
    return JiraDataProcessor(
        input_dir="jira_data",
        output_dir="processed_data"
    )

def init_weaviate():
    return WeaviateSetup(
        input_dir="processed_data",
        weaviate_url=config['weaviate']['url'],
        api_key=config['weaviate']['api_key'],
        use_embedded=config['weaviate']['use_embedded']
    )

def init_gpt4o(weaviate_client):
    return GPT4oIntegration(
        api_key=config['openai']['api_key'],
        model=config['openai']['model'],
        weaviate_client=weaviate_client
    )

def init_ppt_generator():
    return PowerPointGenerator(
        insights_dir="insights",
        output_dir="presentations"
    )

def init_beautiful_ai():
    return BeautifulAIIntegration(
        api_key=config['beautiful_ai']['api_key'],
        insights_dir="insights",
        presentations_dir="presentations"
    )

# Ensure required directories exist
os.makedirs("jira_data", exist_ok=True)
os.makedirs("processed_data", exist_ok=True)
os.makedirs("insights", exist_ok=True)
os.makedirs("presentations", exist_ok=True)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and check_password_hash(users[username]['password'], password):
            login_user(User(username, users[username]['name']))
            flash('Logged in successfully', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get project status summary
    project_status = get_project_status()
    
    return render_template('dashboard.html', 
                          user=current_user,
                          project_status=project_status,
                          config=config)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Update configuration
        config['jira']['url'] = request.form['jira_url']
        config['jira']['username'] = request.form['jira_username']
        config['jira']['api_token'] = request.form['jira_api_token']
        config['jira']['project_key'] = request.form['jira_project_key']
        
        config['openai']['api_key'] = request.form['openai_api_key']
        config['openai']['model'] = request.form['openai_model']
        
        config['beautiful_ai']['api_key'] = request.form['beautiful_ai_api_key']
        
        # Save configuration
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        flash('Settings saved successfully', 'success')
        return redirect(url_for('settings'))
    
    return render_template('settings.html', config=config)

@app.route('/run', methods=['POST'])
@login_required
def run_pipeline():
    try:
        # Get parameters from form
        project_key = request.form.get('project_key', config['jira']['project_key'])
        
        # Run the pipeline
        result = run_full_pipeline(project_key)
        
        if result['status'] == 'success':
            flash('Pipeline executed successfully', 'success')
        else:
            flash(f"Pipeline execution failed: {result['message']}", 'danger')
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Error running pipeline: {e}")
        flash(f"Error running pipeline: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))

@app.route('/presentations')
@login_required
def presentations():
    # Get list of presentations
    pres_list = get_presentations_list()
    return render_template('presentations.html', presentations=pres_list)

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'config_loaded': bool(config)
    })

@app.route('/api/run', methods=['POST'])
def api_run_pipeline():
    # Check API key for authentication
    api_key = request.headers.get('X-API-KEY')
    if not api_key or api_key != os.environ.get('API_KEY'):
        return jsonify({
            'status': 'error',
            'message': 'Invalid API key'
        }), 401
    
    try:
        # Get parameters from JSON
        data = request.get_json()
        project_key = data.get('project_key', config['jira']['project_key'])
        
        # Run the pipeline
        result = run_full_pipeline(project_key)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API error running pipeline: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Helper functions
def get_project_status():
    """Get a summary of the project status"""
    try:
        # Check for existence of files to determine status
        status = {
            'jira_data': False,
            'processed_data': False,
            'weaviate': False,
            'insights': False,
            'presentations': False,
            'beautiful_ai': False
        }
        
        # Check Jira data
        jira_files = os.listdir('jira_data') if os.path.exists('jira_data') else []
        status['jira_data'] = len(jira_files) > 0
        
        # Check processed data
        processed_files = os.listdir('processed_data') if os.path.exists('processed_data') else []
        status['processed_data'] = len(processed_files) > 0
        
        # Check insights
        insight_files = os.listdir('insights') if os.path.exists('insights') else []
        status['insights'] = len(insight_files) > 0
        
        # Check presentations
        ppt_files = os.listdir('presentations') if os.path.exists('presentations') else []
        status['presentations'] = len(ppt_files) > 0
        
        # Get timestamps if available
        latest_run = None
        timestamp_file = 'last_run_timestamp.txt'
        if os.path.exists(timestamp_file):
            with open(timestamp_file, 'r') as f:
                latest_run = f.read().strip()
        
        return {
            'components': status,
            'latest_run': latest_run
        }
        
    except Exception as e:
        logger.error(f"Error getting project status: {e}")
        return {
            'components': {},
            'latest_run': None,
            'error': str(e)
        }

def get_presentations_list():
    """Get a list of generated presentations"""
    try:
        presentations = []
        
        # Get PowerPoint presentations
        ppt_dir = 'presentations'
        if os.path.exists(ppt_dir):
            for file in os.listdir(ppt_dir):
                if file.endswith('.pptx'):
                    presentations.append({
                        'name': file,
                        'type': 'pptx',
                        'path': os.path.join(ppt_dir, file),
                        'created': datetime.fromtimestamp(os.path.getctime(os.path.join(ppt_dir, file))).strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        # Get Beautiful AI presentations (just the IDs for now)
        beautiful_ai_file = 'presentations/beautiful_ai_presentations.json'
        if os.path.exists(beautiful_ai_file):
            with open(beautiful_ai_file, 'r') as f:
                try:
                    beautiful_ai_data = json.load(f)
                    for pres_id, pres_data in beautiful_ai_data.items():
                        presentations.append({
                            'name': pres_data.get('title', 'Untitled'),
                            'type': 'beautiful_ai',
                            'id': pres_id,
                            'url': pres_data.get('url', ''),
                            'created': pres_data.get('created', 'Unknown')
                        })
                except Exception as e:
                    logger.error(f"Error parsing Beautiful AI presentations: {e}")
        
        return presentations
        
    except Exception as e:
        logger.error(f"Error getting presentations list: {e}")
        return []

def run_full_pipeline(project_key):
    """Run the full data pipeline"""
    try:
        # Initialize components
        jira_extractor = init_jira_extractor()
        data_processor = init_data_processor()
        weaviate_client = init_weaviate()
        gpt4o_integration = init_gpt4o(weaviate_client)
        ppt_generator = init_ppt_generator()
        beautiful_ai_integration = init_beautiful_ai()
        
        # 1. Extract data from Jira
        logger.info(f"Extracting data for project: {project_key}")
        jira_data = jira_extractor.extract_all_data(project_key)
        
        # Get the latest data file
        jira_files = os.listdir('jira_data')
        jira_files = [f for f in jira_files if f.startswith(f'jira_complete_data_{project_key}')]
        jira_files.sort(reverse=True)  # Latest first
        
        if not jira_files:
            return {
                'status': 'error',
                'message': 'No Jira data extracted'
            }
        
        latest_jira_file = jira_files[0]
        
        # 2. Process the data
        logger.info("Processing Jira data")
        processed_data = data_processor.process_all_data(os.path.join('jira_data', latest_jira_file))
        
        # 3. Set up Weaviate
        logger.info("Setting up Weaviate")
        weaviate_client.create_schema()
        weaviate_client.import_data("vector_ready_data.json")
        
        # 4. Generate insights with GPT-4o
        logger.info("Generating insights with GPT-4o")
        insights = gpt4o_integration.generate_all_insights(output_dir="insights", use_weaviate=True)
        
        # 5. Generate PowerPoint presentations
        logger.info("Generating PowerPoint presentations")
        ppt_files = ppt_generator.generate_all_presentations()
        
        # 6. Update Beautiful AI presentations
        logger.info("Updating Beautiful AI presentations")
        beautiful_ai_ids = beautiful_ai_integration.create_all_presentations()
        
        # Save timestamp of last run
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('last_run_timestamp.txt', 'w') as f:
            f.write(timestamp)
        
        return {
            'status': 'success',
            'timestamp': timestamp,
            'project_key': project_key,
            'jira_file': latest_jira_file,
            'beautiful_ai_ids': beautiful_ai_ids
        }
        
    except Exception as e:
        logger.error(f"Error running pipeline: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

# Run the app
if __name__ == '__main__':
    # Create necessary directories
    for directory in ['jira_data', 'processed_data', 'insights', 'presentations']:
        os.makedirs(directory, exist_ok=True)
    
    # Initialize Weaviate schema if needed
    try:
        weaviate_client = init_weaviate()
        weaviate_client.create_schema()
    except Exception as e:
        logger.warning(f"Could not initialize Weaviate schema: {e}")
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
