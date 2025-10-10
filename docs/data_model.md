# RACI Relationship & Data Model

## Goals
- Normalize the parsed YAML into explicit entity lists for `roles`, `actions`, and `relationships`.
- Capture derived insights (role workload, missing assignments, lifecycle group summaries) that will feed both regenerated docs and visualizations.

## Source Assumptions
- Input file: `data/raci.yaml` with `activity_groups[].{group_title, description?, roles[], activities[]}`.
- Each activity has `name`, optional `details`, and an `assignments` map `{role_name: [raci_tokens...]}`.
- Some tokens include noise (e.g. `A(C)`, `С` Cyrillic, dangling parentheses) that must collapse to the canonical set `{R, A, C, I}`.
- Role names may vary in casing (`Product owner` vs `Product Owner`) and require normalization.

## Canonical Entities

### Roles
- Fields: `id`, `name`, `aliases`.
- `id`: slugified snake_case (e.g. `product_owner`).
- `name`: display label in Title Case.
- `aliases`: any observed variants from the raw data.
- Derive by scanning both the group `roles` arrays and assignment keys.

### Activity Groups
- Fields: `id`, `title`, `description`.
- `id`: slugified snake_case of the title.
- `description`: optional, carried over when present.

### Actions
- Fields: `id`, `name`, `group_id`, `details?`.
- `id`: deterministic slug built from `group_id` + action name (e.g. `goals_performance__define_goal_setting_framework`).
- `details`: copy of the optional `details` string.

### Relationships (Edges)
- Each edge represents a single `{action_id, role_id, raci}` triple.
- `raci` is one of `R`, `A`, `C`, `I`.
- Include an `source_group_id` column so visualizations can pivot by lifecycle.

## Derived Metrics
- `role_summary`: counts of `R/A/C/I` per role, total assignments, and flags for overloaded roles (top N by `R` or `A` count).
- `action_warnings`: actions missing either an `R` or an `A`, or with duplicate `R/A` assignments.
- `group_summary`: per group counts of actions and distribution of edge types.

## Output Artifacts
1. `build/raci_enriched.json`
   ```jsonc
   {
     "roles": [{"id": "delivery_manager", "name": "Delivery Manager", "aliases": []}],
     "activity_groups": [{"id": "goals_performance", "title": "Goals & Performance"}],
     "actions": [{"id": "goals_performance__define_goal_setting_framework", "name": "Define goal-setting framework", "group_id": "goals_performance"}],
     "relationships": [{"action_id": "goals_performance__define_goal_setting_framework", "role_id": "delivery_manager", "raci": "R"}],
     "metrics": {
       "role_summary": {...},
       "action_warnings": [],
       "group_summary": {...}
     }
   }
   ```
2. `build/raci_table.csv`
   - Flattened table: `group,title,action,role,raci`.
   - Serves as a human-readable check and for Excel import.

## Normalization Rules
- Strip and uppercase all RACI tokens, then extract valid letters via regex `[RACI]`.
- Replace known stray characters (`'С' → 'C'`, remove parentheses, slashes, trailing punctuation).
- Expand tokens that contain multiple letters into separate edges (e.g. `['A', 'C']` from `A(C)`).
- Map role aliases to canonical IDs using case-insensitive matches and a manual merge table:
  - `"Product owner"`, `"Product Owner"` → `product_owner`.
- Ensure each action has at least one `R` and one `A`; flag otherwise.

These definitions provide the contract for the enrichment pipeline and the upcoming visualization layer.
