# RACI Tool

Utilities for normalizing RACI tables, enriching the dataset, and exploring responsibilities interactively.

## Prerequisites
- Python 3.10+

## Generate Enriched Data
```bash
make enrich
```
Outputs land in:
- `build/raci_enriched.json`
- `build/raci_table.csv`
- `build/activity_dependencies.csv`

## Launch the Explorer
```bash
make serve
```
Then open <http://localhost:8003/web/> in your browser. The explorer includes:
- Lifecycle Sankey highlighting role workloads.
- Activity dependency graph with filters for connection type, role, and RACI letter.
- Responsibility matrix to audit and edit coverage across roles.
- Dataset management tools to load alternate RACI JSON files and download updated matrices.

Stop the server with `Ctrl+C` when you're done.
