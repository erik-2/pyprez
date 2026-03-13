# Compilateur de Présentations Médicales

Transforme des fichiers Markdown en présentations HTML interactives avec navigation clavier, détails et questions de révision.

## Installation
```bash
# Cloner le dépôt
git clone <repo>
cd cours

# Aucune dépendance externe requise (Python 3.11+)
```

## Structure du projet
```
pyprez/                       # Racine du projet
├── build.py                  # Script de build principal
├── compile_cours.py          # Compilation d'un seul cours
├── extract_details.py        # Extraction du document imprimable
├── preview.py                # Serveur de dev avec hot reload
├── lib/                      # Bibliothèque Python
│   ├── __init__.py
│   ├── config.py             # Configuration (thèmes, assets)
│   ├── models.py             # Modèles de données
│   ├── parser.py             # Parser Markdown
│   └── generator.py          # Générateurs HTML
├── css/
│   └── style.css             # Styles des présentations
├── js/
│   └── presentation.js       # Navigation interactive
├── fonts/                    # Polices locales (Crimson Pro, Work Sans)
└── cours/                    # Dossiers sources (défaut)
    ├── collections.toml      # Définition des collections
    ├── images/               # Images partagées
    └── <dossiers>/           # Dossiers de cours
        ├── cours.md
        └── images/           # Images locales au dossier
```

## Utilisation

### Serveur de développement (hot reload)
```bash
python preview.py               # Ouvre http://localhost:8000
python preview.py --port 8080   # Port personnalisé
python preview.py --no-watch    # Sans surveillance des fichiers
```

### Build complet
```bash
# Compile tous les cours et génère le catalogue
python build.py

# Options
python build.py --clean                  # Nettoie avant compilation
python build.py -s ./sources -o ./dist   # Dossiers personnalisés
python build.py --title "Mes Formations" # Titre du site
python build.py --preview                # Inclure les cours en draft
```

### Compilation d'un seul cours
```bash
python compile_cours.py mon_cours.md
python compile_cours.py mon_cours.md -o output.html
python compile_cours.py mon_cours.md --theme glacier
```

### Extraction des détails seuls
```bash
python extract_details.py mon_cours.md
python extract_details.py mon_cours.md -o details.html
```

## Collections

Les collections permettent de regrouper les cours par thématique ou par destinataire.

### Définition (`collections.toml`)
```toml
[iade]
title = "Formation IADE"
description = "Formation initiale infirmiers anesthésistes"
icon = "🎓"
theme = "ocean"

[du-medecine-urgence]
title = "DU Médecine d'Urgence"
description = "Formation universitaire en médecine d'urgence"
icon = "🏥"
theme = "bordeaux"

[bibliographies]
title = "Revues de littérature"
description = "Présentations de service"
icon = "📚"
theme = "glacier"
```

### Attribution dans les cours

Chaque cours déclare ses collections dans ses métadonnées :
```yaml
---
title: Prise en Charge de la Noyade
author: Dr Jean Dupont
collections: iade, du-medecine-urgence
---
```

Un cours peut appartenir à plusieurs collections.

## Thèmes

| Thème | Couleur | Usage suggéré |
|-------|---------|---------------|
| `ocean` | Bleu-vert | Noyade, milieu aquatique (défaut) |
| `glacier` | Bleu froid | Hypothermie, froid |
| `bordeaux` | Rouge sombre | Pendaison, strangulation, trauma |
| `qroc` | Gris foncé / vert+rouge | Slides de révision Q&A |

Le thème peut être défini :
- Par collection dans `collections.toml`
- Par cours dans les métadonnées (`theme: glacier`)

## Structure générée
```
dist/
├── index.html                    # Page d'accueil (liste des collections)
├── collections/
│   ├── iade.html                 # Page de la collection IADE
│   └── du-medecine-urgence.html
├── dossier1/
│   └── noyade/
│       ├── index.html            # Présentation interactive (CSS/JS inlinés)
│       └── details.html          # Document imprimable (CSS/JS inlinés)
├── dossier2/
│   └── hypothermie/
│       └── ...
├── fonts/
└── images/
```

> Le CSS et le JS sont inlinés dans chaque fichier HTML — les présentations sont autonomes et ne dépendent d'aucun fichier externe.

## Navigation dans les présentations

| Touche | Action |
|--------|--------|
| `↓` ou `J` | Slide suivante |
| `↑` ou `K` | Slide précédente |
| `→` ou `L` | Détails / Questions |
| `←` ou `H` | Retour |
| `Home` | Première slide |
| `End` | Dernière slide |

## Déploiement cPanel

Créer un fichier `.cpanel.yml` à la racine du dépôt :
```yaml
---
deployment:
  tasks:
    - export DEPLOYPATH=/home/$USER/public_html/cours
    - mkdir -p $DEPLOYPATH
    - /usr/bin/python3 /home/$USER/repositories/cours/build.py -s /home/$USER/repositories/cours -o $DEPLOYPATH --clean --title "Formations Médicales"
```

Chaque `git push` déclenche automatiquement le build.

## Formats supportés

- Voir [FORMAT.md](FORMAT.md) pour la syntaxe Markdown complète
