# Compilateur de Présentations Markdown

Transforme des fichiers Markdown structurés en présentations HTML interactives avec navigation clavier/tactile.

## Fonctionnalités

- **Slides principales** avec points clés
- **Slides de détails** pour approfondir (texte, images)
- **Slides de questions** pour la révision
- **Navigation** : flèches clavier + swipe tactile
- **Export document** : extraction des détails en HTML imprimable/PDF

## Installation

```bash
git clone <repo>
cd cours
```

Aucune dépendance externe requise (Python 3.10+).

## Utilisation

### Compiler une présentation

```bash
python compile_cours.py mon_cours.md
```

Options :
```bash
python compile_cours.py mon_cours.md -o presentation.html
python compile_cours.py mon_cours.md --js-uri https://cdn.example.com/nav.js
```

### Extraire les détails (document imprimable)

```bash
python extract_details.py mon_cours.md
```

Génère `mon_cours_details.html` avec table des matières et bouton d'impression.

## Navigation dans la présentation

| Action | Clavier | Tactile |
|--------|---------|---------|
| Slide suivante | ↓ | Swipe haut |
| Slide précédente | ↑ | Swipe bas |
| Voir détails | → | Swipe gauche |
| Voir questions | → (depuis détails) | Swipe gauche |
| Retour | ← | Swipe droite |

## Structure du projet

```
cours/
├── compile_cours.py      # Compilateur principal
├── extract_details.py    # Extracteur de détails
├── css/
│   └── style.css         # Styles de la présentation
├── js/
│   └── presentation.js   # Navigation interactive
└── lib/
    ├── config.py         # Configuration (marqueurs, etc.)
    ├── models.py         # Modèles de données
    ├── parser.py         # Parser Markdown
    └── generator.py      # Générateur HTML
```

## Documentation

- [FORMAT.md](FORMAT.md) — Syntaxe Markdown pour les présentations
- [PROMPT.md](PROMPT.md) — Instructions pour générer du contenu avec un LLM

## Licence

MIT
