# Contributing

Changes are welcome after the initial public repository is created. Do not claim an integration works unless there is an actual provider-access test, recorded sample request/response contract (without secrets), error handling and cost cap.

## Pull request checklist

- Update corresponding `docs/` section, any `schemas/*.json`, templates and agent/skill instructions.
- Ensure no secrets or private reference images are committed; use fictional test material.
- Run `python -m pytest -q` and `python -m shotloom.cli validate --project projects/night-protocol`.
- Test old-asset invalidation, budget approval, media decodability and explicit human QA.
- Note external source/license requirements; do not copy source code from unlicensed repos or restrictive licenses into this MIT project without permission and proper compliance.
- Include testable claims. A new prompt recipe must have a reproducible example, not just adjectives.

## Code style

Python 3.11+, low dependency surface, typed interfaces for public helpers, meaningful errors, no undeclared network requests, deterministic file operations. Stable IDs and no silent migrations.
