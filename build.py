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
import tomllib
from pathlib import Path
from typing import List, Dict

from lib import parse_presentation, HTMLGenerator, PageGenerator, DEFAULT_THEME, lint_presentation


# Répertoire du script (pour trouver les assets CSS/JS)
SCRIPT_DIR = Path(__file__).resolve().parent


def load_collections_config(source_dir: Path) -> Dict:
    """Charge la configuration des collections depuis TOML"""
    config_file = source_dir / 'collections.toml'
    if config_file.exists():
        with open(config_file, 'rb') as f:
            return tomllib.load(f)
    return {}


def parse_collections_field(value) -> List[str]:
    """Parse le champ collections (string ou liste)"""
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [c.strip() for c in value.split(',') if c.strip()]


def compile_course(md_file: Path, output_dir: Path, folder_name: str, preview: bool) -> Dict | None:
    """Compile un cours et retourne ses métadonnées, ou None si le cours est ignoré"""
    print(f"    📄 {md_file.name}...")

    content = md_file.read_text(encoding='utf-8')
    presentation = parse_presentation(content)

    for warning in lint_presentation(presentation):
        print(f"      ⚠️  {warning}")

    theme = presentation.metadata.get('theme', DEFAULT_THEME)
    collections = parse_collections_field(presentation.metadata.get('collections'))
    status = presentation.metadata.get('status', 'published')

    # Cours obsolète : ignoré complètement (ni placeholder, ni entrée dans les index)
    if status in ('old', 'obsolete'):
        print(f"      🗄️  Obsolète (ignoré)")
        return None

    # Créer le dossier du cours
    course_dir = output_dir / folder_name / md_file.stem
    course_dir.mkdir(parents=True, exist_ok=True)
    
    # Générer la présentation (CSS et JS inlinés)
    if status == "draft" and not preview:
        html = generate_draft_page(presentation, theme)
        print(f"      ⏸️  Draft (non publié)")
    else:
        generator = HTMLGenerator(base_path=SCRIPT_DIR, theme=theme)
        html = generator.generate(presentation, is_draft=(status == 'draft'))
        if status == 'draft':
            print(f"      👁️  Draft (preview)")
    
    (course_dir / 'index.html').write_text(html, encoding='utf-8')
    
    # Générer les détails (document imprimable)
    if status != 'draft' or preview:
        from extract_details import extract_details
        details_output = course_dir / 'details.html'
    
        import io
        from contextlib import redirect_stdout
        with redirect_stdout(io.StringIO()):
            extract_details(md_file, details_output)
    
    return {
        'slug': md_file.stem,
        'folder': folder_name,
        'title': presentation.metadata.get('title', md_file.stem),
        'subtitle': presentation.metadata.get('subtitle', ''),
        'author': presentation.metadata.get('author', ''),
        'date': presentation.metadata.get('date', ''),
        'theme': theme,
        'status': status,
        'university': presentation.metadata.get('university', ''),
        'department': presentation.metadata.get('department', ''),
        'total_slides': presentation.total_slides,
        'collections': collections,
        'url': f'{folder_name}/{md_file.stem}/index.html',
        'details_url': f'{folder_name}/{md_file.stem}/details.html',
    }

def generate_draft_page(presentation, theme: str) -> str:
    """Génère une page placeholder pour un cours en draft"""
    from lib import THEMES, DEFAULT_THEME
    from lib.config import CSS_FONTS
    
    colors = THEMES.get(theme, THEMES[DEFAULT_THEME])
    
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{presentation.title} - En cours d'actualisation</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%230a4d68'/><path d='M14 8h4v16h-4zM8 14h16v4H8z' fill='%23ffffff'/></svg>">
    <style>
        {CSS_FONTS}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Work Sans', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
            color: white;
            text-align: center;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 500px;
        }}
        
        .icon {{
            font-size: 5rem;
            margin-bottom: 1.5rem;
        }}
        
        h1 {{
            font-family: 'Crimson Pro', serif;
            font-size: 2rem;
            margin-bottom: 1rem;
        }}
        
        p {{
            font-size: 1.1rem;
            opacity: 0.9;
            margin-bottom: 2rem;
        }}
        
        .back-link {{
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            text-decoration: none;
            border-radius: 0.5rem;
            transition: background 0.2s;
        }}
        
        .back-link:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">🔄</div>
        <h1>{presentation.title}</h1>
        <p>Ce cours est en cours d'actualisation.<br>Revenez bientôt !</p>
        <a href="javascript:history.back()" class="back-link">← Retour</a>
    </div>
</body>
</html>'''

def copy_assets(output_dir: Path):
    """Copie les fonts (CSS/JS sont inlinés dans les HTML)"""
    fonts_src = SCRIPT_DIR / 'fonts'
    if fonts_src.exists():
        fonts_dst = output_dir / 'fonts'
        if fonts_dst.exists():
            shutil.rmtree(fonts_dst)
        shutil.copytree(fonts_src, fonts_dst)
        print(f"  📁 Fonts copiées")


def copy_images(output_dir: Path, source_dir: Path) -> int:
    """Copie les images depuis source/images/ et les sous-dossiers des collections"""
    img_dst = output_dir / 'images'
    img_dst.mkdir(parents=True, exist_ok=True)
    
    exclude_dirs = {'__pycache__', '.git', 'images'}
    images_extensions = ["svg", "png", "jpg", "jpeg", "webp"]
    total_images = 0
    copied = set()
    
    def copy_if_new(img: Path):
        nonlocal total_images
        if img.name not in copied:
            shutil.copy(img, img_dst / img.name)
            copied.add(img.name)
            total_images += 1
    
    # Images dans source/images/
    images_src = source_dir / 'images'
    if images_src.exists():
        for ext in images_extensions:
            for img in images_src.glob(f"*.{ext}"):
                copy_if_new(img)
    
    # Images dans chaque sous-dossier
    for subdir in source_dir.iterdir():
        if subdir.is_dir() and subdir.name not in exclude_dirs:
            # Images à la racine du sous-dossier
            for ext in images_extensions:
                for img in subdir.glob(f"*.{ext}"):
                    copy_if_new(img)
            
            # Images dans sous-dossier/images/
            coll_images = subdir / 'images'
            if coll_images.exists():
                for ext in images_extensions:
                    for img in coll_images.glob(f"*.{ext}"):
                        copy_if_new(img)
    
    return total_images


def find_folders(source_dir: Path) -> Dict[str, List[Path]]:
    """Trouve tous les dossiers contenant des .md"""
    folders = {}
    
    exclude_dirs = {'images', '__pycache__', '.git', 'fonts', 'css', 'js', 'lib'}
    
    for subdir in sorted(source_dir.iterdir()):
        if not subdir.is_dir():
            continue
        if subdir.name in exclude_dirs:
            continue
        
        md_files = list(subdir.glob('*.md'))
        md_files = [f for f in md_files if f.name not in ('README.md', 'FORMAT.md', 'PROMPT.md')]
        
        if md_files:
            folders[subdir.name] = md_files
    
    return folders


def build(
    source_dir: Path,
    output_dir: Path,
    site_title: str = "Formations Médicales",
    clean: bool = False,
    preview: bool = False
):
    """Build complet : compile tous les cours et génère les pages"""
    
    #print(f"🔨 Build des cours")
    print(f"   Source : {source_dir}")
    print(f"   Output : {output_dir}")
    
    if clean and output_dir.exists():
        print("🧹 Nettoyage du dossier output...")
        shutil.rmtree(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Charger la configuration des collections
    collections_config = load_collections_config(source_dir)
    print(f"📂 {len(collections_config)} collections définies dans collections.toml")
    
    # Trouver les dossiers contenant des cours
    folders = find_folders(source_dir)
    
    if not folders:
        print("⚠️  Aucun dossier avec des .md trouvé")
        return
    
    print(f"📁 {len(folders)} dossiers trouvés")
    
    # Copier les images
    total_images = copy_images(output_dir, source_dir)
    print(f"🖼️  {total_images} image(s) copiée(s)")
    
    # Copier les fonts
    print("📦 Copie des assets...")
    copy_assets(output_dir)
    
    # Compiler les cours
    print("🏗️  Compilation des cours...")
    all_courses = []
    
    for folder_name, md_files in folders.items():
        print(f"  📁 {folder_name}/")
        for md_file in sorted(md_files):
            try:
                metadata = compile_course(md_file, output_dir, folder_name, preview)
                if metadata is not None:
                    all_courses.append(metadata)
            except Exception as e:
                print(f"    ❌ Erreur sur {md_file.name}: {e}")
                import traceback
                traceback.print_exc()
    
    # Organiser les cours par collection (depuis les métadonnées)
    collections_data = {}
    for course in all_courses:
        for coll_id in course.get('collections', []):
            if coll_id not in collections_data:
                collections_data[coll_id] = []
            collections_data[coll_id].append(course)
    
    # Afficher les collections non définies dans le TOML
    for coll_id in collections_data:
        if coll_id not in collections_config:
            print(f"  ⚠️  Collection '{coll_id}' utilisée mais non définie dans collections.toml")
    
    # Générer les pages avec PageGenerator
    page_gen = PageGenerator(base_path=SCRIPT_DIR, preview=preview)
    
    # Pages de collections (seulement celles définies dans le TOML et qui ont des cours)
    print("📋 Génération des pages de collections...")
    collections_pages_dir = output_dir / 'collections'
    collections_pages_dir.mkdir(parents=True, exist_ok=True)
    
    collections_for_index = {}
    for coll_id, config in collections_config.items():
        if coll_id in collections_data and collections_data[coll_id]:
            html = page_gen.generate_collection_page(coll_id, config, collections_data[coll_id], site_title)
            (collections_pages_dir / f'{coll_id}.html').write_text(html, encoding='utf-8')
            collections_for_index[coll_id] = config
            print(f"  📄 {coll_id}.html ({len(collections_data[coll_id])} cours)")
        elif coll_id not in collections_data:
            print(f"  ⚠️  Collection '{coll_id}' définie mais aucun cours associé")
    
    # Page d'accueil
    print("🏠 Génération de la page d'accueil...")
    html = page_gen.generate_home_page(collections_for_index, collections_data, site_title)
    (output_dir / 'index.html').write_text(html, encoding='utf-8')
    
    print(f"\n✅ Build terminé !")
    print(f"   {len(all_courses)} cours compilés")
    print(f"   {len(collections_for_index)} collections générées")
    print(f"   → {output_dir / 'index.html'}")


def main():
    parser = argparse.ArgumentParser(
        description='Compile tous les cours et génère le catalogue avec collections',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Structure attendue:
  cours/
  ├── collections.toml          # Définition des collections
  ├── dossier1/                 # Organisation physique libre
  │   ├── cours1.md             # collections: iade, trauma
  │   └── cours2.md             # collections: iade
  ├── dossier2/
  │   └── cours3.md             # collections: trauma
  └── images/

Métadonnées du cours:
  ---
  title: Mon Cours
  collections: iade, trauma
  ---

Exemples:
  python build.py
  python build.py -s ./cours -o ./dist
  python build.py --clean --title "Mes Formations"
        '''
    )
    parser.add_argument('-s', '--source', type=Path, default=Path('./cours'),
                        help='Dossier contenant les cours (défaut: ./cours)')
    parser.add_argument('-o', '--output', type=Path, default=Path('./dist'),
                        help='Dossier de sortie (défaut: ./dist)')
    parser.add_argument('--title', type=str, default='Formations Médicales',
                        help='Titre du site')
    parser.add_argument('--clean', action='store_true',
                        help='Nettoyer le dossier output avant compilation')
    parser.add_argument('--preview', action='store_true',
                        help='Générer les drafts comme des cours normaux (pour prévisualisation)')
    
    args = parser.parse_args()
    
    try:
        build(args.source, args.output, args.title, args.clean, args.preview)
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
