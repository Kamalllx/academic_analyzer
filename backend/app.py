from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
from datetime import datetime
import uuid

from rag_engine.query_engine import QueryEngine
from rag_engine.pdf_processor import PDFProcessor
from data.mongodb_handler import MongoDBHandler
from analytics.learning_analytics import LearningAnalytics
from analytics.document_analyzer import DocumentAnalyzer
from visualization.dashboard_generator import DashboardGenerator
from agents.tutor_agent import TutorAgent
from agents.researcher_agent import ResearcherAgent

app = Flask(__name__)
CORS(app)

# Initialize components
mongo_handler = MongoDBHandler(
    connection_string="mongodb+srv://kamalkarteek1:rvZSeyVHhgOd2fbE@gbh.iliw2.mongodb.net/",  # Update with your connection string
    db_name="academic_analyzer"
)
pdf_processor = PDFProcessor()
query_engine = QueryEngine(mongo_handler)
learning_analytics = LearningAnalytics(mongo_handler)
document_analyzer = DocumentAnalyzer()
dashboard_generator = DashboardGenerator(mongo_handler)
tutor_agent = TutorAgent()
researcher_agent = ResearcherAgent()

@app.route('/')
def home():
    return jsonify({
        "message": "Academic Document Analyzer API",
        "version": "1.0.0",
        "endpoints": [
            "/upload_pdf", "/ask", "/analytics/progress", 
            "/analytics/patterns", "/visualizations/dashboard",
            "/agents/tutor", "/agents/researcher"
        ]
    })

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        subject = request.form.get('subject', 'general')
        user_id = request.form.get('user_id', str(uuid.uuid4()))
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400
        
        # Process PDF
        text_chunks = pdf_processor.extract_text_from_pdf(file)
        complexity_score = document_analyzer.score_document_complexity(text_chunks)
        
        # Store in vector database and MongoDB
        doc_id = str(uuid.uuid4())
        query_engine.add_document(doc_id, text_chunks, {
            'filename': file.filename,
            'subject': subject,
            'user_id': user_id,
            'complexity_score': complexity_score,
            'upload_date': datetime.now()
        })
        
        # Store metadata in MongoDB
        mongo_handler.store_document_metadata(
            doc_id, file.filename, subject, user_id, 
            len(text_chunks), complexity_score
        )
        
        return jsonify({
            'message': 'PDF processed and stored successfully',
            'document_id': doc_id,
            'chunks': len(text_chunks),
            'complexity_score': complexity_score
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question')
        document_id = data.get('document_id', 'all')
        user_id = data.get('user_id', 'anonymous')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Get answer from RAG system
        answer, sources = query_engine.process_query(question, document_id)
        
        # Get tutor agent response
        tutor_response = tutor_agent.provide_explanation(question, answer)
        
        # Store interaction for analytics
        interaction_id = str(uuid.uuid4())
        mongo_handler.store_user_interaction(
            interaction_id, user_id, question, answer, 
            document_id, sources, datetime.now()
        )
        
        return jsonify({
            'answer': answer,
            'tutor_explanation': tutor_response,
            'sources': sources,
            'interaction_id': interaction_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analytics/progress/<user_id>')
def get_user_progress(user_id):
    try:
        time_range = request.args.get('time_range', '30days')
        progress_data = learning_analytics.analyze_learning_progress(user_id, time_range)
        return jsonify(progress_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analytics/patterns')
def get_query_patterns():
    try:
        patterns = learning_analytics.detect_query_patterns()
        return jsonify(patterns)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/visualizations/dashboard/<user_id>')
def get_dashboard(user_id):
    try:
        dashboard_data = dashboard_generator.generate_user_dashboard(user_id)
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/agents/tutor', methods=['POST'])
def tutor_chat():
    try:
        data = request.get_json()
        question = data.get('question')
        context = data.get('context', '')
        
        response = tutor_agent.chat_with_student(question, context)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/agents/researcher', methods=['POST'])
def research_assistant():
    try:
        data = request.get_json()
        topic = data.get('topic')
        
        suggestions = researcher_agent.suggest_related_resources(topic)
        return jsonify({'suggestions': suggestions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        interaction_id = data.get('interaction_id')
        rating = data.get('rating')  # 1-5 stars
        comments = data.get('comments', '')
        
        mongo_handler.store_feedback(interaction_id, rating, comments, datetime.now())
        return jsonify({'message': 'Feedback stored successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure upload directory exists
    os.makedirs('uploads', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
