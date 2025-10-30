"""
Script pour générer un HTML interactif à partir d'un fichier JSON de généalogie (format D3/arbre_gene)
Usage :
    python export_genealogy_html.py d3_tree_xxx.json arbre_gene.html [--nom "Nom Racine"]

- Injecte le JSON dans le template abre_gene.html
- Remplace le nom du superviseur central si besoin
"""
import sys
import json


import re

TEMPLATE = "abre_gene.html"

if len(sys.argv) < 3:
    print("Usage: python export_genealogy_html.py d3_tree_xxx.json arbre_gene.html [--nom 'Nom Racine']")
    sys.exit(1)

json_path = sys.argv[1]
html_out = sys.argv[2]
nom_racine = None
if '--nom' in sys.argv:
    idx = sys.argv.index('--nom')
    if idx+1 < len(sys.argv):
        nom_racine = sys.argv[idx+1]

with open(json_path, encoding="utf-8") as f:
    tree_data = json.load(f)

# Lire le template
with open(TEMPLATE, encoding="utf-8") as f:
    html = f.read()

# Remplacer la section var treeData = {...}
tree_json = json.dumps(tree_data, ensure_ascii=False, indent=2)
html = re.sub(r"var treeData = [^;]*;", f"var treeData = {tree_json};", html)


# Injection dynamique du nom central via window.centralName
if nom_racine:
    # Ajouter juste avant le script D3 principal
    html = re.sub(r'(<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js"></script>)',
                  r'\1\n<script>window.centralName = "' + nom_racine.replace('"', '\\"') + '";</script>', html, count=1)

with open(html_out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"✅ HTML interactif généré : {html_out}")
