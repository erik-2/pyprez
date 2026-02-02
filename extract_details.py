#!/usr/bin/env python3
"""
Extracteur de Sections Détails - Cours Markdown
Crée un document HTML élégant et imprimable à partir des sections **Détails:**

Usage:
    python extract_details.py cours.md
    python extract_details.py cours.md -o document.html
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class Section:
    """Représente une section avec son titre et son contenu détaillé"""
    def __init__(self, title: str, level: int):
        self.title = title
        self.level = level  # 1 = #, 2 = ##, etc.
        self.details = []  # Liste des paragraphes de détails
        self.is_details_section = False
    
    def __repr__(self):
        return f"<Section {self.level}: {self.title} ({len(self.details)} paragraphes)>"


def parse_markdown_for_details(md_content: str) -> tuple[Dict[str, str], List[Section]]:
    """Parse le Markdown et extrait les métadonnées + sections avec détails"""
    lines = md_content.split('\n')
    metadata = {}
    sections = []
    current_section = None
    in_details = False
    
    i = 0
    
    # Parser les métadonnées
    if lines[0].strip() == '---':
        i = 1
        while i < len(lines) and lines[i].strip() != '---':
            if ':' in lines[i]:
                key, value = lines[i].split(':', 1)
                metadata[key.strip()] = value.strip()
            i += 1
        i += 1
    
    # Parser les sections
    while i < len(lines):
        line = lines[i].strip()
        
        # Nouveau titre de section
        if line.startswith('#'):
            # Sauvegarder la section précédente si elle a des détails
            if current_section and current_section.details:
                sections.append(current_section)
            
            # Déterminer le niveau
            level = 0
            while line[level] == '#':
                level += 1
            
            title = line[level:].strip()
            current_section = Section(title, level)
            in_details = False
        
        # Section détails
        elif line == '**Détails:**' or line == '**Details:**':
            in_details = True
            if current_section:
                current_section.is_details_section = True
        
        # Sortie de la section détails
        elif line.startswith('**Questions:**') or line == '[no-annexes]':
            in_details = False
        
        # Contenu des détails
        elif in_details and line and not line.startswith('#'):
            if current_section:
                # Gérer les sous-titres en gras
                if line.startswith('**') and line.endswith('**') and ':' not in line:
                    # Sous-titre
                    current_section.details.append({
                        'type': 'subtitle',
                        'content': line[2:-2]
                    })
                elif line.startswith('**') and line.endswith(':'):
                    # Sous-titre avec :
                    current_section.details.append({
                        'type': 'subtitle',
                        'content': line[2:-1]
                    })
                elif line.startswith('- ') or line.startswith('* '):
                    # Point de liste
                    current_section.details.append({
                        'type': 'list_item',
                        'content': line[2:]
                    })
                else:
                    # Paragraphe normal
                    current_section.details.append({
                        'type': 'paragraph',
                        'content': line
                    })
        
        i += 1
    
    # Ajouter la dernière section
    if current_section and current_section.details:
        sections.append(current_section)
    
    return metadata, sections


def format_text_with_markdown(text: str) -> str:
    """Convertit le Markdown simple en HTML"""
    # Gras
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italique
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Code inline
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    return text


def generate_html_document(metadata: Dict[str, str], sections: List[Section]) -> str:
    """Génère le document HTML complet"""
    
    # En-tête du document
    title = metadata.get('title', 'Document de Cours')
    author = metadata.get('author', '')
    university = metadata.get('university', '')
    date = metadata.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Notes Détaillées</title>
    <style>
        :root {{
            --primary: #0a4d68;
            --secondary: #088395;
            --accent: #05bfdb;
            --text: #1a1a1a;
            --text-light: #4a5568;
            --bg: #ffffff;
            --bg-section: #f8f9fa;
            --border: #e2e8f0;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        @media print {{
            body {{
                font-size: 11pt;
            }}
            .page-break {{
                page-break-after: always;
            }}
            .no-print {{
                display: none;
            }}
            a {{
                color: #000;
                text-decoration: none;
            }}
            .section {{
                page-break-inside: avoid;
            }}
        }}
        
        body {{
            font-family: 'Georgia', 'Garamond', serif;
            line-height: 1.8;
            color: var(--text);
            background: var(--bg);
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .header {{
            text-align: center;
            border-bottom: 3px solid var(--primary);
            padding-bottom: 2rem;
            margin-bottom: 3rem;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            color: var(--primary);
            margin-bottom: 0.5rem;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.2rem;
            color: var(--secondary);
            font-style: italic;
            margin-bottom: 1rem;
        }}
        
        .header .metadata {{
            font-size: 0.95rem;
            color: var(--text-light);
            margin-top: 1rem;
        }}
        
        .header .metadata span {{
            margin: 0 1rem;
        }}
        
        .toc {{
            background: var(--bg-section);
            border-left: 4px solid var(--accent);
            padding: 1.5rem;
            margin-bottom: 3rem;
            border-radius: 4px;
        }}
        
        .toc h2 {{
            font-size: 1.3rem;
            color: var(--primary);
            margin-bottom: 1rem;
        }}
        
        .toc ul {{
            list-style: none;
        }}
        
        .toc li {{
            margin-bottom: 0.5rem;
        }}
        
        .toc a {{
            color: var(--secondary);
            text-decoration: none;
            transition: color 0.2s;
        }}
        
        .toc a:hover {{
            color: var(--primary);
            text-decoration: underline;
        }}
        
        .section {{
            margin-bottom: 3rem;
        }}
        
        .section-title {{
            font-size: 1.8rem;
            color: var(--primary);
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border);
            font-weight: 600;
        }}
        
        .section-title.level-1 {{
            font-size: 2rem;
            color: var(--secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .section-content {{
            padding-left: 1rem;
        }}
        
        .detail-subtitle {{
            font-size: 1.2rem;
            color: var(--secondary);
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.8rem;
        }}
        
        .detail-paragraph {{
            font-size: 1rem;
            color: var(--text);
            margin-bottom: 1rem;
            text-align: justify;
            line-height: 1.8;
        }}
        
        .detail-list {{
            margin-left: 2rem;
            margin-bottom: 1rem;
        }}
        
        .detail-list li {{
            margin-bottom: 0.5rem;
            color: var(--text);
        }}
        
        strong {{
            color: var(--primary);
            font-weight: 600;
        }}
        
        em {{
            font-style: italic;
            color: var(--text-light);
        }}
        
        code {{
            background: var(--bg-section);
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: var(--secondary);
        }}
        
        .footer {{
            text-align: center;
            margin-top: 4rem;
            padding-top: 2rem;
            border-top: 2px solid var(--border);
            color: var(--text-light);
            font-size: 0.9rem;
        }}
        
        .print-button {{
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
            transition: all 0.3s;
        }}
        
        .print-button:hover {{
            background: var(--secondary);
            box-shadow: 0 6px 16px rgba(10, 77, 104, 0.4);
            transform: translateY(-2px);
        }}
        
        @media screen and (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            .header h1 {{
                font-size: 1.8rem;
            }}
            .section-title {{
                font-size: 1.4rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="subtitle">Notes Détaillées</div>
        <div class="metadata">'''
    
    if author:
        html += f'<span>{author}</span>'
    if university:
        html += f'<span>•</span><span>{university}</span>'
    html += f'<span>•</span><span>{date}</span>'
    
    html += '''
        </div>
    </div>
    
    <div class="toc no-print">
        <h2>📚 Table des Matières</h2>
        <ul>'''
    
    # Générer la table des matières
    for idx, section in enumerate(sections):
        anchor = f"section-{idx}"
        indent = "  " * (section.level - 1)
        html += f'\n            {indent}<li><a href="#{anchor}">{section.title}</a></li>'
    
    html += '''
        </ul>
    </div>
    
    <div class="content">'''
    
    # Générer les sections
    for idx, section in enumerate(sections):
        anchor = f"section-{idx}"
        level_class = f"level-{section.level}"
        
        html += f'\n        <div class="section" id="{anchor}">'
        html += f'\n            <h2 class="section-title {level_class}">{section.title}</h2>'
        html += '\n            <div class="section-content">'
        
        current_list = None
        
        for detail in section.details:
            if detail['type'] == 'subtitle':
                # Fermer la liste en cours si nécessaire
                if current_list:
                    html += '\n                </ul>'
                    current_list = None
                
                content = format_text_with_markdown(detail['content'])
                html += f'\n                <div class="detail-subtitle">{content}</div>'
            
            elif detail['type'] == 'list_item':
                # Ouvrir une liste si nécessaire
                if not current_list:
                    html += '\n                <ul class="detail-list">'
                    current_list = True
                
                content = format_text_with_markdown(detail['content'])
                html += f'\n                    <li>{content}</li>'
            
            else:  # paragraph
                # Fermer la liste en cours si nécessaire
                if current_list:
                    html += '\n                </ul>'
                    current_list = None
                
                content = format_text_with_markdown(detail['content'])
                html += f'\n                <p class="detail-paragraph">{content}</p>'
        
        # Fermer la liste finale si nécessaire
        if current_list:
            html += '\n                </ul>'
        
        html += '\n            </div>'
        html += '\n        </div>\n'
    
    html += '''
    </div>
    
    <div class="footer">
        <p>Document généré automatiquement à partir du cours Markdown</p>
        <p>''' + datetime.now().strftime('%d/%m/%Y à %H:%M') + '''</p>
    </div>
    
    <button class="print-button no-print" onclick="window.print()">🖨️ Imprimer</button>
</body>
</html>'''
    
    return html


def extract_details(md_file: Path, output_file: Optional[Path] = None) -> Path:
    """Extrait les sections détails et génère un HTML imprimable"""
    
    # Lire le Markdown
    print(f"📖 Lecture de {md_file}...")
    md_content = md_file.read_text(encoding='utf-8')
    
    # Parser
    print("🔍 Extraction des sections détails...")
    metadata, sections = parse_markdown_for_details(md_content)
    
    if not sections:
        print("⚠️  Aucune section avec détails trouvée !")
        return None
    
    print(f"📊 {len(sections)} sections avec détails extraites")
    
    # Générer le HTML
    print("🎨 Génération du document HTML...")
    html = generate_html_document(metadata, sections)
    
    # Écrire le fichier de sortie
    if output_file is None:
        output_file = md_file.with_name(md_file.stem + '_details.html')
    
    output_file.write_text(html, encoding='utf-8')
    print(f"✅ Document généré : {output_file}")
    
    # Statistiques
    total_paragraphs = sum(len(s.details) for s in sections)
    print(f"📝 {total_paragraphs} éléments de contenu extraits")
    
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Extrait les sections **Détails:** d\'un cours Markdown et crée un document HTML imprimable',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemples:
  python extract_details.py cours_hypothermie.md
  python extract_details.py cours_hypothermie.md -o notes.html
  
Le script extrait uniquement les sections marquées **Détails:** et crée
un document élégant prêt à imprimer ou convertir en PDF.
        '''
    )
    parser.add_argument('input', type=Path, help='Fichier Markdown d\'entrée')
    parser.add_argument('-o', '--output', type=Path, help='Fichier HTML de sortie (optionnel)')
    
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
