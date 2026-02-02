#!/usr/bin/env python3
"""
Compilateur de Présentation avec diapositives attenantes (détail, question)
Transforme un fichier Markdown structuré en présentation HTML interactive

Usage:
    python compile_cours.py mon_cours.md
    python compile_cours.py mon_cours.md -o ma_presentation.html
"""

import re
import sys
import os
import argparse
from pathlib import Path
from typing import List, Dict, Optional

class Slide:
    """Représente une slide avec ses éléments"""
    def __init__(self, slide_type: str, number: Optional[int] = None):
        self.slide_type = slide_type  # 'title', 'content', 'image'
        self.number = number
        self.title = ""
        self.subtitle = ""
        self.content = []  # Liste de points ou paragraphes
        self.details = []
        self.questions = []
        self.has_annexes = True
        self.image_url = ""
        self.image_caption = ""
        self.metadata = {}

    def __repr__(self):
        return f"<Slide {self.slide_type} #{self.number}: {self.title}>"


def parse_markdown(md_content: str) -> tuple[Dict[str, str], List[Slide]]:
    """Parse le Markdown et retourne les métadonnées et les slides"""
    lines = md_content.split('\n')
    metadata = {}
    slides = []
    current_slide = None
    current_section = None  # 'main', 'details', 'questions'
    
    i = 0
    
    # Parser les métadonnées (en début de fichier)
    if lines[0].strip() == '---':
        i = 1
        while i < len(lines) and lines[i].strip() != '---':
            if ':' in lines[i]:
                key, value = lines[i].split(':', 1)
                metadata[key.strip()] = value.strip()
            i += 1
        i += 1  # Passer le --- final
    
    # Parser les slides
    while i < len(lines):
        line = lines[i].strip()
        
        # Nouvelle slide de titre
        if line.startswith('# '):
            if current_slide:
                slides.append(current_slide)
            current_slide = Slide('title')
            current_slide.title = line[2:].strip()
            current_slide.has_annexes = False
            current_section = 'main'
        
        # Nouvelle slide de contenu
        elif line.startswith('## '):
            if current_slide:
                slides.append(current_slide)
            current_slide = Slide('content', len(slides) + 1)
            current_slide.title = line[3:].strip()
            current_section = 'main'
        
        # Nouvelle slide d'image
        elif line.startswith('### Image: '):
            if current_slide:
                slides.append(current_slide)
            current_slide = Slide('image', len(slides) + 1)
            current_slide.image_url = line[11:].strip()
            current_slide.has_annexes = False
            current_section = 'main'
        
        # Section détails
        elif line == '**Détails:**' or line == '**Details:**':
            current_section = 'details'
        
        # Section questions
        elif line == '**Questions:**':
            current_section = 'questions'
        
        # Option no-annexes
        elif line == '[no-annexes]':
            if current_slide:
                current_slide.has_annexes = False
        
        # Sous-titre
        elif line.startswith('> ') and current_section == 'main':
            if current_slide:
                current_slide.subtitle = line[2:].strip()
        
        # Caption d'image
        elif line.startswith('Caption: ') and current_slide and current_slide.slide_type == 'image':
            current_slide.image_caption = line[9:].strip()
        
        # Points de liste
        elif line.startswith('- ') or line.startswith('* '):
            if current_slide:
                content = line[2:].strip()
                if current_section == 'main':
                    current_slide.content.append(content)
                elif current_section == 'details':
                    current_slide.details.append(content)
                elif current_section == 'questions':
                    current_slide.questions.append(content)
        
        # Paragraphes (dans détails)
        elif line and not line.startswith('#') and current_section == 'details':
            if current_slide:
                current_slide.details.append(line)
        
        i += 1
    
    # Ajouter la dernière slide
    if current_slide:
        slides.append(current_slide)
    
    return metadata, slides


def generate_html_slide_title(slide: Slide) -> str:
    """Génère le HTML pour une slide de titre"""
    return f'''
            <!-- SLIDE TITRE -->
            <div class="slide slide-main" data-no-annexes="true">
                <div class="position-indicator"></div>
                <div class="content">
                    <h1>{slide.title}</h1>
                    {f'<p class="subtitle">{slide.subtitle}</p>' if slide.subtitle else ''}
                </div>
                <div class="nav-hint">
                    <span><span class="key-icon">↓</span> Commencer le cours</span>
                </div>
            </div>'''


def generate_html_slide_content(slide: Slide, total: int) -> str:
    """Génère le HTML pour une slide de contenu"""
    has_annexes_attr = '' if slide.has_annexes else ' data-no-annexes="true"'
    
    # Slide principale
    main_html = f'''
            <!-- SLIDE {slide.number} : {slide.title} -->
            <div class="slide slide-main"{has_annexes_attr}>
                <div class="position-indicator">{slide.number} / {total}</div>
                <div class="content">
                    <h1>{slide.title}</h1>
                    {f'<p class="subtitle">{slide.subtitle}</p>' if slide.subtitle else ''}
                    <ul class="key-points">'''
    
    for point in slide.content:
        main_html += f'\n                        <li>{point}</li>'
    
    main_html += '''
                    </ul>
                </div>
                <div class="nav-hint">'''
    
    if slide.has_annexes:
        main_html += '''
                    <span><span class="key-icon">↑↓</span> Navigation</span>
                    <span><span class="key-icon">→</span> Détails</span>'''
    else:
        main_html += '''
                    <span><span class="key-icon">↑↓</span> Navigation</span>'''
    
    main_html += '''
                </div>
            </div>'''
    
    # Slide détails (si annexes)
    if slide.has_annexes and slide.details:
        main_html += f'''

            <div class="slide slide-detail">
                <div class="position-indicator">{slide.number} / {total}</div>
                <div class="content">
                    <h2>Détails</h2>
                    <div class="detail-text">'''
        
        for detail in slide.details:
            if detail.startswith('**') and detail.endswith('**'):
                # Sous-titre en gras
                title = detail[2:-2]
                main_html += f'\n                        <p><strong>{title}</strong></p>'
            else:
                main_html += f'\n                        <p>{detail}</p>'
        
        main_html += '''
                    </div>
                </div>
                <div class="nav-hint">
                    <span><span class="key-icon">←</span> Retour</span>
                    <span><span class="key-icon">→</span> Questions</span>
                </div>
            </div>'''
    
    # Slide questions (si annexes)
    if slide.has_annexes and slide.questions:
        main_html += f'''

            <div class="slide slide-question">
                <div class="position-indicator">{slide.number} / {total}</div>
                <div class="content">
                    <h2>Questions de révision</h2>
                    <ul class="question-list">'''
        
        for i, question in enumerate(slide.questions, 1):
            main_html += f'''
                        <li class="question-item">
                            <span class="question-number">{i}</span>
                            {question}
                        </li>'''
        
        main_html += '''
                    </ul>
                </div>
                <div class="nav-hint">
                    <span><span class="key-icon">←</span> Retour</span>
                </div>
            </div>'''
    
    return main_html


def generate_html_slide_image(slide: Slide, total: int) -> str:
    """Génère le HTML pour une slide d'image"""
    return f'''
            <!-- SLIDE IMAGE {slide.number} -->
            <div class="slide slide-main" data-no-annexes="true">
                <div class="position-indicator">{slide.number} / {total}</div>
                <div class="content">
                    <img src="{slide.image_url}" style="width: 100%; max-height: 80vh; object-fit: contain;">
                    {f'<p class="subtitle" style="text-align: center; margin-top: 2rem;">{slide.image_caption}</p>' if slide.image_caption else ''}
                </div>
                <div class="nav-hint">
                    <span><span class="key-icon">↑↓</span> Navigation</span>
                </div>
            </div>'''


def get_html_template() -> str:
    """Retourne le template HTML de base"""
    return '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}}</title>
    <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=Work+Sans:wght@300;500;700&display=swap" rel="stylesheet">
    <style>
        {{CSS}}
    </style>
</head>
<body>
    <div class="presentation-container">
        <div class="slides-grid" id="slidesGrid">
{{SLIDES}}
        </div>
    </div>

    {{JS_SCRIPT}}
    <script>
        PresentationNav.init({{TOTAL_SLIDES}});
    </script>
</body>
</html>'''

def get_js_script(uri:Optional[str]) -> str:
    """Retourne le sript js ou un lien vers ce script"""
    if uri is not None:
        return f'<script src="{uri}"></script>'
    else:
        js_file = open("./js/presentation.js")

        return f"<script>{js_file.read()}</script>"


def get_css() -> str:
    """Retourne le CSS complet"""
    # Lire le CSS depuis le fichier cours-noyade-complet.html
    css_file = Path(__file__).parent / 'cours-noyade-complet.html'
    if css_file.exists():
        content = css_file.read_text(encoding='utf-8')
        # Extraire le CSS entre <style> et </style>
        match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # CSS par défaut minimal si fichier non trouvé
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
        .slide-detail { background: var(--bg-detail); overflow-y: auto; }
        .slide-question { background: var(--bg-question); overflow-y: auto; }
        h1 { font-family: 'Crimson Pro', serif; font-size: clamp(2.5rem, 6vw, 5rem); font-weight: 700; margin-bottom: 2rem; line-height: 1.1; }
        h2 { font-family: 'Crimson Pro', serif; font-size: clamp(1.8rem, 4vw, 3.5rem); font-weight: 600; margin-bottom: 1.5rem; color: var(--primary); }
        .slide-question h2 { color: var(--warning); }
        .content { max-width: 900px; margin: 0 auto; width: 100%; }
        .subtitle { font-size: clamp(1.2rem, 2.5vw, 2rem); opacity: 0.9; margin-bottom: 3rem; font-weight: 300; }
        .key-points { list-style: none; font-size: clamp(1rem, 2vw, 1.5rem); line-height: 1.8; }
        .key-points li { margin-bottom: 1.5rem; padding-left: 2rem; position: relative; }
        .key-points li::before { content: "→"; position: absolute; left: 0; font-weight: bold; color: rgba(255, 255, 255, 0.7); }
        .detail-text { font-size: clamp(1rem, 1.8vw, 1.3rem); line-height: 1.8; color: var(--text-light); margin-bottom: 2rem; }
        .detail-text p { margin-bottom: 1.5rem; }
        .detail-text strong { color: var(--primary); font-weight: 600; }
        .question-list { list-style: none; }
        .question-item { background: white; padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); border-left: 4px solid var(--warning); font-size: clamp(1rem, 1.8vw, 1.3rem); line-height: 1.6; }
        .question-number { display: inline-block; background: var(--warning); color: white; width: 32px; height: 32px; border-radius: 50%; text-align: center; line-height: 32px; font-weight: bold; margin-right: 1rem; font-size: 1rem; }
        .position-indicator { position: absolute; top: 2rem; right: 2rem; font-size: 0.9rem; opacity: 0.7; font-weight: 500; z-index: 10; }
        .slide-main .position-indicator { color: white; }
        .slide-detail .position-indicator, .slide-question .position-indicator { position: fixed; }
        .nav-hint { position: absolute; bottom: 2rem; right: 2rem; font-size: 0.9rem; opacity: 0.6; display: flex; gap: 1.5rem; align-items: center; font-weight: 300; z-index: 10; }
        .slide-main .nav-hint { color: white; }
        .slide-detail .nav-hint, .slide-question .nav-hint { position: fixed; }
        .key-icon { display: inline-block; padding: 0.3rem 0.6rem; background: rgba(255, 255, 255, 0.2); border-radius: 4px; font-family: monospace; font-size: 0.85rem; }
        .slide-detail .key-icon, .slide-question .key-icon { background: rgba(0, 0, 0, 0.1); }
    '''


def compile_course(md_file: Path, output_file: Optional[Path] = None) -> Path:
    """Compile un fichier Markdown en présentation HTML"""
    
    # Lire le Markdown
    print(f"📖 Lecture de {md_file}...")
    md_content = md_file.read_text(encoding='utf-8')
    
    # Parser
    print("🔍 Analyse du contenu...")
    metadata, slides = parse_markdown(md_content)
    
    # Compter les slides principales
    total_slides = len(slides)
    print(f"📊 {total_slides} slides détectées")
    
    # Générer le HTML des slides
    print("🏗️  Génération du HTML...")
    slides_html = []
    
    for slide in slides:
        if slide.slide_type == 'title':
            slides_html.append(generate_html_slide_title(slide))
        elif slide.slide_type == 'content':
            slides_html.append(generate_html_slide_content(slide, total_slides))
        elif slide.slide_type == 'image':
            slides_html.append(generate_html_slide_image(slide, total_slides))
    
    # Assembler le HTML complet
    print("🎨 Assemblage final...")
    html = get_html_template()
    html = html.replace('{{TITLE}}', metadata.get('title', 'Présentation'))
    html = html.replace('{{CSS}}', get_css())
    html = html.replace('{{SLIDES}}', '\n'.join(slides_html))
    html = html.replace('{{TOTAL_SLIDES}}', str(total_slides))
    html = html.replace('{{JS_SCRIPT}}', get_js_script(uri=None))
    # Écrire le fichier de sortie
    if output_file is None:
        output_file = md_file.with_suffix('.html')
    
    output_file.write_text(html, encoding='utf-8')
    print(f"✅ Présentation générée : {output_file}")
    print(f"📦 {total_slides} slides principales créées")
    
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Compile un cours Markdown en présentation HTML interactive',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemples:
  python compile_cours.py mon_cours.md
  python compile_cours.py mon_cours.md -o presentation.html
  python compile_cours.py cours/*.md
        '''
    )
    parser.add_argument('input', type=Path, help='Fichier Markdown d\'entrée')
    parser.add_argument('-o', '--output', type=Path, help='Fichier HTML de sortie (optionnel)')
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"❌ Erreur : fichier {args.input} introuvable")
        sys.exit(1)
    
    try:
        output = compile_course(args.input, args.output)
        print(f"\n🎉 Succès ! Ouvrez {output} dans votre navigateur")
    except Exception as e:
        print(f"❌ Erreur lors de la compilation : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
