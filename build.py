#!/usr/bin/env python3
"""
Build script pour compiler tous les cours et générer le catalogue

Usage:
    python build.py                     # Compile tout dans ./dist/
    python build.py -s sources/         # Sources depuis un dossier spécifique
    python build.py -o /var/www/cours/  # Output vers un dossier spécifique
    python build.py --clean             # Nettoie avant de compiler
"""

import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from lib import parse_presentation, HTMLGenerator, THEMES, DEFAULT_THEME
from lib.config import CSS_FONTS


def compile_course(md_file: Path, output_dir: Path, assets_relative: str = '../assets') -> Dict:
    """Compile un cours et retourne ses métadonnées"""
    print(f"  📄 {md_file.name}...")
    
    content = md_file.read_text(encoding='utf-8')
    presentation = parse_presentation(content)
    
    theme = presentation.metadata.get('theme', DEFAULT_THEME)

    course_dir = output_dir / md_file.stem
    course_dir.mkdir(parents=True, exist_ok=True)

    generator = HTMLGenerator(base_path=md_file.parent, theme=theme)
    
    css_file = Path('css/style.css')
    if css_file.exists():
        css = css_file.read_text(encoding='utf-8')
    else:
        raise FileNotFoundError(f"Fichier non trouvé {css_file}")

    html = generator.generate(presentation, js_uri=None, css_style=css)

    (course_dir / 'index.html').write_text(html, encoding='utf-8')
    
    # Générer les détails (document imprimable)
    from extract_details import extract_details
    details_output = course_dir / 'details.html'

    extract_details(md_file, details_output)
    
    return {
        'slug': md_file.stem,
        'title': presentation.metadata.get('title', md_file.stem),
        'subtitle': presentation.metadata.get('subtitle', ''),
        'author': presentation.metadata.get('author', ''),
        'date': presentation.metadata.get('date', ''),
        'theme': theme,
        'university': presentation.metadata.get('university', ''),
        'department': presentation.metadata.get('department', ''),
        'total_slides': presentation.total_slides,
        'url': f'{md_file.stem}/index.html',
        'details_url': f'{md_file.stem}/details.html',
    }


def generate_index(courses: List[Dict], output_dir: Path, site_title: str = "Catalogue des Cours"):
    """Génère la page index.html listant tous les cours"""
    
    # Trier par date (plus récent en premier) ou par titre
    courses_sorted = sorted(courses, key=lambda c: c.get('date', ''), reverse=True)
    
    # Générer les cartes de cours
    cards_html = []
    for course in courses_sorted:
        theme = course.get('theme', DEFAULT_THEME)
        theme_colors = THEMES.get(theme, THEMES[DEFAULT_THEME])
        
        subtitle = f'<p class="course-subtitle">{course["subtitle"]}</p>' if course.get('subtitle') else ''
        author = f'<span class="course-author">👤 {course["author"]}</span>' if course.get('author') else ''
        date = f'<span class="course-date">📅 {course["date"]}</span>' if course.get('date') else ''
        slides = f'<span class="course-slides">📊 {course["total_slides"]} slides</span>'
        
        meta_parts = [m for m in [author, date, slides] if m]
        meta_html = ' · '.join(meta_parts) if meta_parts else ''
        
        cards_html.append(f'''
        <div class="course-card" style="--card-primary: {theme_colors['primary']}; --card-secondary: {theme_colors['secondary']};">
            <div class="course-header">
                <h2 class="course-title">{course['title']}</h2>
                {subtitle}
            </div>
            <div class="course-meta">
                {meta_html}
            </div>
            <div class="course-actions">
                <a href="{course['url']}" class="btn btn-primary">▶ Présentation</a>
                <a href="{course['details_url']}" class="btn btn-secondary">📄 Document</a>
            </div>
        </div>''')
    
    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{site_title}</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%230a4d68'/><path d='M14 8h4v16h-4zM8 14h16v4H8z' fill='%23ffffff'/></svg>">
    <style>
        {CSS_FONTS}
        :root {{
            --bg: #f8fafc;
            --bg-card: #ffffff;
            --text: #1e293b;
            --text-light: #64748b;
            --border: #e2e8f0;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
            --shadow-hover: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Work Sans', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 3rem;
            padding: 3rem 0;
            background: linear-gradient(135deg, #0a4d68 0%, #088395 100%);
            color: white;
            border-radius: 0 0 2rem 2rem;
        }}
        
        header h1 {{
            font-family: 'Crimson Pro', serif;
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .courses-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 2rem;
            padding: 1rem 0;
        }}
        
        .course-card {{
            background: var(--bg-card);
            border-radius: 1rem;
            box-shadow: var(--shadow);
            overflow: hidden;
            transition: transform 0.3s, box-shadow 0.3s;
            display: flex;
            flex-direction: column;
        }}
        
        .course-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-hover);
        }}
        
        .course-header {{
            padding: 1.5rem;
            background: linear-gradient(135deg, var(--card-primary) 0%, var(--card-secondary) 100%);
            color: white;
        }}
        
        .course-title {{
            font-family: 'Crimson Pro', serif;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }}
        
        .course-subtitle {{
            font-size: 0.95rem;
            opacity: 0.9;
            font-weight: 300;
        }}
        
        .course-meta {{
            padding: 1rem 1.5rem;
            color: var(--text-light);
            font-size: 0.9rem;
            border-bottom: 1px solid var(--border);
            flex-grow: 1;
        }}
        
        .course-actions {{
            padding: 1rem 1.5rem;
            display: flex;
            gap: 0.75rem;
        }}
        
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.6rem 1.2rem;
            border-radius: 0.5rem;
            text-decoration: none;
            font-weight: 500;
            font-size: 0.9rem;
            transition: all 0.2s;
            flex: 1;
            justify-content: center;
        }}
        
        .btn-primary {{
            background: var(--card-primary);
            color: white;
        }}
        
        .btn-primary:hover {{
            filter: brightness(1.1);
        }}
        
        .btn-secondary {{
            background: var(--bg);
            color: var(--text);
            border: 1px solid var(--border);
        }}
        
        .btn-secondary:hover {{
            background: var(--border);
        }}
        
        footer {{
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
            color: var(--text-light);
            font-size: 0.9rem;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 4rem 2rem;
            color: var(--text-light);
        }}
        
        .empty-state h2 {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
            color: var(--text);
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}
            
            header {{
                padding: 2rem 1rem;
                border-radius: 0;
            }}
            
            header h1 {{
                font-size: 2rem;
            }}
            
            .courses-grid {{
                grid-template-columns: 1fr;
            }}
            
            .course-actions {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>{site_title}</h1>
            <p>{len(courses)} cours disponibles</p>
        </div>
    </header>
    
    <main class="container">
        {'<div class="courses-grid">' + ''.join(cards_html) + '</div>' if cards_html else '<div class="empty-state"><h2>Aucun cours disponible</h2><p>Ajoutez des fichiers .md dans le dossier source.</p></div>'}
    </main>
    
    <footer>
        <p>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
    </footer>
</body>
</html>'''
    
    (output_dir / 'index.html').write_text(html, encoding='utf-8')


def copy_assets(output_dir: Path, source_dir: Path):
    """Copie les assets partagés (CSS, JS)"""
    assets_dir = output_dir / 'assets'
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # CSS
    css_src = source_dir / 'css' / 'style.css'
    if css_src.exists():
        shutil.copy(css_src, assets_dir / 'style.css')
    
    # JS
    js_src = source_dir / 'js' / 'presentation.js'
    if js_src.exists():
        shutil.copy(js_src, assets_dir / 'presentation.js')

    fonts_src = source_dir / 'fonts'
    if fonts_src.exists():
        fonts_dst = output_dir / 'fonts'
        if fonts_dst.exists():
            shutil.rmtree(fonts_dst)
        shutil.copytree(fonts_src, fonts_dst)



def build(
    source_dir: Path,
    output_dir: Path,
    site_title: str = "Catalogue des Cours",
    clean: bool = False
):
    """Build complet : compile tous les cours et génère l'index"""
    
    print(f"🔨 Build des cours")
    print(f"   Source : {source_dir}")
    print(f"   Output : {output_dir}")
    
    # Nettoyer si demandé
    if clean and output_dir.exists():
        print("🧹 Nettoyage du dossier output...")
        shutil.rmtree(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Trouver tous les fichiers .md
    md_files = list(source_dir.glob('*.md'))
    md_files = [f for f in md_files if f.name not in ('README.md', 'FORMAT.md', 'PROMPT.md')]
    
    if not md_files:
        print("⚠️  Aucun fichier .md trouvé dans le dossier source")
        return
    
    print(f"📚 {len(md_files)} cours trouvés")

    # Trouver les images
    img_dst = output_dir / 'images'
    img_dst.mkdir(parents=True, exist_ok=True)
    images_extensions = ["svg","png","jpg","jpeg","webp"]
    total_images = 0
    for ext in images_extensions:
        img_files = list(source_dir.glob(f"*.{ext}"))
        for img in img_files:
            total_images += 1
            shutil.copy(img, img_dst / img.name)
    print(f"🖼️ {total_images} images copiée(s)")
    
    # Copier les assets
    print("📦 Copie des assets...")
    script_dir = Path(__file__).parent
    copy_assets(output_dir, script_dir)
    
    # Compiler chaque cours
    print("🏗️  Compilation des cours...")
    courses = []
    for md_file in sorted(md_files):
        try:
            metadata = compile_course(md_file, output_dir)
            courses.append(metadata)
        except Exception as e:
            print(f"  ❌ Erreur sur {md_file.name}: {e}")
    
    # Générer l'index
    print("📋 Génération de l'index...")
    generate_index(courses, output_dir, site_title)
    
    print(f"\n✅ Build terminé !")
    print(f"   {len(courses)} cours compilés")
    print(f"   → {output_dir / 'index.html'}")


def main():
    parser = argparse.ArgumentParser(
        description='Compile tous les cours et génère le catalogue',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemples:
  python build.py
  python build.py -s ./sources -o ./dist
  python build.py --clean --title "Mes Formations"
        '''
    )
    parser.add_argument('-s', '--source', type=Path, default=Path('./cours'),
                        help='Dossier contenant les fichiers .md (défaut: ./cours)')
    parser.add_argument('-o', '--output', type=Path, default=Path('./dist'),
                        help='Dossier de sortie (défaut: ./dist)')
    parser.add_argument('--title', type=str, default='Catalogue des Cours',
                        help='Titre du site')
    parser.add_argument('--clean', action='store_true',
                        help='Nettoyer le dossier output avant compilation')
    
    args = parser.parse_args()
    
    try:
        build(args.source, args.output, args.title, args.clean)
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
