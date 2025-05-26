import PyPDF2
import re
from typing import List, Dict
import logging

class PDFProcessor:
    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 200
        
    def extract_text_from_pdf(self, file) -> List[str]:
        """Extract and chunk text from PDF file"""
        try:
            reader = PyPDF2.PdfReader(file)
            full_text = ""
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    # Clean the text
                    text = self._clean_text(text)
                    full_text += f"\n\n[Page {page_num + 1}]\n{text}"
            
            # Split into chunks
            chunks = self._create_chunks(full_text)
            return chunks
            
        except Exception as e:
            logging.error(f"Error processing PDF: {str(e)}")
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\"\']+', '', text)
        return text.strip()
    
    def _create_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        text_length = len(text)
        
        start = 0
        while start < text_length:
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < text_length:
                last_period = text.rfind('.', start, end)
                if last_period != -1 and last_period > start + self.chunk_size // 2:
                    end = last_period + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
            
        return chunks
    
    def extract_metadata(self, file) -> Dict:
        """Extract metadata from PDF"""
        try:
            reader = PyPDF2.PdfReader(file)
            metadata = reader.metadata
            
            return {
                'title': metadata.get('/Title', 'Unknown'),
                'author': metadata.get('/Author', 'Unknown'),
                'pages': len(reader.pages),
                'creation_date': str(metadata.get('/CreationDate', 'Unknown'))
            }
        except:
            return {'title': 'Unknown', 'author': 'Unknown', 'pages': 0}
