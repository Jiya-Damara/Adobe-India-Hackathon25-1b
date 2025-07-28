"""
Enhanced text extractor with section detection capabilities
"""
import fitz  # PyMuPDF
import re

class EnhancedTextExtractor:
    def __init__(self):
        self.section_patterns = [
            # Food/Recipe patterns
            r'^[A-Z][a-zA-Z\s&\'-]{3,50}(?:\s+(?:Salad|Soup|Pasta|Pizza|Curry|Bowl|Dish|Recipe))?$',
            # Business/Academic patterns
            r'^\d+\.\s+[A-Z][A-Za-z\s\-&]{5,60}$',  # Numbered sections
            r'^[A-Z\s\-&]{8,50}$',  # ALL CAPS headings
            r'^[A-Z][A-Za-z\s\-&]{10,60}$',  # Title case headings
            # Content structure patterns
            r'^\•\s+[A-Z][A-Za-z\s\-&]{5,50}$',  # Bullet point headings
            r'^Introduction|^Overview|^Summary|^Conclusion',  # Common section headers
            # Food-specific patterns
            r'^(?:Grilled|Baked|Roasted|Fresh|Steamed|Pan[- ]?fried)\s+[A-Z][a-zA-Z\s]{5,40}$',
            r'^[A-Z][a-zA-Z\s&\'-]+(?:\s+with\s+[A-Z][a-zA-Z\s&]+)?$'  # "Chicken with Vegetables"
        ]
    
    def extract_text_with_sections(self, pdf_path):
        """
        Enhanced PDF text extraction with section detection
        
        Returns:
            List of dicts with page_number, text, potential_sections
        """
        doc = fitz.open(pdf_path)
        extracted_pages = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Get text with layout preservation
            text = page.get_text()
            
            if text.strip():
                # Detect sections within the page
                sections = self.detect_sections(text)
                
                extracted_pages.append({
                    "page_number": page_num + 1,
                    "text": text,
                    "sections": sections,
                    "word_count": len(text.split())
                })

        doc.close()
        return extracted_pages
    
    def detect_sections(self, text):
        """Detect potential section headers in text"""
        lines = text.split('\n')
        sections = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if self.is_section_header(line):
                # Extract some content following the header
                content_lines = lines[i:i+10]  # Next 10 lines
                content = '\n'.join(content_lines)
                
                sections.append({
                    'title': line,
                    'content': content,
                    'line_number': i + 1
                })
        
        return sections
    
    def is_section_header(self, line):
        """Enhanced section header detection with food/content awareness"""
        if not line or len(line) < 3:
            return False
        
        # Remove bullet points and symbols
        clean_line = re.sub(r'^[\s\•\-\*\uf0b7\uf0a7\d\.\)\(]+', '', line).strip()
        
        if not clean_line:
            return False
        
        # Check against enhanced patterns
        for pattern in self.section_patterns:
            if re.match(pattern, clean_line):
                return True
        
        # Additional heuristics for food content
        if (3 <= len(clean_line) <= 80 and 
            len(clean_line.split()) >= 2 and
            not clean_line.lower().startswith(('ingredients', 'instructions', 'directions', 'method', 'serves', 'prep time')) and
            not re.match(r'^\d+\s+(cups?|tablespoons?|teaspoons?|pounds?|ounces?)', clean_line.lower())):
            
            # Check for title-like characteristics
            words = clean_line.split()
            if (len(words) >= 2 and 
                words[0][0].isupper() and 
                not clean_line.endswith('.') and
                not any(word.lower() in ['the', 'and', 'or', 'but', 'with', 'for', 'in', 'on', 'at'] for word in words[:2])):
                return True
                
        return False
    
    def get_page_sections_for_ranking(self, pdf_path, max_pages_per_doc=5):
        """
        Extract pages and prepare sections for ranking
        
        Returns:
            List of section dicts ready for ranking
        """
        pages = self.extract_text_with_sections(pdf_path)
        sections_for_ranking = []
        
        # Limit pages to avoid processing too much content
        limited_pages = pages[:max_pages_per_doc]
        
        for page in limited_pages:
            if page['sections']:
                # Use detected sections
                for section in page['sections']:
                    sections_for_ranking.append({
                        'page_number': page['page_number'],
                        'text': section['content'],
                        'section_title': section['title'],
                        'source': 'detected_section'
                    })
            else:
                # Fallback: use page content as section
                sections_for_ranking.append({
                    'page_number': page['page_number'],
                    'text': page['text'],
                    'section_title': self.generate_section_title(page['text']),
                    'source': 'page_content'
                })
        
        return sections_for_ranking
    
    def generate_section_title(self, text):
        """Enhanced section title generation with content awareness"""
        lines = text.strip().split('\n')
        
        # Look for recipe/content titles in first few lines
        for line in lines[:5]:
            line = line.strip()
            if line and 3 <= len(line) <= 80:
                # Clean up the line
                clean_title = re.sub(r'^[\s\•\-\*\uf0b7\uf0a7\d\.\)]+', '', line)
                clean_title = re.sub(r'[^\w\s\-&\']', '', clean_title).strip()
                
                # Check if this looks like a good title
                if (len(clean_title.split()) >= 2 and 
                    len(clean_title) <= 60 and
                    not clean_title.lower().startswith(('ingredients', 'instructions', 'directions'))):
                    return clean_title
        
        # Enhanced pattern matching for food items
        food_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Salad|Soup|Pasta|Pizza|Curry|Bowl|Dish|Recipe))\b',
            r'\b(?:Grilled|Baked|Roasted|Fresh|Steamed|Pan[- ]?fried)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
            r'\b[A-Z][a-z]+\s+(?:with|and)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        ]
        
        for pattern in food_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0][:60]
        
        # Look for capitalized food names
        cap_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b'
        matches = re.findall(cap_pattern, text)
        for match in matches:
            if (len(match.split()) >= 2 and 
                len(match) <= 50 and
                not match.lower() in ['The United', 'South Of', 'North America']):
                return match
        
        # Fallback: use first meaningful words
        words = [w for w in text.split() if len(w) > 2][:6]
        if words:
            title = ' '.join(words)
            return title[:50] + ('...' if len(title) > 50 else '')
        
        return "Content Section"

# Legacy function for compatibility
def extract_text_from_pdf(pdf_path):
    """Original function for backward compatibility"""
    extractor = EnhancedTextExtractor()
    pages = extractor.extract_text_with_sections(pdf_path)
    
    # Convert to original format
    return [{'page_number': p['page_number'], 'text': p['text']} for p in pages]
