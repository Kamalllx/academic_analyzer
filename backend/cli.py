#!/usr/bin/env python3
"""
Enhanced RAG PDF Assistant CLI
Command-line interface for the enhanced RAG system with CrewAI and visualization capabilities.
"""

import click
import requests
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any
import webbrowser
from datetime import datetime
import tempfile

# Configuration
DEFAULT_BASE_URL = "http://localhost:5000"
CONFIG_FILE = os.path.expanduser("~/.rag_cli_config.json")

class RAGCLIConfig:
    """Configuration management for RAG CLI"""
    
    def __init__(self):
        self.base_url = DEFAULT_BASE_URL
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.base_url = config.get('base_url', DEFAULT_BASE_URL)
        except Exception as e:
            click.echo(f"⚠️ Error loading config: {e}", err=True)
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {'base_url': self.base_url}
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            click.echo(f"⚠️ Error saving config: {e}", err=True)

# Global config instance
config = RAGCLIConfig()

def make_request(method: str, endpoint: str, **kwargs) -> requests.Response:
    """Make HTTP request to the Flask app"""
    url = f"{config.base_url}{endpoint}"
    try:
        response = requests.request(method, url, timeout=300, **kwargs)
        return response
    except requests.exceptions.ConnectionError:
        click.echo(f"❌ Error: Cannot connect to RAG server at {config.base_url}")
        click.echo("💡 Make sure the Flask app is running: python app.py")
        sys.exit(1)
    except requests.exceptions.Timeout:
        click.echo("⏰ Error: Request timed out. The operation might still be processing.")
        sys.exit(1)

def print_response(response: requests.Response, success_message: str = ""):
    """Print formatted response"""
    try:
        data = response.json()
        
        if response.status_code == 200 and data.get('success', True):
            if success_message:
                click.echo(f"✅ {success_message}")
            
            # Pretty print the response
            if 'message' in data:
                click.echo(f"📝 {data['message']}")
            
        else:
            click.echo(f"❌ Error: {data.get('error', 'Unknown error')}")
            
    except json.JSONDecodeError:
        click.echo(f"❌ Error: Invalid response from server")
        click.echo(f"Response: {response.text[:200]}...")

def print_json(data: Any, title: str = ""):
    """Pretty print JSON data"""
    if title:
        click.echo(f"\n📊 {title}")
        click.echo("=" * (len(title) + 4))
    
    click.echo(json.dumps(data, indent=2, default=str))

@click.group()
@click.option('--base-url', default=None, help='Base URL for the RAG server')
@click.option('--config', 'config_cmd', is_flag=True, help='Show current configuration')
def cli(base_url: Optional[str], config_cmd: bool):
    """Enhanced RAG PDF Assistant CLI with CrewAI and Visualization
    
    A comprehensive command-line interface for interacting with your enhanced
    RAG PDF assistant that includes multi-agent processing and data visualization.
    """
    if base_url:
        config.base_url = base_url
        config.save_config()
        click.echo(f"🔧 Base URL updated to: {base_url}")
    
    if config_cmd:
        click.echo(f"🔧 Current configuration:")
        click.echo(f"   Base URL: {config.base_url}")
        click.echo(f"   Config file: {CONFIG_FILE}")
        return

@cli.command()
def health():
    """Check server health and available features"""
    click.echo("🔍 Checking server health...")
    
    response = make_request('GET', '/health')
    
    if response.status_code == 200:
        data = response.json()
        click.echo("✅ Server is healthy!")
        click.echo(f"📅 Timestamp: {data.get('timestamp', 'Unknown')}")
        click.echo(f"🔢 Version: {data.get('version', 'Unknown')}")
        
        features = data.get('features', [])
        if features:
            click.echo("🚀 Available features:")
            for feature in features:
                click.echo(f"   • {feature}")
        
        agents = data.get('agents_available', [])
        if agents:
            click.echo("🤖 Available agents:")
            for agent in agents:
                click.echo(f"   • {agent}")
        
        viz_types = data.get('visualization_types', [])
        if viz_types:
            click.echo("📊 Visualization types:")
            for viz_type in viz_types:
                click.echo(f"   • {viz_type}")
    else:
        print_response(response)

@cli.command()
def list():
    """List all processed documents"""
    click.echo("📚 Retrieving document list...")
    
    response = make_request('GET', '/documents')
    
    if response.status_code == 200:
        data = response.json()
        documents = data.get('documents', [])
        
        if not documents:
            click.echo("📭 No documents found. Process some PDFs first!")
            return
        
        click.echo(f"📋 Found {len(documents)} document(s):")
        click.echo()
        
        for i, doc in enumerate(documents, 1):
            click.echo(f"{i}. 📄 {doc.get('filename', 'Unknown')}")
            click.echo(f"   📅 Uploaded: {doc.get('upload_date', 'Unknown')}")
            click.echo(f"   📊 Pages: {doc.get('total_pages', 'Unknown')}")
            click.echo(f"   🔢 Version: {doc.get('processing_version', 'Unknown')}")
            
            # Enhanced metadata
            data_summary = doc.get('data_summary', {})
            if data_summary:
                click.echo(f"   📈 Numerical items: {data_summary.get('numerical_items', 0)}")
                click.echo(f"   📊 Has data: {'Yes' if data_summary.get('has_numerical_data') else 'No'}")
            
            toc = doc.get('table_of_contents', {})
            if toc:
                click.echo(f"   🏷️ Topics: {len(toc)} ({', '.join(list(toc.keys())[:3])}{'...' if len(toc) > 3 else ''})")
            click.echo()
    else:
        print_response(response)

@cli.command()
@click.argument('filepath', type=click.Path(exists=True, path_type=Path))
@click.option('--enhanced', '-e', is_flag=True, default=True, help='Use enhanced processing with data analysis')
def process(filepath: Path, enhanced: bool):
    """Process a PDF document
    
    FILEPATH: Path to the PDF file to process
    """
    if not filepath.suffix.lower() == '.pdf':
        click.echo("❌ Error: Only PDF files are supported")
        return
    
    processing_type = "enhanced" if enhanced else "standard"
    click.echo(f"📤 Uploading and processing: {filepath.name} ({processing_type})")
    
    # Show progress
    with click.progressbar(length=100, label='Processing') as bar:
        try:
            with open(filepath, 'rb') as f:
                files = {'file': (filepath.name, f, 'application/pdf')}
                
                # Simulate progress during upload
                bar.update(20)
                
                response = make_request('POST', '/process', files=files)
                
                # Simulate processing progress
                for i in range(20, 100, 10):
                    time.sleep(0.5)
                    bar.update(10)
                
                bar.update(100)
        
        except Exception as e:
            click.echo(f"\n❌ Error uploading file: {e}")
            return
    
    if response.status_code == 200:
        data = response.json()
        details = data.get('processing_details', {})
        
        click.echo("\n✅ Document processed successfully!")
        click.echo(f"📄 Filename: {data.get('filename')}")
        click.echo(f"📊 Pages processed: {details.get('pages_processed', 'Unknown')}")
        click.echo(f"🏷️ Topics extracted: {details.get('topics_extracted', 'Unknown')}")
        
        if enhanced and details.get('structured_data_extracted'):
            click.echo(f"📈 Numerical items found: {details.get('numerical_items', 0)}")
            click.echo("🎯 Document is ready for advanced analysis and visualization!")
        
    else:
        print_response(response)

@cli.command()
@click.option('--filename', '-f', required=True, help='Document filename to query')
@click.option('--question', '-q', prompt='Question', help='Question to ask about the document')
@click.option('--agentic', '-a', is_flag=True, help='Use CrewAI multi-agent processing')
@click.option('--visualize', '-v', is_flag=True, help='Include data visualization')
@click.option('--save', '-s', help='Save answer to file')
def ask(filename: str, question: str, agentic: bool, visualize: bool, save: Optional[str]):
    """Ask a question about a processed document
    
    Choose between traditional RAG or enhanced CrewAI multi-agent processing.
    """
    processing_mode = "🤖 CrewAI multi-agent" if agentic else "📚 Traditional RAG"
    click.echo(f"❓ Processing question with {processing_mode}...")
    click.echo(f"📄 Document: {filename}")
    click.echo(f"❓ Question: {question}")
    
    if visualize and not agentic:
        click.echo("⚠️ Visualization requires agentic mode. Enabling agentic processing...")
        agentic = True
    
    # Choose endpoint based on processing mode
    endpoint = '/ask/agentic' if agentic else '/ask'
    
    payload = {
        'filename': filename,
        'question': question
    }
    
    if agentic:
        payload['visualize'] = visualize
    
    with click.progressbar(length=100, label='Processing') as bar:
        response = make_request('POST', endpoint, json=payload)
        
        # Simulate processing time
        for i in range(0, 100, 20):
            time.sleep(1)
            bar.update(20)
    
    if response.status_code == 200:
        data = response.json()
        
        click.echo("\n" + "="*80)
        click.echo("📝 ANSWER")
        click.echo("="*80)
        
        if agentic:
            # Handle agentic response
            agentic_result = data.get('agentic_result', {})
            
            if 'crew_result' in agentic_result:
                click.echo(agentic_result['crew_result'])
            
            click.echo(f"\n🤖 Processing details:")
            click.echo(f"   • Tasks completed: {agentic_result.get('tasks_completed', 'Unknown')}")
            click.echo(f"   • Agents involved: {', '.join(agentic_result.get('agents_involved', []))}")
            
            # Handle visualization results
            if visualize and agentic_result.get('visualization'):
                viz_data = agentic_result['visualization']
                if 'visualizations' in viz_data:
                    click.echo(f"\n📊 Generated {len(viz_data['visualizations'])} visualization(s):")
                    for viz in viz_data['visualizations']:
                        click.echo(f"   • {viz.get('title', 'Unknown')}: {viz.get('path', 'No path')}")
        else:
            # Handle traditional response
            click.echo(data.get('answer', 'No answer provided'))
            
            references = data.get('references', [])
            if references:
                click.echo(f"\n📚 References: {', '.join(references)}")
        
        # Save answer if requested
        if save:
            try:
                answer_content = data.get('answer', str(data.get('agentic_result', {})))
                with open(save, 'w', encoding='utf-8') as f:
                    f.write(f"Question: {question}\n")
                    f.write(f"Document: {filename}\n")
                    f.write(f"Processing Mode: {processing_mode}\n")
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    f.write("\n" + "="*50 + "\n\n")
                    f.write(answer_content)
                
                click.echo(f"\n💾 Answer saved to: {save}")
            except Exception as e:
                click.echo(f"\n⚠️ Error saving answer: {e}")
    
    else:
        print_response(response)

@cli.command()
@click.option('--filename', '-f', required=True, help='Document filename')
@click.option('--type', '-t', 'viz_type', default='auto', 
              type=click.Choice(['auto', 'bar', 'line', 'scatter', 'heatmap', 'summary']),
              help='Type of visualization to create')
@click.option('--query', '-q', default='', help='Query to focus visualization')
@click.option('--open', '-o', 'open_viz', is_flag=True, help='Open visualization in browser')
@click.option('--save-to', '-s', help='Save visualization info to file')
def visualize(filename: str, viz_type: str, query: str, open_viz: bool, save_to: Optional[str]):
    """Create data visualizations from document content"""
    click.echo(f"📊 Creating {viz_type} visualization for: {filename}")
    
    if query:
        click.echo(f"🔍 Query focus: {query}")
    
    payload = {
        'filename': filename,
        'type': viz_type,
        'query': query
    }
    
    with click.progressbar(length=100, label='Generating visualization') as bar:
        response = make_request('POST', '/visualize', json=payload)
        
        for i in range(0, 100, 25):
            time.sleep(0.5)
            bar.update(25)
    
    if response.status_code == 200:
        data = response.json()
        viz_data = data.get('visualization', {})
        
        if 'error' in viz_data:
            click.echo(f"\n❌ Visualization error: {viz_data['error']}")
            return
        
        visualizations = viz_data.get('visualizations', [])
        
        if visualizations:
            click.echo(f"\n✅ Generated {len(visualizations)} visualization(s):")
            
            viz_info = []
            for i, viz in enumerate(visualizations, 1):
                click.echo(f"\n{i}. 📈 {viz.get('title', 'Untitled')}")
                click.echo(f"   Type: {viz.get('type', 'unknown')}")
                click.echo(f"   Description: {viz.get('description', 'No description')}")
                click.echo(f"   File: {viz.get('path', 'No path')}")
                
                viz_info.append({
                    'title': viz.get('title'),
                    'type': viz.get('type'),
                    'description': viz.get('description'),
                    'path': viz.get('path')
                })
                
                # Open in browser if requested
                if open_viz and viz.get('path'):
                    viz_url = f"{config.base_url}/visualizations/{os.path.basename(viz['path'])}"
                    try:
                        webbrowser.open(viz_url)
                        click.echo(f"   🌐 Opened in browser: {viz_url}")
                    except Exception as e:
                        click.echo(f"   ⚠️ Could not open in browser: {e}")
            
            # Show data summary
            data_summary = viz_data.get('data_summary', {})
            if data_summary:
                click.echo(f"\n📊 Data Summary:")
                click.echo(f"   • Numbers found: {data_summary.get('total_numbers', 0)}")
                click.echo(f"   • Years found: {data_summary.get('total_years', 0)}")
                click.echo(f"   • Categories found: {data_summary.get('total_categories', 0)}")
            
            # Save visualization info if requested
            if save_to:
                try:
                    save_data = {
                        'filename': filename,
                        'visualization_type': viz_type,
                        'query': query,
                        'timestamp': datetime.now().isoformat(),
                        'visualizations': viz_info,
                        'data_summary': data_summary
                    }
                    
                    with open(save_to, 'w', encoding='utf-8') as f:
                        json.dump(save_data, f, indent=2)
                    
                    click.echo(f"\n💾 Visualization info saved to: {save_to}")
                except Exception as e:
                    click.echo(f"\n⚠️ Error saving visualization info: {e}")
        else:
            click.echo("\n🤷 No visualizations could be generated from the document data.")
            click.echo("💡 Try processing documents with more quantitative content.")
    
    else:
        print_response(response)

@cli.command()
@click.option('--filename', '-f', required=True, help='Document filename')
@click.option('--type', '-t', 'data_type', default='tables',
              type=click.Choice(['tables', 'numbers', 'dates', 'entities']),
              help='Type of data to extract')
@click.option('--output', '-o', help='Output file for extracted data (JSON format)')
@click.option('--format', '-fmt', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'txt']),
              help='Output format')
def extract(filename: str, data_type: str, output: Optional[str], output_format: str):
    """Extract structured data from document"""
    click.echo(f"📈 Extracting {data_type} data from: {filename}")
    
    payload = {
        'filename': filename,
        'data_type': data_type
    }
    
    response = make_request('POST', '/extract-data', json=payload)
    
    if response.status_code == 200:
        data = response.json()
        extracted_data = data.get('extracted_data', {})
        
        if 'error' in extracted_data:
            click.echo(f"❌ Extraction error: {extracted_data['error']}")
            return
        
        # Display summary
        click.echo("✅ Data extraction completed!")
        click.echo(f"📊 Extraction method: {extracted_data.get('extraction_method', 'unknown')}")
        click.echo(f"📈 Total items found: {extracted_data.get('total_found', 0)}")
        
        # Show sample data
        data_key = {
            'tables': 'tables',
            'numbers': 'numerical_data', 
            'dates': 'dates',
            'entities': 'entities'
        }.get(data_type, data_type)
        
        items = extracted_data.get(data_key, [])
        
        if items:
            click.echo(f"\n📋 Sample {data_type} (showing first 5):")
            for i, item in enumerate(items[:5], 1):
                if isinstance(item, dict):
                    if data_type == 'entities':
                        click.echo(f"{i}. {item.get('entity', 'Unknown')} (Page {item.get('page', '?')}, Freq: {item.get('frequency', 0)})")
                    elif data_type == 'numbers':
                        click.echo(f"{i}. {item.get('value', 'Unknown')} {item.get('unit', '')} (Page {item.get('page', '?')})")
                    elif data_type == 'dates':
                        click.echo(f"{i}. {item.get('date', 'Unknown')} (Page {item.get('page', '?')})")
                    else:
                        click.echo(f"{i}. {item}")
                else:
                    click.echo(f"{i}. {item}")
        
        # Save to file if requested
        if output:
            try:
                if output_format == 'json':
                    with open(output, 'w', encoding='utf-8') as f:
                        json.dump(extracted_data, f, indent=2, default=str)
                
                elif output_format == 'csv' and items:
                    import pandas as pd
                    df = pd.DataFrame(items)
                    df.to_csv(output, index=False)
                
                elif output_format == 'txt':
                    with open(output, 'w', encoding='utf-8') as f:
                        f.write(f"Data Type: {data_type}\n")
                        f.write(f"Document: {filename}\n")
                        f.write(f"Extraction Date: {datetime.now().isoformat()}\n")
                        f.write(f"Total Items: {extracted_data.get('total_found', 0)}\n\n")
                        
                        for i, item in enumerate(items, 1):
                            f.write(f"{i}. {item}\n")
                
                click.echo(f"\n💾 Data saved to: {output}")
            except Exception as e:
                click.echo(f"\n⚠️ Error saving data: {e}")
        
    else:
        print_response(response)

@cli.command()
@click.option('--filename', '-f', required=True, help='Document filename')
@click.option('--type', '-t', 'analysis_type', default='comprehensive',
              type=click.Choice(['comprehensive', 'statistical', 'temporal']),
              help='Type of analysis to perform')
@click.option('--output', '-o', help='Output file for analysis results')
def analyze(filename: str, analysis_type: str, output: Optional[str]):
    """Perform comprehensive document analysis using magnetic approach"""
    click.echo(f"🔬 Performing {analysis_type} analysis for: {filename}")
    click.echo("🧲 Using magnetic approach for data clustering...")
    
    payload = {
        'filename': filename,
        'analysis_type': analysis_type
    }
    
    with click.progressbar(length=100, label='Analyzing') as bar:
        response = make_request('POST', '/analyze', json=payload)
        
        for i in range(0, 100, 20):
            time.sleep(0.8)
            bar.update(20)
    
    if response.status_code == 200:
        data = response.json()
        analysis_result = data.get('analysis_result', {})
        
        if 'error' in analysis_result:
            click.echo(f"\n❌ Analysis error: {analysis_result['error']}")
            return
        
        click.echo("\n✅ Analysis completed!")
        click.echo(f"📊 Analysis type: {analysis_result.get('analysis_type', 'unknown')}")
        
        # Display results based on analysis type
        if analysis_type == 'comprehensive':
            click.echo("\n🔍 Comprehensive Analysis Results:")
            
            insights = analysis_result.get('insights', {})
            if insights:
                click.echo(f"   • Total concepts: {insights.get('total_concepts', 0)}")
                click.echo(f"   • Data richness score: {insights.get('data_richness_score', 0):.2f}")
                click.echo(f"   • Content diversity: {insights.get('content_diversity', 0):.2f}")
            
            concept_clusters = analysis_result.get('concept_clusters', {})
            if concept_clusters:
                click.echo(f"\n🏷️ Top concept clusters:")
                for i, (concept, data) in enumerate(list(concept_clusters.items())[:5], 1):
                    click.echo(f"   {i}. {concept.title()}: {data.get('frequency', 0)} occurrences")
        
        elif analysis_type == 'statistical':
            click.echo("\n📊 Statistical Analysis Results:")
            
            results = analysis_result.get('results', {})
            desc_stats = results.get('descriptive_stats', {})
            if desc_stats:
                click.echo(f"   • Count: {desc_stats.get('count', 0)}")
                click.echo(f"   • Mean: {desc_stats.get('mean', 0):.2f}")
                click.echo(f"   • Median: {desc_stats.get('median', 0):.2f}")
                click.echo(f"   • Std Dev: {desc_stats.get('std', 0):.2f}")
            
            data_quality = analysis_result.get('data_quality', {})
            if data_quality:
                click.echo(f"\n🎯 Data Quality:")
                click.echo(f"   • Analysis confidence: {data_quality.get('analysis_confidence', 'unknown')}")
        
        elif analysis_type == 'temporal':
            click.echo("\n📅 Temporal Analysis Results:")
            
            temporal_stats = analysis_result.get('temporal_statistics', {})
            if temporal_stats:
                time_span = temporal_stats.get('time_span', {})
                click.echo(f"   • Time span: {time_span.get('start', '?')} - {time_span.get('end', '?')}")
                click.echo(f"   • Duration: {time_span.get('duration', 0)} years")
                click.echo(f"   • Total years mentioned: {temporal_stats.get('total_years', 0)}")
        
        # Save results if requested
        if output:
            try:
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(analysis_result, f, indent=2, default=str)
                click.echo(f"\n💾 Analysis results saved to: {output}")
            except Exception as e:
                click.echo(f"\n⚠️ Error saving results: {e}")
    
    else:
        print_response(response)

@cli.command()
@click.option('--filename', '-f', required=True, help='Document filename')
@click.option('--open', '-o', 'open_screenshots', is_flag=True, help='Open screenshots directory')
def screenshots(filename: str, open_screenshots: bool):
    """View available screenshots for a document"""
    click.echo(f"📸 Retrieving screenshots for: {filename}")
    
    response = make_request('GET', f'/document/{filename}/screenshots')
    
    if response.status_code == 200:
        data = response.json()
        screenshots_list = data.get('screenshots', [])
        
        if screenshots_list:
            click.echo(f"✅ Found {len(screenshots_list)} screenshot(s):")
            
            for screenshot in screenshots_list:
                page_num = screenshot.get('page_number')
                filename_ss = screenshot.get('filename')
                click.echo(f"   📄 Page {page_num}: {filename_ss}")
            
            if open_screenshots:
                # Open screenshots directory URL
                screenshots_url = f"{config.base_url}/context/"
                click.echo(f"\n🌐 Screenshots available at: {screenshots_url}")
                try:
                    webbrowser.open(screenshots_url)
                    click.echo("🌐 Opened screenshots in browser")
                except Exception as e:
                    click.echo(f"⚠️ Could not open browser: {e}")
        else:
            click.echo("📭 No screenshots available for this document.")
    
    else:
        print_response(response)

@cli.command()
@click.option('--url', prompt='Server URL', default=DEFAULT_BASE_URL, 
              help='Base URL for the RAG server')
def configure(url: str):
    """Configure CLI settings"""
    config.base_url = url.rstrip('/')
    config.save_config()
    
    click.echo(f"✅ Configuration updated!")
    click.echo(f"🔧 Base URL: {config.base_url}")
    click.echo(f"📁 Config file: {CONFIG_FILE}")
    
    # Test connection
    try:
        response = make_request('GET', '/health')
        if response.status_code == 200:
            click.echo("✅ Connection test successful!")
        else:
            click.echo("⚠️ Connection test failed. Check if the server is running.")
    except:
        click.echo("⚠️ Cannot connect to server. Make sure it's running.")

@cli.command()
def status():
    """Show detailed system status and statistics"""
    click.echo("📊 Retrieving system status...")
    
    # Get health info
    health_response = make_request('GET', '/health')
    
    if health_response.status_code != 200:
        click.echo("❌ Cannot retrieve system status")
        return
    
    health_data = health_response.json()
    
    # Get documents info
    docs_response = make_request('GET', '/documents')
    docs_data = docs_response.json() if docs_response.status_code == 200 else {}
    documents = docs_data.get('documents', [])
    
    click.echo("\n🎯 SYSTEM STATUS")
    click.echo("=" * 50)
    
    # Server info
    click.echo(f"🔧 Server: {config.base_url}")
    click.echo(f"📅 Server time: {health_data.get('timestamp', 'Unknown')}")
    click.echo(f"🔢 Version: {health_data.get('version', 'Unknown')}")
    
    # Features
    features = health_data.get('features', [])
    click.echo(f"🚀 Features: {', '.join(features)}")
    
    # Documents statistics
    click.echo(f"\n📚 Documents: {len(documents)}")
    
    if documents:
        enhanced_docs = sum(1 for doc in documents if doc.get('processing_version', '').startswith('2.0'))
        total_pages = sum(doc.get('total_pages', 0) for doc in documents)
        docs_with_data = sum(1 for doc in documents if doc.get('data_summary', {}).get('has_numerical_data'))
        
        click.echo(f"   • Enhanced processing: {enhanced_docs}/{len(documents)}")
        click.echo(f"   • Total pages: {total_pages}")
        click.echo(f"   • Documents with data: {docs_with_data}")
    
    # Agents info
    agents = health_data.get('agents_available', [])
    if agents:
        click.echo(f"\n🤖 Available agents: {len(agents)}")
        for agent in agents:
            click.echo(f"   • {agent}")
    
    # Visualization types
    viz_types = health_data.get('visualization_types', [])
    if viz_types:
        click.echo(f"\n📊 Visualization types: {', '.join(viz_types)}")

@cli.command()
@click.option('--filename', '-f', help='Filter by document filename')
@click.option('--count', '-c', default=10, help='Number of recent operations to show')
def recent(filename: Optional[str], count: int):
    """Show recent operations and activity"""
    click.echo(f"📋 Showing recent activity (last {count} operations)...")
    
    if filename:
        click.echo(f"🔍 Filtered by document: {filename}")
    
    # This would require implementing activity logging in the backend
    # For now, show a placeholder message
    click.echo("\n⚠️ Activity logging not yet implemented in backend.")
    click.echo("💡 This feature requires additional backend implementation.")

@cli.command()
def interactive():
    """Start interactive mode for exploratory analysis"""
    click.echo("🚀 Starting interactive mode...")
    click.echo("💡 Type 'help' for available commands, 'exit' to quit")
    
    while True:
        try:
            command = input("\n📚 RAG> ").strip()
            
            if command.lower() in ['exit', 'quit', 'q']:
                click.echo("👋 Goodbye!")
                break
            
            elif command.lower() in ['help', 'h']:
                click.echo("\n📖 Interactive Commands:")
                click.echo("  list - List documents")
                click.echo("  ask <filename> - Ask a question about a document")
                click.echo("  viz <filename> - Create visualization")
                click.echo("  analyze <filename> - Perform analysis")
                click.echo("  health - Check system health")
                click.echo("  exit - Exit interactive mode")
            
            elif command.lower() == 'list':
                # Call the list command
                from click.testing import CliRunner
                runner = CliRunner()
                result = runner.invoke(list)
                click.echo(result.output)
            
            elif command.lower() == 'health':
                from click.testing import CliRunner
                runner = CliRunner()
                result = runner.invoke(health)
                click.echo(result.output)
            
            elif command.startswith('ask '):
                parts = command.split(' ', 1)
                if len(parts) > 1:
                    filename = parts[1]
                    question = input(f"❓ Question for {filename}: ")
                    
                    # Simple ask implementation
                    payload = {'filename': filename, 'question': question}
                    response = make_request('POST', '/ask', json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        click.echo(f"\n📝 Answer: {data.get('answer', 'No answer')}")
                    else:
                        click.echo("❌ Error processing question")
                else:
                    click.echo("❌ Please specify a filename: ask <filename>")
            
            elif command.startswith('viz '):
                parts = command.split(' ', 1)
                if len(parts) > 1:
                    filename = parts[1]
                    viz_type = input("📊 Visualization type (auto/bar/line/scatter/heatmap): ") or "auto"
                    
                    payload = {'filename': filename, 'type': viz_type}
                    response = make_request('POST', '/visualize', json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        viz_data = data.get('visualization', {})
                        visualizations = viz_data.get('visualizations', [])
                        
                        if visualizations:
                            click.echo(f"✅ Generated {len(visualizations)} visualization(s)")
                            for viz in visualizations:
                                click.echo(f"   📈 {viz.get('title', 'Unknown')}")
                        else:
                            click.echo("📊 No visualizations generated")
                    else:
                        click.echo("❌ Error creating visualization")
                else:
                    click.echo("❌ Please specify a filename: viz <filename>")
            
            elif command.startswith('analyze '):
                parts = command.split(' ', 1)
                if len(parts) > 1:
                    filename = parts[1]
                    analysis_type = input("🔬 Analysis type (comprehensive/statistical/temporal): ") or "comprehensive"
                    
                    payload = {'filename': filename, 'analysis_type': analysis_type}
                    response = make_request('POST', '/analyze', json=payload)
                    
                    if response.status_code == 200:
                        click.echo("✅ Analysis completed successfully")
                    else:
                        click.echo("❌ Error performing analysis")
                else:
                    click.echo("❌ Please specify a filename: analyze <filename>")
            
            elif command.strip() == '':
                continue
            
            else:
                click.echo(f"❌ Unknown command: {command}")
                click.echo("💡 Type 'help' for available commands")
        
        except KeyboardInterrupt:
            click.echo("\n👋 Goodbye!")
            break
        except EOFError:
            click.echo("\n👋 Goodbye!")
            break

if __name__ == '__main__':
    cli()
