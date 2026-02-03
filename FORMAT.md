# Format Markdown pour les Présentations

Ce document décrit la syntaxe Markdown utilisée pour créer des présentations interactives.

## Structure générale

```markdown
---
title: Titre de la Présentation
subtitle: Sous-titre optionnel
author: Nom de l'auteur
date: Janvier 2025
university: Institution
department: Département
---

# Titre de la Présentation
> Sous-titre affiché sur la slide

## Première Section
...

## Deuxième Section
...

# Conclusion
> Citation ou message clé
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

Exemple :
```yaml
---
title: Hypothermie Accidentelle
theme: glacier
---
```

Le thème peut aussi être spécifié en ligne de commande :
```bash
python compile_cours.py cours.md --theme bordeaux
```

## Types de slides

### Slide de titre (`#`)

```markdown
# Titre Principal
> Sous-titre ou citation
```

- Affichée en plein écran avec fond dégradé
- Pas de détails ni questions (automatique)

### Slide de contenu (`##`)

```markdown
## Titre de la Section

- Premier point clé
- Deuxième point clé
- Troisième point clé

:::details

**Sous-titre:**

Paragraphe de détail explicatif...

![Légende](https://url-image.png)

**Références:** Auteur et al. Journal 2024

:::questions

- Première question de révision ?
- Deuxième question ?
```

### Slide d'image (`###`)

```markdown
### Image: https://url-de-image.png
Caption: Légende de l'image
```

## Sections spéciales

### Section détails (`:::details`)

Contient les explications approfondies, accessibles via la flèche droite.

```markdown
:::details

**Définition:**

Texte explicatif détaillé...

**Mécanisme:**

- Point de liste dans les détails
- Autre point

![Schéma explicatif](https://url.png)

**Références:** Source et al. 2024
```

Éléments supportés :
- **Sous-titres en gras** : `**Titre:**` ou `**Titre**`
- **Paragraphes** : texte simple
- **Listes** : `- item` ou `* item`
- **Images** : `![légende](url)`
- **Formatage inline** : `**gras**`, `*italique*`, `` `code` ``

### Section questions (`:::questions`)

Questions de révision, accessibles depuis les détails.

```markdown
:::questions

- Quelle est la définition de X ?
- Citez 3 exemples de Y.
- Expliquez le mécanisme de Z.
```

### Désactiver les annexes (`:::no-annexes`)

Pour une slide sans détails ni questions :

```markdown
## Slide Simple

- Point 1
- Point 2

:::no-annexes
```

## Exemples complets

### Slide standard complète

```markdown
## Physiopathologie de l'Hypothermie

- Thermorégulation : contrôle hypothalamique
- Mécanismes compensateurs : frissons, vasoconstriction
- Échec : épuisement glycogène (3-5h)
- Cascade systémique multi-organes

:::details

**Thermorégulation normale:**

L'hypothalamus maintient la température centrale à 37°C ± 0.5°C via des thermorécepteurs centraux et périphériques.

**Mécanismes de défense:**

Les frissons débutent par les masséters puis se généralisent. Leur efficacité est limitée dans le temps (3-5 heures).

![Schéma thermorégulation](https://example.com/schema.png)

**Références:** Giesbrecht et al. J Appl Physiol 2000

:::questions

- À quelle température les frissons cessent-ils ?
- Pourquoi l'hypothermie peut-elle être neuroprotectrice ?
```

### Slide avec détails seuls (sans questions)

```markdown
## Références Bibliographiques

- Guidelines internationales
- Articles de référence
- Revues systématiques

:::details

**Textes fondamentaux:**

1. Brown DJA et al. Accidental hypothermia. N Engl J Med. 2012.

2. Paal P et al. Accidental hypothermia update. Resuscitation. 2022.

**Guidelines:**

3. Zafren K et al. Wilderness Medical Society guidelines. 2014.
```

### Slide titre/conclusion

```markdown
# Conclusion
> "Personne n'est mort tant qu'il n'est pas chaud et mort"

:::no-annexes
```

## Bonnes pratiques

### Points clés (slide principale)
- 3 à 6 points maximum
- Phrases courtes et percutantes
- Mots-clés essentiels

### Détails
- Structurer avec des sous-titres en gras
- Un paragraphe = une idée
- Ajouter des images/schémas quand pertinent
- Terminer par les références

### Questions
- 2 à 4 questions par slide
- Questions ouvertes ou fermées
- Couvrir les points essentiels des détails

## Conversion depuis l'ancien format

Si vous avez des fichiers avec l'ancien format (`**Détails:**`), convertissez-les avec :

```vim
:%s/^\*\*Détails:\*\*$/:::details/g
:%s/^\*\*Questions:\*\*$/:::questions/g
```

Ou en sed :
```bash
sed -i 's/^\*\*Détails:\*\*$/:::details/; s/^\*\*Questions:\*\*$/:::questions/' fichier.md
```
