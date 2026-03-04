#!/usr/bin/env python3
"""
Extracteur de Sections Détails

Crée un document HTML élégant et imprimable à partir des sections :::details

Usage:
    python extract_details.py cours.md
    python extract_details.py cours.md -o document.html
"""

import sys
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple

from lib import parse_details_only, format_markdown, format_table_html


def parse_references_from_details(details: list) -> Tuple[list, Dict[str, dict]]:
    """
    Sépare le contenu des définitions de références.
    Retourne (details_sans_refs, {id: attrs_reference})
    """
    content_details = []
    references = {}
    
    for detail in details:
        if detail['type'] == 'paragraph':
            # Chercher une définition de référence : [^id]: [@ref ...]
            ref_def_match = re.match(r'^\[\^(\w+)\]:\s*\[@ref\s+(.+)\]$', detail['content'].strip())
            if ref_def_match:
                ref_id = ref_def_match.group(1)
                ref_attrs_str = ref_def_match.group(2)
                attrs = {}
                for m in re.finditer(r'(\w+)="([^"]*)"', ref_attrs_str):
                    attrs[m.group(1)] = m.group(2)
                references[ref_id] = attrs
                continue
        
        content_details.append(detail)
    
    return content_details, references


def format_reference_footnote(attrs: dict) -> str:
    """Formate une référence pour la liste en bas de section"""
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
        text += f'. <a href="https://doi.org/{doi}" class="ref-doi" target="_blank">DOI ↗</a>'
    
    return text


def generate_details_document(metadata: dict, sections: list) -> str:
    """Génère le document HTML des détails"""
    
    title = metadata.get('title', 'Document de Cours')
    subtitle = metadata.get('subtitle', '')
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
    
    # Table des matières hiérarchique
    toc_html = _generate_toc(sections)
    
    # Sections
    sections_html = _generate_sections_html(sections)
    
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Notes Détaillées</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%230a4d68'/><path d='M14 8h4v16h-4zM8 14h16v4H8z' fill='%23ffffff'/></svg>">
    <style>
{_get_details_css()}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="subtitle">{subtitle}</div>
        <div class="metadata">
            {metadata_html}
        </div>
    </div>
    
    <div class="toc no-print">
        <h2>📚 Table des Matières</h2>
        {toc_html}
    </div>
    
    <div class="content">
{sections_html}
    </div>
    
    <div class="footer">
        <p>Document généré automatiquement à partir du cours Markdown</p>
        <p>{datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
    </div>
    
    <button class="print-button no-print" onclick="window.print()">🖨️ Imprimer</button>
</body>
</html>'''


def _generate_toc(sections: list) -> str:
    """Génère la table des matières hiérarchique"""
    toc_parts = ['<ul class="toc-list">']
    current_section_idx = 0
    
    for section in sections:
        if section.level == 1:
            # Fermer la sous-liste précédente si existante
            if current_section_idx > 0:
                toc_parts.append('</ul></li>')
            toc_parts.append(f'<li class="toc-section"><a href="#section-{section.title.lower().replace(" ", "-")}">{section.title}</a>')
            toc_parts.append('<ul class="toc-subsections">')
            current_section_idx += 1
        else:
            toc_parts.append(f'<li><a href="#subsection-{section.title.lower().replace(" ", "-")}">{section.title}</a></li>')
    
    if current_section_idx > 0:
        toc_parts.append('</ul></li>')
    toc_parts.append('</ul>')
    
    return '\n            '.join(toc_parts)


def _generate_sections_html(sections: list) -> str:
    """Génère le HTML des sections avec hiérarchie"""
    html_parts = []
    
    for section in sections:
        if section.level == 1:
            # Section principale
            section_id = section.title.lower().replace(" ", "-")
            if section.details:
                content_html = _generate_section_content(section)
                html_parts.append(f'''
        <div class="main-section" id="section-{section_id}">
            <h1 class="section-title level-1">{section.title}</h1>
            <div class="section-intro">
                {content_html}
            </div>
        </div>''')
            else:
                html_parts.append(f'''
        <div class="main-section" id="section-{section_id}">
            <h1 class="section-title level-1">{section.title}</h1>
        </div>''')


        else:
            # Sous-section avec détails
            section_id = section.title.lower().replace(" ", "-")
            content_html = _generate_section_content(section)
            html_parts.append(f'''
        <div class="sub-section" id="subsection-{section_id}">
            <h2 class="section-title level-2">{section.title}</h2>
            <div class="section-content">
                {content_html}
            </div>
        </div>''')
    
    return '\n'.join(html_parts)


def _generate_section_content(section) -> str:
    """Génère le contenu d'une sous-section avec gestion des références"""
    
    # Séparer les définitions de références du contenu
    content_details, references = parse_references_from_details(section.details)
    
    # Numéroter les références par ordre d'apparition
    ref_order = []
    
    def replace_ref_in_text(text: str) -> str:
        """Remplace [^id] par le numéro de référence"""
        def replacer(match):
            ref_id = match.group(1)
            if ref_id not in ref_order and ref_id in references:
                ref_order.append(ref_id)
            if ref_id in references:
                num = ref_order.index(ref_id) + 1
                return f'<sup class="ref-number">{num}</sup>'
            return match.group(0)  # Garder tel quel si référence non trouvée
        
        return re.sub(r'\[\^(\w+)\]', replacer, text)
    
    content_parts = []
    current_list = False
    
    for detail in content_details:
         # Fermer la liste si on change de type
        if current_list and (not isinstance(detail, dict) or detail.get('type') != 'list_item'):
            content_parts.append('</ul>')
            current_list = False
        
        # Tableau
        if isinstance(detail, dict) and detail.get('type') == 'table':
            content_parts.append(format_table_html(detail, 'detail-table'))
            continue

        if detail['type'] == 'subtitle':
            if current_list:
                content_parts.append('</ul>')
                current_list = False
            content = format_markdown(detail['content'])
            content = replace_ref_in_text(content)
            content_parts.append(f'<div class="detail-subtitle">{content}</div>')
        
        elif detail['type'] == 'list_item':
            if not current_list:
                content_parts.append('<ul class="detail-list">')
                current_list = True
            content = format_markdown(detail['content'])
            content = replace_ref_in_text(content)
            content_parts.append(f'    <li>{content}</li>')
        
        elif detail['type'] == 'image':
            if current_list:
                content_parts.append('</ul>')
                current_list = False
            alt = detail.get('alt', '')
            url = detail.get('url', '')
            if not url.startswith(('http://', 'https://', '/')):
                url = f'../../images/{url}'
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
            content = replace_ref_in_text(content)
            content_parts.append(f'<blockquote class="detail-blockquote">{content}</blockquote>')
        
        elif detail['type'] == 'perspective':
            if current_list:
                content_parts.append('</ul>')
                current_list = False
            paras = ''.join(
                f'<p>{format_markdown(l)}</p>'
                for l in detail['content'].split('\n') if l.strip()
            )
            content_parts.append(f'<div class="perspective-block"><div class="perspective-label">Perspective</div>{paras}</div>')

        elif detail['type'] == 'reference':
            # Référence inline ancienne syntaxe ([@ref ...]) - garder compatibilité
            if current_list:
                content_parts.append('</ul>')
                current_list = False
            content_parts.append(format_reference_html(detail))
        
        else:  # paragraph
            if current_list:
                content_parts.append('</ul>')
                current_list = False
            content = format_markdown(detail['content'])
            content = replace_ref_in_text(content)
            content_parts.append(f'<p class="detail-paragraph">{content}</p>')
    
    if current_list:
        content_parts.append('</ul>')
    
    # Ajouter les références en bas de section si présentes
    if ref_order:
        ref_items = []
        for i, ref_id in enumerate(ref_order, 1):
            if ref_id in references:
                ref_text = format_reference_footnote(references[ref_id])
                ref_items.append(f'<li value="{i}">{ref_text}</li>')
        
        if ref_items:
            content_parts.append(f'''
                <div class="references-section">
                    <h4>Références</h4>
                    <ol class="references-list">
                        {''.join(ref_items)}
                    </ol>
                </div>''')
    
    return '\n                '.join(content_parts)


def format_reference_html(attrs: dict) -> str:
    """Formate une référence bibliographique (ancienne syntaxe inline)"""
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

def _get_details_css() -> str:
    """Charge le CSS depuis le fichier ou retourne un fallback"""
    css_path = Path(__file__).parent / 'css' / 'details.css'
    if css_path.exists():
        return css_path.read_text(encoding='utf-8')
    
    # Fallback minimal si fichier non trouvé
    return '''
        body { font-family: Georgia, serif; max-width: 900px; margin: 0 auto; padding: 2rem; }
        h1, h2 { color: #0a4d68; }
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

Syntaxe des références:
  Dans le texte: La noyade cause une hypoxie[^szpilman].
  Définition:    [^szpilman]: [@ref auteurs="Szpilman D" titre="Drowning" ...]
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
