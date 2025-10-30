# Générateur d'Arbre Généalogique Académique

Outil pour construire et visualiser des arbres généalogiques académiques à partir de la base de données [theses.fr](https://theses.fr).

## Objectif

Partant d'un directeur de thèse, ce projet :
1. Récupère toutes ses thèses dirigées (direction et codirection)
2. Pour chaque étudiant, recherche s'il est devenu directeur
3. Continue récursivement sur plusieurs générations
4. Génère un graphique de l'arbre généalogique académique

## Prérequis

```bash
pip install -r requirements.txt
```

## Workflow en 2 étapes

### 1. Trouver l'identifiant d'une personne

1. Allez sur https://theses.fr
2. Recherchez le nom du directeur de thèse
3. Cliquez sur son profil
4. L'identifiant est dans l'URL : `https://theses.fr/personnes/XXXXXXXXX`

### 2. Générer le JSON de l'arbre généalogique

```bash
# Recherche récursive avec profondeur maximale de 3 niveaux
python academic_genealogy.py <person_id> --max-depth 3
# Conversion au format D3/arbre interactif
python export_d3_tree.py genealogy_<person_id>.json d3_tree_<person_id>.json
```

Cela génère un fichier `d3_tree_<person_id>.json` prêt à être injecté dans le HTML interactif.

### 3. Générer le HTML interactif

```bash
# Produit un HTML interactif prêt à ouvrir dans le navigateur
python export_genealogy_html.py d3_tree_<person_id>.json arbre.html --nom "Nom Racine"
```

- Le paramètre `--nom` permet d'afficher dynamiquement le nom central dans l'arbre (ex: "God Father").
- Ouvrez simplement `arbre.html` dans votre navigateur pour explorer l'arbre généalogique interactif (zoom, tooltip, navigation, etc.).

## Structure du projet

```
/
├── academic_genealogy.py          # Construction récursive de l'arbre
├── export_d3_tree.py              # Conversion JSON pour D3
├── export_genealogy_html.py       # Génération du HTML interactif
├── abre_gene.html                 # Template HTML D3 interactif
├── requirements.txt               # Dépendances Python
├── example/                       # Exemple d'arbre généalogique produit
│   └── arbre_gene_JMM.html        # HTML interactif d'exemple
└── README.md                      # Ce fichier
```