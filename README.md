# RACI Tool

Utilities for normalizing RACI tables, enriching the dataset, and exploring responsibilities interactively.

## 🌐 Live Demo

**Try the RACI Explorer online**: [https://yourusername.github.io/RACI_tool/web/](https://yourusername.github.io/RACI_tool/web/)

The interactive explorer includes:
- **Lifecycle Sankey** highlighting role workloads
- **Activity dependency graph** with filters for connection type, role, and RACI letter
- **Responsibility matrix** to audit and edit coverage across roles
- **Dataset management** tools to load alternate RACI JSON files and download updated matrices

## 🚀 Quick Start

### Prerequisites
- Python 3.10+

### Generate Enriched Data
```bash
make enrich
```
Outputs land in:
- `build/raci_enriched.json`
- `build/raci_table.csv`
- `build/activity_dependencies.csv`

### Launch Local Explorer
```bash
make serve
```
Then open <http://localhost:8003/web/> in your browser.

Stop the server with `Ctrl+C` when you're done.

## 📦 Deploy to GitHub Pages

1. **Fork or clone this repository**
2. **Enable GitHub Pages**:
   - Go to your repository Settings → Pages
   - Source: "GitHub Actions"
3. **Push your changes** - the site will automatically deploy!

Your RACI Explorer will be available at: `https://yourusername.github.io/RACI_tool/web/`
