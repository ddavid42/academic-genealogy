"""
Générateur d'arbre généalogique académique à partir de theses.fr

Ce script construit récursivement l'arbre de supervision académique :
- Identifie toutes les thèses dirigées par une personne
- Pour chaque étudiant, recherche s'il est devenu directeur de thèse
- Continue récursivement jusqu'à une profondeur maximale
- Génère un graphique de l'arbre généalogique

Usage:
    python academic_genealogy.py <person_id> [--max-depth 3] [--output genealogy.png]
"""

import requests
import json
import sys
import time
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

API_SEARCH = "https://theses.fr/api/v1/theses/recherche/"
REQUEST_DELAY = 1  # Délai entre les requêtes pour ne pas surcharger l'API


@dataclass
class Person:
    """Représente une personne dans l'arbre généalogique"""
    person_id: str
    name: str
    is_supervisor: bool = False


@dataclass
class Thesis:
    """Représente une thèse"""
    thesis_id: str
    title: str
    author_name: str
    author_id: Optional[str]
    defense_date: str
    supervisor_id: str
    supervisor_name: str


class AcademicGenealogy:
    """Construit et gère l'arbre généalogique académique"""
    
    def __init__(self, max_depth: int = 3, verbose: bool = True):
        self.max_depth = max_depth
        self.verbose = verbose
        self.persons: Dict[str, Person] = {}
        self.theses: List[Thesis] = []
        self.processed_ids: Set[str] = set()
        self.edges: List[Tuple[str, str]] = []  # (supervisor_id, student_id)
        
    def fetch_person_data(self, person_id: str) -> Optional[dict]:
        """Récupère les thèses dirigées par une personne via l'API de recherche"""
        if person_id in self.processed_ids:
            return None
            
        try:
            if self.verbose:
                print(f"🔍 Récupération des données pour l'identifiant {person_id}...")
            
            # Première requête pour connaître le nombre total
            url = f"{API_SEARCH}?q=directeursPpn:({person_id})"
            resp = requests.get(url, timeout=30)
            
            if resp.status_code != 200:
                if self.verbose:
                    print(f"❌ Erreur HTTP {resp.status_code} pour {person_id}")
                return None
                
            data = resp.json()
            total_hits = data.get('totalHits', 0)
            
            if total_hits == 0:
                if self.verbose:
                    print(f"⚠️  Aucune thèse trouvée pour l'identifiant {person_id}")
                return None
            
            # Si plus de 10 résultats, refaire la requête avec le bon nombre
            if total_hits > 10:
                url_all = f"{API_SEARCH}?q=directeursPpn:({person_id})&nombre={total_hits}"
                resp_all = requests.get(url_all, timeout=30)
                
                if resp_all.status_code == 200:
                    data = resp_all.json()
                    if self.verbose:
                        print(f"   📥 Récupération de toutes les {total_hits} thèses...")
            
            self.processed_ids.add(person_id)
            return data
            
        except requests.RequestException as e:
            if self.verbose:
                print(f"❌ Erreur réseau pour {person_id}: {e}")
            return None
    
    def extract_theses_from_data(self, data: dict, supervisor_id: str) -> List[Thesis]:
        """Extrait les thèses d'un superviseur depuis les données de l'API de recherche"""
        theses = []
        
        # Récupérer le nom du superviseur depuis la première thèse
        supervisor_name = "Inconnu"
        theses_list = data.get("theses", [])
        
        if theses_list:
            # Trouver le nom du superviseur dans la première thèse
            for directeur in theses_list[0].get("directeurs", []):
                if directeur.get("ppn") == supervisor_id:
                    prenom = directeur.get("prenom", "")
                    nom = directeur.get("nom", "")
                    supervisor_name = f"{prenom} {nom}".strip()
                    break
        
        for item in theses_list:
            # Extraire les informations de la thèse
            title = item.get("titrePrincipal") or item.get("titreEN") or "Sans titre"
            title = title.strip()
            
            # Informations sur l'auteur (premier auteur)
            author_name = ""
            author_id = None
            auteurs = item.get("auteurs", [])
            
            if auteurs:
                a = auteurs[0]
                prenom = a.get("prenom", "")
                nom = a.get("nom", "")
                author_name = f"{prenom} {nom}".strip()
                author_id = a.get("ppn")
            
            # Date de soutenance
            date = item.get("dateSoutenance", "")
            
            # Identifiant de la thèse
            thesis_id = item.get("id", "")
            
            thesis = Thesis(
                thesis_id=thesis_id,
                title=title,
                author_name=author_name,
                author_id=author_id,
                defense_date=date,
                supervisor_id=supervisor_id,
                supervisor_name=supervisor_name
            )
            theses.append(thesis)
        
        return theses
    
    def build_tree(self, root_person_id: str, current_depth: int = 0):
        """Construit l'arbre généalogique récursivement"""
        if current_depth > self.max_depth:
            return
        
        if root_person_id in self.processed_ids:
            return
        
        # Récupérer les données de la personne
        data = self.fetch_person_data(root_person_id)
        if not data:
            return
        
        # Extraire les thèses dirigées
        theses = self.extract_theses_from_data(data, root_person_id)
        
        if not theses:
            return
        
        # Le nom du superviseur est extrait dans extract_theses_from_data
        person_name = theses[0].supervisor_name if theses else "Inconnu"
        
        # Ajouter la personne
        if root_person_id not in self.persons:
            self.persons[root_person_id] = Person(
                person_id=root_person_id,
                name=person_name,
                is_supervisor=True
            )
        
        if self.verbose:
            print(f"{'  ' * current_depth}📚 {person_name}: {len(theses)} thèse(s) dirigée(s)")
        
        self.theses.extend(theses)
        
        # Pour chaque étudiant, ajouter à l'arbre et rechercher récursivement
        for thesis in theses:
            if thesis.author_id:
                # Ajouter l'étudiant comme personne
                if thesis.author_id not in self.persons:
                    self.persons[thesis.author_id] = Person(
                        person_id=thesis.author_id,
                        name=thesis.author_name,
                        is_supervisor=False
                    )
                
                # Ajouter l'arête (relation de supervision)
                edge = (root_person_id, thesis.author_id)
                if edge not in self.edges:
                    self.edges.append(edge)
                
                # Délai pour ne pas surcharger l'API
                time.sleep(REQUEST_DELAY)
                
                # Recherche récursive : l'étudiant est-il devenu directeur ?
                self.build_tree(thesis.author_id, current_depth + 1)
    
    def export_to_json(self, filename: str):
        """Exporte les données en JSON"""
        data = {
            "persons": {pid: asdict(p) for pid, p in self.persons.items()},
            "theses": [asdict(t) for t in self.theses],
            "edges": self.edges,
            "metadata": {
                "root_person": list(self.persons.keys())[0] if self.persons else None,
                "max_depth": self.max_depth,
                "total_persons": len(self.persons),
                "total_theses": len(self.theses)
            }
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        if self.verbose:
            print(f"\n💾 Données exportées dans {filename}")
    
    def print_summary(self):
        """Affiche un résumé de l'arbre généalogique"""
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DE L'ARBRE GÉNÉALOGIQUE ACADÉMIQUE")
        print("="*60)
        print(f"Nombre total de personnes : {len(self.persons)}")
        print(f"Nombre total de thèses : {len(self.theses)}")
        print(f"Nombre de relations de supervision : {len(self.edges)}")
        print(f"Profondeur maximale explorée : {self.max_depth}")
        print("="*60)


def main():
    """Point d'entrée principal"""
    if len(sys.argv) < 2:
        print("Usage: python academic_genealogy.py <person_id> [--max-depth N]")
        print("\nExemple: python academic_genealogy.py 123456789 --max-depth 3")
        sys.exit(1)
    
    person_id = sys.argv[1]
    max_depth = 3
    
    # Parser les arguments optionnels
    if "--max-depth" in sys.argv:
        idx = sys.argv.index("--max-depth")
        if idx + 1 < len(sys.argv):
            max_depth = int(sys.argv[idx + 1])
    
    print("🌳 GÉNÉRATEUR D'ARBRE GÉNÉALOGIQUE ACADÉMIQUE")
    print(f"📍 Personne racine : {person_id}")
    print(f"📏 Profondeur maximale : {max_depth}")
    print()
    
    # Construire l'arbre
    genealogy = AcademicGenealogy(max_depth=max_depth, verbose=True)
    genealogy.build_tree(person_id)
    
    # Afficher le résumé
    genealogy.print_summary()
    
    # Exporter les données
    output_json = f"genealogy_{person_id}.json"
    genealogy.export_to_json(output_json)
    
    print(f"\n✅ Arbre généalogique construit avec succès !")
    print(f"📄 Données disponibles dans : {output_json}")
    print(f"\n💡 Prochaine étape : générer le graphique avec visualize_genealogy.py")


if __name__ == "__main__":
    main()
