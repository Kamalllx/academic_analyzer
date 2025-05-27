import os
import tempfile
import uuid
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json
import re
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
from PyPDF2 import PdfReader
import fitz  # PyMuPDF for screenshots
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import pymongo
import traceback
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# CrewAI imports
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

class EnhancedRAGFlaskApp:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app, origins=['*'])
        
        # Configuration
        self.app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
        self.app.config['UPLOAD_FOLDER'] = 'uploads'
        
        # Create necessary folders
        os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs('stored_pdfs', exist_ok=True)
        os.makedirs('context', exist_ok=True)
        os.makedirs('visualizations', exist_ok=True)  # For storing generated charts
        
        # Initialize components
        self._initialize_components()
        self._initialize_crewai_agents()
        
        # Register routes
        self._register_routes()

    def _initialize_components(self):
        """Initialize embeddings, LLMs, and MongoDB connection"""
        try:
            print("🔧 Initializing components...")
            
            # Initialize embeddings
            self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
            print("✅ Embeddings model loaded")
            
            # Initialize LLMs
            self.llm = ChatGroq(
                model_name="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.2,
                groq_api_key=os.getenv("GROQ_API_KEY")
            )
            
            # CrewAI compatible LLM
            self.crew_llm = ChatOpenAI(
                openai_api_base="https://api.groq.com/openai/v1",
                openai_api_key=os.getenv("GROQ_API_KEY"),
                model_name="llama3-8b-8192",
                temperature=0.1
            )
            
            print("✅ LLMs initialized")
            
            # MongoDB setup
            mongo_client = pymongo.MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
            self.db = mongo_client["rag_database"]
            self.collection = self.db["documents"]
            self.db.list_collection_names()
            print("✅ Connected to MongoDB")
            
        except Exception as e:
            print(f"❌ Error initializing components: {e}")
            raise

    def _initialize_crewai_agents(self):
        """Initialize CrewAI agents for agentic processing"""
        try:
            print("🤖 Initializing CrewAI agents...")
            
            # Document Research Expert Agent
            self.research_agent = Agent(
                role='Document Research Expert',
                goal='Extract and analyze relevant information from PDF documents with high accuracy',
                backstory='''You are an expert document analyst with years of experience in 
                extracting meaningful insights from technical and academic documents. You excel 
                at identifying key concepts, relationships, and important details.''',
                verbose=True,
                allow_delegation=False,
                llm=self.crew_llm
            )
            
            # Data Analysis Agent
            self.data_analyst = Agent(
                role='Data Analysis Specialist',
                goal='Identify patterns, trends, and quantitative insights from document content',
                backstory='''You are a skilled data analyst who can extract numerical data, 
                identify trends, and perform statistical analysis on document content. You 
                excel at finding data-driven insights and patterns.''',
                verbose=True,
                allow_delegation=False,
                llm=self.crew_llm
            )
            
            # Visualization Agent
            self.visualization_agent = Agent(
                role='Data Visualization Expert',
                goal='Create meaningful and insightful visualizations from extracted data',
                backstory='''You are a data visualization expert who creates compelling 
                charts, graphs, and visual representations of data. You understand which 
                visualization types best represent different kinds of data and insights.''',
                verbose=True,
                allow_delegation=False,
                llm=self.crew_llm
            )
            
            # Answer Generation Agent
            self.answer_agent = Agent(
                role='Answer Generation Specialist',
                goal='Synthesize research findings into comprehensive, well-structured answers',
                backstory='''You are an expert communicator who excels at synthesizing 
                complex information into clear, comprehensive answers. You ensure accuracy 
                while maintaining readability and proper citations.''',
                verbose=True,
                allow_delegation=False,
                llm=self.crew_llm
            )
            
            print("✅ CrewAI agents initialized")
            
        except Exception as e:
            print(f"❌ Error initializing CrewAI agents: {e}")
            raise

    @tool
    def extract_document_data(self, filename: str) -> str:
        """Tool to extract document data for agents"""
        try:
            doc_data = self.collection.find_one({"filename": filename})
            if not doc_data:
                return f"Document {filename} not found"
            
            # Return structured document information
            info = {
                "filename": filename,
                "total_pages": doc_data.get("total_pages", 0),
                "table_of_contents": doc_data.get("table_of_contents", {}),
                "pages_sample": doc_data.get("pages_data", [])[:3]  # First 3 pages as sample
            }
            return json.dumps(info, indent=2)
        except Exception as e:
            return f"Error extracting document data: {str(e)}"

    @tool  
    def search_document_content(self, filename: str, query: str) -> str:
        """Tool to search document content using vector similarity"""
        try:
            doc_data = self.collection.find_one({"filename": filename})
            if not doc_data:
                return f"Document {filename} not found"
            
            # Recreate vectorstore
            vectorstore = self._recreate_vectorstore(doc_data)
            
            # Perform similarity search
            docs = vectorstore.similarity_search(query, k=5)
            
            results = []
            for doc in docs:
                page_num = doc.metadata.get('page_number', 'Unknown')
                content = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
                results.append(f"Page {page_num}: {content}")
            
            return "\n\n".join(results)
            
        except Exception as e:
            return f"Error searching document: {str(e)}"

    def _register_routes(self):
        """Register all Flask routes"""
        
        # Enhanced health check
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint with enhanced features"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0_enhanced',
                'features': ['basic_rag', 'crewai_agents', 'data_visualization', 'magnetic_approach'],
                'agents_available': ['research_expert', 'data_analyst', 'visualization_expert', 'answer_generator'],
                'visualization_types': ['auto', 'bar', 'line', 'scatter', 'heatmap', 'summary']
            })

        @self.app.route('/documents', methods=['GET'])
        def list_documents():
            """Get list of processed documents with enhanced metadata"""
            try:
                documents = list(self.collection.find({}, {
                    'filename': 1,
                    'upload_date': 1,
                    'total_pages': 1,
                    'table_of_contents': 1,
                    'structured_data': 1,
                    'processing_version': 1,
                    '_id': 0
                }))
                
                # Add summary statistics
                for doc in documents:
                    structured_data = doc.get('structured_data', {})
                    doc['data_summary'] = {
                        'has_numerical_data': bool(structured_data.get('data', {}).get('numerical')),
                        'numerical_items': len(structured_data.get('data', {}).get('numerical', [])),
                        'temporal_items': len(structured_data.get('data', {}).get('temporal', [])),
                        'categorical_items': len(structured_data.get('data', {}).get('categorical', []))
                    }
                
                return jsonify({
                    'success': True,
                    'documents': documents,
                    'total': len(documents)
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/process', methods=['POST'])
        def process_document():
            """Process a PDF document with enhanced analysis"""
            try:
                if 'file' not in request.files:
                    return jsonify({'success': False, 'error': 'No file provided'}), 400

                file = request.files['file']
                if file.filename == '' or not file.filename.lower().endswith('.pdf'):
                    return jsonify({'success': False, 'error': 'Invalid PDF file'}), 400

                # Save uploaded file
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                filepath = os.path.join(self.app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                
                print(f"📁 File saved: {filepath}")
                
                # Process with enhanced analysis
                result = self._process_pdf_pipeline_enhanced(filepath, filename)
                
                # Clean up uploaded file
                os.remove(filepath)
                
                return jsonify({
                    'success': True,
                    'message': 'Document processed successfully with enhanced analysis',
                    'filename': filename,
                    'processing_details': result
                })
                
            except Exception as e:
                print(f"❌ Error processing document: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        # Enhanced agentic query endpoint
        @self.app.route('/ask/agentic', methods=['POST'])
        def ask_agentic_question():
            """Ask a question using CrewAI multi-agent approach"""
            try:
                data = request.get_json()
                if not data or 'question' not in data or 'filename' not in data:
                    return jsonify({
                        'success': False,
                        'error': 'Question and filename are required'
                    }), 400

                question = data['question']
                filename = data['filename']
                include_visualization = data.get('visualize', False)
                
                print(f"🤖 Processing agentic question: {question}")
                print(f"📄 Document: {filename}")
                
                # Execute agentic workflow
                result = self._execute_agentic_workflow(filename, question, include_visualization)
                
                return jsonify({
                    'success': True,
                    'question': question,
                    'agentic_result': result,
                    'processing_type': 'multi_agent_crewai'
                })
                
            except Exception as e:
                print(f"❌ Error in agentic processing: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        # Data visualization endpoint
        @self.app.route('/visualize', methods=['POST'])
        def create_visualization():
            """Create data visualizations from document content"""
            try:
                data = request.get_json()
                filename = data.get('filename')
                viz_type = data.get('type', 'auto')  # auto, bar, line, scatter, heatmap
                query = data.get('query', '')
                
                if not filename:
                    return jsonify({'success': False, 'error': 'Filename required'}), 400
                
                print(f"📊 Creating visualization for {filename}")
                
                # Extract and visualize data
                result = self._create_dynamic_visualization(filename, viz_type, query)
                
                return jsonify({
                    'success': True,
                    'visualization': result,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"❌ Error creating visualization: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        # Data extraction endpoint
        @self.app.route('/extract-data', methods=['POST'])
        def extract_data():
            """Extract structured data from document for analysis"""
            try:
                data = request.get_json()
                filename = data.get('filename')
                data_type = data.get('data_type', 'tables')  # tables, numbers, dates, entities
                
                if not filename:
                    return jsonify({'success': False, 'error': 'Filename required'}), 400
                
                print(f"📈 Extracting {data_type} data from {filename}")
                
                # Extract structured data
                result = self._extract_structured_data(filename, data_type)
                
                return jsonify({
                    'success': True,
                    'extracted_data': result,
                    'data_type': data_type
                })
                
            except Exception as e:
                print(f"❌ Error extracting data: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        # Enhanced analysis endpoint
        @self.app.route('/analyze', methods=['POST'])
        def comprehensive_analysis():
            """Perform comprehensive document analysis using magnetic approach"""
            try:
                data = request.get_json()
                filename = data.get('filename')
                analysis_type = data.get('analysis_type', 'comprehensive')  # comprehensive, statistical, temporal
                
                if not filename:
                    return jsonify({'success': False, 'error': 'Filename required'}), 400
                
                print(f"🔬 Performing {analysis_type} analysis for {filename}")
                
                # Execute magnetic approach analysis
                result = self._magnetic_approach_analysis(filename, analysis_type)
                
                return jsonify({
                    'success': True,
                    'analysis_result': result,
                    'analysis_type': analysis_type,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"❌ Error in analysis: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        # Preserve original endpoints
        @self.app.route('/ask', methods=['POST'])
        def ask_question():
            """Original question answering endpoint"""
            try:
                data = request.get_json()
                if not data or 'question' not in data or 'filename' not in data:
                    return jsonify({
                        'success': False,
                        'error': 'Question and filename are required'
                    }), 400

                question = data['question']
                filename = data['filename']
                
                result = self._answer_question_pipeline(filename, question)
                
                return jsonify({
                    'success': True,
                    'question': question,
                    'answer': result['answer'],
                    'context': result['context'],
                    'references': result['references'],
                    'processing_type': 'traditional_rag'
                })
                
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/document/<filename>/screenshots', methods=['GET'])
        def get_latest_screenshots(filename):
            """Get screenshots for a document"""
            try:
                context_dir = "context"
                if not os.path.exists(context_dir):
                    return jsonify({'success': False, 'error': 'No screenshots available'}), 404

                screenshots = []
                for file in os.listdir(context_dir):
                    if file.endswith('.png') and file.startswith('page_'):
                        try:
                            page_num = int(file.split('_')[1].split('.')[0])
                            screenshots.append({
                                'filename': file,
                                'page_number': page_num,
                                'path': os.path.join(context_dir, file)
                            })
                        except (ValueError, IndexError):
                            continue

                if not screenshots:
                    return jsonify({'success': False, 'error': 'No screenshots available'}), 404

                screenshots.sort(key=lambda x: x['page_number'])
                
                return jsonify({
                    'success': True,
                    'screenshots': screenshots,
                    'total_screenshots': len(screenshots)
                })
                
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/context/<filename>', methods=['GET'])
        def serve_context_file(filename):
            """Serve files from the context directory"""
            try:
                context_dir = "context"
                return send_file(os.path.join(context_dir, filename))
            except Exception as e:
                return jsonify({'success': False, 'error': f"File not found: {filename}"}), 404

        @self.app.route('/visualizations/<filename>', methods=['GET'])
        def serve_visualization_file(filename):
            """Serve visualization files"""
            try:
                viz_dir = "visualizations"
                return send_file(os.path.join(viz_dir, filename))
            except Exception as e:
                return jsonify({'success': False, 'error': f"Visualization not found: {filename}"}), 404

    def _execute_agentic_workflow(self, filename: str, question: str, include_visualization: bool = False) -> Dict[str, Any]:
        """Execute CrewAI multi-agent workflow for comprehensive analysis"""
        try:
            print("🤖 Starting CrewAI multi-agent workflow...")
            
            # Create tasks for agents
            research_task = Task(
                description=f"""Research and analyze the document '{filename}' to find information 
                relevant to this question: '{question}'. Extract key facts, concepts, and supporting evidence.
                Use the available tools to search document content effectively.""",
                agent=self.research_agent,
                expected_output="Detailed research findings with key facts and evidence",
                tools=[self.extract_document_data, self.search_document_content]
            )
            
            data_analysis_task = Task(
                description=f"""Analyze the research findings for quantitative data, trends, patterns, 
                and statistical insights related to: '{question}'. Identify any numerical data, 
                percentages, comparisons, or measurable elements.""",
                agent=self.data_analyst,
                expected_output="Data analysis with identified patterns, trends, and quantitative insights",
                context=[research_task]
            )
            
            tasks = [research_task, data_analysis_task]
            agents = [self.research_agent, self.data_analyst]
            
            # Add visualization task if requested
            if include_visualization:
                viz_task = Task(
                    description=f"""Based on the research and data analysis, determine what 
                    visualizations would best represent the findings. Suggest chart types, 
                    data points to visualize, and visual insights for: '{question}'""",
                    agent=self.visualization_agent,
                    expected_output="Visualization recommendations and specifications",
                    context=[research_task, data_analysis_task]
                )
                tasks.append(viz_task)
                agents.append(self.visualization_agent)
            
            # Final answer synthesis task
            answer_task = Task(
                description=f"""Synthesize all findings into a comprehensive, well-structured 
                answer to: '{question}'. Include proper citations, organize information logically, 
                and ensure accuracy while maintaining readability.""",
                agent=self.answer_agent,
                expected_output="Comprehensive, well-structured final answer with proper citations",
                context=tasks
            )
            
            tasks.append(answer_task)
            agents.append(self.answer_agent)
            
            # Create and execute crew
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            
            # Execute the crew workflow
            result = crew.kickoff()
            
            # Generate visualization if requested
            visualization_result = None
            if include_visualization:
                try:
                    visualization_result = self._create_dynamic_visualization(filename, 'auto', question)
                except Exception as viz_error:
                    print(f"⚠️ Visualization generation failed: {viz_error}")
            
            return {
                'crew_result': str(result),
                'tasks_completed': len(tasks),
                'agents_involved': [agent.role for agent in agents],
                'visualization': visualization_result,
                'processing_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error in agentic workflow: {e}")
            return {
                'error': str(e),
                'fallback_result': 'Agentic processing failed, falling back to traditional RAG'
            }

    def _create_dynamic_visualization(self, filename: str, viz_type: str, query: str = '') -> Dict[str, Any]:
        """Create dynamic visualizations from document data"""
        try:
            print(f"📊 Creating dynamic visualization: {viz_type}")
            
            # Get document data
            doc_data = self.collection.find_one({"filename": filename})
            if not doc_data:
                raise Exception(f"Document not found: {filename}")
            
            # Extract data for visualization
            extracted_data = self._extract_visualization_data(doc_data, query)
            
            if not extracted_data or not extracted_data.get('data'):
                return {
                    'message': 'No quantitative data found for visualization',
                    'suggested_analysis': 'Consider text-based analysis instead'
                }
            
            # Create visualizations based on data type
            viz_results = []
            
            # Generate different visualization types
            if viz_type == 'auto' or viz_type == 'summary':
                # Create summary dashboard
                viz_results.extend(self._create_summary_visualizations(extracted_data, filename))
            
            elif viz_type == 'bar':
                viz_results.append(self._create_bar_chart(extracted_data, filename))
            
            elif viz_type == 'line':
                viz_results.append(self._create_line_chart(extracted_data, filename))
            
            elif viz_type == 'scatter':
                viz_results.append(self._create_scatter_plot(extracted_data, filename))
            
            elif viz_type == 'heatmap':
                viz_results.append(self._create_heatmap(extracted_data, filename))
            
            return {
                'visualizations': viz_results,
                'data_summary': extracted_data.get('summary', {}),
                'generation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error creating visualization: {e}")
            return {'error': str(e)}

    def _magnetic_approach_analysis(self, filename: str, analysis_type: str) -> Dict[str, Any]:
        """Implement magnetic approach for document analysis"""
        try:
            print(f"🧲 Executing magnetic approach analysis: {analysis_type}")
            
            doc_data = self.collection.find_one({"filename": filename})
            if not doc_data:
                raise Exception(f"Document not found: {filename}")
            
            pages_data = doc_data.get('pages_data', [])
            structured_data = doc_data.get('structured_data', {})
            
            # Magnetic approach: Attract related data points and cluster insights
            if analysis_type == 'comprehensive':
                return self._comprehensive_magnetic_analysis(pages_data, structured_data)
            elif analysis_type == 'statistical':
                return self._statistical_magnetic_analysis(structured_data)
            elif analysis_type == 'temporal':
                return self._temporal_magnetic_analysis(structured_data)
            else:
                return {'error': f'Unknown analysis type: {analysis_type}'}
                
        except Exception as e:
            return {'error': str(e)}

    def _comprehensive_magnetic_analysis(self, pages_data: List[Dict], structured_data: Dict) -> Dict[str, Any]:
        """Comprehensive magnetic analysis clustering related concepts"""
        try:
            # Extract key concepts and cluster them
            concept_clusters = {}
            statistical_summary = {}
            
            # Analyze numerical patterns
            numerical_data = structured_data.get('data', {}).get('numerical', [])
            if numerical_data:
                values = [item['value'] for item in numerical_data]
                statistical_summary['numerical'] = {
                    'count': len(values),
                    'mean': np.mean(values),
                    'median': np.median(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values)
                }
            
            # Analyze topic frequency across pages
            all_topics = []
            for page in pages_data:
                all_topics.extend(page.get('topics', []))
            
            if all_topics:
                topic_freq = pd.Series(all_topics).value_counts().to_dict()
                statistical_summary['topics'] = {
                    'total_topics': len(set(all_topics)),
                    'most_frequent': dict(list(topic_freq.items())[:5]),
                    'topic_distribution': topic_freq
                }
            
            # Magnetic clustering: Group related concepts
            for page in pages_data:
                topics = page.get('topics', [])
                keywords = page.get('keywords', [])
                
                # Create concept clusters based on semantic similarity
                for topic in topics:
                    if topic not in concept_clusters:
                        concept_clusters[topic] = {
                            'pages': [],
                            'related_keywords': [],
                            'frequency': 0
                        }
                    
                    concept_clusters[topic]['pages'].append(page.get('page_number'))
                    concept_clusters[topic]['related_keywords'].extend(keywords)
                    concept_clusters[topic]['frequency'] += 1
            
            return {
                'analysis_type': 'comprehensive_magnetic',
                'concept_clusters': concept_clusters,
                'statistical_summary': statistical_summary,
                'insights': {
                    'total_concepts': len(concept_clusters),
                    'data_richness_score': len(numerical_data) / len(pages_data) if pages_data else 0,
                    'content_diversity': len(set(all_topics)) / len(all_topics) if all_topics else 0
                }
            }
            
        except Exception as e:
            return {'error': str(e)}

    def _statistical_magnetic_analysis(self, structured_data: Dict) -> Dict[str, Any]:
        """Statistical magnetic analysis focusing on quantitative patterns"""
        try:
            numerical_data = structured_data.get('data', {}).get('numerical', [])
            temporal_data = structured_data.get('data', {}).get('temporal', [])
            
            analysis_results = {}
            
            if numerical_data:
                df_num = pd.DataFrame(numerical_data)
                
                # Statistical analysis
                values = df_num['value'].astype(float)
                analysis_results['descriptive_stats'] = {
                    'count': len(values),
                    'mean': float(values.mean()),
                    'median': float(values.median()),
                    'std': float(values.std()),
                    'skewness': float(values.skew()),
                    'kurtosis': float(values.kurtosis())
                }
                
                # Distribution analysis
                analysis_results['distribution'] = {
                    'quartiles': {
                        'Q1': float(values.quantile(0.25)),
                        'Q2': float(values.quantile(0.50)),
                        'Q3': float(values.quantile(0.75))
                    },
                    'outliers': self._detect_outliers(values.tolist())
                }
                
                # Page-based analysis
                page_stats = df_num.groupby('page')['value'].agg(['count', 'mean', 'sum']).to_dict()
                analysis_results['page_statistics'] = page_stats
            
            if temporal_data:
                df_temp = pd.DataFrame(temporal_data)
                year_counts = df_temp['year'].value_counts().to_dict()
                analysis_results['temporal_patterns'] = {
                    'year_distribution': year_counts,
                    'time_span': {
                        'earliest': min(df_temp['year']) if not df_temp.empty else None,
                        'latest': max(df_temp['year']) if not df_temp.empty else None
                    }
                }
            
            return {
                'analysis_type': 'statistical_magnetic',
                'results': analysis_results,
                'data_quality': {
                    'numerical_completeness': len(numerical_data) > 0,
                    'temporal_completeness': len(temporal_data) > 0,
                    'analysis_confidence': 'high' if len(numerical_data) > 10 else 'medium' if len(numerical_data) > 5 else 'low'
                }
            }
            
        except Exception as e:
            return {'error': str(e)}

    def _temporal_magnetic_analysis(self, structured_data: Dict) -> Dict[str, Any]:
        """Temporal magnetic analysis for time-based patterns"""
        try:
            temporal_data = structured_data.get('data', {}).get('temporal', [])
            numerical_data = structured_data.get('data', {}).get('numerical', [])
            
            if not temporal_data:
                return {'message': 'No temporal data found for analysis'}
            
            df_temporal = pd.DataFrame(temporal_data)
            
            # Time series analysis
            year_trends = df_temporal['year'].value_counts().sort_index()
            
            # Magnetic clustering of time periods
            time_clusters = {
                'decades': {},
                'periods': {},
                'trends': {}
            }
            
            # Group by decades
            for year in df_temporal['year']:
                decade = (year // 10) * 10
                if decade not in time_clusters['decades']:
                    time_clusters['decades'][decade] = []
                time_clusters['decades'][decade].append(year)
            
            # Trend analysis
            if len(year_trends) > 1:
                years = year_trends.index.tolist()
                counts = year_trends.values.tolist()
                
                # Simple trend calculation
                if len(years) >= 2:
                    trend_slope = (counts[-1] - counts[0]) / (years[-1] - years[0])
                    time_clusters['trends'] = {
                        'overall_trend': 'increasing' if trend_slope > 0 else 'decreasing' if trend_slope < 0 else 'stable',
                        'trend_strength': abs(trend_slope),
                        'peak_year': years[counts.index(max(counts))],
                        'peak_frequency': max(counts)
                    }
            
            return {
                'analysis_type': 'temporal_magnetic',
                'time_clusters': time_clusters,
                'temporal_statistics': {
                    'total_years': len(df_temporal['year'].unique()),
                    'time_span': {
                        'start': int(df_temporal['year'].min()),
                        'end': int(df_temporal['year'].max()),
                        'duration': int(df_temporal['year'].max() - df_temporal['year'].min())
                    },
                    'year_distribution': year_trends.to_dict()
                }
            }
            
        except Exception as e:
            return {'error': str(e)}

    def _detect_outliers(self, values: List[float]) -> List[float]:
        """Detect outliers using IQR method"""
        try:
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = [x for x in values if x < lower_bound or x > upper_bound]
            return outliers
        except:
            return []

    # Import all visualization methods from previous implementation
    def _extract_visualization_data(self, doc_data: Dict, query: str = '') -> Dict[str, Any]:
        """Extract quantitative data from document for visualization"""
        try:
            pages_data = doc_data.get('pages_data', [])
            
            # Extract numerical patterns
            numerical_data = []
            temporal_data = []
            categorical_data = []
            
            for page in pages_data:
                content = page.get('raw_content', '')
                page_num = page.get('page_number', 0)
                
                # Extract numbers with context
                number_pattern = r'(\d+(?:\.\d+)?)\s*(?:%|percent|percentage|million|billion|thousand|k|m|b)?'
                numbers = re.findall(number_pattern, content.lower())
                
                for num in numbers:
                    try:
                        value = float(num)
                        if 1 <= value <= 1000000:  # Reasonable range
                            numerical_data.append({
                                'value': value,
                                'page': page_num,
                                'context': self._extract_number_context(content, num)
                            })
                    except ValueError:
                        continue
                
                # Extract years/dates
                year_pattern = r'\b(19|20)\d{2}\b'
                years = re.findall(year_pattern, content)
                for year in years:
                    temporal_data.append({
                        'year': int(year),
                        'page': page_num,
                        'context': self._extract_number_context(content, year)
                    })
                
                # Extract categories from topics
                topics = page.get('topics', [])
                for topic in topics:
                    categorical_data.append({
                        'category': topic.lower(),
                        'page': page_num,
                        'frequency': content.lower().count(topic.lower())
                    })
            
            return {
                'data': {
                    'numerical': numerical_data,
                    'temporal': temporal_data,
                    'categorical': categorical_data
                },
                'summary': {
                    'total_numbers': len(numerical_data),
                    'total_years': len(temporal_data),
                    'total_categories': len(categorical_data)
                }
            }
            
        except Exception as e:
            print(f"❌ Error extracting visualization data: {e}")
            return {'data': None, 'error': str(e)}

    def _extract_number_context(self, content: str, number: str, window: int = 50) -> str:
        """Extract context around a number for better understanding"""
        try:
            index = content.lower().find(str(number).lower())
            if index == -1:
                return ""
            
            start = max(0, index - window)
            end = min(len(content), index + len(number) + window)
            
            return content[start:end].strip()
        except:
            return ""

    def _create_summary_visualizations(self, data: Dict, filename: str) -> List[Dict]:
        """Create a set of summary visualizations"""
        viz_results = []
        
        try:
            numerical_data = data['data'].get('numerical', [])
            temporal_data = data['data'].get('temporal', [])
            categorical_data = data['data'].get('categorical', [])
            
            # 1. Numbers distribution by page
            if numerical_data:
                page_numbers = [item['page'] for item in numerical_data]
                values = [item['value'] for item in numerical_data]
                
                plt.figure(figsize=(10, 6))
                plt.scatter(page_numbers, values, alpha=0.6, c='blue', s=50)
                plt.xlabel('Page Number')
                plt.ylabel('Numerical Values')
                plt.title(f'Numerical Data Distribution - {filename}')
                plt.grid(True, alpha=0.3)
                
                viz_path = f"visualizations/numbers_distribution_{uuid.uuid4().hex[:8]}.png"
                plt.savefig(viz_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                viz_results.append({
                    'type': 'scatter',
                    'title': 'Numerical Data Distribution',
                    'path': viz_path,
                    'description': f'Distribution of {len(numerical_data)} numerical values across document pages'
                })
            
            # 2. Category frequency analysis
            if categorical_data:
                df_cat = pd.DataFrame(categorical_data)
                category_counts = df_cat.groupby('category')['frequency'].sum().sort_values(ascending=False).head(10)
                
                plt.figure(figsize=(12, 8))
                category_counts.plot(kind='bar', color='skyblue')
                plt.title(f'Top Categories by Frequency - {filename}')
                plt.xlabel('Categories')
                plt.ylabel('Frequency')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                
                viz_path = f"visualizations/categories_{uuid.uuid4().hex[:8]}.png"
                plt.savefig(viz_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                viz_results.append({
                    'type': 'bar',
                    'title': 'Top Categories by Frequency',
                    'path': viz_path,
                    'description': f'Most frequent categories found in the document'
                })
            
            # 3. Temporal analysis
            if temporal_data:
                df_temporal = pd.DataFrame(temporal_data)
                year_counts = df_temporal['year'].value_counts().sort_index()
                
                plt.figure(figsize=(10, 6))
                year_counts.plot(kind='line', marker='o', color='green', linewidth=2)
                plt.title(f'Temporal References - {filename}')
                plt.xlabel('Year')
                plt.ylabel('Frequency')
                plt.grid(True, alpha=0.3)
                
                viz_path = f"visualizations/temporal_{uuid.uuid4().hex[:8]}.png"
                plt.savefig(viz_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                viz_results.append({
                    'type': 'line',
                    'title': 'Temporal References',
                    'path': viz_path,
                    'description': f'Timeline of year references in the document'
                })
            
        except Exception as e:
            print(f"❌ Error creating summary visualizations: {e}")
        
        return viz_results

    def _create_bar_chart(self, data: Dict, filename: str) -> Dict:
        """Create a bar chart from extracted data"""
        try:
            categorical_data = data['data'].get('categorical', [])
            if not categorical_data:
                return {'error': 'No categorical data found for bar chart'}
            
            df = pd.DataFrame(categorical_data)
            category_counts = df.groupby('category')['frequency'].sum().sort_values(ascending=False).head(15)
            
            plt.figure(figsize=(12, 8))
            bars = plt.bar(range(len(category_counts)), category_counts.values, color='lightcoral')
            plt.title(f'Category Frequency Analysis - {filename}')
            plt.xlabel('Categories')
            plt.ylabel('Frequency')
            plt.xticks(range(len(category_counts)), category_counts.index, rotation=45, ha='right')
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        f'{int(category_counts.values[i])}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            viz_path = f"visualizations/bar_chart_{uuid.uuid4().hex[:8]}.png"
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                'type': 'bar',
                'title': 'Category Frequency Bar Chart',
                'path': viz_path,
                'description': f'Bar chart showing frequency of top {len(category_counts)} categories'
            }
            
        except Exception as e:
            return {'error': f'Error creating bar chart: {str(e)}'}

    def _create_line_chart(self, data: Dict, filename: str) -> Dict:
        """Create a line chart from temporal data"""
        try:
            temporal_data = data['data'].get('temporal', [])
            if not temporal_data:
                return {'error': 'No temporal data found for line chart'}
            
            df = pd.DataFrame(temporal_data)
            year_counts = df['year'].value_counts().sort_index()
            
            plt.figure(figsize=(12, 6))
            plt.plot(year_counts.index, year_counts.values, marker='o', linewidth=2, markersize=6, color='purple')
            plt.title(f'Temporal Trend Analysis - {filename}')
            plt.xlabel('Year')
            plt.ylabel('References')
            plt.grid(True, alpha=0.3)
            
            # Add value labels
            for x, y in zip(year_counts.index, year_counts.values):
                plt.annotate(f'{int(y)}', (x, y), textcoords="offset points", xytext=(0,10), ha='center')
            
            plt.tight_layout()
            
            viz_path = f"visualizations/line_chart_{uuid.uuid4().hex[:8]}.png"
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                'type': 'line',
                'title': 'Temporal Trend Line Chart',
                'path': viz_path,
                'description': f'Line chart showing temporal trends in the document'
            }
            
        except Exception as e:
            return {'error': f'Error creating line chart: {str(e)}'}

    def _create_scatter_plot(self, data: Dict, filename: str) -> Dict:
        """Create a scatter plot from numerical data"""
        try:
            numerical_data = data['data'].get('numerical', [])
            if len(numerical_data) < 2:
                return {'error': 'Insufficient numerical data for scatter plot'}
            
            pages = [item['page'] for item in numerical_data]
            values = [item['value'] for item in numerical_data]
            
            plt.figure(figsize=(10, 8))
            scatter = plt.scatter(pages, values, alpha=0.6, s=60, c=values, cmap='viridis')
            plt.colorbar(scatter, label='Value')
            plt.title(f'Numerical Values by Page - {filename}')
            plt.xlabel('Page Number')
            plt.ylabel('Numerical Value')
            plt.grid(True, alpha=0.3)
            
            viz_path = f"visualizations/scatter_plot_{uuid.uuid4().hex[:8]}.png"
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                'type': 'scatter',
                'title': 'Numerical Values Scatter Plot',
                'path': viz_path,
                'description': f'Scatter plot of {len(numerical_data)} numerical values across pages'
            }
            
        except Exception as e:
            return {'error': f'Error creating scatter plot: {str(e)}'}

    def _create_heatmap(self, data: Dict, filename: str) -> Dict:
        """Create a heatmap from categorical data"""
        try:
            categorical_data = data['data'].get('categorical', [])
            if not categorical_data:
                return {'error': 'No categorical data found for heatmap'}
            
            df = pd.DataFrame(categorical_data)
            
            # Create page vs category matrix
            pivot_data = df.pivot_table(
                values='frequency', 
                index='category', 
                columns='page', 
                fill_value=0
            ).head(15)  # Top 15 categories
            
            if pivot_data.empty:
                return {'error': 'Insufficient data for heatmap'}
            
            plt.figure(figsize=(14, 10))
            sns.heatmap(pivot_data, annot=True, fmt='d', cmap='YlOrRd', cbar_kws={'label': 'Frequency'})
            plt.title(f'Category Frequency Heatmap - {filename}')
            plt.xlabel('Page Number')
            plt.ylabel('Category')
            plt.tight_layout()
            
            viz_path = f"visualizations/heatmap_{uuid.uuid4().hex[:8]}.png"
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                'type': 'heatmap',
                'title': 'Category-Page Frequency Heatmap',
                'path': viz_path,
                'description': f'Heatmap showing category distribution across document pages'
            }
            
        except Exception as e:
            return {'error': f'Error creating heatmap: {str(e)}'}

    def _extract_structured_data(self, filename: str, data_type: str) -> Dict[str, Any]:
        """Extract structured data from document"""
        try:
            doc_data = self.collection.find_one({"filename": filename})
            if not doc_data:
                raise Exception(f"Document not found: {filename}")
            
            pages_data = doc_data.get('pages_data', [])
            
            if data_type == 'tables':
                return self._extract_table_data(pages_data)
            elif data_type == 'numbers':
                return self._extract_numerical_data(pages_data)
            elif data_type == 'dates':
                return self._extract_date_data(pages_data)
            elif data_type == 'entities':
                return self._extract_entity_data(pages_data)
            else:
                return {'error': f'Unknown data type: {data_type}'}
                
        except Exception as e:
            return {'error': str(e)}

    def _extract_table_data(self, pages_data: List[Dict]) -> Dict[str, Any]:
        """Extract table-like structured data from pages"""
        try:
            tables = []
            
            for page in pages_data:
                content = page.get('raw_content', '')
                page_num = page.get('page_number', 0)
                
                # Look for table-like patterns
                lines = content.split('\n')
                potential_tables = []
                
                for i, line in enumerate(lines):
                    # Simple heuristic: lines with multiple numbers/separators
                    if len(re.findall(r'\d+', line)) >= 2 and ('|' in line or '\t' in line or '  ' in line):
                        potential_tables.append({
                            'page': page_num,
                            'line': i + 1,
                            'content': line.strip(),
                            'type': 'table_row'
                        })
                
                if potential_tables:
                    tables.extend(potential_tables)
            
            return {
                'tables': tables,
                'total_found': len(tables),
                'extraction_method': 'pattern_based'
            }
            
        except Exception as e:
            return {'error': str(e)}

    def _extract_numerical_data(self, pages_data: List[Dict]) -> Dict[str, Any]:
        """Extract numerical data with enhanced context"""
        try:
            numerical_items = []
            
            for page in pages_data:
                content = page.get('raw_content', '')
                page_num = page.get('page_number', 0)
                
                # Enhanced number pattern matching
                patterns = [
                    r'(\d+(?:\.\d+)?)\s*%',  # Percentages
                    r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # Currency
                    r'(\d+(?:,\d{3})*)\s*(million|billion|thousand)',  # Large numbers
                    r'(\d{4})',  # Years
                    r'(\d+(?:\.\d+)?)\s*(kg|g|lb|oz|m|cm|km|ft|in)',  # Measurements
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        numerical_items.append({
                            'value': match.group(1),
                            'unit': match.group(2) if len(match.groups()) > 1 else None,
                            'page': page_num,
                            'context': self._extract_number_context(content, match.group(0), 100),
                            'pattern_type': 'enhanced_extraction'
                        })
            
            return {
                'numerical_data': numerical_items,
                'total_found': len(numerical_items),
                'extraction_method': 'pattern_enhanced'
            }
            
        except Exception as e:
            return {'error': str(e)}

    def _extract_date_data(self, pages_data: List[Dict]) -> Dict[str, Any]:
        """Extract date and temporal information"""
        try:
            dates = []
            
            for page in pages_data:
                content = page.get('raw_content', '')
                page_num = page.get('page_number', 0)
                
                # Date patterns
                date_patterns = [
                    r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',  # MM/DD/YYYY
                    r'\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b',    # YYYY/MM/DD
                    r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
                    r'\b(\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b'  # DD Month YYYY
                ]
                
                for pattern in date_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        dates.append({
                            'date': match.group(0),
                            'page': page_num,
                            'context': self._extract_number_context(content, match.group(0), 80),
                            'pattern_type': 'date_extraction'
                        })
            
            return {
                'dates': dates,
                'total_found': len(dates),
                'extraction_method': 'date_patterns'
            }
            
        except Exception as e:
            return {'error': str(e)}

    def _extract_entity_data(self, pages_data: List[Dict]) -> Dict[str, Any]:
        """Extract named entities and important terms"""
        try:
            entities = []
            
            for page in pages_data:
                content = page.get('raw_content', '')
                page_num = page.get('page_number', 0)
                topics = page.get('topics', [])
                keywords = page.get('keywords', [])
                
                # Combine topics and keywords as entities
                all_entities = list(set(topics + keywords))
                
                for entity in all_entities:
                    frequency = content.lower().count(entity.lower())
                    if frequency > 0:
                        entities.append({
                            'entity': entity,
                            'page': page_num,
                            'frequency': frequency,
                            'type': 'topic' if entity in topics else 'keyword',
                            'context': self._extract_number_context(content, entity, 60)
                        })
            
            return {
                'entities': entities,
                'total_found': len(entities),
                'extraction_method': 'topic_keyword_based'
            }
            
        except Exception as e:
            return {'error': str(e)}

    # Enhanced PDF processing pipeline
    def _process_pdf_pipeline_enhanced(self, pdf_path: str, original_filename: str) -> Dict[str, Any]:
        """Enhanced PDF processing pipeline with data analysis"""
        print(f"🚀 Starting enhanced PDF processing pipeline for: {original_filename}")
        
        # Store PDF permanently
        stored_pdfs_dir = "stored_pdfs"
        os.makedirs(stored_pdfs_dir, exist_ok=True)
        stored_pdf_path = os.path.join(stored_pdfs_dir, original_filename)
        shutil.copy2(pdf_path, stored_pdf_path)
        
        # Extract and analyze pages
        pages_data = self._extract_pages_with_analysis(pdf_path)
        if not pages_data:
            raise Exception("No content extracted from PDF")
        
        # Create table of contents
        toc = self._create_table_of_contents(pages_data)
        
        # Vectorize content
        vectorstore = self._vectorize_content(pages_data)
        
        # Enhanced: Extract structured data for visualization
        structured_data = self._extract_visualization_data({'pages_data': pages_data})
        
        # Store in MongoDB with enhanced data
        self._store_in_mongodb_enhanced(original_filename, pages_data, toc, vectorstore, stored_pdf_path, structured_data)
        
        return {
            'pages_processed': len(pages_data),
            'topics_extracted': len(toc),
            'structured_data_extracted': bool(structured_data.get('data')),
            'numerical_items': len(structured_data.get('data', {}).get('numerical', [])),
            'processing_timestamp': datetime.now().isoformat(),
            'pdf_stored_at': stored_pdf_path
        }

    def _store_in_mongodb_enhanced(self, filename: str, pages_data: List[Dict[str, Any]],
                                 toc: Dict[str, List[int]], vectorstore: FAISS, 
                                 pdf_path: str, structured_data: Dict):
        """Store enhanced data in MongoDB"""
        print("💾 Storing enhanced data in MongoDB...")
        
        # Serialize vectorstore
        temp_dir = tempfile.mkdtemp()
        vectorstore_path = os.path.join(temp_dir, "vectorstore")
        vectorstore.save_local(vectorstore_path)
        
        with open(os.path.join(vectorstore_path, "index.faiss"), "rb") as f:
            faiss_index = f.read()
        with open(os.path.join(vectorstore_path, "index.pkl"), "rb") as f:
            faiss_metadata = f.read()
        
        document_data = {
            "filename": filename,
            "upload_date": datetime.now(),
            "pages_data": pages_data,
            "table_of_contents": toc,
            "total_pages": len(pages_data),
            "faiss_index": faiss_index,
            "faiss_metadata": faiss_metadata,
            "pdf_path": pdf_path,
            "structured_data": structured_data,  # Enhanced: store structured data
            "processing_version": "2.0_enhanced"
        }
        
        # Store or update document
        existing = self.collection.find_one({"filename": filename})
        if existing:
            self.collection.update_one({"filename": filename}, {"$set": document_data})
            print(f"🔄 Updated existing document: {filename}")
        else:
            self.collection.insert_one(document_data)
            print(f"✅ Stored new document: {filename}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        print("✅ Enhanced data stored in MongoDB")

    # Import all other original methods (preserving existing functionality)
    def save_screenshots_with_cleanup(self, pdf_path: str, page_numbers: list, base_context_dir: str = "context") -> list:
        """Save screenshots with cleanup of previous images"""
        print(f"📸 Saving screenshots for pages: {', '.join(map(str, page_numbers))}")
        
        os.makedirs(base_context_dir, exist_ok=True)
        
        # Delete all previous images in the context directory
        if os.path.exists(base_context_dir):
            print("🧹 Cleaning up previous screenshots...")
            for file in os.listdir(base_context_dir):
                if file.endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(base_context_dir, file)
                    os.remove(file_path)
                    print(f"🗑️ Deleted: {file}")
        
        screenshot_paths = []
        try:
            print("🔄 Opening PDF for screenshot extraction...")
            doc = fitz.open(pdf_path)
            for page_num in sorted(page_numbers):
                if page_num <= len(doc):
                    print(f"📸 Taking screenshot of page {page_num}...")
                    page = doc[page_num - 1]  # 0-based index
                    mat = fitz.Matrix(2, 2)  # zoom for better quality
                    pix = page.get_pixmap(matrix=mat)
                    screenshot_path = os.path.join(base_context_dir, f"page_{page_num}.png")
                    pix.save(screenshot_path)
                    screenshot_paths.append(screenshot_path)
                    print(f"✅ Screenshot saved: page_{page_num}.png")
                else:
                    print(f"⚠️ Page {page_num} exceeds document length")
            
            doc.close()
            print(f"🎉 All screenshots saved directly in: {base_context_dir}")
        except Exception as e:
            print(f"❌ Error taking screenshots: {e}")
        
        return screenshot_paths

    def _extract_pages_with_analysis(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF pages and analyze topics"""
        print("📖 Extracting and analyzing PDF pages...")
        pdf_reader = PdfReader(pdf_path)
        pages_data = []
        
        for page_num, page in enumerate(pdf_reader.pages, 1):
            print(f"🔄 Processing page {page_num}/{len(pdf_reader.pages)}")
            text = page.extract_text() or ""
            
            if not text.strip():
                continue
            
            tagged_content = f"[PAGE_{page_num}] {text}"
            topic_analysis = self._analyze_page_topics(text, page_num)
            
            page_data = {
                "page_number": page_num,
                "raw_content": text,
                "tagged_content": tagged_content,
                "topics": topic_analysis["topics"],
                "summary": topic_analysis["summary"],
                "keywords": topic_analysis["keywords"]
            }
            
            pages_data.append(page_data)
            print(f"✅ Page {page_num} processed")
        
        return pages_data

    def _analyze_page_topics(self, text: str, page_num: int) -> Dict[str, Any]:
        """Analyze topics and content of a page using LLM"""
        prompt = f"""
        Analyze the following text from page {page_num} and provide:
        1. Main topics/themes (list of 3-5 key topics)
        2. Brief summary (1-2 sentences)
        3. Important keywords (5-10 keywords)

        Text:
        {text[:2000]}

        Respond in this exact JSON format:
        {{
            "topics": ["topic1", "topic2", "topic3"],
            "summary": "Brief summary here",
            "keywords": ["keyword1", "keyword2", "keyword3"]
        }}
        """
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
            else:
                return {
                    "topics": ["General Content"],
                    "summary": f"Content from page {page_num}",
                    "keywords": ["content", "page", str(page_num)]
                }
        except Exception as e:
            print(f"⚠️ Error analyzing page {page_num}: {e}")
            return {
                "topics": ["General Content"],
                "summary": f"Content from page {page_num}",
                "keywords": ["content", "page", str(page_num)]
            }

    def _create_table_of_contents(self, pages_data: List[Dict[str, Any]]) -> Dict[str, List[int]]:
        """Create table of contents with topics and page numbers"""
        print("📚 Creating table of contents...")
        toc = {}
        
        for page_data in pages_data:
            page_num = page_data["page_number"]
            topics = page_data["topics"]
            
            for topic in topics:
                topic_clean = topic.strip().lower()
                if topic_clean not in toc:
                    toc[topic_clean] = []
                if page_num not in toc[topic_clean]:
                    toc[topic_clean].append(page_num)
        
        # Sort page numbers for each topic
        for topic in toc:
            toc[topic].sort()
        
        print(f"✅ Created TOC with {len(toc)} topics")
        return toc

    def _vectorize_content(self, pages_data: List[Dict[str, Any]]) -> FAISS:
        """Vectorize tagged content"""
        print("🔢 Vectorizing content...")
        texts = []
        metadatas = []
        
        for page_data in pages_data:
            texts.append(page_data["tagged_content"])
            metadatas.append({
                "page_number": page_data["page_number"],
                "topics": page_data["topics"],
                "summary": page_data["summary"],
                "keywords": page_data["keywords"]
            })
        
        vectorstore = FAISS.from_texts(texts, self.embeddings, metadatas=metadatas)
        print("✅ Vectorization complete")
        return vectorstore

    def _recreate_vectorstore(self, doc_data: Dict) -> FAISS:
        """Recreate vectorstore from stored data"""
        temp_dir = tempfile.mkdtemp()
        
        # Write FAISS files
        with open(os.path.join(temp_dir, "index.faiss"), "wb") as f:
            f.write(doc_data["faiss_index"])
        with open(os.path.join(temp_dir, "index.pkl"), "wb") as f:
            f.write(doc_data["faiss_metadata"])
        
        # Load vectorstore
        vectorstore = FAISS.load_local(temp_dir, self.embeddings, allow_dangerous_deserialization=True)
        
        # Cleanup
        shutil.rmtree(temp_dir)
        return vectorstore

    def _answer_question_pipeline(self, filename: str, question: str) -> Dict[str, Any]:
        """Complete question answering pipeline"""
        print(f"❓ Processing question: {question}")
        
        # Retrieve document data
        doc_data = self.collection.find_one({"filename": filename})
        if not doc_data:
            raise Exception(f"Document not found: {filename}")
        
        pages_data = doc_data["pages_data"]
        toc = doc_data["table_of_contents"]
        pdf_path = doc_data.get("pdf_path")
        
        # Find relevant topics
        relevant_topics = self._find_relevant_topics(question, toc)
        
        # Get page numbers for topics
        relevant_pages = self._retrieve_pages_for_topics(relevant_topics, toc)
        
        if not relevant_pages:
            raise Exception("No relevant pages found for the question")
        
        # Get context
        context = self._devectorize_and_get_context(relevant_pages, pages_data)
        
        # Generate answer
        answer = self._generate_answer_with_references(question, context, relevant_pages)
        
        # Save screenshots if PDF path is available
        screenshot_paths = []
        if pdf_path and os.path.exists(pdf_path):
            print("📸 Saving screenshots for answer context...")
            screenshot_paths = self.save_screenshots_with_cleanup(pdf_path, relevant_pages)
            print(f"✅ Screenshots saved: {len(screenshot_paths)} images")
        else:
            print("⚠️ PDF file not found, skipping screenshots")
        
        return {
            'answer': answer,
            'context': context[:1000] + "..." if len(context) > 1000 else context,
            'references': [f"Page {p}" for p in sorted(relevant_pages)],
            'topics_used': relevant_topics,
            'pages_used': relevant_pages,
            'screenshots': screenshot_paths
        }

    def _find_relevant_topics(self, question: str, toc: Dict[str, List[int]]) -> List[str]:
        """Find topics relevant to the question"""
        question_lower = question.lower()
        relevant_topics = []
        
        # Keyword matching
        for topic, pages in toc.items():
            if any(word in topic for word in question_lower.split() if len(word) > 2):
                relevant_topics.append(topic)
        
        # LLM fallback if no matches
        if not relevant_topics:
            topic_list = list(toc.keys())
            prompt = f"""
            Given this question: "{question}"
            And these available topics: {', '.join(topic_list)}
            Which topics are most relevant to answer this question?
            Return only the topic names that are relevant, separated by commas.
            """
            
            try:
                response = self.llm.invoke(prompt)
                suggested_topics = [t.strip().lower() for t in response.content.split(',')]
                relevant_topics = [t for t in suggested_topics if t in toc]
            except:
                relevant_topics = list(toc.keys())[:3]
        
        return relevant_topics or list(toc.keys())[:5]

    def _retrieve_pages_for_topics(self, topics: List[str], toc: Dict[str, List[int]]) -> List[int]:
        """Get ordered list of page numbers for topics"""
        page_numbers = set()
        for topic in topics:
            if topic in toc:
                page_numbers.update(toc[topic])
        return sorted(list(page_numbers))

    def _devectorize_and_get_context(self, page_numbers: List[int], pages_data: List[Dict[str, Any]]) -> str:
        """Get full context for specified pages"""
        context_parts = []
        for page_num in page_numbers:
            page_data = next((p for p in pages_data if p["page_number"] == page_num), None)
            if page_data:
                context_parts.append(f"[PAGE {page_num}]\n{page_data['raw_content']}\n")
        return "\n".join(context_parts)

    def _generate_answer_with_references(self, question: str, context: str, page_numbers: List[int]) -> str:
        """Generate answer with references"""
        prompt = f"""
        Based on the following context from a PDF document, answer the question comprehensively.

        IMPORTANT INSTRUCTIONS:
        1. Use the information from the context to provide a detailed answer
        2. Include page references throughout your answer using [Page X] format when citing specific information
        3. Structure your answer clearly with proper formatting
        4. At the end, include a "References" section listing all pages used

        Question: {question}

        Context from PDF:
        {context}

        Please provide a comprehensive, well-structured answer with proper citations.
        """
        
        try:
            response = self.llm.invoke(prompt)
            answer = response.content
            
            # Ensure references section exists
            if "References:" not in answer and "REFERENCES:" not in answer:
                references = ", ".join([f"Page {p}" for p in sorted(page_numbers)])
                answer += f"\n\n**References:** {references}"
            
            return answer
        except Exception as e:
            return f"Error generating answer: {e}"

def create_app():
    """Create and configure Flask application"""
    # Validate environment variables
    if not os.getenv("GROQ_API_KEY"):
        raise Exception("GROQ_API_KEY environment variable not found!")
    
    rag_app = EnhancedRAGFlaskApp()
    return rag_app.app

# Create app instance
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Enhanced RAG Flask Application with CrewAI...")
    print("📡 Server will be available at: http://localhost:5000")
    print("🔧 CORS enabled for all origins")
    print("📚 Available endpoints:")
    print(" - GET /health - Health check with enhanced features")
    print(" - GET /documents - List processed documents with metadata")
    print(" - POST /process - Process PDF document with enhanced analysis")
    print(" - POST /ask - Ask questions about documents (traditional RAG)")
    print(" - POST /ask/agentic - Ask questions using CrewAI multi-agent approach")
    print(" - POST /visualize - Create dynamic data visualizations")
    print(" - POST /extract-data - Extract structured data (tables, numbers, dates, entities)")
    print(" - POST /analyze - Comprehensive analysis using magnetic approach")
    print(" - GET /visualizations/<filename> - Serve visualization files")
    print(" - GET /document/<filename>/screenshots - Get document screenshots")
    print(" - GET /context/<filename> - Serve context files")
    print("")
    print("🤖 CrewAI Features:")
    print(" • Multi-agent processing with specialized roles")
    print(" • Research Expert, Data Analyst, Visualization Expert, Answer Generator")
    print(" • Collaborative intelligence for comprehensive analysis")
    print("")
    print("📊 Data Visualization Features:")
    print(" • Matplotlib, Seaborn, Plotly integration")
    print(" • Auto-generated charts: bar, line, scatter, heatmap")
    print(" • Dynamic visualization based on document content")
    print(" • Statistical analysis and pattern recognition")
    print("")
    print("🧲 Magnetic Approach Features:")
    print(" • Concept clustering and relationship mapping")
    print(" • Statistical magnetic analysis")
    print(" • Temporal pattern analysis")
    print(" • Enhanced data extraction and structuring")
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
