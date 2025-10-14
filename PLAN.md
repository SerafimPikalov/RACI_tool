## RACI Tool Project Plan

**Purpose** Build a toolchain that ingests RACI documents, enriches them with relationship analysis, and outputs both refreshed documentation and visualizations that clarify how actions, roles, and responsibilities interconnect.

1. Convert the existing `RACI_Platform.doc` Word document into a structured, machine-readable format (e.g., JSON or CSV) while preserving RACI assignments.
2. Analyze the structured data to identify every action-role relationship, define connection types, and document any dependencies or special cases.
3. Extend the dataset with explicit activity-to-activity relationships (depends on / supports / informed by) and re-run enrichment to expose the dependency graph.
4. Generate an updated RACI document from the structured data to confirm consistency and correct any gaps.
5. Design and implement a visualization tool that presents roles, responsibilities, and activity dependencies, with filtering by connection type, role, and responsibility level.

**Progress so far**
- Extracted the Confluence HTML payload from `RACI_Platform.doc` and parsed all RACI tables into a canonical YAML (`data/raci.yaml`), ordered by lifecycle and annotated with group intent.
- Produced enriched JSON/CSV exports plus a Sankey prototype showing lifecycle-to-role responsibilities.
- Drafted activity dependency schema requirements in `docs/activity_analysis.md` and updated the visualization plan for dependency, matrix, and dataset-management enhancements.
