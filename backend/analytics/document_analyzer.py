import re
import numpy as np
from typing import List, Dict, Any
import logging
from collections import Counter
import textstat

class DocumentAnalyzer:
    def __init__(self):
        self.academic_indicators = [
            'abstract', 'introduction', 'methodology', 'results', 'conclusion',
            'references', 'bibliography', 'hypothesis', 'analysis', 'research'
        ]
        
        self.complexity_indicators = [
            'furthermore', 'moreover', 'consequently', 'nevertheless', 'therefore',
            'hypothesis', 'paradigm', 'phenomenon', 'empirical', 'theoretical'
        ]
    
    def score_document_complexity(self, text_chunks: List[str]) -> float:
        """Score document complexity on a scale of 0-1"""
        try:
            full_text = ' '.join(text_chunks)
            
            # Multiple complexity metrics
            readability_score = self._calculate_readability_score(full_text)
            vocabulary_score = self._calculate_vocabulary_complexity(full_text)
            structure_score = self._calculate_structure_complexity(full_text)
            academic_score = self._calculate_academic_complexity(full_text)
            
            # Weighted average
            weights = [0.3, 0.25, 0.2, 0.25]
            scores = [readability_score, vocabulary_score, structure_score, academic_score]
            
            complexity_score = sum(w * s for w, s in zip(weights, scores))
            
            return min(max(complexity_score, 0.0), 1.0)
            
        except Exception as e:
            logging.error(f"Error calculating complexity: {str(e)}")
            return 0.5  # Default moderate complexity
    
    def analyze_document_structure(self, text_chunks: List[str]) -> Dict:
        """Analyze document structure and content distribution"""
        try:
            full_text = ' '.join(text_chunks)
            
            # Basic statistics
            word_count = len(full_text.split())
            sentence_count = len(re.findall(r'[.!?]+', full_text))
            paragraph_count = len(text_chunks)
            
            # Content analysis
            topics = self._extract_topics(full_text)
            key_concepts = self._extract_key_concepts(full_text)
            
            # Structural elements
            headers = self._identify_headers(text_chunks)
            citations = self._count_citations(full_text)
            
            return {
                'word_count': word_count,
                'sentence_count': sentence_count,
                'paragraph_count': paragraph_count,
                'avg_words_per_sentence': round(word_count / sentence_count, 2) if sentence_count > 0 else 0,
                'avg_sentences_per_paragraph': round(sentence_count / paragraph_count, 2) if paragraph_count > 0 else 0,
                'main_topics': topics[:5],
                'key_concepts': key_concepts[:10],
                'structural_elements': headers,
                'citation_count': citations,
                'document_type': self._classify_document_type(full_text)
            }
            
        except Exception as e:
            logging.error(f"Error analyzing document structure: {str(e)}")
            return {}
    
    def _calculate_readability_score(self, text: str) -> float:
        """Calculate readability score using multiple metrics"""
        try:
            # Flesch Reading Ease (converted to 0-1 scale)
            flesch_score = textstat.flesch_reading_ease(text)
            flesch_normalized = (100 - flesch_score) / 100.0
            
            # Average sentence length
            sentences = re.findall(r'[.!?]+', text)
            words = text.split()
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            sentence_complexity = min(avg_sentence_length / 25.0, 1.0)
            
            # Syllable complexity
            syllable_count = textstat.syllable_count(text)
            syllable_complexity = min(syllable_count / len(words) / 2.0, 1.0) if words else 0
            
            # Combine metrics
            readability_score = (flesch_normalized + sentence_complexity + syllable_complexity) / 3.0
            
            return min(max(readability_score, 0.0), 1.0)
            
        except Exception:
            # Fallback simple calculation
            words = text.split()
            sentences = re.findall(r'[.!?]+', text)
            if not sentences:
                return 0.3
            
            avg_words_per_sentence = len(words) / len(sentences)
            return min(avg_words_per_sentence / 30.0, 1.0)
    
    def _calculate_vocabulary_complexity(self, text: str) -> float:
        """Calculate vocabulary complexity"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words:
            return 0.0
        
        # Unique word ratio
        unique_words = set(words)
        vocabulary_diversity = len(unique_words) / len(words)
        
        # Long word ratio
        long_words = [word for word in words if len(word) > 6]
        long_word_ratio = len(long_words) / len(words)
        
        # Technical term detection (simplified)
        technical_terms = [word for word in words if len(word) > 8 and any(c.isupper() for c in word)]
        technical_ratio = len(technical_terms) / len(words)
        
        # Complex word indicators
        complex_indicators = sum(1 for word in words if word in self.complexity_indicators)
        complexity_ratio = complex_indicators / len(words)
        
        # Combine metrics
        vocab_score = (vocabulary_diversity + long_word_ratio + technical_ratio + complexity_ratio) / 4.0
        
        return min(max(vocab_score, 0.0), 1.0)
    
    def _calculate_structure_complexity(self, text: str) -> float:
        """Calculate structural complexity"""
        # Paragraph variation
        paragraphs = text.split('\n\n')
        if len(paragraphs) < 2:
            return 0.2
        
        paragraph_lengths = [len(p.split()) for p in paragraphs if p.strip()]
        if not paragraph_lengths:
            return 0.2
        
        # Variation in paragraph lengths indicates structure complexity
        length_variation = np.std(paragraph_lengths) / np.mean(paragraph_lengths) if np.mean(paragraph_lengths) > 0 else 0
        
        # Presence of lists, citations, etc.
        structural_elements = 0
        if re.search(r'\d+\.', text):  # Numbered lists
            structural_elements += 0.1
        if re.search(r'[•\-]\s', text):  # Bullet points
            structural_elements += 0.1
        if re.search(r'\([^)]*\d{4}[^)]*\)', text):  # Citations
            structural_elements += 0.2
        if re.search(r'[A-Z][^.]*:', text):  # Headers/sections
            structural_elements += 0.1
        
        structure_score = min(length_variation + structural_elements, 1.0)
        
        return structure_score
    
    def _calculate_academic_complexity(self, text: str) -> float:
        """Calculate academic writing complexity"""
        text_lower = text.lower()
        
        # Academic indicators
        academic_count = sum(1 for indicator in self.academic_indicators if indicator in text_lower)
        academic_ratio = academic_count / len(self.academic_indicators)
        
        # Formal language indicators
        formal_patterns = [
            r'\bit is\b.*\bthat\b',  # "it is ... that" constructions
            r'\bthis study\b',
            r'\bthe present\b.*\bresearch\b',
            r'\baccording to\b',
            r'\bin conclusion\b',
            r'\bfurthermore\b',
            r'\bmoreover\b'
        ]
        
        formal_count = sum(1 for pattern in formal_patterns if re.search(pattern, text_lower))
        formal_ratio = formal_count / len(formal_patterns)
        
        # Citation patterns
        citation_patterns = [
            r'\([^)]*\d{4}[^)]*\)',  # (Author, 2023)
            r'\bet al\.',  # et al.
            r'\bibid\.',  # ibid.
        ]
        
        citation_count = sum(1 for pattern in citation_patterns if re.search(pattern, text))
        citation_ratio = min(citation_count / 10.0, 1.0)  # Normalize
        
        # Combine academic indicators
        academic_score = (academic_ratio + formal_ratio + citation_ratio) / 3.0
        
        return min(max(academic_score, 0.0), 1.0)
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text"""
        # Simple topic extraction based on frequent meaningful words
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Filter out common words
        stop_words = {
            'that', 'this', 'with', 'from', 'they', 'been', 'have', 'were', 'said',
            'each', 'which', 'their', 'time', 'will', 'about', 'would', 'there',
            'could', 'other', 'after', 'first', 'well', 'year', 'work', 'such',
            'make', 'them', 'these', 'many', 'then', 'more', 'very', 'when',
            'much', 'new', 'also', 'may', 'used', 'most', 'way', 'even', 'back',
            'only', 'good', 'water', 'long', 'little', 'right', 'old', 'too',
            'any', 'same', 'tell', 'boy', 'follow', 'came', 'want', 'show',
            'also', 'around', 'form', 'three', 'small', 'set', 'put', 'end',
            'why', 'again', 'turn', 'here', 'how', 'go', 'our', 'own', 'under',
            'name', 'very', 'through', 'just', 'where', 'much', 'good', 'think',
            'say', 'great', 'help', 'low', 'line', 'before', 'move', 'right',
            'too', 'means', 'old', 'any', 'same', 'tell', 'boy', 'follow',
            'came', 'want', 'show'
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 4]
        
        # Count frequency
        word_freq = Counter(filtered_words)
        
        # Return most common topics
        return [word for word, count in word_freq.most_common(10) if count > 2]
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts (often capitalized terms)"""
        # Find capitalized terms that might be concepts
        concepts = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Filter out common words that are often capitalized
        common_caps = {'The', 'This', 'That', 'These', 'Those', 'In', 'On', 'At', 'To', 'For', 'Of', 'With'}
        concepts = [c for c in concepts if c not in common_caps and len(c) > 3]
        
        # Count and return most frequent
        concept_freq = Counter(concepts)
        return [concept for concept, count in concept_freq.most_common(10)]
    
    def _identify_headers(self, text_chunks: List[str]) -> List[str]:
        """Identify potential headers in the text"""
        headers = []
        
        for chunk in text_chunks:
            lines = chunk.split('\n')
            for line in lines:
                line = line.strip()
                # Potential header patterns
                if (len(line) < 100 and 
                    (re.match(r'^\d+\.?\s+[A-Z]', line) or  # Numbered sections
                     re.match(r'^[A-Z][A-Z\s]+$', line) or  # ALL CAPS
                     (line.endswith(':') and len(line.split()) < 6))):  # Short lines ending with :
                    headers.append(line)
        
        return headers[:10]  # Return first 10 headers
    
    def _count_citations(self, text: str) -> int:
        """Count citation-like patterns in text"""
        citation_patterns = [
            r'\([^)]*\d{4}[^)]*\)',  # (Author, 2023)
            r'\[[^\]]*\d{4}[^\]]*\]',  # [Author, 2023]
            r'\bet al\.',  # et al.
        ]
        
        citation_count = 0
        for pattern in citation_patterns:
            citation_count += len(re.findall(pattern, text))
        
        return citation_count
    
    def _classify_document_type(self, text: str) -> str:
        """Classify the type of document"""
        text_lower = text.lower()
        
        # Research paper indicators
        research_indicators = ['abstract', 'methodology', 'results', 'conclusion', 'references']
        research_score = sum(1 for indicator in research_indicators if indicator in text_lower)
        
        # Textbook indicators
        textbook_indicators = ['chapter', 'exercise', 'problems', 'summary', 'review']
        textbook_score = sum(1 for indicator in textbook_indicators if indicator in text_lower)
        
        # Technical manual indicators
        manual_indicators = ['installation', 'configuration', 'steps', 'procedure', 'guide']
        manual_score = sum(1 for indicator in manual_indicators if indicator in text_lower)
        
        # Presentation indicators
        presentation_indicators = ['slide', 'presentation', 'overview', 'agenda']
        presentation_score = sum(1 for indicator in presentation_indicators if indicator in text_lower)
        
        # Determine document type
        scores = {
            'research_paper': research_score,
            'textbook': textbook_score,
            'technical_manual': manual_score,
            'presentation': presentation_score
        }
        
        max_score = max(scores.values())
        if max_score == 0:
            return 'general_document'
        
        return max(scores, key=scores.get)
