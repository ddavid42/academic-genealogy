import json
import sys

def build_d3_tree(persons, edges, root_id):
    # Construire un mapping parent -> enfants
    children_map = {}
    for parent, child in edges:
        children_map.setdefault(parent, []).append(child)
    
    def build_node(node_id, theses_by_author):
        node = persons[node_id]
        children = [build_node(child, theses_by_author) for child in children_map.get(node_id, [])]
        d3_node = {
            "name": node.get("name", node_id),
            "id": node_id,
        }
        # Ajouter année et titre de thèse si disponibles
        these = theses_by_author.get(node_id)
        if these:
            d3_node["annee"] = these.get("defense_date")
            d3_node["titre"] = these.get("title")
        if children:
            d3_node["children"] = children
        return d3_node
    return build_node(root_id, build_d3_tree.theses_by_author)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python export_d3_tree.py genealogy_xxx.json d3_tree_xxx.json")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)
    root_id = data["metadata"]["root_person"]
    # Construire un index theses_by_author_id
    theses_by_author = {}
    for these in data.get("theses", []):
        author_id = these.get("author_id")
        if author_id:
            theses_by_author[author_id] = these
    # Injecter dans la fonction
    build_d3_tree.theses_by_author = theses_by_author
    d3_tree = build_d3_tree(data["persons"], data["edges"], root_id)
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump(d3_tree, f, ensure_ascii=False, indent=2)
    print(f"Export D3 terminé : {sys.argv[2]}")
