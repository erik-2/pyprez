"""
Générateur HTML pour les présentations et pages statiques
"""

import re
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from .models import Slide, Presentation
from .config import CSS_FONTS, ASSETS, THEMES, DEFAULT_THEME


def format_markdown(text: str) -> str:
    """Convertit le Markdown simple en HTML"""
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
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
    """Formate une ligne de détail en HTML"""
    img_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', line.strip())
    if img_match:
        alt = img_match.group(1)
        url = img_match.group(2)
        caption = f'<figcaption>{alt}</figcaption>' if alt else ''
        return f'''<figure class="detail-image">
                            <img src="{url}" alt="{alt}">
                            {caption}
                        </figure>'''
    
    ref_match = re.match(r'^\[@ref\s+(.+)\]$', line.strip())
    if ref_match:
        attrs = {}
        for m in re.finditer(r'(\w+)="([^"]*)"', ref_match.group(1)):
            attrs[m.group(1)] = m.group(2)
        return format_reference(attrs)

    if line.strip().startswith('> '):
        content = format_markdown(line.strip()[2:])
        return f'<blockquote class="detail-blockquote">{content}</blockquote>'
    
    return f'<p>{format_markdown(line)}</p>'


class BaseGenerator:
    """Classe de base pour la génération HTML"""
    
    FAVICON = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%230a4d68'/><path d='M14 8h4v16h-4zM8 14h16v4H8z' fill='%23ffffff'/></svg>"
    
    def __init__(self, base_path: Optional[Path] = None, theme: Optional[str] = None):
        self.base_path = base_path or Path(__file__).parent.parent
        self.theme = theme if theme in THEMES else DEFAULT_THEME
    
    def _get_theme_colors(self, theme: Optional[str] = None) -> Dict[str, str]:
        """Retourne les couleurs du thème"""
        t = theme or self.theme
        return THEMES.get(t, THEMES[DEFAULT_THEME])
    
    def _get_header_gradient(self, theme: Optional[str] = None) -> str:
        """Retourne le gradient CSS pour les headers"""
        colors = self._get_theme_colors(theme)
        return f"linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%)"
    
    def _get_base_css(self) -> str:
        """Retourne le CSS de base commun"""
        colors = self._get_theme_colors()
        return f'''{CSS_FONTS}
        
:root {{
    --primary: {colors['primary']};
    --secondary: {colors['secondary']};
    --accent: {colors['accent']};
    --warning: {colors['warning']};
    --bg: #f8fafc;
    --bg-card: #ffffff;
    --text: #1e293b;
    --text-light: #4a5568;
    --border: #e2e8f0;
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
    --shadow-hover: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
    font-family: 'Work Sans', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
}}

h1, h2, h3 {{
    font-family: 'Crimson Pro', serif;
}}

a {{
    transition: all 0.2s;
}}'''
    
    def _load_css(self) -> str:
        """Charge le CSS depuis le fichier ou retourne le CSS par défaut"""
        css_path = self.base_path / ASSETS['css']
        if css_path.exists():
            css = css_path.read_text(encoding='utf-8')
        else:
            css = self._get_base_css()
        
        # Appliquer les couleurs du thème
        colors = self._get_theme_colors()
        css = css.replace('#0a4d68', colors['primary'])
        css = css.replace('#088395', colors['secondary'])
        css = css.replace('#05bfdb', colors['accent'])
        css = css.replace('#ff6b35', colors['warning'])
        
        return CSS_FONTS + css


class HTMLGenerator(BaseGenerator):
    """Génère le HTML d'une présentation"""
    
    def generate(self, presentation: Presentation, js_uri: Optional[str] = None) -> str:
        """Génère le HTML complet de la présentation"""
        slides_html = self._generate_slides(presentation)
        css = self._load_css()
        js_script = self._get_js_script(js_uri)
        
        return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{presentation.title}</title>
    <link rel="icon" href="{self.FAVICON}">
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
                html_parts.append(self._slide_title(slide))
            elif slide.slide_type == 'section':
                html_parts.append(self._slide_section(slide))
            elif slide.slide_type == 'content':
                html_parts.append(self._slide_content(slide, total))
            elif slide.slide_type == 'image':
                html_parts.append(self._slide_image(slide, total))
        
        return '\n'.join(html_parts)
    
    def _slide_title(self, slide: Slide) -> str:
        """Génère une slide de titre"""
        subtitle = f'<p class="subtitle">{slide.subtitle}</p>' if slide.subtitle else ''
        return f'''
            <!-- SLIDE TITRE -->
            <div class="slide slide-main" data-no-annexes="true">
                <div class="position-indicator"></div>
                <div class="content">
                    <h1>{slide.title}</h1>
                    {subtitle}
                </div>
                <div class="nav-hint">
                    <span><span class="key-icon">↓</span> Commencer le cours</span>
                </div>
            </div>'''
    
    def _slide_section(self, slide: Slide) -> str:
        """Génère une slide de section"""
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
    
    def _slide_content(self, slide: Slide, total: int) -> str:
        """Génère une slide de contenu avec ses annexes"""
        max_view = slide.max_view
        
        if max_view == 0:
            data_attrs = ' data-no-annexes="true"'
        elif max_view == 1:
            data_attrs = ' data-max-view="1"'
        else:
            data_attrs = ''
        
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
        
        has_list_items = any(not isinstance(p, dict) for p in slide.content)
        if has_list_items:
            points = f'<ul class="key-points">\n' + '\n'.join(points_html) + '\n                    </ul>'
        else:
            points = '\n'.join(points_html)
        
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
        
        if max_view >= 1:
            html += self._slide_details(slide, total, has_questions=(max_view == 2))
        
        if max_view == 2:
            html += self._slide_questions(slide, total)
        elif max_view == 1:
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
        
        if max_view == 0:
            data_attrs = ' data-no-annexes="true"'
        elif max_view == 1:
            data_attrs = ' data-max-view="1"'
        else:
            data_attrs = ''

        caption = f'<p class="image-caption">{slide.image_caption}</p>' if slide.image_caption else ''
        
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
                <img src="/images/{slide.image_url}" class="slide-image" alt="">
                {caption}
                <div class="nav-hint">{nav_hint}
                </div>
            </div>'''

        if max_view >= 1:
            html += self._slide_details(slide, total, has_questions=(max_view == 2))
        
        if max_view == 2:
            html += self._slide_questions(slide, total)
        elif max_view == 1:
            html += '''

            <div class="slide" style="visibility: hidden;"></div>'''

        return html
    
    def _get_js_script(self, uri: Optional[str] = None) -> str:
        """Retourne le script JS"""
        if uri:
            return f'<script src="{uri}"></script>'
        
        js_path = self.base_path / ASSETS['js']
        if js_path.exists():
            js_content = js_path.read_text(encoding='utf-8')
            return f'<script>\n{js_content}\n    </script>'
        
        return '<script>console.error("JS not found");</script>'


class PageGenerator(BaseGenerator):
    """Génère les pages statiques (accueil, collections)"""
    
    def _get_page_css(self) -> str:
        """CSS spécifique aux pages statiques"""
        return f'''
        {self._get_base_css()}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        header {{
            text-align: center;
            padding: 4rem 2rem;
            background: {self._get_header_gradient()};
            color: white;
        }}
        
        header h1 {{
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        header p {{
            font-size: 1.3rem;
            opacity: 0.9;
        }}
        
        footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-light);
            font-size: 0.9rem;
        }}
        
        @media (max-width: 768px) {{
            header h1 {{ font-size: 2.5rem; }}
            .container {{ padding: 1rem; }}
        }}
        '''
    
    def generate_home_page(self, collections_config: Dict, collections_data: Dict, site_title: str) -> str:
        """Génère la page d'accueil"""
        
        cards_html = []
        for coll_id, coll_info in collections_config.items():
            if coll_id not in collections_data or not collections_data[coll_id]:
                continue
            
            colors = self._get_theme_colors(coll_info.get('theme'))
            course_count = len(collections_data[coll_id])
            
            cards_html.append(f'''
            <a href="collections/{coll_id}.html" class="collection-card" style="--card-primary: {colors['primary']}; --card-secondary: {colors['secondary']};">
                <div class="collection-icon">{coll_info.get('icon', '📚')}</div>
                <h2 class="collection-title">{coll_info.get('title', coll_id)}</h2>
                <p class="collection-description">{coll_info.get('description', '')}</p>
                <div class="collection-count">{course_count} cours</div>
            </a>''')
        
        total_collections = len([c for c in collections_config if c in collections_data and collections_data[c]])
        
        return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{site_title}</title>
    <link rel="icon" href="{self.FAVICON}">
    <style>
        {self._get_page_css()}
        
        .collections-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 2rem;
            padding: 3rem 0;
        }}
        
        .collection-card {{
            background: var(--bg-card);
            border-radius: 1rem;
            box-shadow: var(--shadow);
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
            padding: 2rem;
            text-align: center;
            border-top: 4px solid var(--card-primary);
        }}
        
        .collection-card:hover {{
            transform: translateY(-6px);
            box-shadow: var(--shadow-hover);
        }}
        
        .collection-icon {{ font-size: 4rem; margin-bottom: 1rem; }}
        .collection-title {{ font-size: 1.5rem; font-weight: 600; color: var(--card-primary); margin-bottom: 0.5rem; }}
        .collection-description {{ font-size: 0.95rem; color: var(--text-light); margin-bottom: 1rem; flex-grow: 1; }}
        .collection-count {{ font-size: 0.9rem; font-weight: 500; color: var(--card-secondary); padding: 0.5rem 1rem; background: rgba(0,0,0,0.05); border-radius: 2rem; display: inline-block; }}
        
        @media (max-width: 768px) {{
            .collections-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>{site_title}</h1>
        <p>{total_collections} collections disponibles</p>
    </header>
    
    <main class="container">
        <div class="collections-grid">
{''.join(cards_html)}
        </div>
    </main>
    
    <footer>
        <p>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
    </footer>
</body>
</html>'''
    
    def generate_collection_page(self, coll_id: str, coll_info: Dict, courses: List, site_title: str) -> str:
        """Génère la page d'une collection"""
        
        theme = coll_info.get('theme', DEFAULT_THEME)
        courses_sorted = sorted(courses, key=lambda c: c.get('date', ''), reverse=True)
        
        cards_html = []
        for course in courses_sorted:
            colors = self._get_theme_colors(course.get('theme'))
            
            subtitle = f'<p class="course-subtitle">{course["subtitle"]}</p>' if course.get('subtitle') else ''
            meta_parts = []
            if course.get('author'):
                meta_parts.append(f'👤 {course["author"]}')
            if course.get('date'):
                meta_parts.append(f'📅 {course["date"]}')
            meta_parts.append(f'📊 {course["total_slides"]} slides')
            meta_html = ' · '.join(meta_parts)
            
            cards_html.append(f'''
            <div class="course-card" style="--card-primary: {colors['primary']}; --card-secondary: {colors['secondary']};">
                <div class="course-header">
                    <h2 class="course-title">{course['title']}</h2>
                    {subtitle}
                </div>
                <div class="course-meta">{meta_html}</div>
                <div class="course-actions">
                    <a href="../{course['url']}" class="btn btn-primary">▶ Présentation</a>
                    <a href="../{course['details_url']}" class="btn btn-secondary">📄 Document</a>
                </div>
            </div>''')
        
        return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{coll_info.get('title', coll_id)} - {site_title}</title>
    <link rel="icon" href="{self.FAVICON}">
    <style>
        {self._get_page_css()}
        
        .container {{ max-width: 1000px; }}
        
        .back-link {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-light);
            text-decoration: none;
            font-size: 0.95rem;
            margin-bottom: 2rem;
        }}
        .back-link:hover {{ color: var(--text); }}
        
        header {{
            padding: 3rem 2rem;
            background: {self._get_header_gradient(theme)};
            border-radius: 1rem;
            margin-bottom: 2rem;
        }}
        
        header h1 {{ font-size: 2.5rem; }}
        .collection-icon {{ font-size: 4rem; margin-bottom: 1rem; }}
        header .description {{ font-size: 1.1rem; opacity: 0.9; margin-bottom: 0.5rem; }}
        header .count {{ font-size: 0.95rem; opacity: 0.8; }}
        
        .courses-list {{ display: flex; flex-direction: column; gap: 1.5rem; }}
        
        .course-card {{
            background: var(--bg-card);
            border-radius: 1rem;
            box-shadow: var(--shadow);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        .course-card:hover {{ transform: translateX(8px); box-shadow: var(--shadow-hover); }}
        
        .course-header {{
            padding: 1.5rem;
            background: linear-gradient(135deg, var(--card-primary) 0%, var(--card-secondary) 100%);
            color: white;
        }}
        .course-title {{ font-size: 1.4rem; font-weight: 600; margin-bottom: 0.25rem; }}
        .course-subtitle {{ font-size: 0.95rem; opacity: 0.9; font-weight: 300; }}
        .course-meta {{ padding: 1rem 1.5rem; color: var(--text-light); font-size: 0.9rem; border-bottom: 1px solid var(--border); }}
        .course-actions {{ padding: 1rem 1.5rem; display: flex; gap: 0.75rem; }}
        
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.6rem 1.2rem;
            border-radius: 0.5rem;
            text-decoration: none;
            font-weight: 500;
            font-size: 0.9rem;
            flex: 1;
            justify-content: center;
        }}
        .btn-primary {{ background: var(--card-primary); color: white; }}
        .btn-primary:hover {{ filter: brightness(1.1); }}
        .btn-secondary {{ background: var(--bg); color: var(--text); border: 1px solid var(--border); }}
        .btn-secondary:hover {{ background: var(--border); }}
        
        @media (max-width: 768px) {{
            header {{ padding: 2rem 1rem; border-radius: 0; }}
            header h1 {{ font-size: 2rem; }}
            .course-actions {{ flex-direction: column; }}
        }}
    </style>
</head>
<body>
    <main class="container">
        <a href="../index.html" class="back-link">← Retour aux collections</a>
        
        <header>
            <div class="collection-icon">{coll_info.get('icon', '📚')}</div>
            <h1>{coll_info.get('title', coll_id)}</h1>
            <p class="description">{coll_info.get('description', '')}</p>
            <p class="count">{len(courses)} cours</p>
        </header>
        
        <div class="courses-list">
{''.join(cards_html)}
        </div>
    </main>
    
    <footer>
        <p>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
    </footer>
</body>
</html>'''
