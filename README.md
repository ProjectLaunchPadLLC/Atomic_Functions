atomfun

Compose, borrow, and monetize atomic functions across libraries.

Atomfun is a registry driven platform that lets developers and agents discover, borrow, and compose single responsibility Python functions into ephemeral session toolkits called bags. The core project provides a global registry, a dynamic loader, a bag API, an AI metadata analyzer, and a lightweight dashboard for discovery.

---

Overview

What atomfun does

• Provides a global registry of atomic functions with rich metadata.
• Lets users create ephemeral bags that bundle libraries, categories, or individual functions into a single, session scoped namespace.
• Dynamically loads only the functions a user needs to keep startup fast and reduce resource usage.
• Uses an AI analyzer to generate consistent descriptions, tags, examples, and category suggestions for every registered function.
• Tracks usage and supports contributor revenue share so authors earn a fraction of value when their functions are used.
• Exposes a lightweight dashboard with semantic search and a visual bag builder.


Why it matters

• Reduces import friction and cognitive load for developers.
• Makes code discoverable and agent friendly.
• Enables cross library composition without deep import trees.
• Creates incentives for high quality, well documented atomic functions.


---

Quick start

Install

pip install atomfun


Basic usage

import atomfun as atom

# Create a bag that borrows entire libraries
atom.bag = atom{numpy, matplotlib}

# Use aliased sub namespaces
atom.np.array([1, 2, 3])
atom.ml.plot([1,2,3])

# Create a bag that borrows specific functions
tools = atom.bag{normalize, slugify, correlation_matrix}
tools.normalize(data)


Register a function from your library

from atomfun import register

register(
  library="mylib",
  functions=[
    {
      "name": "normalize",
      "callable": mylib.preprocessing.normalize,
      "category": "data",
      "description": "Normalize numeric columns in a dataframe"
    }
  ]
)


---

Key features

• Registry driven
A single source of truth for function discovery, metadata, versioning, and usage tracking.
• Ephemeral bags
Session scoped micro libraries that compress namespaces and prevent collisions.
• Three tier borrowing model
Borrow entire libraries, categories, or individual functions.
• Dynamic loader
Lazy imports and signature validation to keep runtime overhead minimal.
• AI metadata analyzer
Automatic generation of tags, descriptions, examples, and naming suggestions to ensure consistency.
• Contributor revenue share
Contributors earn a configurable fraction of revenue per use of their functions.
• Dashboard and semantic search
Lightweight UI for discovery, bag building, contributor and library profiles, and analytics.


---

Architecture summary

Core components

• Registry
Stores function metadata including unique id, name, module path, signature, category, tags, contributor id, usage counts, payout config, and AI generated metadata.
• Loader
Resolves module paths, imports callables, validates signatures, and supports lazy loading.
• Bag system
Creates ephemeral namespaces that map chosen libraries or functions to short aliases and exposes them as attributes on the bag object.
• Registration API
Simple hook for external libraries to register functions with minimal changes to their codebase.
• AI analyzer
Asynchronously inspects registered callables and enriches registry entries with descriptions, examples, tags, and quality flags.
• Dashboard
Web UI for semantic search, bag builder, and contributor dashboards.


Alias rules

• Use known aliases when available (numpy -> np).
• Auto generate aliases when needed.
• Guarantee collision free naming with deterministic fallback and optional user override.


---

Registry schema summary

Core fields per function

• id unique identifier
• name snake_case unique name
• module_path import path module:callable
• category primary controlled category
• signature typed inputs and output schema
• description short summary
• tags keywords for search
• source library id
• contributor_id contributor account id
• license SPDX identifier
• visibility public org or private
• version semantic version
• usage_count aggregated calls
• payout_config revenue share settings
• ai_metadata analyzer outputs and confidence


A full JSON Schema and SQL DDL are included in the repository under registry_schema.json and sql/ for Postgres.

---

Contributing and governance

Repository model

• Core components are public to encourage adoption and contributions.
• Premium connectors, billing, and payout accounting are maintained in private repositories until production readiness.


Legal and contributor requirements

• Code is licensed under Apache License 2.0.
• Contributors must sign a Contributor License Agreement or accept a Developer Certificate of Origin to enable revenue sharing and legal clarity.
• Revenue share terms are governed by a separate contributor agreement that contributors must accept before payouts are enabled.


How to contribute

• Fork the repo and open a pull request.
• Add tests for new functions and follow the code style guide.
• Include docstrings and type hints.
• For function registration, add a mylib_atomfun.py registration file or use the register API in your package initialization.


Community standards

• Follow the CODE OF CONDUCT.
• Report security issues via SECURITY.md.
• Use issue and PR templates for consistent triage.


---

License and legal

License
This repository is released under the Apache License 2.0. See the LICENSE file for full terms.

Contributor agreements
Contributors must sign the CLA or accept the DCO. Revenue share requires a separate payout agreement.

Privacy and data
Usage tracking is collected for analytics and payout. Sensitive payment details are stored encrypted and off registry. See SECURITY.md and the privacy section in the docs for details.

---

Roadmap and next steps

Immediate priorities

• Implement registry JSON Schema and Postgres DDL.
• Build the loader and Bag class with aliasing rules.
• Implement registration API and basic auth.
• Integrate a first pass AI analyzer for metadata enrichment.
• Create a minimal dashboard with text search and bag builder.


Medium term

• Add semantic vector search and advanced AI suggestions.
• Implement contributor payout pipeline and accounting.
• Publish SDKs and language bindings.
• Launch curated function packs and marketplace features.


Long term

• Expand to multi language function registries.
• Provide hosted micro API deployments for high volume functions.
• Build enterprise governance and private registry options.


---

Contact and resources

• Repository: link to the GitHub repo in the project home.
• Docs: docs directory and hosted documentation site.
• Security: see SECURITY.md for vulnerability reporting.
• Contributing: see CONTRIBUTING.md for CLA and PR process.


---

Get started

Atomfun is designed to make code discovery and composition effortless. Clone the repo, read the registry schema, and try creating your first bag. If you maintain a library, add a small registration file and let atomfun do the rest.

Welcome to atomfun — build smaller functions, compose faster, and let your work earn.
