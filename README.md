# Compilateur de Présentations Markdown

Transforme des fichiers Markdown structurés en présentations HTML interactives avec navigation clavier/tactile.

## Fonctionnalités

- **Slides principales** avec points clés
- **Slides de détails** pour approfondir (texte, images)
- **Slides de questions** pour la révision
- **Navigation** : flèches clavier + swipe tactile
- **Thèmes** : ocean, glacier, bordeaux
- **Export document** : extraction des détails en HTML imprimable/PDF
- **Catalogue** : génération automatique d'un index des cours

## Installation

```bash
git clone <repo>
cd cours
```

Aucune dépendance externe requise (Python 3.10+).

## Utilisation

### Compiler un seul cours

```bash
python compile_cours.py mon_cours.md
python compile_cours.py mon_cours.md -o presentation.html
python compile_cours.py mon_cours.md --theme glacier
```

### Extraire les détails (document imprimable)

```bash
python extract_details.py mon_cours.md
```

### Build complet (tous les cours + catalogue)

```bash
python build.py                              # Compile ./*.md → ./dist/
python build.py -s sources/ -o public/       # Dossiers personnalisés
python build.py --clean --title "Mes Cours"  # Nettoie et titre custom
```

Structure générée :
```
dist/
├── index.html              # Catalogue des cours
├── assets/
│   ├── style.css
│   └── presentation.js
├── noyade/
│   ├── index.html          # Présentation
│   └── details.html        # Document imprimable
└── hypothermie/
    ├── index.html
    └── details.html
```

### Déployer vers un serveur FTP

```bash
python deploy.py --host ftp.example.com --user admin
```

Ou avec un fichier `.env` :
```env
FTP_HOST=ftp.example.com
FTP_USER=admin
FTP_PASSWORD=secret
FTP_PATH=/public_html/cours
```

## Workflow recommandé

```bash
# 1. Éditer les cours .md
vim mon_cours.md

# 2. Build local
python build.py --clean

# 3. Prévisualiser
open dist/index.html

# 4. Déployer
python deploy.py
```

### Avec Git + cPanel

1. Créer un repo Git avec vos fichiers `.md`
2. Dans cPanel > Git Version Control, cloner le repo
3. Ajouter un cron job :
   ```bash
   cd /home/user/cours && git pull && python build.py -o /home/user/public_html/cours
   ```

## Navigation dans la présentation

| Action | Clavier | Tactile |
|--------|---------|---------|
| Slide suivante | ↓ | Swipe haut |
| Slide précédente | ↑ | Swipe bas |
| Voir détails | → | Swipe gauche |
| Voir questions | → (depuis détails) | Swipe gauche |
| Retour | ← | Swipe droite |

## Thèmes

| Thème | Couleurs | Usage suggéré |
|-------|----------|---------------|
| `ocean` | Bleu-vert turquoise | Noyade, milieu aquatique |
| `glacier` | Bleu froid | Hypothermie, froid |
| `bordeaux` | Rouge sombre | Trauma, pendaison |

## Structure du projet

```
cours/
├── build.py              # Build tous les cours + index
├── deploy.py             # Déploiement FTP
├── compile_cours.py      # Compilateur unitaire
├── extract_details.py    # Extracteur de détails
├── css/
│   └── style.css
├── js/
│   └── presentation.js
└── lib/
    ├── config.py         # Thèmes, marqueurs
    ├── models.py         # Modèles de données
    ├── parser.py         # Parser Markdown
    └── generator.py      # Générateur HTML
```

## Documentation

- [FORMAT.md](FORMAT.md) — Syntaxe Markdown pour les présentations
- [PROMPT.md](PROMPT.md) — Instructions pour générer du contenu avec un LLM

## Licence

MIT
