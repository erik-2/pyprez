#!/usr/bin/env python3
"""
Extracteur de Sections Détails

Crée un document HTML élégant et imprimable à partir des sections :::details

Usage:
    python extract_details.py cours.md
    python extract_details.py cours.md -o document.html
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

from lib import parse_details_only, format_markdown


def generate_details_document(metadata: dict, sections: list) -> str:
    """Génère le document HTML des détails"""
    
    title = metadata.get('title', 'Document de Cours')
    author = metadata.get('author', '')
    university = metadata.get('university', '')
    date = metadata.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Métadonnées header
    meta_parts = []
    if author:
        meta_parts.append(f'<span>{author}</span>')
    if university:
        meta_parts.append(f'<span>•</span><span>{university}</span>')
    meta_parts.append(f'<span>•</span><span>{date}</span>')
    metadata_html = '\n            '.join(meta_parts)
    
    # Table des matières
    toc_items = []
    for idx, section in enumerate(sections):
        indent = "  " * (section.level - 1)
        toc_items.append(f'{indent}<li><a href="#section-{idx}">{section.title}</a></li>')
    toc_html = '\n            '.join(toc_items)
    
    # Sections
    sections_html = []
    for idx, section in enumerate(sections):
        section_html = _generate_section(section, idx)
        sections_html.append(section_html)
    
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Notes Détaillées</title>
    <style>
{_get_details_css()}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="subtitle">Notes Détaillées</div>
        <div class="metadata">
            {metadata_html}
        </div>
    </div>
    
    <div class="toc no-print">
        <h2>📚 Table des Matières</h2>
        <ul>
            {toc_html}
        </ul>
    </div>
    
    <div class="content">
{''.join(sections_html)}
    </div>
    
    <div class="footer">
        <p>Document généré automatiquement à partir du cours Markdown</p>
        <p>{datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
    </div>
    
    <button class="print-button no-print" onclick="window.print()">🖨️ Imprimer</button>
</body>
</html>'''


def format_reference_html(attrs: dict) -> str:
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


def _generate_section(section, idx: int) -> str:
    """Génère le HTML d'une section"""
    level_class = f"level-{section.level}"
    
    content_parts = []
    current_list = False
    
    for detail in section.details:
        if detail['type'] == 'subtitle':
            if current_list:
                content_parts.append('</ul>')
                current_list = False
            content = format_markdown(detail['content'])
            content_parts.append(f'<div class="detail-subtitle">{content}</div>')
        
        elif detail['type'] == 'list_item':
            if not current_list:
                content_parts.append('<ul class="detail-list">')
                current_list = True
            content = format_markdown(detail['content'])
            content_parts.append(f'    <li>{content}</li>')
        
        elif detail['type'] == 'image':
            if current_list:
                content_parts.append('</ul>')
                current_list = False
            alt = detail.get('alt', '')
            url = detail.get('url', '')
            caption = f'<figcaption>{alt}</figcaption>' if alt else ''
            content_parts.append(f'''<figure class="detail-image">
                <img src="{url}" alt="{alt}">
                {caption}
            </figure>''')
        elif detail['type'] == 'blockquote':
            if current_list:
                content_parts.append('</ul>')
                current_list = False
            content = format_markdown(detail['content'])
            content_parts.append(f'<blockquote class="detail-blockquote">{content}</blockquote>')

        elif detail['type'] == 'reference':
            if current_list:
                content_parts.append('</ul>')
                current_list = False
            content_parts.append(format_reference_html(detail))

        else:  # paragraph
            if current_list:
                content_parts.append('</ul>')
                current_list = False
            content = format_markdown(detail['content'])
            content_parts.append(f'<p class="detail-paragraph">{content}</p>')
    
    if current_list:
        content_parts.append('</ul>')
    
    content_html = '\n                '.join(content_parts)
    
    return f'''
        <div class="section" id="section-{idx}">
            <h2 class="section-title {level_class}">{section.title}</h2>
            <div class="section-content">
                {content_html}
            </div>
        </div>
'''


def _get_details_css() -> str:
    """Retourne le CSS pour le document de détails"""
    return '''
        :root {
            --primary: #0a4d68;
            --secondary: #088395;
            --accent: #05bfdb;
            --text: #1a1a1a;
            --text-light: #4a5568;
            --bg: #ffffff;
            --bg-section: #f8f9fa;
            --border: #e2e8f0;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        @media print {
            body { font-size: 11pt; }
            .no-print { display: none; }
            a { color: #000; text-decoration: none; }
            .section { page-break-inside: avoid; }
            .ref-doi {display: none;}
        }
        body {
            font-family: 'Georgia', serif;
            line-height: 1.8;
            color: var(--text);
            background: var(--bg);
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }
        .header {
            text-align: center;
            border-bottom: 3px solid var(--primary);
            padding-bottom: 2rem;
            margin-bottom: 3rem;
        }
        .header h1 { font-size: 2.5rem; color: var(--primary); margin-bottom: 0.5rem; }
        .header .subtitle { font-size: 1.2rem; color: var(--secondary); font-style: italic; margin-bottom: 1rem; }
        .header .metadata { font-size: 0.95rem; color: var(--text-light); }
        .header .metadata span { margin: 0 0.5rem; }
        .toc {
            background: var(--bg-section);
            border-left: 4px solid var(--accent);
            padding: 1.5rem;
            margin-bottom: 3rem;
            border-radius: 4px;
        }
        .toc h2 { font-size: 1.3rem; color: var(--primary); margin-bottom: 1rem; }
        .toc ul { list-style: none; }
        .toc li { margin-bottom: 0.5rem; }
        .toc a { color: var(--secondary); text-decoration: none; }
        .toc a:hover { color: var(--primary); text-decoration: underline; }
        .section { margin-bottom: 3rem; }
        .section-title {
            font-size: 1.8rem;
            color: var(--primary);
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border);
        }
        .section-title.level-1 { font-size: 2rem; color: var(--secondary); text-transform: uppercase; letter-spacing: 1px; }
        .section-content { padding-left: 1rem; }
        .detail-subtitle { font-size: 1.2rem; color: var(--secondary); font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.8rem; }
        .detail-paragraph { font-size: 1rem; margin-bottom: 1rem; text-align: justify; }
        .detail-list { margin-left: 2rem; margin-bottom: 1rem; }
        .detail-list li { margin-bottom: 0.5rem; }
        .detail-image {
            margin: 1.5rem 0;
            text-align: center;
        }
        .detail-blockquote {
            margin: 1.5rem 0;
            padding: 1rem 1.5rem;
            background: rgba(10, 77, 104, 0.08);
            border-left: 4px solid var(--primary);
            border-radius: 0 4px 4px 0;
            font-style: italic;
        }
        .detail-image img {
            max-width: 100%;
            max-height: 400px;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        .detail-image figcaption {
            margin-top: 0.5rem;
            font-size: 0.9rem;
            color: var(--text-light);
            font-style: italic;
        }
        @media print {
            .detail-image img {
                max-height: 300px;
            }
        }
        strong { color: var(--primary); font-weight: 600; }
        em { font-style: italic; color: var(--text-light); }
        code { background: var(--bg-section); padding: 0.2rem 0.4rem; border-radius: 3px; font-family: monospace; color: var(--secondary); }
        .footer { text-align: center; margin-top: 4rem; padding-top: 2rem; border-top: 2px solid var(--border); color: var(--text-light); font-size: 0.9rem; }
        .print-button {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: var(--primary);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(10, 77, 104, 0.3);
        }
        .print-button:hover { background: var(--secondary); transform: translateY(-2px); }
    '''


def extract_details(md_file: Path, output_file: Path | None = None) -> Path | None:
    """Extrait les sections détails et génère un HTML imprimable"""
    
    print(f"📖 Lecture de {md_file}...")
    md_content = md_file.read_text(encoding='utf-8')
    
    print("🔍 Extraction des sections détails...")
    metadata, sections = parse_details_only(md_content)
    
    if not sections:
        print("⚠️  Aucune section avec détails trouvée !")
        return None
    
    print(f"📊 {len(sections)} sections avec détails extraites")
    
    print("🎨 Génération du document HTML...")
    html = generate_details_document(metadata, sections)
    
    if output_file is None:
        output_file = md_file.with_name(md_file.stem + '_details.html')
    
    output_file.write_text(html, encoding='utf-8')
    print(f"✅ Document généré : {output_file}")
    
    total_paragraphs = sum(len(s.details) for s in sections)
    print(f"📝 {total_paragraphs} éléments de contenu extraits")
    
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Extrait les sections :::details et crée un document HTML imprimable',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemples:
  python extract_details.py cours_hypothermie.md
  python extract_details.py cours_hypothermie.md -o notes.html
  
Le script extrait uniquement les sections marquées :::details et crée
un document élégant prêt à imprimer ou convertir en PDF.
        '''
    )
    parser.add_argument('input', type=Path, help='Fichier Markdown d\'entrée')
    parser.add_argument('-o', '--output', type=Path, help='Fichier HTML de sortie')
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"❌ Erreur : fichier {args.input} introuvable")
        sys.exit(1)
    
    try:
        output = extract_details(args.input, args.output)
        if output:
            print(f"\n🎉 Succès ! Ouvrez {output} dans votre navigateur")
            print("💡 Astuce : Utilisez le bouton 'Imprimer' ou Ctrl+P pour générer un PDF")
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
