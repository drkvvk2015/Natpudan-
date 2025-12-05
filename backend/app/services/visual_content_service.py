"""
Medical Visual Content Service
Fetches relevant medical images and videos from trusted online sources
"""

import logging
import re
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class MedicalVisualContentService:
    """Service to find relevant medical images and videos"""
    
    def __init__(self):
        # Trusted medical content sources
        self.image_sources = {
            'medlineplus': 'https://medlineplus.gov/images/',
            'nih': 'https://www.nih.gov/',
            'cdc': 'https://www.cdc.gov/',
            'who': 'https://www.who.int/',
            'wikimedia_commons': 'https://commons.wikimedia.org/wiki/'
        }
        
        self.video_sources = {
            'youtube_medical': 'https://www.youtube.com/results?search_query=',
            'medlineplus_videos': 'https://medlineplus.gov/videos/',
            'nih_videos': 'https://www.nih.gov/health-information/nih-multimedia-video',
            'osmosis': 'https://www.osmosis.org/search?q=',
            'khan_academy': 'https://www.khanacademy.org/search?page_search_query='
        }
    
    def get_visual_resources(self, query: str, medical_condition: Optional[str] = None) -> Dict[str, List[Dict[str, str]]]:
        """
        Get relevant medical images and videos for a query
        
        Args:
            query: Search query
            medical_condition: Specific medical condition name if identified
            
        Returns:
            Dictionary with 'images' and 'videos' lists
        """
        try:
            # Extract medical terms from query
            search_term = self._extract_medical_terms(query, medical_condition)
            
            images = self._generate_image_links(search_term, query)
            videos = self._generate_video_links(search_term, query)
            
            return {
                'images': images,
                'videos': videos,
                'search_term': search_term
            }
        except Exception as e:
            logger.error(f"Error getting visual resources: {e}")
            return {'images': [], 'videos': [], 'search_term': query}
    
    def _extract_medical_terms(self, query: str, medical_condition: Optional[str] = None) -> str:
        """Extract the most relevant medical term from query"""
        if medical_condition:
            # Clean up medical condition - remove database references
            import re
            # Extract condition name from patterns like "Medical Database - Gastroenteritis (Stomach Flu)"
            condition_match = re.search(r'(?:Medical Database|Local Database)\s*-\s*(.+?)(?:\s*\(|$)', medical_condition)
            if condition_match:
                return condition_match.group(1).strip()
            # Extract from patterns like "**Pneumonia** (ICD-10: J18)"
            condition_match = re.search(r'\*\*([^*]+)\*\*', medical_condition)
            if condition_match:
                return condition_match.group(1).strip()
            return medical_condition
        
        # Common medical keywords to prioritize (including symptoms)
        medical_keywords = [
            'fever', 'cough', 'pain', 'headache', 'nausea', 'diarrhea',
            'diabetes', 'hypertension', 'asthma', 'copd', 'pneumonia',
            'sepsis', 'heart attack', 'stroke', 'cancer', 'arthritis',
            'infection', 'inflammation', 'fracture', 'wound', 'surgery',
            'gastroenteritis', 'uti', 'covid', 'flu', 'influenza',
            'anatomy', 'physiology', 'pathology', 'treatment', 'diagnosis',
            'medication', 'drug', 'antibiotic', 'vaccine', 'therapy'
        ]
        
        query_lower = query.lower()
        
        # Find matching medical terms
        for keyword in medical_keywords:
            if keyword in query_lower:
                # Return the keyword and surrounding context
                words = query_lower.split()
                if keyword in words:
                    idx = words.index(keyword)
                    # Get keyword and one word before/after if available
                    context = []
                    if idx > 0:
                        context.append(words[idx-1])
                    context.append(keyword)
                    if idx < len(words) - 1:
                        context.append(words[idx+1])
                    return ' '.join(context)
                return keyword
        
        # If no specific keyword, return first few words
        words = query.split()[:3]
        return ' '.join(words)
    
    def _generate_image_links(self, search_term: str, original_query: str) -> List[Dict[str, str]]:
        """Generate image search links from trusted medical sources"""
        images = []
        encoded_term = quote_plus(search_term)
        encoded_medical = quote_plus(f"{search_term} medical anatomy")
        
        # MedlinePlus Images
        images.append({
            'source': 'MedlinePlus',
            'title': f'{search_term.title()} - Medical Images',
            'url': f'https://medlineplus.gov/ency/imagepages.htm',
            'icon': '[MEDICAL]',
            'description': 'Trusted medical encyclopedia with anatomical illustrations',
            'type': 'image_gallery'
        })
        
        # Google Images (Medical Sites Only)
        images.append({
            'source': 'Medical Image Search',
            'title': f'{search_term.title()} - Medical Diagrams',
            'url': f'https://www.google.com/search?q={encoded_medical}&tbm=isch&tbs=sur:f',
            'icon': '[RESEARCH]',
            'description': 'Medical diagrams and anatomical images',
            'type': 'image_search'
        })
        
        # Wikimedia Commons (Medical)
        images.append({
            'source': 'Wikimedia Medical',
            'title': f'{search_term.title()} - Educational Images',
            'url': f'https://commons.wikimedia.org/w/index.php?search={encoded_term}+medical&title=Special:MediaSearch&type=image',
            'icon': '[BOOK]',
            'description': 'Free medical and anatomical images',
            'type': 'image_gallery'
        })
        
        # CDC Images (if relevant)
        if any(term in search_term.lower() for term in ['infection', 'disease', 'vaccine', 'outbreak']):
            images.append({
                'source': 'CDC',
                'title': f'{search_term.title()} - Public Health Images',
                'url': f'https://www.cdc.gov/search.htm?query={encoded_term}',
                'icon': '[PUBLIC_HEALTH]',
                'description': 'Public health and disease information',
                'type': 'resource_page'
            })
        
        return images
    
    def _generate_video_links(self, search_term: str, original_query: str) -> List[Dict[str, str]]:
        """Generate educational video links from trusted sources"""
        videos = []
        encoded_term = quote_plus(search_term)
        encoded_medical = quote_plus(f"{search_term} medical education")
        
        # Osmosis - High-quality medical videos
        videos.append({
            'source': 'Osmosis',
            'title': f'{search_term.title()} - Medical Video',
            'url': f'https://www.osmosis.org/search?q={encoded_term}',
            'icon': '[EDUCATION]',
            'description': 'Medical education videos for healthcare professionals',
            'type': 'educational_video',
            'channel': 'Osmosis Medical Education'
        })
        
        # YouTube - Medical channels
        videos.append({
            'source': 'YouTube Medical',
            'title': f'{search_term.title()} - Educational Videos',
            'url': f'https://www.youtube.com/results?search_query={encoded_medical}',
            'icon': '[VIDEO]',
            'description': 'Medical education videos from trusted channels',
            'type': 'video_search',
            'channel': 'Various Medical Educators'
        })
        
        # MedlinePlus Videos
        videos.append({
            'source': 'MedlinePlus Videos',
            'title': f'{search_term.title()} - Patient Education',
            'url': f'https://medlineplus.gov/videos/',
            'icon': '[PATIENT_ED]',
            'description': 'Patient education videos from NIH',
            'type': 'patient_education',
            'channel': 'MedlinePlus (NIH)'
        })
        
        # Khan Academy (if anatomy/physiology related)
        if any(term in search_term.lower() for term in ['anatomy', 'physiology', 'body', 'system', 'organ']):
            videos.append({
                'source': 'Khan Academy',
                'title': f'{search_term.title()} - Anatomy & Physiology',
                'url': f'https://www.khanacademy.org/search?page_search_query={encoded_term}',
                'icon': '[ANATOMY]',
                'description': 'Anatomy and physiology educational videos',
                'type': 'educational_video',
                'channel': 'Khan Academy Medicine'
            })
        
        # Armando Hasudungan (Medical illustrations)
        videos.append({
            'source': 'Medical Illustrations',
            'title': f'{search_term.title()} - Animated Explanation',
            'url': f'https://www.youtube.com/results?search_query=armando+hasudungan+{encoded_term}',
            'icon': '[ILLUSTRATION]',
            'description': 'Hand-drawn medical illustrations and animations',
            'type': 'educational_video',
            'channel': 'Armando Hasudungan'
        })
        
        # Ninja Nerd (Detailed medical lectures)
        videos.append({
            'source': 'Ninja Nerd',
            'title': f'{search_term.title()} - Detailed Lecture',
            'url': f'https://www.youtube.com/results?search_query=ninja+nerd+{encoded_term}',
            'icon': '[LECTURE]',
            'description': 'In-depth medical lectures with visual aids',
            'type': 'educational_video',
            'channel': 'Ninja Nerd'
        })
        
        return videos
    
    def format_visual_resources_markdown(self, resources: Dict[str, Any]) -> str:
        """Format visual resources as markdown for chat response"""
        if not resources or (not resources.get('images') and not resources.get('videos')):
            return ""
        
        markdown = "\n\n[TV] **VISUAL LEARNING RESOURCES**\n\n"
        markdown += f"**Search Term:** {resources.get('search_term', 'N/A')}\n\n"
        
        # Add images section
        if resources.get('images'):
            markdown += "### [IMAGE] Medical Images & Diagrams\n\n"
            for img in resources['images']:
                markdown += f"**{img['icon']} [{img['source']}]({img['url']})** - {img['title']}\n"
                markdown += f"   _{img['description']}_\n\n"
        
        # Add videos section
        if resources.get('videos'):
            markdown += "### [CINEMA] Educational Videos\n\n"
            for video in resources['videos']:
                markdown += f"**{video['icon']} [{video['source']}]({video['url']})** - {video['title']}\n"
                markdown += f"   _{video['description']}_"
                if video.get('channel'):
                    markdown += f" | Channel: {video['channel']}"
                markdown += "\n\n"
        
        markdown += "---\n\n"
        markdown += "[TIP] **Tip:** Visual learning enhances understanding - watch videos for procedures and view diagrams for anatomy!\n\n"
        
        return markdown


# Global instance
_visual_service = None

def get_visual_service() -> MedicalVisualContentService:
    """Get or create visual service instance"""
    global _visual_service
    if _visual_service is None:
        _visual_service = MedicalVisualContentService()
    return _visual_service
