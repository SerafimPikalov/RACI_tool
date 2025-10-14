# User Stories

## Story 1: Data Steward Parses and Normalizes RACI Source
**As a** data steward  
**I want** to convert the original Word-based RACI tables into structured YAML  
**So that** downstream tools can ingest consistent, machine-readable assignments without manual cleanup.

### Acceptance Criteria
- Source conversion handles nested tables and merged cells in the Word/HTML export.
- Resulting YAML uses the canonical schema (`activity_groups[].{group_title, roles[], activities[]}`) with normalized role names.
- Automated tests or scripts flag malformed rows or missing R/A assignments.

## Story 2: Analyst Validates and Enriches RACI Assignments
**As an** analyst  
**I want** to run an enrichment job that cleans tokens, computes metrics, and exports JSON/CSV  
**So that** I can trust that a single command (`make enrich`) populates current data for analysis and visualization.

### Acceptance Criteria
- Enrichment script normalizes RACI tokens (`A`, `C`, `R`, `I`), resolves role aliases, and emits warnings for missing or duplicate key assignments.
- Output includes `raci_enriched.json`, `raci_table.csv`, and `activity_dependencies.csv`.
- Metrics call out overloaded roles, action-level warnings, and dependency counts.
- Analysts can upload alternate datasets, tweak RACI assignments directly in the matrix, and download updated CSV/JSON extracts with one click.

## Story 3: Delivery Lead Explores Lifecycle-to-Role Workload
**As a** delivery lead  
**I want** a Sankey visualization grouped by lifecycle stages flowing into roles with R/A/C/I coloring  
**So that** I can quickly spot responsibility load and hand-offs across the portfolio.

### Acceptance Criteria
- Users can filter the Sankey by role or RACI letter; non-matching links disappear with feedback.
- Lifecycle sections remain readable (banded, labeled), and tooltips expose role/action details.
- The chart refreshes when data is regenerated without manual edits.

## Story 4: Process Owner Traces Activity Dependencies
**As a** process owner  
**I want** an activity dependency graph that highlights hand-offs and sequencing  
**So that** I can understand how upstream work impacts downstream teams and find bottlenecks.

### Acceptance Criteria
- Graph columns align with lifecycle groups; activities render as labeled cards with multiline wrapping.
- Role/RACI filters dim unrelated nodes and brighten matching paths; header bands mirror the filter state.
- Connection type filter (e.g., `depends_on`) controls edge visibility, and arrows connect to card edges.
- Tooltips show role assignments (R/A/C/I) plus group context.

## Story 5: Portfolio Manager Reviews Responsibility Coverage (Suggested Matrix View)
**As a** portfolio manager  
**I want** a responsibility matrix heatmap (activities × roles)  
**So that** I can audit coverage, detect gaps (missing R/A) and observe concentration of responsibilities.

### Acceptance Criteria
- Rows group by lifecycle with expand/collapse; cells encode R/A/C/I using color or icon badges.
- Filters align with existing controls (role, lifecycle, responsibility type) and update the matrix live.
- Clicking a cell reveals detail (activity summary, role notes, dependency links).

## Story 6: Program Planner Sequences Work in Timeline View (Suggested Gantt-like)
**As a** program planner  
**I want** a timeline view that sequences activities and annotates key roles  
**So that** I can align initiatives with calendar windows and identify schedule risks.

### Acceptance Criteria
- Activities appear on a timeline by lifecycle phase with optional start/end placeholders or relative ordering.
- Overlays highlight critical dependency chains; hovering shows responsible/accountable roles.
- View syncs with filters to focus on specific teams or responsibility types.

~~## Story 7: Change Manager Audits Responsibility Network (Suggested Network Graph)~~
~~**As a** change manager~~  
~~**I want** a force-directed responsibility network linking roles and activities~~  
~~**So that** I can detect overloaded roles, clusters of collaboration, and cross-function interactions.~~
