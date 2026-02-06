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
collections: iade, du-medecine-urgence
university: Institution
department: Département
---

# Première Section

## Première Slide
> Sous-titre optionnel

- Point clé 1
- Point clé 2

:::details
Explications détaillées...
:::questions
- Question 1 ?

## Deuxième Slide
...

# Deuxième Section

## Autre Slide
...
```

## Métadonnées (front matter)

Le fichier commence par un bloc YAML entre `---` :

| Champ | Description | Obligatoire |
|-------|-------------|-------------|
| `title` | Titre de la présentation | Oui |
| `subtitle` | Sous-titre (affiché sur la slide de titre) | Non |
| `author` | Auteur(s) | Non |
| `date` | Date | Non |
| `theme` | Thème de couleurs | Non |
| `collections` | Collections (séparées par virgules) | Non |
| `university` | Institution | Non |
| `department` | Département/Service | Non |

### Thèmes disponibles

| Thème | Couleur dominante | Usage suggéré |
|-------|-------------------|---------------|
| `ocean` | Bleu-vert turquoise | Noyade, milieu aquatique (défaut) |
| `glacier` | Bleu froid | Hypothermie, froid |
| `bordeaux` | Rouge sombre | Pendaison, strangulation, trauma |

### Collections

Les collections regroupent les cours par thématique ou destinataire :
```yaml
collections: iade, du-medecine-urgence
```

Les collections doivent être définies dans `collections.toml` à la racine du projet.

## Types de slides

### Slide de titre (automatique)

Générée automatiquement depuis les métadonnées `title` et `subtitle`.

### Slide de section (`#`)
```markdown
# Nom de la Section
```

Crée une slide de transition avec le titre de la section.

### Slide de contenu (`##`)
```markdown
## Titre de la Slide
> Sous-titre optionnel

- Premier point clé
- Deuxième point clé

> Citation ou définition encadrée

### Sous-section

- Autres points

:::details

**Explication:**

Paragraphe détaillé...

![Schéma explicatif](schema.png)

[@ref auteurs="Dupont J" titre="Article" revue="Journal" date="2024" doi="10.1234/xyz"]

:::questions

- Question 1 ?
- Question 2 ?
```

### Slide d'image (`## Image:`)
```markdown
## Image: nom_image.svg
> Légende de l'image
Caption: Texte alternatif pour accessibilité

:::details

**Explication de l'image:**

Description détaillée...

:::questions

- Que représente ce schéma ?
```

## Éléments de contenu

### Points clés (slide principale)
```markdown
- Point avec **texte en gras**
- Point avec *texte en italique*
- Point avec `code`
```

### Sous-titre de slide

Le `>` juste après un titre `##` devient le sous-titre :
```markdown
## Ma Slide
> Ce texte est le sous-titre
```

### Blockquote / Citation

Le `>` ailleurs dans la slide devient un blockquote stylisé :
```markdown
## Ma Slide

- Point 1

> Cette citation apparaîtra dans un encadré

- Point 2
```

### Sous-titre intermédiaire (`###`)
```markdown
### Catégorie A

- Point 1
- Point 2

### Catégorie B

- Point 3
```

## Section détails (`:::details`)

Contient les explications approfondies, affichées en appuyant sur `→`.

### Éléments supportés

**Sous-titres en gras :**
```markdown
**Définition:**
```

**Paragraphes :**
```markdown
Texte explicatif sur une ou plusieurs lignes.
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
![Légende](nom_image.png)
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
- `doi` — Identifiant DOI (génère un lien cliquable)

## Section questions (`:::questions`)
```markdown
:::questions

- Quelle est la définition de X ?
- Citez 3 exemples de Y.
```

Affichées en appuyant sur `→` depuis les détails.

## Désactiver les annexes (`:::no-annexes`)
```markdown
## Slide Simple

- Point 1
- Point 2

:::no-annexes
```

Cette slide n'aura pas de détails ni de questions.

## Gestion des images

### Structure recommandée
```
cours/
├── images/                   # Images partagées entre tous les cours
│   └── schema-general.svg
└── ma-collection/
    ├── cours.md
    └── images/               # Images spécifiques à cette collection
        └── schema-local.png
```

### Référencement

**Dans une slide d'image :**
```markdown
## Image: szpilman.svg
> Classification de Szpilman
```

**Dans les détails :**
```markdown
![Légende](schema.png)
```

**Image externe :**
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
collections: iade, du-medecine-urgence
university: CHU Bordeaux
department: SAMU 33
---

# Physiopathologie

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

[@ref auteurs="OMS" titre="Global Report on Drowning" date="2021"]

:::questions

- Quelle est la définition OMS de la noyade ?
- Citez 3 facteurs de risque.

## Image: szpilman.svg
> Classification de Szpilman — Arbre décisionnel

:::details

**Utilisation:**

Cet algorithme permet de classifier rapidement la gravité.

[@ref auteurs="Szpilman D" titre="Drowning" revue="N Engl J Med" date="2012" doi="10.1056/NEJMra1013317"]

:::questions

- Quel stade correspond à l'arrêt cardiaque ?

# Prise en charge

## Sur le terrain

- Extraction de l'eau
- Évaluation ABCDE

:::details

**Priorités:**

La ventilation est prioritaire sur les compressions thoraciques.

:::questions

- Quelle est la priorité initiale ?

# Conclusion
```

## Bonnes pratiques

### Slides principales
- 3 à 6 points maximum par slide
- Phrases courtes (< 10 mots)
- Utiliser les blockquotes pour les définitions clés

### Détails
- Structurer avec des sous-titres en gras
- Un paragraphe = une idée
- Toujours citer les références

### Questions
- 2 à 4 questions par slide
- Mélanger questions factuelles et réflexives

### Images
- SVG pour les schémas (qualité, légèreté)
- Noms de fichiers explicites
- Toujours ajouter une légende

### Collections
- Définir les collections dans `collections.toml`
- Un cours peut appartenir à plusieurs collections
- Utiliser des IDs en minuscules avec tirets (`du-medecine-urgence`)

