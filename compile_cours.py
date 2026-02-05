#!/usr/bin/env python3
"""
Compilateur de Présentation Markdown → HTML

Transforme un fichier Markdown structuré en présentation HTML interactive
avec slides principales, détails et questions.

Usage:
    python compile_cours.py mon_cours.md
    python compile_cours.py mon_cours.md -o ma_presentation.html
    python compile_cours.py mon_cours.md --theme glacier
"""

import sys
import argparse
from pathlib import Path

from lib import parse_presentation, HTMLGenerator, THEMES, DEFAULT_THEME


def compile_course(
    md_file: Path,
    output_file: Path | None = None,
    js_uri: str | None = None,
    theme: str | None = None
) -> Path:
    """Compile un fichier Markdown en présentation HTML"""
    
    print(f"📖 Lecture de {md_file}...")
    md_content = md_file.read_text(encoding='utf-8')
    
    print("🔍 Analyse du contenu...")
    presentation = parse_presentation(md_content)
    
    print(f"📊 {presentation.total_slides} slides détectées")
    
    # Statistiques par type
    stats = {
        'avec_questions': sum(1 for s in presentation.slides if s.max_view == 2),
        'details_seuls': sum(1 for s in presentation.slides if s.max_view == 1),
        'sans_annexes': sum(1 for s in presentation.slides if s.max_view == 0),
    }
    print(f"   ├─ {stats['avec_questions']} avec détails + questions")
    print(f"   ├─ {stats['details_seuls']} avec détails seuls")
    print(f"   └─ {stats['sans_annexes']} sans annexes")
    
    # Thème : argument CLI > métadonnées > défaut
    final_theme = theme or presentation.metadata.get('theme') or DEFAULT_THEME
    print(f"🎨 Thème : {final_theme}")

    # Charger le CSS depuis le dossier du projet
    project_root = Path(__file__).parent
    css_file = project_root / 'css' / 'style.css'
    if css_file.exists():
        css = css_file.read_text(encoding='utf-8')
    else:
        raise FileNotFoundError(f"Fichier CSS introuvable: {css_file}")

    generator = HTMLGenerator(base_path=md_file.parent, theme=final_theme)
    html = generator.generate(presentation, js_uri=js_uri, css_style=css)

    
    if output_file is None:
        output_file = md_file.with_suffix('.html')
    
    output_file.write_text(html, encoding='utf-8')
    print(f"✅ Présentation générée : {output_file}")
    
    return output_file


def main():
    theme_list = ', '.join(THEMES.keys())
    
    parser = argparse.ArgumentParser(
        description='Compile un cours Markdown en présentation HTML interactive',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
Syntaxe Markdown supportée:
  # Titre           → Slide de titre (sans annexes)
  ## Section        → Slide de contenu
  ### Image: url    → Slide d'image
  > sous-titre      → Sous-titre de la slide
  - point           → Point clé (slide principale)
  
  :::details        → Début de la section détails
  :::questions      → Début de la section questions  
  :::no-annexes     → Désactive les annexes pour cette slide

Thèmes disponibles: {theme_list}

Exemples:
  python compile_cours.py mon_cours.md
  python compile_cours.py mon_cours.md -o presentation.html
  python compile_cours.py mon_cours.md --theme glacier
        '''
    )
    parser.add_argument('input', type=Path, help='Fichier Markdown d\'entrée')
    parser.add_argument('-o', '--output', type=Path, help='Fichier HTML de sortie')
    parser.add_argument('--theme', type=str, choices=THEMES.keys(), help='Thème de couleurs')
    parser.add_argument('--js-uri', type=str, help='URI externe pour le script JS')
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"❌ Erreur : fichier {args.input} introuvable")
        sys.exit(1)
    
    try:
        output = compile_course(args.input, args.output, args.js_uri, args.theme)
        print(f"\n🎉 Succès ! Ouvrez {output} dans votre navigateur")
    except Exception as e:
        print(f"❌ Erreur lors de la compilation : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
