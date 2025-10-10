# Activity & Dependency Analysis

## Current State
- The dataset (`data/raci.yaml`) captures lifecycle-oriented groups with 48 activities.
- Activities are grouped into seven phases: Goals & Performance → SDLC & Process Management → Discovery → Delivery → Quality → Release → Support.
- First-pass cross-activity dependencies are now captured via `depends_on`, giving us a directional graph of 67 links across lifecycle bands.

## Implied Sequences
- Group ordering implies a macro flow: goal definition precedes SDLC/process design, which precedes discovery, delivery, quality, release, and support.
- Within groups, tasks often follow an implied order (`Define goal-setting framework` before `Set team-level goals`; `Define discovery framework` before running sessions), but these sequences are not formally captured.
- Several activities suggest cross-group reliance (e.g., `Quality gates enforcement` in Release & Deployment relying on `Enforce quality gates` in Quality & Risk Management), indicating the need for explicit cross-links.

## Data Gaps for Graph Visualization
- Only a single relationship type (`depends_on`) exists; strength/criticality and alternative semantics (supports/informed_by) are still missing.
- No edge weights indicating strength/criticality of connections.
- RACI assignments exist, but responsibility types do not currently drive activity-to-activity edges.

## Recommended Enhancements
1. Extend `data/raci.yaml` schema with optional `relationships` per activity:
   ```yaml
   activities:
     - name: Execute deployment
       depends_on:
         - group: Quality & Risk Management
           activity: Enforce quality gates
         - group: Release & Deployment
           activity: Approve release scope
   ```
2. Introduce relationship types (`precedes`, `supports`, `informed_by`) to clarify edge semantics.
3. For responsibility-driven links, allow activity references scoped by RACI (e.g., a role accountable for `Define release process framework` might also be responsible for `Approve release scope`).
4. Capture metadata for cross-functional dependencies (e.g., hand-offs to PRE, Tech Lead involvement) to support arrow annotations in the graph.

## Next Steps
- Workshop with domain experts to gather explicit activity dependencies and capture them in the YAML.
- Extend the enrichment pipeline (done) so downstream visualizations consume `activity_dependencies` from the JSON/CSV exports.
- Iterate on relationship typing/strength once stakeholder validation is complete.

## Update Log
- 2024-04-04 Added first-pass `depends_on` annotations across all activities in `data/raci.yaml`, reflecting lifecycle sequencing and key hand-offs. Further validation with stakeholders is still required.
