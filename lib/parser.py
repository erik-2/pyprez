"""
Parser Markdown pour les présentations
"""

from typing import Dict, List, Tuple
from .models import Slide, Section, Presentation
from .config import MARKERS, MD_PREFIXES, SLIDE_TYPES


def parse_metadata(lines: List[str], start: int) -> Tuple[Dict[str, str], int]:
    """Parse les métadonnées YAML en début de fichier"""
    metadata = {}
    i = start
    
    if i < len(lines) and lines[i].strip() == '---':
        i += 1
        while i < len(lines) and lines[i].strip() != '---':
            if ':' in lines[i]:
                key, value = lines[i].split(':', 1)
                metadata[key.strip()] = value.strip()
            i += 1
        i += 1  # Passer le --- final
    
    return metadata, i


def parse_presentation(md_content: str) -> Presentation:
    """Parse le Markdown et retourne une Presentation"""
    lines = md_content.split('\n')
    slides = []
    current_slide = None
    current_section = None  # 'main', 'details', 'questions'
    
    # Parser les métadonnées
    metadata, i = parse_metadata(lines, 0)
    just_after_title = False 
    # Parser les slides
    while i < len(lines):
        line = lines[i].strip()
        
        # Nouvelle slide de titre (# )
        if line.startswith(MD_PREFIXES['h1']):
            if current_slide:
                slides.append(current_slide)
            current_slide = Slide(
                slide_type=SLIDE_TYPES['title'],
                title=line[len(MD_PREFIXES['h1']):].strip(),
                has_annexes=False
            )
            current_section = 'main'
            just_after_title = False
        
        # Nouvelle slide de contenu (## )
        elif line.startswith(MD_PREFIXES['h2']):
            if current_slide:
                slides.append(current_slide)
            current_slide = Slide(
                slide_type=SLIDE_TYPES['content'],
                number=len(slides) + 1,
                title=line[len(MD_PREFIXES['h2']):].strip()
            )
            current_section = 'main'
            just_after_title = True


        
        # Nouvelle slide d'image (### Image: )
        elif line.startswith(MD_PREFIXES['image']):
            if current_slide:
                slides.append(current_slide)
            current_slide = Slide(
                slide_type=SLIDE_TYPES['image'],
                number=len(slides) + 1,
                image_url=line[len(MD_PREFIXES['image']):].strip(),
                has_annexes=False
            )
            current_section = 'main'
            just_after_title = False
        
        # Section détails
        elif line == MARKERS['details']:
            current_section = 'details'
        
        # Section questions
        elif line == MARKERS['questions']:
            current_section = 'questions'
        
        # Option no-annexes
        elif line == MARKERS['no_annexes']:
            if current_slide:
                current_slide.has_annexes = False
        
        # Sous-titre (> ) seulement juste après le titre
        elif line.startswith('> ') and current_section == 'main' and just_after_title:
            if current_slide:
                current_slide.subtitle = line[2:].strip()
            just_after_title = False  # AJOUTER

        # Blockquote (> ) ailleurs dans main
        elif line.startswith('> ') and current_section == 'main' and not just_after_title:
            if current_slide:
                current_slide.content.append({'type': 'blockquote', 'text': line[2:].strip()})
    
        elif line.startswith(MD_PREFIXES['h3']) and current_section == 'main' :
            if current_slide:
                current_slide.content.append({'type': 'h3', 'text': line[len(MD_PREFIXES['h3']):].strip()})
            just_after_title = False
        # Caption d'image
        elif line.startswith(MD_PREFIXES['caption']) and current_slide and current_slide.slide_type == SLIDE_TYPES['image']:
            current_slide.image_caption = line[len(MD_PREFIXES['caption']):].strip()
            just_after_title = False
        
        # Points de liste (- ou *)
        elif line.startswith(MD_PREFIXES['list_item'][0]) or line.startswith(MD_PREFIXES['list_item'][1]):
            just_after_title = False
            if current_slide:
                content = line[2:].strip()
                if current_section == 'main':
                    current_slide.content.append(content)
                elif current_section == 'details':
                    current_slide.details.append(content)
                elif current_section == 'questions':
                    current_slide.questions.append(content)
        
        # Paragraphes (dans détails uniquement)
        elif line and not line.startswith('#') and current_section == 'details':
            if current_slide:
                current_slide.details.append(line)
        
        i += 1
    
    # Ajouter la dernière slide
    if current_slide:
        slides.append(current_slide)
    
    return Presentation(metadata=metadata, slides=slides)


def parse_details_only(md_content: str) -> Tuple[Dict[str, str], List[Section]]:
    """Parse le Markdown et extrait uniquement les sections avec détails"""
    lines = md_content.split('\n')
    sections = []
    current_section = None
    in_details = False
    
    # Parser les métadonnées
    metadata, i = parse_metadata(lines, 0)
    
    # Parser les sections
    while i < len(lines):
        line = lines[i].strip()
        
        # Nouveau titre de section
        if line.startswith('#'):
            if current_section and current_section.details:
                sections.append(current_section)
            
            # Déterminer le niveau
            level = 0
            while level < len(line) and line[level] == '#':
                level += 1
            
            title = line[level:].strip()
            current_section = Section(title=title, level=level)
            in_details = False
        
        # Section détails
        elif line == MARKERS['details']:
            in_details = True
        
        # Sortie de la section détails
        elif line == MARKERS['questions'] or line == MARKERS['no_annexes']:
            in_details = False
        
        # Contenu des détails
        elif in_details and line and not line.startswith('#'):
            if current_section:
                detail = _parse_detail_line(line)
                current_section.details.append(detail)
        
        i += 1
    
    # Ajouter la dernière section
    if current_section and current_section.details:
        sections.append(current_section)
    
    return metadata, sections


def _parse_detail_line(line: str) -> Dict[str, str]:
    """Parse une ligne de détail et retourne son type et contenu"""
    import re
   
    # Image Markdown: ![légende](url)
    img_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', line)
    if img_match:
        return {
            'type': 'image',
            'alt': img_match.group(1),
            'url': img_match.group(2)
        }
    
    # Sous-titre en gras sans deux-points
    if line.startswith('**') and line.endswith('**') and ':' not in line:
        return {'type': 'subtitle', 'content': line[2:-2]}
    
    # Sous-titre en gras avec deux-points à la fin
    if line.startswith('**') and line.endswith(':'):
        return {'type': 'subtitle', 'content': line[2:-1]}
    
    # Point de liste
    if line.startswith('- ') or line.startswith('* '):
        return {'type': 'list_item', 'content': line[2:]}

    # Blockquote: > texte
    if line.startswith('> '):
        return {'type': 'blockquote', 'content': line[2:]}

    # Référence: [@ref auteurs="..." titre="..." ...]
    ref_match = re.match(r'^\[@ref\s+(.+)\]$', line.strip())
    if ref_match:
        attrs = {}
        for m in re.finditer(r'(\w+)="([^"]*)"', ref_match.group(1)):
            attrs[m.group(1)] = m.group(2)
        return {'type': 'reference', **attrs}
    
    # Paragraphe normal
    return {'type': 'paragraph', 'content': line}
