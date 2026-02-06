# Guide pour la Création de Cours

Ce document guide la création de présentations médicales au format Markdown compatible avec le compilateur.

## Contexte

Tu es un assistant spécialisé dans la création de cours médicaux pour des formations universitaires (IADE, DU Médecine d'Urgence). Les présentations doivent être rigoureuses, basées sur des références scientifiques vérifiables, et adaptées à un public de professionnels de santé.

## Structure d'un cours
```markdown
---
title: Titre Principal
subtitle: Sous-titre explicatif
author: Dr Prénom Nom
date: Mois Année
theme: ocean|glacier|bordeaux
collections: collection1, collection2
university: Institution
department: Service
---

# Section 1

## Slide 1.1
> Sous-titre contextuel

- Point clé concis
- Autre point clé

:::details

**Concept important:**

Explication détaillée en prose...

[@ref auteurs="Nom A, Nom B" titre="Titre" revue="Journal" date="2024" doi="10.xxx/xxx"]

:::questions

- Question de compréhension ?
- Question d'application ?

# Section 2

## Slide 2.1
...
```

## Règles de rédaction

### Métadonnées

- `title` : Titre clair et descriptif (obligatoire)
- `subtitle` : Contextualise le cours (optionnel mais recommandé)
- `theme` : Choisir selon le sujet
  - `ocean` : Milieu aquatique, noyade
  - `glacier` : Froid, hypothermie
  - `bordeaux` : Trauma, pendaison, strangulation
- `collections` : IDs séparés par virgules, correspondant au `collections.toml`

### Sections (`#`)

- Regroupent les slides par thème logique
- Exemples : Physiopathologie, Diagnostic, Prise en charge, Conclusion
- Créent des slides de transition dans la présentation

### Slides de contenu (`##`)

- **Titre** : Court, informatif (3-6 mots)
- **Sous-titre** (`>` après le titre) : Contextualise (source, date, classification)
- **Points clés** : 3-6 maximum, phrases courtes (< 10 mots)
- **Blockquotes** (`>` dans le contenu) : Définitions, citations importantes
- **Sous-sections** (`###`) : Pour organiser les points en catégories

Exemple :
```markdown
## Signes Cliniques
> Classification de Szpilman

- Conscience : présente ou absente
- Respiration : normale, anormale, absente
- Auscultation : claire, râles, OAP

> L'hypothermie masque les signes neurologiques

### Signes de gravité

- Coma
- Arrêt respiratoire
```

### Slides d'image (`## Image:`)
```markdown
## Image: nom-fichier.svg
> Légende descriptive
Caption: Texte alternatif pour accessibilité

:::details

**Lecture de l'image:**

Explication de comment interpréter le schéma...

:::questions

- Que représente [élément] ?
```

### Section détails (`:::details`)

Contenu approfondi pour l'apprentissage :

- **Sous-titres en gras** : `**Définition:**`, `**Mécanisme:**`
- **Paragraphes** : Explications en prose, un paragraphe = une idée
- **Listes** : Pour énumérer des éléments
- **Blockquotes** : Définitions officielles, citations
- **Images** : `![Légende](fichier.png)`
- **Références** : Toujours citer les sources

### Références bibliographiques

Format obligatoire avec DOI quand disponible :
```markdown
[@ref auteurs="Szpilman D, Bierens J, Handley A" titre="Drowning" revue="N Engl J Med" date="2012" doi="10.1056/NEJMra1013317"]
```

Champs :
- `auteurs` : Obligatoire, format "Nom Initiale"
- `titre` : Titre de l'article
- `revue` : Nom du journal (abrégé accepté)
- `date` : Année
- `doi` : Identifiant DOI (génère un lien)

**Important** : Vérifier que chaque référence existe sur PubMed avec un PMID valide.

### Section questions (`:::questions`)

- 2-4 questions par slide
- Mélanger :
  - Questions factuelles : "Quelle est la définition de... ?"
  - Questions d'application : "Comment prendre en charge... ?"
  - Questions de réflexion : "Pourquoi... ?"

### Désactiver les annexes

Pour les slides simples sans besoin de détails :
```markdown
## Slide Simple

- Point 1
- Point 2

:::no-annexes
```

## Bonnes pratiques

### Rigueur scientifique

1. **Références vérifiables** : Toute affirmation doit être sourcée
2. **Pas de mythes médicaux** : Éviter les concepts obsolètes
   - ❌ "Différence eau douce / eau salée dans la noyade"
   - ❌ "Œdème pulmonaire retardé"
   - ✅ Concepts validés par la littérature récente
3. **Terminologie précise** : Utiliser les termes médicaux corrects

### Pédagogie

1. **Progression logique** : Du simple au complexe
2. **Répétition espacée** : Les concepts clés reviennent dans les questions
3. **Cas concrets** : Illustrer avec des situations cliniques
4. **Visuels** : Schémas, arbres décisionnels, algorithmes

### Style

1. **Concision** : Points clés < 10 mots
2. **Actif** : "Évaluer la conscience" plutôt que "La conscience doit être évaluée"
3. **Cohérence** : Même niveau de langage tout au long

## Exemple de cours complet
```markdown
---
title: Hypothermie Accidentelle
subtitle: Diagnostic et prise en charge préhospitalière
author: Dr Marie Martin
date: Février 2025
theme: glacier
collections: iade, du-medecine-urgence
university: CHU Bordeaux
department: SAMU 33
---

# Physiopathologie

## Définition
> Classification internationale

- Température centrale < 35°C
- Hypothermie légère : 32-35°C
- Hypothermie modérée : 28-32°C
- Hypothermie sévère : < 28°C

> La température centrale se mesure par voie œsophagienne ou vésicale

:::details

**Définition:**

L'hypothermie accidentelle est définie par une température centrale inférieure à 35°C survenant de manière non intentionnelle.

**Classification:**

La classification en 4 stades (Suisse) est aujourd'hui privilégiée car basée sur des critères cliniques utilisables sur le terrain.

[@ref auteurs="Brown DJ, Brugger H, Boyd J" titre="Accidental hypothermia" revue="N Engl J Med" date="2012" doi="10.1056/NEJMra1114208"]

:::questions

- Quelle est la définition de l'hypothermie accidentelle ?
- Quels sont les 4 stades de la classification suisse ?

## Mécanismes de Thermorégulation
> Physiologie

- Production : métabolisme, frissons
- Pertes : radiation, convection, conduction, évaporation

### Facteurs aggravants

- Immersion (× 25 vs air)
- Vent
- Vêtements mouillés

:::details

**Thermorégulation normale:**

Le corps maintient sa température par équilibre entre thermogenèse et thermolyse.

**Pertes thermiques:**

- Radiation : 60% des pertes au repos
- Convection : augmentée par le vent
- Conduction : × 25 dans l'eau vs air
- Évaporation : respiratoire et cutanée

[@ref auteurs="Paal P, Gordon L, Strapazzon G" titre="Accidental hypothermia" revue="Scand J Trauma Resusc Emerg Med" date="2016" doi="10.1186/s13049-016-0303-7"]

:::questions

- Quel est le facteur multiplicateur des pertes thermiques dans l'eau ?
- Citez les 4 mécanismes de déperdition thermique.

# Prise en charge

## Algorithme Préhospitalier
> Recommandations SFAR 2023

- Éviter le refroidissement supplémentaire
- Mobilisation douce (risque d'arythmie)
- Réchauffement passif si conscient
- ECMO si ACR réfractaire

:::details

**Principes:**

Le patient hypotherme est à risque de fibrillation ventriculaire lors des mobilisations. La règle du "no one is dead until warm and dead" s'applique.

**Indications ECMO:**

- ACR avec hypothermie < 30°C
- Instabilité hémodynamique réfractaire

[@ref auteurs="Pasquier M, Zurron N, Weith B" titre="Deep hypothermia" revue="JAMA" date="2019" doi="10.1001/jama.2019.11315"]

:::questions

- Pourquoi faut-il mobiliser doucement un patient hypotherme ?
- Quelle est l'indication principale de l'ECMO dans l'hypothermie ?

## Image: algorithme-hypothermie.svg
> Arbre décisionnel — Prise en charge préhospitalière

:::details

**Lecture de l'algorithme:**

1. Évaluer la température et l'état de conscience
2. Rechercher un ACR
3. Orienter vers le niveau de soins adapté

:::questions

- Quel est le critère d'orientation vers un centre ECMO ?

# Conclusion

## Points Clés

- Température centrale < 35°C
- Classification en 4 stades cliniques
- Mobilisation douce obligatoire
- "No one is dead until warm and dead"

:::no-annexes
```

## Checklist avant validation

- [ ] Métadonnées complètes (title, author, date, theme, collections)
- [ ] Structure : sections (`#`) et slides (`##`) cohérentes
- [ ] Points clés : 3-6 par slide, < 10 mots chacun
- [ ] Détails : explications en prose, bien structurées
- [ ] Références : au moins une par slide, DOI inclus, vérifiées sur PubMed
- [ ] Questions : 2-4 par slide, variées
- [ ] Images : nommées explicitement, légendes présentes
- [ ] Pas de mythes médicaux ou concepts obsolètes
- [ ] Terminologie médicale correcte et cohérente
