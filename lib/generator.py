"""
Générateur HTML pour les présentations
"""

import re
from pathlib import Path
from typing import Optional

from .models import Slide, Presentation
from .config import CSS_FONTS, ASSETS, THEMES, DEFAULT_THEME


def resolve_image_url(url: str) -> str:
    """Résout l'URL d'une image (locale ou externe)"""
    if url.startswith(("http://","https://","/")):
        return url
    return f'../images/{url}'

def format_markdown(text: str) -> str:
    """Convertit le Markdown simple en HTML"""
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)  # Gras
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)  # Italique
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)  # Code
    return text

def format_reference(attrs: dict) -> str:
    """Formate une référence bibliographique"""
    parts = []
    if attrs.get('auteurs'):
        parts.append(f'<span class="ref-auteurs">{attrs["auteurs"]}</span>')
    if attrs.get('titre'):
        parts.append(f'<em class="ref-titre">{attrs["titre"]}</em>')
    if attrs.get('revue'):
        parts.append(f'<span class="ref-revue">{attrs["revue"]}</span>')
    if attrs.get('date'):
        parts.append(f'<span class="ref-date">{attrs["date"]}</span>')
    if attrs.get('doi'):
        doi = attrs["doi"]
        parts.append(f'<a href="https://doi.org/{doi}" class="ref-doi" target="_blank">DOI ↗</a>')
    
    return f'<p class="reference">{". ".join(parts)}.</p>'

def format_detail_line(line: str) -> str:
    """Formate une ligne de détail (texte, image, etc.) en HTML"""
    # Image Markdown: ![légende](url)
    img_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', line.strip())
    if img_match:
        alt = img_match.group(1)
        url = img_match.group(2)
        caption = f'<figcaption>{alt}</figcaption>' if alt else ''
        return f'''<figure class="detail-image">
                            <img src="{resolve_image_url(url)}" alt="{alt}">
                            {caption}
                        </figure>'''
    ref_match = re.match(r'^\[@ref\s+(.+)\]$', line.strip())
    if ref_match:
        attrs = {}
        for m in re.finditer(r'(\w+)="([^"]*)"', ref_match.group(1)):
            attrs[m.group(1)] = m.group(2)
        return format_reference(attrs)

    # Blockquote
    if line.strip().startswith('> '):
        content = format_markdown(line.strip()[2:])
        return f'<blockquote class="detail-blockquote">{content}</blockquote>'
    
    # Texte normal avec formatage Markdown
    return f'<p>{format_markdown(line)}</p>'


class HTMLGenerator:
    """Génère le HTML d'une présentation"""
    
    def __init__(self, base_path: Optional[Path] = None, theme: Optional[str] = None):
        self.base_path = base_path or Path(__file__).parent.parent
        self.theme = theme or DEFAULT_THEME
        if self.theme not in THEMES:
            self.theme = DEFAULT_THEME
    
    def generate(self, presentation: Presentation, js_uri: str | None, css_style: str) -> str:
        """Génère le HTML complet de la présentation"""
        slides_html = self._generate_slides(presentation)
        css = self._load_css(css_style)
        js_script = self._get_js_script(js_uri)
        
        return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{presentation.title}</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%230a4d68'/><path d='M14 8h4v16h-4zM8 14h16v4H8z' fill='%23ffffff'/></svg>">
    <style>
{css}
    </style>
</head>
<body>
    <div class="presentation-container">
        <div class="slides-grid" id="slidesGrid">
{slides_html}
        </div>
    </div>

    {js_script}
    <script>
        PresentationNav.init({presentation.total_slides});
    </script>
</body>
</html>'''
    
    def _generate_slides(self, presentation: Presentation) -> str:
        """Génère le HTML de toutes les slides"""
        html_parts = []
        total = presentation.total_slides

        for slide in presentation.slides:
            if slide.slide_type == 'title':
                html_parts.append(self._slide_title(slide, presentation.metadata))
            elif slide.slide_type == 'section':
                html_parts.append(self._slide_section(slide))
            elif slide.slide_type == 'content':
                html_parts.append(self._slide_content(slide, total))
            elif slide.slide_type == 'image':
                html_parts.append(self._slide_image(slide, total))

        return '\n'.join(html_parts)

    def _slide_section(self, slide: Slide) -> str:
        """Génère une slide de section (transition)"""
        subtitle = f'<p class="subtitle">{slide.subtitle}</p>' if slide.subtitle else ''
        return f'''
                <!-- SLIDE SECTION -->
                <div class="slide slide-section" data-no-annexes="true">
                    <div class="content">
                        <h1>{slide.title}</h1>
                        {subtitle}
                    </div>
                    <div class="nav-hint">
                        <span><span class="key-icon">↓</span> Continuer</span>
                    </div>
                </div>'''
        
    def _slide_title(self, slide: Slide, metadata: dict) -> str:
        """Génère une slide de titre"""
        subtitle = f'<p class="subtitle">{slide.subtitle}</p>' if slide.subtitle else ''

        # Construire les métadonnées
        meta_parts = []
        if metadata.get('author'):
            meta_parts.append(f'<span class="meta-item">{metadata["author"]}</span>')
        if metadata.get('university'):
            meta_parts.append(f'<span class="meta-item">{metadata["university"]}</span>')
        if metadata.get('date'):
            meta_parts.append(f'<span class="meta-item">{metadata["date"]}</span>')

        meta_html = f'<div class="title-meta">{" · ".join(meta_parts)}</div>' if meta_parts else ''

        return f'''
            <!-- SLIDE TITRE -->
            <div class="slide slide-main" data-no-annexes="true">
                <div class="position-indicator"></div>
                <div class="content">
                    <h1>{slide.title}</h1>
                    {subtitle}
                    {meta_html}
                </div>
                <div class="nav-hint">
                    <span><span class="key-icon">↓</span> Commencer le cours</span>
                </div>
            </div>'''
    
    def _slide_content(self, slide: Slide, total: int) -> str:
        """Génère une slide de contenu avec ses annexes"""
        max_view = slide.max_view
        
        # Attributs de la slide principale
        if max_view == 0:
            data_attrs = ' data-no-annexes="true"'
        elif max_view == 1:
            data_attrs = ' data-max-view="1"'
        else:
            data_attrs = ''
        
        # Subtitle
        subtitle = f'<p class="subtitle">{slide.subtitle}</p>' if slide.subtitle else ''
        
        points_html = []
        for p in slide.content:
            if isinstance(p, dict) and p.get('type') == 'blockquote':
                text = format_markdown(p["text"])
                points_html.append(f'                        <blockquote class="slide-blockquote">{text}</blockquote>')
            elif isinstance(p, dict) and p.get('type') == 'h3':
                text = format_markdown(p["text"])
                points_html.append(f'                        <h3>{text}</h3>')
            elif isinstance(p, str):
                p = format_markdown(p)
                points_html.append(f'                        <li>{p}</li>')
            else:
                raise TypeError

        # Wrapper les <li> dans <ul> seulement s'il y en a
        has_list_items = any(not isinstance(p, dict) for p in slide.content)
        if has_list_items:
            points = f'<ul class="key-points">\n' + '\n'.join(points_html) + '\n                    </ul>'
        else:
            points = '\n'.join(points_html)
        
        # Nav hint
        if max_view > 0:
            nav_hint = '''
                    <span><span class="key-icon">↑↓</span> Navigation</span>
                    <span><span class="key-icon">→</span> Détails</span>'''
        else:
            nav_hint = '''
                    <span><span class="key-icon">↑↓</span> Navigation</span>'''
        
        html = f'''
            <!-- SLIDE {slide.number} : {slide.title} -->
            <div class="slide slide-main"{data_attrs}>
                <div class="position-indicator">{slide.number} / {total}</div>
                <div class="content">
                    <h1>{slide.title}</h1>
                    {subtitle}
                    {points}
                </div>
                <div class="nav-hint">{nav_hint}
                </div>
            </div>'''
        
        # Slide détails
        if max_view >= 1:
            html += self._slide_details(slide, total, has_questions=(max_view == 2))
        
        # Slide questions
        if max_view == 2:
            html += self._slide_questions(slide, total)
        elif max_view == 1:
            # Placeholder pour maintenir la grille
            html += '''

            <div class="slide" style="visibility: hidden;"></div>'''
        
        return html
    
    def _slide_details(self, slide: Slide, total: int, has_questions: bool) -> str:
        """Génère la slide de détails"""
        paragraphs = '\n'.join(
            f'                        {format_detail_line(d)}' 
            for d in slide.details
        )
        
        if has_questions:
            nav = '''
                    <span><span class="key-icon">←</span> Retour</span>
                    <span><span class="key-icon">→</span> Questions</span>'''
        else:
            nav = '''
                    <span><span class="key-icon">←</span> Retour</span>'''
        
        return f'''

            <div class="slide slide-detail">
                <div class="position-indicator">{slide.number} / {total}</div>
                <div class="content">
                    <h2>Détails</h2>
                    <div class="detail-text">
{paragraphs}
                    </div>
                </div>
                <div class="nav-hint">{nav}
                </div>
            </div>'''
    
    def _slide_questions(self, slide: Slide, total: int) -> str:
        """Génère la slide de questions"""
        items = '\n'.join(
            f'''                        <li class="question-item">
                            <span class="question-number">{i}</span>
                            {q}
                        </li>'''
            for i, q in enumerate(slide.questions, 1)
        )
        
        return f'''

            <div class="slide slide-question">
                <div class="position-indicator">{slide.number} / {total}</div>
                <div class="content">
                    <h2>Questions de révision</h2>
                    <ul class="question-list">
{items}
                    </ul>
                </div>
                <div class="nav-hint">
                    <span><span class="key-icon">←</span> Retour</span>
                </div>
            </div>'''
    
    def _slide_image(self, slide: Slide, total: int) -> str:
        """Génère une slide d'image"""
        max_view = slide.max_view
        
        # Attributs de la slide principale
        if max_view == 0:
            data_attrs = ' data-no-annexes="true"'
        elif max_view == 1:
            data_attrs = ' data-max-view="1"'
        else:
            data_attrs = ''

        caption = (
            f'<p class="image-caption" >{slide.image_caption}</p>'
            if slide.image_caption else ''
        )
        if max_view > 0:
            nav_hint = '''
                    <span><span class="key-icon">↑↓</span> Navigation</span>
                    <span><span class="key-icon">→</span> Détails</span>'''
        else:
            nav_hint = '''
                    <span><span class="key-icon">↑↓</span> Navigation</span>'''

        html = f'''
            <!-- SLIDE IMAGE {slide.number} -->
            <div class="slide slide-main"{data_attrs}>
                <div class="position-indicator">{slide.number} / {total}</div>
                    <img src="{resolve_image_url(slide.image_url)}" class="slide-image" alt="">
                    {caption}
                <div class="nav-hint">
                    {nav_hint} 
                </div>
            </div>'''

        # Slide détails
        if max_view >= 1:
            html += self._slide_details(slide, total, has_questions=(max_view == 2))
        
        # Slide questions
        if max_view == 2:
            html += self._slide_questions(slide, total)
        elif max_view == 1:
            # Placeholder pour maintenir la grille
            html += '''

            <div class="slide" style="visibility: hidden;"></div>'''

        return html
        

    
    def _load_css(self, css: str) -> str:
        """Charge le CSS avec le thème appliqué"""
        colors = THEMES.get(self.theme, THEMES[DEFAULT_THEME])
        
        css += CSS_FONTS
        
        # Appliquer les couleurs du thème
        css = css.replace('#0a4d68', colors['primary'])
        css = css.replace('#088395', colors['secondary'])
        css = css.replace('#05bfdb', colors['accent'])
        css = css.replace('#ff6b35', colors['warning'])
        
        return css
    
    def _get_js_script(self, uri: Optional[str] = None) -> str:
        """Retourne le script JS (lien ou inline minifié)"""
        if uri:
            return f'<script src="{uri}"></script>'

        # Chercher le JS depuis la racine du projet
        project_root = Path(__file__).parent.parent
        js_path = project_root / ASSETS['js']

        if js_path.exists():
            js_content = js_path.read_text(encoding='utf-8')
            minified = self._minify_js(js_content)
            return f'<script>{minified}</script>'
        else:
            raise FileNotFoundError(f"Fichier JS introuvable: {js_path}")

    def _minify_js(self, js_code: str) -> str:
        """Minifie le code JavaScript"""
        import re

        # Supprimer les commentaires multilignes
        js_code = re.sub(r'/\*[\s\S]*?\*/', '', js_code)
        # Supprimer les commentaires de ligne
        js_code = re.sub(r'//.*?$', '', js_code, flags=re.MULTILINE)
        # Supprimer les lignes vides
        js_code = re.sub(r'\n\s*\n', '\n', js_code)
        # Supprimer les espaces en début/fin de ligne
        js_code = re.sub(r'^\s+', '', js_code, flags=re.MULTILINE)
        js_code = re.sub(r'\s+$', '', js_code, flags=re.MULTILINE)
        # Remplacer les multiples espaces par un seul
        js_code = re.sub(r'\s+', ' ', js_code)
        # Supprimer les espaces autour des opérateurs et symboles
        js_code = re.sub(r'\s*([{}()\[\];,:.=<>!+\-*/&|?])\s*', r'\1', js_code)

        return js_code.strip()
        
