import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Document {
  document_id: string;
  filename: string;
  subject: string;
  upload_date: string;
  complexity_score: number;
  chunk_count: number;
}

export interface UserInteraction {
  interaction_id: string;
  user_id: string;
  question: string;
  answer: string;
  document_id: string;
  timestamp: string;
  sources?: Array<{
    document: string;
    chunk_id: string;
    relevance_score: number;
    preview: string;
  }>;
}

export interface AnalyticsData {
  total_questions: number;
  unique_documents: number;
  avg_questions_per_day: number;
  avg_question_complexity: number;
  comprehension_score: number;
  main_topics: string[];
  learning_sessions: number;
}

// API functions
export const apiService = {
  // Upload PDF
  uploadPDF: async (file: File, subject: string, userId: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('subject', subject);
    formData.append('user_id', userId);
    
    return api.post('/upload_pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Ask question
  askQuestion: async (question: string, documentId: string = 'all', userId: string) => {
    return api.post('/ask', {
      question,
      document_id: documentId,
      user_id: userId,
    });
  },

  // Get analytics
  getAnalytics: async (userId: string, timeRange: string = '30days') => {
    return api.get(`/analytics/progress/${userId}`, {
      params: { time_range: timeRange },
    });
  },

  // Get dashboard
  getDashboard: async (userId: string) => {
    return api.get(`/visualizations/dashboard/${userId}`);
  },

  // Chat with tutor
  chatTutor: async (message: string, context: string = '') => {
    return api.post('/agents/tutor', {
      question: message,
      context,
    });
  },

  // Research assistant
  getResearchSuggestions: async (topic: string) => {
    return api.post('/agents/researcher', {
      topic,
    });
  },

  // Submit feedback
  submitFeedback: async (interactionId: string, rating: number, comments: string = '') => {
    return api.post('/feedback', {
      interaction_id: interactionId,
      rating,
      comments,
    });
  },
};
