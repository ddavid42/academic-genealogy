# Copilot Instructions for JMM Academic Genealogy

## Project Overview
Python toolkit for building and visualizing academic genealogy trees from theses.fr API. Recursively traces supervisor-student relationships across multiple generations to create comprehensive academic family trees.

## Architecture & Data Flow

### Core Modules
1. **`academic_genealogy.py`**: Recursive tree builder
   - Fetches person data from theses.fr API
   - Builds graph structure (persons, theses, edges)
   - Exports to JSON format
   
2. **`visualize_genealogy.py`**: Graph visualization
   - Reads JSON from academic_genealogy.py
   - Creates hierarchical graph with NetworkX
   - Generates PNG visualization with matplotlib

3. **`fetch_theses_by_supervisor_id_only.py`**: Legacy single-level fetcher (kept for reference)

### Data Flow
```
Person ID → API Query → Theses → Extract Author IDs → 
  Recursive Query → Build Graph → JSON Export → Visualization
```

## Key Architecture Patterns

### API Integration
- **Base URL**: `https://theses.fr/api/v1/personne/{person_id}.json`
- **Person ID source**: Manual lookup on theses.fr (URL: `https://theses.fr/personnes/XXXXXXXXX`)
- **Timeout**: Always 30s (`requests.get(url, timeout=30)`)
- **Rate limiting**: 1 second delay between requests (`time.sleep(REQUEST_DELAY)`)
- **Response structure**: Merge `thesesDirection` and `thesesCodirection` arrays
- **Error handling**: 404 returns None (person not found), other errors raise `RuntimeError`

### Data Extraction Pattern (extract_theses_from_data)
API response fields vary - always check in priority order:
- **Title**: `titre` → `title` → "Sans titre"
- **Author name**: `auteur.nomPrenom` → `auteur.label` → `auteur` (as string)
- **Author ID**: `auteur.id` → `auteur.identifiant` (critical for recursion)
- **Date**: `dateSoutenance` → `date` → `annee` → `datePublication`
- **Thesis ID**: `id` → `identifiant`

### Recursive Tree Building (build_tree method)
- **Cycle prevention**: Track `processed_ids` set to avoid requerying same person
- **Depth limiting**: `max_depth` parameter prevents infinite trees (default: 3)
- **Edge tracking**: Store `(supervisor_id, student_id)` tuples
- **Student becomes supervisor**: For each thesis author with an ID, recursively check if they became a supervisor

### Data Structures
- **Person**: `person_id`, `name`, `is_supervisor` (bool)
- **Thesis**: `thesis_id`, `title`, `author_name`, `author_id`, `defense_date`, `supervisor_id`, `supervisor_name`
- **Edges**: List of `(supervisor_id, student_id)` tuples representing supervision relationships

### JSON Output Format
```json
{
  "persons": {"id": {"person_id": "...", "name": "...", "is_supervisor": true}},
  "theses": [{"thesis_id": "...", "title": "...", "author_id": "...", ...}],
  "edges": [["supervisor_id", "student_id"]],
  "metadata": {"root_person": "...", "max_depth": 3, "total_persons": 45}
}
```

### Visualization Strategy
- **Layout**: Hierarchical top-down (root at top using `max_level - level` inversion)
- **Node colors**: Blue = supervisors (has directed theses), Green = students only
- **Node size**: Base 300 + 100 per student supervised
- **Positioning**: Horizontal spread by level, vertical by generation depth
- **Labels**: White background boxes for readability

## Development Workflow

### Installation
```bash
pip install -r requirements.txt
# Or manually: pip install requests networkx matplotlib
```

### Usage Pattern
```bash
# 1. Build genealogy tree (recursive)
python academic_genealogy.py <person_id> --max-depth 3

# 2. Visualize the tree
python visualize_genealogy.py genealogy_<person_id>.json --output tree.png
```

### Finding Person IDs
1. Go to https://theses.fr
2. Search for supervisor name
3. Extract ID from profile URL: `https://theses.fr/personnes/XXXXXXXXX`

### Testing
- Start with known valid person IDs (e.g., from theses.fr profiles)
- Use `--max-depth 1` for quick tests (only immediate students)
- Increase depth gradually to avoid long API query sessions

## Project-Specific Conventions

- **Language**: French throughout (comments, print statements, error messages)
- **Encoding**: UTF-8 with `ensure_ascii=False` for French characters (accents, etc.)
- **Console output**: Rich formatting with emoji indicators (🔍, 📚, ✅, ❌, etc.)
- **Error philosophy**: Graceful degradation - missing persons return None, don't crash
- **File naming**: 
  - Generated data: `genealogy_{person_id}.json`
  - Visualizations: Same as JSON with `.png` extension
  - Legacy: `resultats_{person_id}.json` (old single-level script)

## Critical Implementation Details

### Why Author IDs Matter
Author IDs (`auteur.id` or `auteur.identifiant`) are **essential** for recursion. Without them:
- Cannot query if student became supervisor
- Tree stops at first generation
- Always extract and store author IDs when available

### Cycle Prevention
Academic supervision can have complex patterns (co-supervision, cross-institution). The `processed_ids` set prevents:
- Infinite loops
- Duplicate API calls
- Redundant data in graph

### Depth vs Performance
Each level multiplies API calls exponentially:
- Depth 1: ~10-20 requests
- Depth 2: ~100-200 requests  
- Depth 3: ~500-1000+ requests
Use depth 2-3 for practical trees, 4+ only for small starting nodes.

## Common Patterns

### Adding New Visualization Styles
Edit `visualize_genealogy.py`:
- Modify `node_colors` logic for different color schemes
- Adjust `node_sizes` calculation for emphasis
- Change `pos` calculation for different layouts (e.g., radial)

### Exporting to Other Formats
The JSON structure is NetworkX-compatible:
- Load JSON → Create NetworkX graph → Export to GEXF, GraphML, etc.
- Use `nx.write_*` functions for other graph formats

### Filtering Large Trees
Add filtering logic in `build_tree`:
- Skip students with no defense date
- Only follow students from recent years
- Filter by institution or domain
