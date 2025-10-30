# Nettoyage du projet : scripts et fichiers principaux

## À conserver
- academic_genealogy.py
- export_d3_tree.py
- export_genealogy_html.py
- abre_gene.html
- README.md
- requirements.txt

## À archiver ou supprimer
- fetch_theses_by_supervisor_id_only.py
- check_person_id.py
- find_person_id.sh
- arbre_genealogique_d3.html
- treeData.js
- visualize_genealogy.py
- visualize_genealogy_dash.py
- visualize_genealogy_interactive.py
- genealogy_*.json (anciens tests)
- genealogy_*.png (anciens tests)
- d3_tree_*.json (anciens tests)
- genealogy_*.html (anciens tests)
- QUICKSTART.md

# Pour archiver, déplacer dans un dossier "archive/" ou supprimer si plus utile.

# Nouveau workflow (README à mettre à jour)
1. Générer le JSON :
   python academic_genealogy.py <person_id> --max-depth 3
   python export_d3_tree.py genealogy_<person_id>.json d3_tree_<person_id>.json
2. Générer le HTML interactif :
   python export_genealogy_html.py d3_tree_<person_id>.json arbre_gene.html --nom "Nom Racine"

# Le HTML généré est prêt à être ouvert dans un navigateur.
