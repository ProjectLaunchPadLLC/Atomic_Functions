Registry Overview

The registry is the canonical, machine‑readable index of every atomic function and registered library in atomfun. It is the single source of truth for discovery, loading, bag creation, analytics, AI enrichment, and payouts. The registry is stored as structured records (JSON/JSONB) and validated against registry_schema.json.

---

Location and Artifacts

• Schema file: registry_schema.json (JSON Schema Draft 2020‑12).
• SQL DDL: sql/001_create_registry_tables.sql (Postgres DDL for MVP).
• Docs: docs/registry.md (this file).
• Examples: examples/registry_sample.json (sample function entries).
• Tests: tests/test_registry_schema.py (validates examples against the schema).


Use the JSON Schema to validate every registry write. Use the SQL DDL for the production schema; local development may use SQLite with compatible types.

---

Record Shape and Required Fields

Each function record is a single JSON object. Required fields include:

• id — global unique identifier (UUID or prefixed id).
• name — globally unique snake_case name.
• module_path — import path in module:callable or module.callable form.
• category — primary controlled category.
• signature — structured inputs and output schema.
• description — short summary.
• source — library id or core.
• license — SPDX identifier.
• visibility — public, org, or private.
• created_at, updated_at, version.


Optional but recommended fields: display_name, subcategories, examples, tags, contributor_id, usage_count, payout_config, ai_metadata, integrity_hash.

---

module_path Conventions

Accepted formats

• module:callable — preferred (explicit separator).
• module.callable — supported (legacy style).


Normalization rules

• Normalize to module:callable internally.
• Support nested callables (e.g., package.subpackage.module:Class.method) when the callable is a bound function or static method.
• For top‑level modules that expose a default callable, allow module only if the loader can resolve a single callable entry point; prefer explicit callable.


Examples

• mylib.math:correlation_matrix
• numpy.linalg:inv
• mylib.visuals:Plotter.plot


Loader responsibilities

• Validate that the module imports successfully.
• Resolve the callable attribute and confirm it is callable.
• Normalize and store the resolved import form in the registry audit log.
• Reject registrations where the module cannot be imported or the callable cannot be resolved (unless registering as a placeholder with explicit consent).


---

Signature Object Conventions

Purpose
The signature object describes inputs and outputs so agents, the loader, and the dashboard can validate calls, generate examples, and reason about safety and side effects.

Structure

"signature": {
  "inputs": [
    {"name":"rows","type":"Sequence[Dict[str,Any]]","required":true,"description":"list of row dicts"}
  ],
  "output": {"type":"Dict[str,Dict[str,float]]","description":"pairwise correlation matrix"},
  "pure": true,
  "side_effects": [],
  "complexity": "O(n*m^2)"
}


Field details

• inputs — array of parameter descriptors:• name: parameter name (string).
• type: human and machine readable type hint (string). Use PEP 484 style where possible.
• required: boolean.
• description: short explanation of the parameter.

• output — object with type and optional description.
• pure — boolean indicating whether the function is pure (no external state changes). Prefer true for atomic functions.
• side_effects — array of strings describing side effects (e.g., writes_file, network_call). Use these to gate agent usage.
• complexity — optional complexity hint (e.g., O(n log n)).


Best practices

• Prefer explicit, narrow types over Any.
• Mark side effects clearly; functions with side effects should include tests and examples.
• Provide 1–3 short examples in the examples field to show typical usage.
• Keep functions single responsibility; split multi‑concern functions into smaller atomic functions.


---

Validation, Versioning, and Evolution

• Validation: All POST/PUT operations must validate against registry_schema.json. Use jsonschema or equivalent on write.
• Versioning: Use semantic version per function. For breaking changes publish a new version and record the change in audit_log. The loader may accept id@version to pin a specific implementation.
• Audit log: Keep an append‑only audit_log of registry changes for dispute resolution and payout audits.
• Signature changes: Treat signature changes as a new version; do not mutate signatures in place without a version bump.
• AI metadata: Store analyzer outputs in ai_metadata with analyzed_at and analyzer_version. Human edits are allowed and recorded.


---

Usage Tracking and Payout Hooks

• Usage events: Emit lightweight usage_events for each function call. Batch or stream these events to avoid write hot spots. Aggregate into functions.usage_count periodically.
• Payout config: Store non‑sensitive payout settings in payout_config (share percent, revenue model). Keep payment credentials in a secure vault and reference them by id.
• Privacy: Do not store secrets or PII in registry records. Use encrypted storage for any payment identifiers.


---

Practical Examples

Minimal function record

{
  "id": "f_3a9b2c4d",
  "name": "correlation_matrix",
  "module_path": "mylib.math:correlation_matrix",
  "category": "math",
  "signature": { "inputs": [...], "output": {...}, "pure": true },
  "description": "Compute pairwise correlations between specified columns.",
  "source": "mylib",
  "license": "MIT",
  "visibility": "public",
  "created_at": "2026-05-27T06:00:00Z",
  "updated_at": "2026-05-27T06:00:00Z",
  "version": "1.0.0"
}


Registering a library batch

• Use the register API or a mylib_atomfun.py registration file that calls register(library="mylib", functions=[...]). Validate each entry against the schema before writing.


---
