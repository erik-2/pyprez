# Format Markdown pour les Présentations

Ce document décrit la syntaxe Markdown utilisée pour créer des présentations interactives.

## Structure générale
```markdown
---
title: Titre de la Présentation
subtitle: Sous-titre optionnel
author: Nom de l'auteur
date: Janvier 2025
theme: ocean
university: Institution
department: Département
---

# Titre de la Première section
> Sous-titre affiché sur la slide

## Première Sous-Section
...

## Deuxième Sous-Section
...

# Deuxième Section

# Conclusion
> Citation ou message clé

:::no-annexes
```

## Métadonnées (front matter)

Le fichier commence par un bloc YAML entre `---` :

| Champ | Description | Obligatoire |
|-------|-------------|-------------|
| `title` | Titre de la présentation | Oui |
| `subtitle` | Sous-titre | Non |
| `author` | Auteur(s) | Non |
| `date` | Date | Non |
| `theme` | Thème de couleurs | Non |
| `university` | Institution | Non |
| `department` | Département/Service | Non |

### Thèmes disponibles

| Thème | Couleur dominante | Usage suggéré |
|-------|-------------------|---------------|
| `ocean` | Bleu-vert turquoise | Noyade, milieu aquatique (défaut) |
| `glacier` | Bleu froid | Hypothermie, froid |
| `bordeaux` | Rouge sombre | Pendaison, strangulation, trauma |

## Types de slides

### Slide de Section (`#`)
```markdown
# Titre Principal
> Sous-titre ou citation

:::no-annexes
```

- Affichée en plein écran avec fond dégradé
- Pas de détails ni questions par défaut

### Slide de contenu (`##`)
```markdown
## Titre de la SousSection
> Sous-titre optionnel

- Premier point clé
- Deuxième point clé

> Citation ou définition encadrée

### Sous-section

- Autres points

:::details

**Explication:**

Paragraphe détaillé...

> Définition importante à retenir

![Schéma explicatif](schema.png)

[@ref auteurs="Dupont J, Martin P" titre="Article" revue="Journal" date="2024" doi="10.1234/xyz"]

:::questions

- Question 1 ?
- Question 2 ?
```

### Slide d'image (`## Image:`)
```markdown
## Image: nom_image.svg
> Légende de l'image
Caption: Texte alternatif

:::details

**Explication de l'image:**

Description détaillée du schéma...

:::questions

- Que représente ce schéma ?
```

- L'image occupe la majeure partie de l'écran
- Peut avoir des détails et questions associés
- Les images locales sont dans le dossier `images/`

## Éléments de contenu

### Points clés (slide principale)
```markdown
- Point avec **texte en gras**
- Point avec *texte en italique*
- Point avec `code`
```

### Blockquote / Citation (slide principale)
```markdown
> Cette citation apparaîtra dans un encadré stylisé
```

Le `>` juste après un titre (`#` ou `##`) devient le sous-titre.
Le `>` juste après une slide d'image (`## Image:`) devient la légende de l'image.
Le `>` ailleurs dans la slide principale devient un blockquote.

### Sous-titre intermédiaire (`###`)
```markdown
### Catégorie

- Point 1
- Point 2

### Autre catégorie

- Point 3
```

## Section détails (`:::details`)

Contient les explications approfondies.

### Éléments supportés

**Sous-titres en gras :**
```markdown
**Définition:**
**Mécanisme**
```

**Paragraphes :**
```markdown
Texte explicatif simple sur une ou plusieurs lignes.
```

**Listes :**
```markdown
- Premier élément
- Deuxième élément
```

**Blockquotes :**
```markdown
> Définition ou citation importante
```

**Images :**
```markdown
![Légende de l'image](nom_image.png)
```

**Références bibliographiques :**
```markdown
[@ref auteurs="Nom A, Nom B" titre="Titre article" revue="Nom Journal" date="2024" doi="10.1234/exemple"]
```

Champs disponibles pour les références :
- `auteurs` — Liste des auteurs (obligatoire)
- `titre` — Titre de l'article
- `revue` — Nom du journal
- `date` — Année de publication
- `doi` — Identifiant DOI (génère un lien)

**Formatage inline :**
- `**gras**` → **gras**
- `*italique*` → *italique*
- `` `code` `` → `code`

## Section questions (`:::questions`)
```markdown
:::questions

- Quelle est la définition de X ?
- Citez 3 exemples de Y.
- Expliquez le mécanisme de Z.
```

## Désactiver les annexes (`:::no-annexes`)
```markdown
## Slide Simple

- Point 1
- Point 2

:::no-annexes
```

## Gestion des images

### Structure des fichiers
```
projet/
├── cours/
│   ├── noyade.md
│   ├── hypothermie.md
│   ├── szpilman.svg
│   ├── schema_thermo.png
│   └── photo_cas.jpg
└── build.py
```

### Référencement

**Dans une slide d'image :**
```markdown
## Image: szpilman.svg
> Classification de Szpilman
```

**Dans les détails :**
```markdown
![Légende](szpilman.svg)
```

**Image externe (URL complète) :**
```markdown
![Légende](https://example.com/image.png)
```

### Formats recommandés

| Format | Usage |
|--------|-------|
| `.svg` | Schémas, diagrammes, arbres décisionnels |
| `.png` | Captures, images avec transparence |
| `.jpg` | Photos |
| `.webp` | Photos optimisées web |

## Exemple complet
```markdown
---
title: Prise en Charge de la Noyade
subtitle: Du sauvetage à la réanimation
author: Dr Jean Dupont
date: Janvier 2025
theme: ocean
university: CHU Bordeaux
department: SAMU 33
---

# Prise en Charge de la Noyade
> Du sauvetage à la réanimation

:::no-annexes

## Définition et Épidémiologie
> OMS 2021

- 236 000 décès/an dans le monde
- 3ème cause de décès accidentel

> La noyade est une insuffisance respiratoire résultant de la submersion

### Facteurs de risque

- Absence de surveillance
- Alcool

:::details

**Définition OMS:**

> La noyade est une insuffisance respiratoire résultant de la submersion ou de l'immersion en milieu liquide.

Cette définition inclut les cas mortels et non mortels.

**Épidémiologie française:**

En France, environ 1000 décès par an sont liés à la noyade.

[@ref auteurs="InVS" titre="Enquête NOYADES" revue="BEH" date="2023"]

:::questions

- Quelle est la définition OMS de la noyade ?
- Citez 3 facteurs de risque de noyade.

## Image: szpilman.svg
> Classification de Szpilman — Arbre décisionnel
Caption: Algorithme de classification des noyades

:::details

**Utilisation de l'arbre:**

Cet algorithme permet de classifier rapidement la gravité d'une noyade en 6 stades.

**Stade 0 (Rescue):** Patient conscient, pas de toux, pas de détresse.

[@ref auteurs="Szpilman D" titre="Drowning" revue="N Engl J Med" date="2012" doi="10.1056/NEJMra1013317"]

:::questions

- À quel stade les frissons disparaissent-ils ?
- Quel stade correspond à l'arrêt cardiaque ?

# Conclusion
> Chaque minute compte

:::no-annexes
```

## Bonnes pratiques

### Points clés (slide principale)
- 3 à 6 points maximum
- Phrases courtes (< 10 mots)
- Utiliser les blockquotes pour les définitions clés

### Détails
- Structurer avec des sous-titres en gras
- Un paragraphe = une idée
- Inclure les images/schémas pertinents
- Toujours citer les références

### Questions
- 2 à 4 questions par slide
- Mélanger factuelles et réflexives
- Couvrir les points essentiels

### Images
- SVG pour les schémas (qualité, légèreté)
- Noms explicites (ex: `szpilman_arbre.svg`)
- Toujours ajouter une légende
