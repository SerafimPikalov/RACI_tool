#!/usr/bin/env python3
"""
Normalize the parsed RACI YAML into an enriched JSON dataset plus a flattened CSV export.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict, OrderedDict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "data" / "raci.yaml"
BUILD_DIR = ROOT / "build"
ENRICHED_JSON = BUILD_DIR / "raci_enriched.json"
TABLE_CSV = BUILD_DIR / "raci_table.csv"
DEPENDENCY_CSV = BUILD_DIR / "activity_dependencies.csv"

VALID_RACI = {"R", "A", "C", "I"}

# Manual overrides for canonical role display names.
PREFERRED_ROLE_NAMES = {
    "product owner": "Product Owner",
}


@dataclass
class Role:
    id: str
    name: str
    aliases: List[str]


@dataclass
class ActivityGroup:
    id: str
    title: str
    description: str | None


@dataclass
class Action:
    id: str
    name: str
    group_id: str
    details: str | None


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def normalize_role_name(raw_name: str, canonical_roles: Dict[str, Role]) -> Tuple[Role, bool]:
    cleaned = " ".join(raw_name.strip().split())
    key = cleaned.lower()

    display = PREFERRED_ROLE_NAMES.get(key, cleaned)
    canonical_key = display.lower()

    if canonical_key not in canonical_roles:
        role_id = slugify(display.replace("&", "and"))
        canonical_roles[canonical_key] = Role(id=role_id, name=display, aliases=[])
        created = True
    else:
        created = False

    role = canonical_roles[canonical_key]
    if cleaned != role.name and cleaned not in role.aliases:
        role.aliases.append(cleaned)

    return role, created


def normalize_raci_tokens(tokens: Iterable[str]) -> List[str]:
    normalized: List[str] = []
    for token in tokens:
        token = token.strip()
        if not token:
            continue

        # Replace known stray characters (Cyrillic C looks like 'С').
        token = token.replace("С", "C")
        letters = re.findall(r"[RACI]", token.upper())
        for letter in letters:
            if letter not in VALID_RACI:
                continue
            normalized.append(letter)

    return normalized


def load_yaml() -> Dict:
    with SOURCE_PATH.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def ensure_build_dir() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    raw = load_yaml()
    groups = raw.get("activity_groups", [])

    canonical_roles: Dict[str, Role] = OrderedDict()
    role_usage = Counter()
    group_records: List[ActivityGroup] = []
    action_records: List[Action] = []
    relationships = []
    dependency_specs = []
    action_lookup = {}

    action_warnings = []
    group_summary = {}

    for group in groups:
        title = group["group_title"]
        group_id = slugify(title)
        description = group.get("description")
        group_records.append(ActivityGroup(id=group_id, title=title, description=description))

        # Register roles declared at the group level.
        for role_name in group.get("roles", []):
            role, _ = normalize_role_name(role_name, canonical_roles)
            role_usage[role.id] += 0  # ensure key exists

        group_edge_counts = Counter()

        for activity in group.get("activities", []):
            action_name = activity["name"]
            action_id = f"{group_id}__{slugify(action_name)}"
            details = activity.get("details")
            action_records.append(Action(id=action_id, name=action_name, group_id=group_id, details=details))
            action_lookup[(title, action_name)] = (action_id, group_id)

            assignments = activity.get("assignments", {})
            letter_roles = {letter: [] for letter in VALID_RACI}

            for raw_role_name, tokens in sorted(assignments.items()):
                role, _created = normalize_role_name(raw_role_name, canonical_roles)
                normalized_letters = normalize_raci_tokens(tokens)

                if not normalized_letters:
                    action_warnings.append(
                        {
                            "action_id": action_id,
                            "action_name": action_name,
                            "issue": f"No valid RACI tokens for role '{raw_role_name}'",
                        }
                    )
                    continue

                role_usage[role.id] += len(normalized_letters)

                for letter in normalized_letters:
                    relationships.append(
                        {
                            "action_id": action_id,
                            "role_id": role.id,
                            "raci": letter,
                            "group_id": group_id,
                        }
                    )
                    letter_roles[letter].append(role.id)
                    group_edge_counts[letter] += 1

            # Missing or duplicate core assignments warnings.
            for critical_letter, label in (("R", "Responsible"), ("A", "Accountable")):
                roles = letter_roles[critical_letter]
                if not roles:
                    action_warnings.append(
                        {
                            "action_id": action_id,
                            "action_name": action_name,
                            "issue": f"Missing {label} assignment",
                        }
                    )
                elif len(roles) > 1:
                    action_warnings.append(
                        {
                            "action_id": action_id,
                            "action_name": action_name,
                            "issue": f"Multiple {label} assignments: {roles}",
                        }
                    )

            depends_on = activity.get("depends_on") or []
            if depends_on:
                dependency_specs.append(
                    {
                        "source_action_id": action_id,
                        "source_action_name": action_name,
                        "source_group_id": group_id,
                        "source_group_title": title,
                        "depends_on": depends_on,
                    }
                )

        group_summary[group_id] = {
            "title": title,
            "action_count": len(group.get("activities", [])),
            "edge_distribution": dict(group_edge_counts),
        }

    # Build role summaries.
    role_letter_counts: Dict[str, Counter] = defaultdict(Counter)
    for edge in relationships:
        role_letter_counts[edge["role_id"]][edge["raci"]] += 1

    role_summaries = []
    for role in canonical_roles.values():
        counts = {letter: role_letter_counts[role.id].get(letter, 0) for letter in sorted(VALID_RACI)}
        total = sum(counts.values())
        role_summaries.append(
            {
                "role_id": role.id,
                "role_name": role.name,
                "aliases": role.aliases,
                "counts": counts,
                "total_assignments": total,
            }
        )

    role_summaries.sort(key=lambda entry: entry["total_assignments"], reverse=True)

    overloaded_roles = sorted(
        role_summaries,
        key=lambda entry: (entry["counts"]["R"] + entry["counts"]["A"], entry["total_assignments"]),
        reverse=True,
    )[:3]

    dependency_edges = []
    dependency_warnings = []
    dependency_counts = Counter()
    seen_dependencies = set()

    for spec in dependency_specs:
        for dependency in spec["depends_on"]:
            target_activity = dependency.get("activity")
            if not target_activity:
                dependency_warnings.append(
                    {
                        "source_action_id": spec["source_action_id"],
                        "source_action_name": spec["source_action_name"],
                        "issue": "Dependency missing activity name",
                    }
                )
                continue

            target_group_title = dependency.get("group") or spec["source_group_title"]
            target_key = (target_group_title, target_activity)
            if target_key not in action_lookup:
                dependency_warnings.append(
                    {
                        "source_action_id": spec["source_action_id"],
                        "source_action_name": spec["source_action_name"],
                        "issue": f"Dependency target not found: {target_group_title} :: {target_activity}",
                    }
                )
                continue

            target_action_id, target_group_id = action_lookup[target_key]
            relation_type = dependency.get("type", "depends_on")

            dedupe_key = (spec["source_action_id"], target_action_id, relation_type)
            if dedupe_key in seen_dependencies:
                continue
            seen_dependencies.add(dedupe_key)

            dependency_edges.append(
                {
                    "source_action_id": spec["source_action_id"],
                    "source_action_name": spec["source_action_name"],
                    "source_group_id": spec["source_group_id"],
                    "source_group_title": spec["source_group_title"],
                    "target_action_id": target_action_id,
                    "target_action_name": target_activity,
                    "target_group_id": target_group_id,
                    "target_group_title": target_group_title,
                    "type": relation_type,
                }
            )
            dependency_counts[relation_type] += 1

    dependency_edges.sort(
        key=lambda edge: (
            edge["source_group_id"],
            edge["source_action_name"],
            edge["target_group_id"],
            edge["target_action_name"],
            edge["type"],
        )
    )

    enriched_payload = {
        "roles": [asdict(role) for role in canonical_roles.values()],
        "activity_groups": [asdict(group) for group in group_records],
        "actions": [asdict(action) for action in action_records],
        "relationships": relationships,
        "activity_dependencies": dependency_edges,
        "metrics": {
            "role_summary": role_summaries,
            "overloaded_roles": overloaded_roles,
            "action_warnings": action_warnings,
            "group_summary": group_summary,
            "dependency_summary": {
                "total": len(dependency_edges),
                "counts_by_type": dict(dependency_counts),
            },
            "dependency_warnings": dependency_warnings,
        },
    }

    ensure_build_dir()

    with ENRICHED_JSON.open("w", encoding="utf-8") as fh:
        json.dump(enriched_payload, fh, indent=2, sort_keys=False)

    # Export flattened CSV table.
    with TABLE_CSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["group_id", "group_title", "action_id", "action_name", "role_id", "role_name", "raci"])
        # Pre-compute lookups.
        group_lookup = {group.id: group.title for group in group_records}
        role_lookup = {role.id: role.name for role in canonical_roles.values()}
        action_lookup = {action.id: action.name for action in action_records}

        for edge in relationships:
            writer.writerow(
                [
                    edge["group_id"],
                    group_lookup[edge["group_id"]],
                    edge["action_id"],
                    action_lookup[edge["action_id"]],
                    edge["role_id"],
                    role_lookup[edge["role_id"]],
                    edge["raci"],
                ]
            )

    with DEPENDENCY_CSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "source_group_id",
                "source_group_title",
                "source_action_id",
                "source_action_name",
                "target_group_id",
                "target_group_title",
                "target_action_id",
                "target_action_name",
                "type",
            ]
        )
        for dep in dependency_edges:
            writer.writerow(
                [
                    dep["source_group_id"],
                    dep["source_group_title"],
                    dep["source_action_id"],
                    dep["source_action_name"],
                    dep["target_group_id"],
                    dep["target_group_title"],
                    dep["target_action_id"],
                    dep["target_action_name"],
                    dep["type"],
                ]
            )


if __name__ == "__main__":
    main()
