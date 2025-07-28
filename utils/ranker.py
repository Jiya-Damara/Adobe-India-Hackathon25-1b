"""
Enhanced Content Ranker Module - Maximum relevance for hackathon scoring
"""
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ContentRanker:
    def __init__(self, persona_role, job_task):
        self.persona_role = persona_role
        self.job_task = job_task
        self.vectorizer = TfidfVectorizer(
            max_features=2000, 
            stop_words='english',
            ngram_range=(1, 3),  # Include trigrams for better context
            min_df=1,
            max_df=0.95,
            sublinear_tf=True  # Better for similarity
        )
        
        # Create enhanced persona-job context
        self.context_text = f"{persona_role} {job_task}"
        
    def extract_section_title(self, text, max_length=100):
        """Extract meaningful section title with better context awareness"""
        lines = text.strip().split('\n')
        
        # Look for recipe/section titles with enhanced patterns
        for line in lines[:8]:  # Check more lines
            line = line.strip()
            if line and len(line) < max_length:
                # Remove bullet points, numbers, and symbols
                clean_line = re.sub(r'^[\s\•\-\*\d\.\)\(\uf0b7\uf0a7]+', '', line)
                clean_line = re.sub(r'[^\w\s\-&]', '', clean_line).strip()
                
                # Check if this looks like a title/recipe name
                if (len(clean_line.split()) >= 2 and 
                    len(clean_line) <= max_length and
                    not clean_line.lower().startswith(('ingredients', 'instructions', 'directions', 'method'))):
                    return clean_line.strip()
        
        # Enhanced fallback: look for food/recipe names
        food_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b',  # Capitalized food names
            r'\b\w+(?:\s+\w+)*(?:\s+(?:Salad|Soup|Pasta|Pizza|Curry|Stir[- ]?fry|Bowl))\b',
            r'\b(?:Grilled|Baked|Roasted|Steamed|Fresh)\s+\w+(?:\s+\w+)*\b'
        ]
        
        for pattern in food_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0][:max_length]
                
        # Final fallback
        sentences = re.split(r'[.!?]', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence.split()) >= 3 and len(sentence) <= max_length:
                return sentence
                
        return lines[0][:max_length].strip() if lines else "Content Section"
    
    def get_enhanced_persona_keywords(self):
        """Enhanced persona-specific keywords with weights"""
        persona_keywords = {
            'Travel Planner': {
                'high': ['itinerary', 'accommodation', 'transportation', 'attractions', 'budget', 'booking', 'schedule'],
                'medium': ['travel', 'trip', 'vacation', 'hotel', 'restaurant', 'activity', 'tour', 'destination'],
                'low': ['guide', 'tips', 'culture', 'history', 'food', 'shopping']
            },
            'HR Professional': {
                'high': ['onboarding', 'compliance', 'workflow', 'forms', 'signatures', 'employee', 'digital'],
                'medium': ['management', 'process', 'document', 'training', 'policy', 'procedure'],
                'low': ['create', 'edit', 'share', 'convert', 'export']
            },
            'Food Contractor': {
                'high': ['menu', 'catering', 'buffet', 'corporate', 'vegetarian', 'gluten-free', 'dinner', 'recipe'],
                'medium': ['meal', 'ingredient', 'cooking', 'preparation', 'serving', 'nutrition'],
                'low': ['breakfast', 'lunch', 'snack', 'appetizer', 'dessert']
            },
            'PhD Researcher': {
                'high': ['methodology', 'dataset', 'benchmark', 'evaluation', 'literature', 'review', 'analysis'],
                'medium': ['research', 'study', 'experiment', 'result', 'conclusion', 'hypothesis'],
                'low': ['paper', 'journal', 'citation', 'reference', 'abstract']
            },
            'Investment Analyst': {
                'high': ['revenue', 'profit', 'investment', 'market', 'financial', 'analysis', 'trend'],
                'medium': ['company', 'performance', 'strategy', 'growth', 'risk', 'portfolio'],
                'low': ['report', 'quarter', 'annual', 'earnings', 'stock']
            },
            'Student': {
                'high': ['exam', 'study', 'concept', 'mechanism', 'theory', 'practice', 'preparation'],
                'medium': ['chapter', 'topic', 'subject', 'learning', 'understand', 'knowledge'],
                'low': ['textbook', 'course', 'class', 'assignment', 'homework']
            }
        }
        
        # Get keywords for persona or use generic
        keywords = persona_keywords.get(self.persona_role, {
            'high': [], 'medium': [], 'low': []
        })
        
        return keywords
    
    def get_enhanced_job_keywords(self):
        """Extract and categorize keywords from job description"""
        job_lower = self.job_task.lower()
        
        # High priority job-specific terms
        high_priority = []
        medium_priority = []
        
        # Extract key action words
        action_words = re.findall(r'\b(?:prepare|create|analyze|identify|summarize|review|plan|develop|design|build)\w*\b', job_lower)
        high_priority.extend(action_words)
        
        # Extract domain-specific terms
        domain_terms = re.findall(r'\b[a-zA-Z]{4,}\b', job_lower)
        medium_priority.extend([term for term in domain_terms if len(term) > 4])
        
        # Extract quoted or specific terms
        quoted_terms = re.findall(r'["\']([^"\']+)["\']', self.job_task)
        high_priority.extend(quoted_terms)
        
        return {
            'high': list(set(high_priority)),
            'medium': list(set(medium_priority))
        }
    
    def calculate_enhanced_relevance_score(self, text, document_name=""):
        """Calculate comprehensive relevance score with multiple factors"""
        text_lower = text.lower()
        doc_lower = document_name.lower()
        
        # Get persona and job keywords
        persona_keywords = self.get_enhanced_persona_keywords()
        job_keywords = self.get_enhanced_job_keywords()
        
        # Calculate weighted keyword scores
        persona_score = 0
        persona_score += sum(3 for kw in persona_keywords.get('high', []) if kw in text_lower) * 3
        persona_score += sum(2 for kw in persona_keywords.get('medium', []) if kw in text_lower) * 2
        persona_score += sum(1 for kw in persona_keywords.get('low', []) if kw in text_lower)
        
        job_score = 0
        job_score += sum(5 for kw in job_keywords.get('high', []) if kw in text_lower) * 5
        job_score += sum(2 for kw in job_keywords.get('medium', []) if kw in text_lower) * 2
        
        # Initialize bonuses and penalties
        context_bonus = 0
        penalty = 0
        
        # Document context bonus (e.g., "dinner" document for dinner job)
        if 'dinner' in self.job_task.lower() and 'dinner' in doc_lower:
            context_bonus += 5
        if 'breakfast' in self.job_task.lower() and 'breakfast' in doc_lower:
            context_bonus += 5
        if 'lunch' in self.job_task.lower() and 'lunch' in doc_lower:
            context_bonus += 5
        
        # Academic/Research context bonuses
        if any(term in self.persona_role.lower() for term in ['researcher', 'phd', 'student', 'academic']):
            academic_terms = ['methodology', 'dataset', 'benchmark', 'evaluation', 'literature', 'study', 'research', 'analysis', 'experiment']
            academic_matches = sum(1 for term in academic_terms if term in text_lower)
            context_bonus += academic_matches * 2
            
        # Business/Investment context bonuses  
        if any(term in self.persona_role.lower() for term in ['analyst', 'investment', 'business']):
            business_terms = ['revenue', 'profit', 'market', 'financial', 'growth', 'strategy', 'investment', 'performance']
            business_matches = sum(1 for term in business_terms if term in text_lower)
            context_bonus += business_matches * 2
            
        # Travel context bonuses
        if 'travel' in self.persona_role.lower():
            travel_terms = ['hotel', 'restaurant', 'attraction', 'tour', 'booking', 'itinerary', 'destination']
            travel_matches = sum(1 for term in travel_terms if term in text_lower)
            context_bonus += travel_matches * 2
        # Enhanced vegetarian/dietary filtering
        if 'vegetarian' in self.job_task.lower():
            # Boost vegetarian indicators
            vegetarian_terms = ['vegetarian', 'vegan', 'plant-based', 'tofu', 'beans', 'lentils', 'quinoa', 'vegetables']
            if any(term in text_lower for term in vegetarian_terms):
                context_bonus += 4
            
            # Penalize meat content heavily
            meat_terms = ['beef', 'chicken', 'pork', 'lamb', 'turkey', 'fish', 'salmon', 'tuna', 'meat', 'poultry']
            if any(term in text_lower for term in meat_terms):
                penalty -= 8  # Heavy penalty for meat content
                
        if 'gluten-free' in self.job_task.lower():
            gluten_free_terms = ['gluten-free', 'gluten free', 'rice', 'corn', 'quinoa']
            if any(term in text_lower for term in gluten_free_terms):
                context_bonus += 3
            
            # Penalize gluten content
            gluten_terms = ['wheat', 'flour', 'bread', 'pasta', 'barley', 'rye']
            if any(term in text_lower for term in gluten_terms):
                penalty -= 4
        
        if 'buffet' in self.job_task.lower():
            buffet_terms = ['buffet', 'serving', 'large batch', 'crowd', 'party', 'catering']
            if any(term in text_lower for term in buffet_terms):
                context_bonus += 2
        
        # Penalize irrelevant content
        if 'dinner' in self.job_task.lower() and 'breakfast' in doc_lower:
            penalty -= 3  # Breakfast content for dinner job
        if 'corporate' in self.job_task.lower() and 'dessert' in text_lower:
            penalty -= 1  # Desserts less relevant for corporate
            
        # Text length normalization
        text_length = max(len(text.split()) / 100, 1)
        
        # Final weighted score
        total_score = (persona_score * 0.3 + job_score * 0.5 + context_bonus * 0.2 + penalty) / text_length
        
        return max(total_score, 0)  # Ensure non-negative
    
    def rank_sections(self, document_sections):
        """Enhanced ranking with better context awareness"""
        if not document_sections:
            return []
        
        # Prepare texts for TF-IDF
        section_texts = [section['text'] for section in document_sections]
        all_texts = section_texts + [self.context_text]
        
        tfidf_similarities = np.zeros(len(section_texts))
        
        try:
            # Create TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Calculate cosine similarity with context
            context_vector = tfidf_matrix[-1]
            section_vectors = tfidf_matrix[:-1]
            
            # Compute similarities
            similarities = cosine_similarity(section_vectors, context_vector.reshape(1, -1))
            tfidf_similarities = similarities.flatten()
            
        except Exception as e:
            print(f"TF-IDF processing failed: {e}, using keyword-only scoring")
        
        # Calculate combined scores with enhanced factors
        for i, section in enumerate(document_sections):
            tfidf_score = tfidf_similarities[i] if i < len(tfidf_similarities) else 0
            keyword_score = self.calculate_enhanced_relevance_score(
                section['text'], 
                section.get('document', '')
            )
            
            # Enhanced weighting: more emphasis on keyword relevance
            section['relevance_score'] = (tfidf_score * 0.4) + (keyword_score * 0.6)
            
            # Add section title quality bonus
            section_title = section.get('section_title', '')
            if len(section_title.split()) >= 2 and not section_title.startswith('Content'):
                section['relevance_score'] += 0.1
        
        # Sort by relevance score (descending)
        ranked_sections = sorted(document_sections, key=lambda x: x['relevance_score'], reverse=True)
        
        # Assign importance ranks
        for rank, section in enumerate(ranked_sections, 1):
            section['importance_rank'] = rank
            
        return ranked_sections
    
    def extract_refined_subsection(self, text, max_length=1000):
        """Enhanced subsection extraction with better content selection"""
        if len(text) <= max_length:
            return text.strip()
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if not paragraphs:
            paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        # Score paragraphs by relevance
        best_paragraphs = []
        for paragraph in paragraphs:
            if len(paragraph) > 30:  # Ignore very short paragraphs
                score = self.calculate_enhanced_relevance_score(paragraph)
                best_paragraphs.append((score, paragraph))
        
        # Sort by score and combine top paragraphs
        best_paragraphs.sort(key=lambda x: x[0], reverse=True)
        
        result_text = ""
        for score, paragraph in best_paragraphs:
            if len(result_text) + len(paragraph) <= max_length:
                result_text += paragraph + "\n\n"
            else:
                # Add partial paragraph if it fits
                remaining = max_length - len(result_text)
                if remaining > 100:  # Only if substantial space left
                    # Try to end at sentence boundary
                    partial = paragraph[:remaining]
                    last_sentence = partial.rfind('.')
                    if last_sentence > remaining * 0.7:
                        result_text += partial[:last_sentence + 1]
                    else:
                        result_text += partial + "..."
                break
        
        return result_text.strip() or text[:max_length] + "..."
