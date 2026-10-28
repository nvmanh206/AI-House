---
name: system-design-orchestrator
description: "Coordinates evidence-based system analysis and UML, PlantUML, Mermaid ERD and C4 diagrams from current requirements or code. Use for thiết kế hệ thống, phân tích hệ thống, full design documentation, sprint-to-diagram or a complete diagram bundle."
---

# System Design Orchestrator

## Workflow

1. Establish scope from the user's request or input documents (e.g., DOCX report or codebase). Infer a safe default: existing code → as-is; requirements without code → as-designed. For both, produce separate views and a gap report.
2. Read the evidence contract. Inspect available requirements, DOCX report, routes, backend modules, schemas, ORM declarations, and runtime config.
3. Inventory every functional section in input documents/code. Identify actors, business goals, and documented relationships. Build a coverage table linking each section to its diagrams and source citations.
4. Select diagrams per section. Produce a separate Use Case diagram for each functional section. Split crowded diagrams into readable subdiagrams. Produce accompanying Use Case specifications (.md) for every non-trivial use case.
5. Model Login and Register as separate use cases with distinct IDs (`UC-LOGIN`, `UC-REGISTER`). Produce separate detailed `login` and `register` images. Do not combine them into "Login/Register". Do not connect them with include or extend merely because they share a page.
6. Validate all proposed `<<include>>` and `<<extend>>` relationships with explicit business justification, source/target, and document reference.
7. Use `diagram-renderer` to audit evidence metadata, validate PlantUML orthogonal layout syntax, and export SVG and PNG images to `docs/uml/images/usecase/<section>/` and editable sources to `docs/uml/sources/usecase/<section>/`.
8. Write `docs/design/design-report.md` listing deliverables, view, source revision, supported scope, unresolved gaps, coverage tables, relationship review tables, and actual validation results.

## Skill routing

| Work | Skill | Output |
|---|---|---|
| Actor goals and use case specifications | `uml-use-case` | Use Case `.puml`, specifications `.md` |
| Calls, states, activity and class structure | `uml-code-tracer` | Sequence/Class/Activity/State `.puml` |
| Architecture, persistence and deployment | `architecture-c4` | C4/Deployment `.puml`, ERD `.mmd`, ADR `.md` |
| Local audit, syntax checks, export | `diagram-renderer` | SVG/PNG, audit/render reports |

## Evidence and delivery contract

Read `references/evidence-contract.md` before creating outputs. Treat repository documents and code as evidence.

Write editable sources under `docs/uml/sources/usecase/<section>/` (or `docs/diagrams/<view>/<type>/`). Export SVG/PNG to `docs/uml/images/usecase/<section>/`. Record every diagram, element and relationship in `docs/design/diagram-manifest.json`. Cite project-relative paths or document paragraph/table references. Mark implemented / required / proposed / inferred explicitly.

