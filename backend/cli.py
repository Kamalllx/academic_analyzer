#!/usr/bin/env python3
"""
CLI interface for the Intelligent Academic Document Analyzer & Learning Assistant
"""

import click
import requests
import json
import os
import sys
from datetime import datetime
import pandas as pd
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:5000"
CONFIG_FILE = os.path.expanduser("~/.academic_analyzer_config.json")

class AcademicAnalyzerCLI:
    def __init__(self):
        self.config = self.load_config()
        self.session = requests.Session()
    
    def load_config(self):
        """Load CLI configuration"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {"user_id": "cli_user", "api_url": API_BASE_URL}
    
    def save_config(self):
        """Save CLI configuration"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def api_request(self, method, endpoint, data=None, files=None):
        """Make API request with error handling"""
        url = f"{self.config['api_url']}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=data)
            elif method.upper() == "POST":
                if files:
                    response = self.session.post(url, data=data, files=files)
                else:
                    response = self.session.post(url, json=data)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            click.echo("❌ Error: Cannot connect to the server. Make sure the Flask app is running on localhost:5000")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            click.echo(f"❌ HTTP Error: {e}")
            return {"error": str(e)}
        except Exception as e:
            click.echo(f"❌ Error: {e}")
            return {"error": str(e)}

cli_app = AcademicAnalyzerCLI()

@click.group()
@click.option('--user-id', help='Set user ID for session')
@click.option('--api-url', help='Set API base URL')
def cli(user_id, api_url):
    """Intelligent Academic Document Analyzer CLI"""
    if user_id:
        cli_app.config['user_id'] = user_id
    if api_url:
        cli_app.config['api_url'] = api_url
    cli_app.save_config()

@cli.command()
@click.option('--file', '-f', type=click.Path(exists=True), required=True, help='PDF file to upload')
@click.option('--subject', '-s', help='Subject/topic of the document')
@click.option('--user-id', help='User ID (overrides config)')
def upload_pdf(file, subject, user_id):
    """Upload a PDF document for analysis"""
    click.echo(f"📄 Uploading PDF: {file}")
    
    if not subject:
        subject = click.prompt('Enter the subject/topic for this document')
    
    current_user_id = user_id or cli_app.config['user_id']
    
    with open(file, 'rb') as f:
        files = {'file': f}
        data = {
            'subject': subject,
            'user_id': current_user_id
        }
        
        result = cli_app.api_request('POST', '/upload_pdf', data=data, files=files)
    
    if 'error' in result:
        click.echo(f"❌ Upload failed: {result['error']}")
    else:
        click.echo("✅ PDF uploaded successfully!")
        click.echo(f"   Document ID: {result.get('document_id')}")
        click.echo(f"   Chunks created: {result.get('chunks')}")
        click.echo(f"   Complexity score: {result.get('complexity_score'):.3f}")

@cli.command()
@click.option('--question', '-q', help='Question to ask')
@click.option('--document-id', '-d', help='Specific document ID (default: search all)')
@click.option('--user-id', help='User ID (overrides config)')
@click.option('--interactive', '-i', is_flag=True, help='Start interactive Q&A session')
def ask(question, document_id, user_id, interactive):
    """Ask questions about uploaded documents"""
    current_user_id = user_id or cli_app.config['user_id']
    doc_id = document_id or 'all'
    
    if interactive:
        click.echo("🤖 Starting interactive Q&A session. Type 'quit' to exit.")
        while True:
            question = click.prompt('\n📝 Your question')
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            _process_question(question, doc_id, current_user_id)
    else:
        if not question:
            question = click.prompt('📝 Enter your question')
        
        _process_question(question, doc_id, current_user_id)

def _process_question(question, doc_id, user_id):
    """Process a single question"""
    data = {
        'question': question,
        'document_id': doc_id,
        'user_id': user_id
    }
    
    click.echo("🔍 Searching for answer...")
    result = cli_app.api_request('POST', '/ask', data=data)
    
    if 'error' in result:
        click.echo(f"❌ Error: {result['error']}")
    else:
        click.echo("\n💡 Answer:")
        click.echo(f"   {result.get('answer', 'No answer available')}")
        
        if result.get('tutor_explanation'):
            click.echo("\n🎓 Tutor Explanation:")
            click.echo(f"   {result['tutor_explanation']}")
        
        sources = result.get('sources', [])
        if sources:
            click.echo("\n📚 Sources:")
            for i, source in enumerate(sources[:3], 1):
                click.echo(f"   {i}. {source.get('document', 'Unknown')} (relevance: {source.get('relevance_score', 0):.2f})")

@cli.command()
@click.option('--user-id', help='User ID to analyze (overrides config)')
@click.option('--time-range', default='30days', help='Time range for analysis (e.g., 30days, 12weeks)')
@click.option('--output', '-o', help='Output file path for saving results')
def analyze_progress(user_id, time_range, output):
    """Analyze learning progress and patterns"""
    current_user_id = user_id or cli_app.config['user_id']
    
    click.echo(f"📊 Analyzing learning progress for user: {current_user_id}")
    
    result = cli_app.api_request('GET', f'/analytics/progress/{current_user_id}', 
                                data={'time_range': time_range})
    
    if 'error' in result:
        click.echo(f"❌ Analysis failed: {result['error']}")
        return
    
    # Display results
    click.echo("\n📈 Learning Progress Summary:")
    click.echo(f"   Total questions asked: {result.get('total_questions', 0)}")
    click.echo(f"   Documents accessed: {result.get('unique_documents', 0)}")
    click.echo(f"   Average questions/day: {result.get('avg_questions_per_day', 0)}")
    click.echo(f"   Learning sessions: {result.get('learning_sessions', 0)}")
    click.echo(f"   Comprehension score: {result.get('comprehension_score', 0):.2f}")
    
    # Display main topics
    topics = result.get('main_topics', [])
    if topics:
        click.echo(f"\n🎯 Main topics studied: {', '.join(topics[:5])}")
    
    # Display trends
    complexity_trend = result.get('complexity_trend', 'unknown')
    if complexity_trend == 'increasing':
        click.echo("📈 Question complexity is increasing - great progress!")
    elif complexity_trend == 'stable':
        click.echo("📊 Question complexity is stable")
    
    if output:
        with open(output, 'w') as f:
            json.dump(result, f, indent=2)
        click.echo(f"💾 Results saved to: {output}")

@cli.command()
@click.option('--limit', default=100, help='Number of recent interactions to analyze')
@click.option('--output', '-o', help='Output file path')
def analyze_patterns(limit, output):
    """Analyze query patterns across all users"""
    click.echo("🔍 Analyzing query patterns...")
    
    result = cli_app.api_request('GET', '/analytics/patterns', 
                                data={'limit': limit})
    
    if 'error' in result:
        click.echo(f"❌ Analysis failed: {result['error']}")
        return
    
    click.echo("\n📊 Query Pattern Analysis:")
    
    # Question types
    question_types = result.get('question_types', {})
    if question_types:
        click.echo("\n❓ Question Types:")
        for q_type, count in question_types.items():
            click.echo(f"   {q_type}: {count}")
    
    # Popular topics
    topics = result.get('popular_topics', {})
    if topics:
        click.echo("\n🎯 Popular Topics:")
        for topic, count in list(topics.items())[:5]:
            click.echo(f"   {topic}: {count}")
    
    # Activity by hour
    hourly = result.get('hourly_activity', {})
    if hourly:
        peak_hour = max(hourly, key=hourly.get)
        click.echo(f"\n🕐 Peak activity hour: {peak_hour}:00 ({hourly[peak_hour]} questions)")
    
    if output:
        with open(output, 'w') as f:
            json.dump(result, f, indent=2)
        click.echo(f"💾 Results saved to: {output}")

@cli.command()
@click.option('--user-id', help='User ID (overrides config)')
@click.option('--output-dir', default='./dashboard', help='Output directory for dashboard files')
def generate_dashboard(user_id, output_dir):
    """Generate visualization dashboard"""
    current_user_id = user_id or cli_app.config['user_id']
    
    click.echo(f"📊 Generating dashboard for user: {current_user_id}")
    
    result = cli_app.api_request('GET', f'/visualizations/dashboard/{current_user_id}')
    
    if 'error' in result:
        click.echo(f"❌ Dashboard generation failed: {result['error']}")
        return
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Save dashboard data
    dashboard_file = f"{output_dir}/dashboard_{current_user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(dashboard_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    click.echo(f"✅ Dashboard generated successfully!")
    click.echo(f"💾 Saved to: {dashboard_file}")
    
    # Display summary
    summary = result.get('summary_stats', {})
    if summary:
        click.echo("\n📈 Summary Statistics:")
        for key, value in summary.items():
            click.echo(f"   {key.replace('_', ' ').title()}: {value}")

@cli.command()
@click.option('--message', '-m', help='Message to send to tutor')
@click.option('--user-id', help='User ID (overrides config)')
def chat_tutor(message, user_id):
    """Chat with the AI tutor"""
    current_user_id = user_id or cli_app.config['user_id']
    
    if not message:
        click.echo("🎓 Starting chat with AI tutor. Type 'quit' to exit.")
        while True:
            message = click.prompt('\n💬 You')
            if message.lower() in ['quit', 'exit', 'q']:
                break
            
            _chat_with_tutor(message, current_user_id)
    else:
        _chat_with_tutor(message, current_user_id)

def _chat_with_tutor(message, user_id):
    """Send message to tutor"""
    data = {
        'question': message,
        'context': ''
    }
    
    result = cli_app.api_request('POST', '/agents/tutor', data=data)
    
    if 'error' in result:
        click.echo(f"❌ Error: {result['error']}")
    else:
        click.echo(f"\n🎓 Tutor: {result.get('response', 'No response available')}")

@cli.command()
@click.option('--topic', '-t', help='Research topic')
def research_assistant(topic):
    """Get research suggestions from AI assistant"""
    if not topic:
        topic = click.prompt('🔬 Enter research topic')
    
    click.echo(f"🔍 Researching topic: {topic}")
    
    data = {'topic': topic}
    result = cli_app.api_request('POST', '/agents/researcher', data=data)
    
    if 'error' in result:
        click.echo(f"❌ Error: {result['error']}")
    else:
        suggestions = result.get('suggestions', 'No suggestions available')
        click.echo(f"\n📚 Research Suggestions:\n{suggestions}")

@cli.command()
@click.option('--user-id', help='User ID (overrides config)')
@click.option('--format', default='json', type=click.Choice(['json', 'csv']), help='Export format')
@click.option('--output', '-o', help='Output file path')
def export_data(user_id, format, output):
    """Export user data"""
    current_user_id = user_id or cli_app.config['user_id']
    
    click.echo(f"📤 Exporting data for user: {current_user_id}")
    
    # Get user interactions
    result = cli_app.api_request('GET', f'/analytics/progress/{current_user_id}', 
                                data={'time_range': '365days'})
    
    if 'error' in result:
        click.echo(f"❌ Export failed: {result['error']}")
        return
    
    if not output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output = f"user_data_{current_user_id}_{timestamp}.{format}"
    
    if format == 'json':
        with open(output, 'w') as f:
            json.dump(result, f, indent=2)
    elif format == 'csv':
        # Convert to DataFrame and save as CSV
        df = pd.DataFrame([result])  # Simplified for summary data
        df.to_csv(output, index=False)
    
    click.echo(f"✅ Data exported to: {output}")

@cli.command()
def status():
    """Check system status and configuration"""
    click.echo("🔧 System Status:")
    click.echo(f"   API URL: {cli_app.config['api_url']}")
    click.echo(f"   User ID: {cli_app.config['user_id']}")
    click.echo(f"   Config file: {CONFIG_FILE}")
    
    # Test API connection
    try:
        result = cli_app.api_request('GET', '/')
        if result:
            click.echo("✅ API connection: OK")
            click.echo(f"   Server version: {result.get('version', 'Unknown')}")
        else:
            click.echo("❌ API connection: Failed")
    except:
        click.echo("❌ API connection: Failed")

@cli.command()
@click.option('--output-dir', default='./sample_data', help='Directory to generate sample data')
def generate_sample_data(output_dir):
    """Generate sample datasets for testing"""
    click.echo("📊 Generating sample datasets...")
    
    try:
        from data.csv_generator import CSVDatasetGenerator
        
        generator = CSVDatasetGenerator()
        files = generator.generate_all_datasets(output_dir)
        
        click.echo("✅ Sample datasets generated successfully!")
        for dataset_type, file_path in files.items():
            click.echo(f"   {dataset_type}: {file_path}")
    
    except ImportError:
        click.echo("❌ Error: CSV generator module not found")
    except Exception as e:
        click.echo(f"❌ Error generating sample data: {e}")

@cli.command()
@click.option('--interaction-id', help='Interaction ID to rate')
@click.option('--rating', type=click.IntRange(1, 5), help='Rating (1-5 stars)')
@click.option('--comments', help='Additional comments')
def feedback(interaction_id, rating, comments):
    """Provide feedback on answers"""
    if not interaction_id:
        interaction_id = click.prompt('Enter interaction ID')
    
    if not rating:
        rating = click.prompt('Rate the answer (1-5 stars)', type=click.IntRange(1, 5))
    
    if not comments:
        comments = click.prompt('Comments (optional)', default='', show_default=False)
    
    data = {
        'interaction_id': interaction_id,
        'rating': rating,
        'comments': comments
    }
    
    result = cli_app.api_request('POST', '/feedback', data=data)
    
    if 'error' in result:
        click.echo(f"❌ Error submitting feedback: {result['error']}")
    else:
        click.echo("✅ Feedback submitted successfully!")

if __name__ == '__main__':
    cli()
