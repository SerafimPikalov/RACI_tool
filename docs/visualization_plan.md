# Visualization Plan

## Objectives
- Provide an interactive way to explore how actions relate to roles across lifecycle stages.
- Surface overloaded roles and gaps flagged in the enrichment metrics.
- Visualize activity dependencies so users can trace how work items connect and where hand-offs occur.
- Support exportable graphics for presentations or documentation.

## Tooling Choice
- **Primary**: Observable/D3 for an interactive browser-based explorer (hostable via GitHub Pages).
- **Secondary**: Graphviz or Mermaid for quick static diagrams (generated from the JSON output).
- Rationale: D3 offers fine-grained control over dynamic filtering and highlighting, while Graphviz/Mermaid can produce shareable snapshots with minimal extra code.

## Proposed Views
- **Lifecycle Sankey**: Actions grouped by `activity_group` flowing into roles, colored by R/A/C/I. Highlights workload distribution per phase.
- **Activity Dependency Graph**: Tree + cross-link hybrid. Lifecycle groups act as columns; activities render as nodes arranged by group order. Arrows illustrate `depends_on` / `supports` edges, colored by relationship type. Filters allow narrowing by responsible role and RACI letter.
- **Role Workload Dashboard**: Bar charts using `metrics.role_summary` to chart counts of R/A/C/I per role and flag those above configurable thresholds.
- **Action Detail Panel**: Click an action node to reveal all role relationships, dependency metadata, and any `metrics.action_warnings`.
- **Matrix Explorer**: Heatmap (actions vs roles) filtered by lifecycle to expose missing assignments or concentration of responsibilities.

## Data Inputs
- `build/raci_enriched.json` drives all visualizations:
  - `activity_groups` for column/section headers.
  - `actions` for node labels and grouping.
  - `relationships` for edges with RACI codes.
  - `metrics` section to pre-populate warnings and overloaded-role annotations.
- `activity_dependencies` payload provides cross-activity edges (`depends_on` by default).
- `build/activity_dependencies.csv` offers a flat extract of the same edges for quick spreadsheet review.
- Future enrichment should add optional relationship types (`supports`, `informed_by`) and per-action RACI summaries (counts per role) to power the dependency graph and filters.
- `build/raci_table.csv` supports quick validation by analysts in spreadsheets and can serve as a fallback data source for static charts.

## Next Implementation Steps
1. Extend the YAML schema to capture activity relationships; update the enrichment script to emit a dependency graph dataset.
2. Implement shared data loaders that normalize the JSON into graph structures (`nodes`, `links`, `dependencies`) consumed by D3 components.
3. Enhance the Activity Dependency Graph (initial version live) with richer detail panes, cross-highlighting, and support for additional relationship types beyond `depends_on`.
4. Expand the responsibility matrix with additional insights (e.g., quick filters, export options).
5. Generate scripted Mermaid/Graphviz exports for static reporting, using the same normalized data pipeline.
