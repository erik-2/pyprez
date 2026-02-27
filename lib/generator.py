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
        if not url.startswith(('http://', 'https://', '/')):
            url = f'../../images/{url}'
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
    
    def _load_js(self) -> str:
        """Charge le JavaScript depuis le fichier"""
        js_path = self.base_path / ASSETS['js']
        if js_path.exists():
            return js_path.read_text(encoding='utf-8')
        
        # Fallback : chercher dans le répertoire du script
        script_dir = Path(__file__).parent.parent
        js_path = script_dir / ASSETS['js']
        if js_path.exists():
            return js_path.read_text(encoding='utf-8')
        
        return 'console.error("JS not found");'


class HTMLGenerator(BaseGenerator):
    """Génère le HTML d'une présentation"""
    

    def generate(self, presentation: Presentation, is_draft: bool) -> str:
        """Génère le HTML complet de la présentation avec CSS et JS inlinés"""
        slides_html = self._generate_slides(presentation)
        css = self._load_css()
        js = self._load_js()
        draft_banner = ''
        draft_css = ''
        if is_draft:
            draft_banner = '<div class="draft-banner">🔄 DRAFT — En cours d\'actualisation</div>'
            draft_css = '''.draft-banner { position: fixed; top: 0; left: 0; right: 0; background: #f59e0b; color: #000; text-align: center; padding: 0.5rem; font-weight: 600; font-size: 0.9rem; z-index: 9999;}'''
        
        return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{presentation.title}</title>
    <link rel="icon" href="{self.FAVICON}">
    <style>
{css}{draft_css}
    </style>
</head>
<body>
            {draft_banner}
    <div class="presentation-container">
        <div class="slides-grid" id="slidesGrid">
{slides_html}
        </div>
    </div>

    <script>
{js}
    </script>
    <script>
        PresentationNav.init({presentation.total_slides});
    </script>
</body>
</html>'''
    
    def _generate_slides(self, presentation: Presentation) -> str:
        """Génère le HTML de toutes les slides"""
        html_parts = []
        total = presentation.total_slides
        
        
        for i, slide in enumerate(presentation.slides):
            is_last = (i == len (presentation.slides) -1)
            if slide.slide_type == 'title':
                html_parts.append(self._slide_title(slide))
            elif slide.slide_type == 'section':
                html_parts.append(self._slide_section(slide, is_last))
            elif slide.slide_type == 'content':
                html_parts.append(self._slide_content(slide, total, is_last))
            elif slide.slide_type == 'image':
                html_parts.append(self._slide_image(slide, total, is_last))
        
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
    
    def _slide_section(self, slide: Slide, is_last: bool = False) -> str:
        """Génère une slide de section"""
        subtitle = f'<p class="subtitle">{slide.subtitle}</p>' if slide.subtitle else ''
        if is_last:
            nav_hint = '''
                <span><span class="key-icon">Q</span> Quitter</span>'''
        else:
            nav_hint = '''
                <span><span class="key-icon">↓</span> Continuer</span>'''
        
        return f'''
            <!-- SLIDE SECTION -->
            <div class="slide slide-section" data-no-annexes="true">
                <div class="content">
                    <h1>{slide.title}</h1>
                    {subtitle}
                </div>
                <div class="nav-hint">
                        {nav_hint}
                </div>
            </div>'''
    
    def _slide_content(self, slide: Slide, total: int, is_last: bool = False) -> str:
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
            if isinstance(p, dict):
                if p.get('type') == 'blockquote':
                    text = format_markdown(p["text"])
                    points_html.append(f'                        <blockquote class="slide-blockquote">{text}</blockquote>')
                elif p.get('type') == 'h3':
                    text = format_markdown(p["text"])
                    points_html.append(f'                        <h3>{text}</h3>')
                elif p.get('type') == 'table':
                    points_html.append(f'                        {format_table_html(p, "slide-table")}')
            elif isinstance(p, str):
                p = format_markdown(p)
                points_html.append(f'                        <li>{p}</li>')

        # Envelopper les <li> dans <ul>
        final_html = []
        in_list = False
        for html in points_html:
            if '<li>' in html:
                if not in_list:
                    final_html.append('                    <ul class="key-points">')
                    in_list = True
                final_html.append(html)
            else:
                if in_list:
                    final_html.append('                    </ul>')
                    in_list = False
                final_html.append(html)
        
        if in_list:
            final_html.append('                    </ul>')
    
        points = '\n'.join(final_html)
        if is_last:
            if max_view > 0:
                nav_hint = '''
                    <span><span class="key-icon">Q</span> Quitter</span>
                    <span><span class="key-icon">→</span> Détails</span>'''
            else:
                nav_hint = '''
                    <span><span class="key-icon">Q</span> Quitter</span>'''
        else:
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
        """Génère la slide de détails avec références en bas"""
        from .parser import parse_details_with_references
        
        content_lines, references = parse_details_with_references(slide.details)
        
        # Numéroter les références par ordre d'apparition
        ref_order = []
        
        def replace_ref(match):
            ref_id = match.group(1)
            if ref_id not in ref_order:
                ref_order.append(ref_id)
            num = ref_order.index(ref_id) + 1
            return f'<sup class="ref-number">{num}</sup>'
        
        paragraphs_html = []
        for item in content_lines:
            # Tableau
            if isinstance(item, dict) and item.get('type') == 'table':
                paragraphs_html.append(f'                        {format_table_html(item, "detail-table")}')
            # Texte normal
            elif isinstance(item, str):
                line_with_refs = re.sub(r'\[\^(\w+)\]', replace_ref, item)
                paragraphs_html.append(f'                        {format_detail_line(line_with_refs)}')
      
        paragraphs = '\n'.join(paragraphs_html)
        
        # Générer la liste des références en bas
        references_html = ''
        if ref_order:
            ref_items = []
            for i, ref_id in enumerate(ref_order, 1):
                if ref_id in references:
                    attrs = references[ref_id]
                    ref_text = format_reference_inline(attrs)
                    ref_items.append(f'<li value="{i}">{ref_text}</li>')
            
            if ref_items:
                references_html = f'''
                        <div class="references-section">
                            <hr>
                            <h3>Références</h3>
                            <ol class="references-list">
                                {''.join(ref_items)}
                            </ol>
                        </div>'''
        
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
    {references_html}
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
    
    def _slide_image(self, slide: Slide, total: int, is_last: bool = False) -> str:
        """Génère une slide d'image"""
        max_view = slide.max_view
        
        if max_view == 0:
            data_attrs = ' data-no-annexes="true"'
        elif max_view == 1:
            data_attrs = ' data-max-view="1"'
        else:
            data_attrs = ''

        # Résoudre l'URL de l'image
        image_url = slide.image_url
        if image_url and not image_url.startswith(('http://', 'https://', '/')):
            image_url = f'../../images/{image_url}'

        caption = f'<p class="image-caption">{slide.image_caption}</p>' if slide.image_caption else ''
       
        if is_last:
            if max_view > 0:
                nav_hint = '''
                    <span><span class="key-icon">Q</span> Quitter</span>
                    <span><span class="key-icon">→</span> Détails</span>'''
            else:
                nav_hint = '''
                    <span><span class="key-icon">Q</span> Quitter</span>'''
        else:
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
                <img src="{image_url}" class="slide-image" alt="">
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


class PageGenerator(BaseGenerator):
    """Génère les pages statiques (accueil, collections)"""
    def __init__(self, base_path: Optional[Path] = None, theme: Optional[str] = None, preview: bool = False):
        super().__init__(base_path, theme)
        self.preview = preview
    
    def _get_page_css(self, file: str) -> str:
        """CSS spécifique aux pages statiques"""

        css_path = self.base_path / f'css/{file}.css'
        if css_path.exists():
            css = css_path.read_text(encoding='utf-8')
        else:
            raise FileNotFoundError(f"css/{file}.css non trouvé")
        return f'''
        {self._get_base_css()}
        {css}
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
        {self._get_page_css("collection")}
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
            status = course.get('status', 'puplished')
            
            subtitle = f'<p class="course-subtitle">{course["subtitle"]}</p>' if course.get('subtitle') else ''
            meta_parts = []
            if course.get('author'):
                meta_parts.append(f'👤 {course["author"]}')
            if course.get('date'):
                meta_parts.append(f'📅 {course["date"]}')
            meta_parts.append(f'📊 {course["total_slides"]} slides')
            meta_html = ' · '.join(meta_parts)
            
            if status == 'draft' and not self.preview:
                cards_html.append(f'''
        <div class="course-card course-draft" style="--card-primary: {colors['primary']}; --card-secondary: {colors['secondary']};">
            <div class="course-header">
                <h2 class="course-title">{course['title']}</h2>
                {subtitle}
                <span class="draft-badge">🔄 En cours d'actualisation</span>
            </div>
            <div class="course-meta">{meta_html}</div>
            <div class="course-actions">
                <span class="btn btn-disabled">▶ Présentation</span>
                <span class="btn btn-disabled">📄 Document</span>
            </div>
        </div>''')
            elif status == 'draft' and self.preview:
                # Carte active avec badge draft (preview)
                cards_html.append(f'''
    <div class="course-card course-draft-preview" style="--card-primary: {colors['primary']}; --card-secondary: {colors['secondary']};">
        <div class="course-header">
            <h2 class="course-title">{course['title']}</h2>
            {subtitle}
            <span class="draft-badge">🔄 Draft</span>
        </div>
        <div class="course-meta">{meta_html}</div>
        <div class="course-actions">
            <a href="../{course['url']}" class="btn btn-warning">👁️ Prévisualiser</a>
            <a href="../{course['details_url']}" class="btn btn-secondary">📄 Document</a>
        </div>
    </div>''')
            else:
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
        {self._get_page_css("homepage")}
        header {{
            padding: 3rem 2rem;
            background: {self._get_header_gradient(theme)};
            border-radius: 1rem;
            margin-bottom: 2rem;
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


def format_reference_inline(attrs: dict) -> str:
        """Formate une référence pour la liste en bas de slide"""
        parts = []
        if attrs.get('auteurs'):
            parts.append(f'{attrs["auteurs"]}')
        if attrs.get('titre'):
            parts.append(f'<em>{attrs["titre"]}</em>')
        if attrs.get('revue'):
            parts.append(f'{attrs["revue"]}')
        if attrs.get('date'):
            parts.append(f'{attrs["date"]}')
        
        text = '. '.join(parts)
        
        if attrs.get('doi'):
            doi = attrs["doi"]
            text += f' <a href="https://doi.org/{doi}" class="ref-doi" target="_blank">DOI ↗</a>'
        
        return text

def format_table_html(table: dict, css_class: str = 'detail-table') -> str:
    """Génère le HTML d'un tableau"""
    headers = table.get('headers', [])
    alignments = table.get('alignments', [])
    rows = table.get('rows', [])
    
    # En-têtes
    thead_cells = []
    for i, header in enumerate(headers):
        align = alignments[i] if i < len(alignments) else 'left'
        style = f' style="text-align: {align};"' if align != 'left' else ''
        thead_cells.append(f'<th{style}>{format_markdown(header)}</th>')
    
    thead = f'<thead><tr>{"".join(thead_cells)}</tr></thead>'
    
    # Lignes
    tbody_rows = []
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            align = alignments[i] if i < len(alignments) else 'left'
            style = f' style="text-align: {align};"' if align != 'left' else ''
            cells.append(f'<td{style}>{format_markdown(cell)}</td>')
        tbody_rows.append(f'<tr>{"".join(cells)}</tr>')
    
    tbody = f'<tbody>{"".join(tbody_rows)}</tbody>'
    
    return f'<table class="{css_class}">{thead}{tbody}</table>'
