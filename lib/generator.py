"""
Générateur HTML pour les présentations
"""

import re
from pathlib import Path
from typing import Optional

from .models import Slide, Presentation
from .config import CSS_FONTS, GOOGLE_FONTS_URL, ASSETS, THEMES, DEFAULT_THEME


def format_bold(text: str) -> str:
    """Convertit **texte** en <strong>texte</strong>"""
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)


def format_markdown(text: str) -> str:
    """Convertit le Markdown simple en HTML"""
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)  # Gras
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)  # Italique
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)  # Code
    return text


def format_detail_line(line: str) -> str:
    """Formate une ligne de détail (texte, image, etc.) en HTML"""
    # Image Markdown: ![légende](url)
    img_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', line.strip())
    if img_match:
        alt = img_match.group(1)
        url = img_match.group(2)
        caption = f'<figcaption>{alt}</figcaption>' if alt else ''
        return f'''<figure class="detail-image">
                            <img src="{url}" alt="{alt}">
                            {caption}
                        </figure>'''
    
    # Texte normal avec formatage Markdown
    return f'<p>{format_markdown(line)}</p>'


class HTMLGenerator:
    """Génère le HTML d'une présentation"""
    
    def __init__(self, base_path: Optional[Path] = None, theme: Optional[str] = None):
        self.base_path = base_path or Path(__file__).parent.parent
        self.theme = theme or DEFAULT_THEME
        if self.theme not in THEMES:
            self.theme = DEFAULT_THEME
    
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
        
        # Points clés
        points = '\n'.join(f'                        <li>{p}</li>' for p in slide.content)
        
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
                    <ul class="key-points">
{points}
                    </ul>
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
        caption = (
            f'<p class="subtitle" style="text-align: center; margin-top: 2rem;">{slide.image_caption}</p>'
            if slide.image_caption else ''
        )
        return f'''
            <!-- SLIDE IMAGE {slide.number} -->
            <div class="slide slide-main" data-no-annexes="true">
                <div class="position-indicator">{slide.number} / {total}</div>
                <div class="content">
                    <img src="{slide.image_url}" style="width: 100%; max-height: 80vh; object-fit: contain;">
                    {caption}
                </div>
                <div class="nav-hint">
                    <span><span class="key-icon">↑↓</span> Navigation</span>
                </div>
            </div>'''
    
    def _load_css(self) -> str:
        """Charge le CSS avec le thème appliqué"""
        colors = THEMES.get(self.theme, THEMES[DEFAULT_THEME])
        
        css_path = self.base_path / ASSETS['css']
        if css_path.exists():
            css = css_path.read_text(encoding='utf-8')
        else:
            css = self._default_css()

        css += CSS_FONTS
        
        # Appliquer les couleurs du thème
        css = css.replace('#0a4d68', colors['primary'])
        css = css.replace('#088395', colors['secondary'])
        css = css.replace('#05bfdb', colors['accent'])
        css = css.replace('#ff6b35', colors['warning'])
        
        return css
    
    def _get_js_script(self, uri: Optional[str] = None) -> str:
        """Retourne le script JS (lien ou inline)"""
        if uri:
            return f'<script src="{uri}"></script>'
        
        js_path = self.base_path / ASSETS['js']
        if js_path.exists():
            js_content = js_path.read_text(encoding='utf-8')
            return f'<script>\n{js_content}\n    </script>'
        
        return f'<script>\n{self._default_js()}\n    </script>'
    
    def _default_css(self) -> str:
        """CSS par défaut minimal"""
        return '''
        :root {
            --primary: #0a4d68;
            --secondary: #088395;
            --accent: #05bfdb;
            --warning: #ff6b35;
            --bg-main: #f8f9fa;
            --bg-detail: #e8f4f8;
            --bg-question: #fff4e6;
            --text: #1a1a1a;
            --text-light: #4a5568;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Work Sans', sans-serif; background: var(--bg-main); overflow: hidden; color: var(--text); }
        .presentation-container { width: 100vw; height: 100vh; position: relative; overflow: hidden; }
        .slides-grid { display: grid; grid-template-columns: repeat(3, 100vw); grid-auto-rows: 100vh; transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1); }
        .slide { width: 100vw; height: 100vh; padding: 4rem; display: flex; flex-direction: column; justify-content: center; position: relative; }
        .slide-main { background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%); color: white; }
        .slide-detail { background: var(--bg-detail); overflow-y: auto; justify-content: flex-start; }
        .slide-question { background: var(--bg-question); overflow-y: auto; justify-content: flex-start; }
        .slide-detail .content, .slide-question .content { padding-top: 4rem; padding-bottom: 6rem; }
        h1 { font-family: 'Crimson Pro', serif; font-size: clamp(2.5rem, 6vw, 5rem); font-weight: 700; margin-bottom: 2rem; line-height: 1.1; }
        h2 { font-family: 'Crimson Pro', serif; font-size: clamp(1.8rem, 4vw, 3.5rem); font-weight: 600; margin-bottom: 1.5rem; color: var(--primary); }
        .slide-question h2 { color: var(--warning); }
        .content { max-width: 900px; margin: 0 auto; width: 100%; }
        .subtitle { font-size: clamp(1.2rem, 2.5vw, 2rem); opacity: 0.9; margin-bottom: 3rem; font-weight: 300; }
        .key-points { list-style: none; font-size: clamp(1rem, 2vw, 1.5rem); line-height: 1.8; }
        .key-points li { margin-bottom: 1.5rem; padding-left: 2rem; position: relative; }
        .key-points li::before { content: "→"; position: absolute; left: 0; color: rgba(255,255,255,0.7); }
        .detail-text { font-size: clamp(1rem, 1.8vw, 1.3rem); line-height: 1.8; color: var(--text-light); }
        .detail-text p { margin-bottom: 1.5rem; }
        .detail-text strong { color: var(--primary); font-weight: 600; }
        .detail-image { margin: 2rem 0; text-align: center; }
        .detail-image img { max-width: 100%; max-height: 50vh; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .detail-image figcaption { margin-top: 0.75rem; font-size: 0.95rem; color: var(--text-light); font-style: italic; }
        .question-list { list-style: none; }
        .question-item { background: white; padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 4px solid var(--warning); font-size: clamp(1rem, 1.8vw, 1.3rem); }
        .question-number { display: inline-block; background: var(--warning); color: white; width: 32px; height: 32px; border-radius: 50%; text-align: center; line-height: 32px; font-weight: bold; margin-right: 1rem; }
        .position-indicator { position: absolute; top: 2rem; right: 2rem; font-size: 0.9rem; opacity: 0.7; }
        .slide-main .position-indicator { color: white; }
        .slide-detail .position-indicator, .slide-question .position-indicator { position: fixed; }
        .nav-hint { position: absolute; bottom: 2rem; right: 2rem; font-size: 0.9rem; opacity: 0.6; display: flex; gap: 1.5rem; }
        .slide-main .nav-hint { color: white; }
        .slide-detail .nav-hint, .slide-question .nav-hint { position: fixed; }
        .key-icon { padding: 0.3rem 0.6rem; background: rgba(255,255,255,0.2); border-radius: 4px; font-family: monospace; }
        .slide-detail .key-icon, .slide-question .key-icon { background: rgba(0,0,0,0.1); }
        '''
    
    def _default_js(self) -> str:
        """JS par défaut minimal"""
        return '''
const PresentationNav = (function() {
    let currentSlide = 0, currentView = 0, totalSlides = 0, slideGroups = [];
    
    function buildSlideGroups() {
        slideGroups = [];
        const allSlides = Array.from(document.querySelectorAll('.slide'));
        let i = 0;
        while (i < allSlides.length) {
            const main = allSlides[i];
            if (!main.classList.contains('slide-main')) { i++; continue; }
            let maxView = 2;
            if (main.dataset.noAnnexes === 'true') maxView = 0;
            else if (main.dataset.maxView === '1') maxView = 1;
            const group = { main, detail: null, question: null, maxView };
            if (maxView === 0) {
                for (let j = 0; j < 2; j++) {
                    const ph = document.createElement('div');
                    ph.className = 'slide';
                    ph.style.visibility = 'hidden';
                    main.after(ph);
                }
                i += 1;
            } else {
                group.detail = allSlides[i + 1];
                if (maxView === 2) group.question = allSlides[i + 2];
                i += 3;
            }
            slideGroups.push(group);
        }
    }
    
    function getMaxView(idx) { return slideGroups[idx]?.maxView ?? 0; }
    function getActive() {
        const g = slideGroups[currentSlide];
        if (!g) return null;
        if (currentView === 0) return g.main;
        if (currentView === 1) return g.detail;
        return g.question;
    }
    
    function updatePosition() {
        const grid = document.getElementById('slidesGrid');
        if (currentView > getMaxView(currentSlide)) currentView = getMaxView(currentSlide);
        grid.style.transform = `translate(${-currentView * 100}vw, ${-currentSlide * 100}vh)`;
        document.querySelectorAll('.slide-detail, .slide-question').forEach(s => {
            const p = s.querySelector('.position-indicator'), n = s.querySelector('.nav-hint');
            if (p) p.style.opacity = '0';
            if (n) n.style.opacity = '0';
        });
        if (currentView > 0) {
            const a = getActive();
            if (a) {
                const p = a.querySelector('.position-indicator'), n = a.querySelector('.nav-hint');
                if (p) p.style.opacity = '0.7';
                if (n) n.style.opacity = '0.6';
            }
        }
        setTimeout(() => { const el = getActive(); if (el) el.scrollTop = 0; }, 100);
    }
    
    function handleKey(e) {
        const maxView = getMaxView(currentSlide);
        switch(e.key) {
            case 'ArrowDown': e.preventDefault(); if (currentSlide < totalSlides - 1) { currentSlide++; currentView = 0; updatePosition(); } break;
            case 'ArrowUp': e.preventDefault(); if (currentSlide > 0) { currentSlide--; currentView = 0; updatePosition(); } break;
            case 'ArrowRight': e.preventDefault(); if (currentView < maxView) { currentView++; updatePosition(); } break;
            case 'ArrowLeft': e.preventDefault(); if (currentView > 0) { currentView--; updatePosition(); } break;
        }
    }
    
    function init(total) {
        totalSlides = total;
        buildSlideGroups();
        document.addEventListener('keydown', handleKey);
        updatePosition();
    }
    
    return { init, goTo: (s, v=0) => { currentSlide = s; currentView = v; updatePosition(); } };
})();
'''
