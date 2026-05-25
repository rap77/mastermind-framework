# Todo — artifact-versioning-and-lineage

## Execution Checklist

- [x] AV1: Schema foundation — artifact_versions + artifact_links
  - [x] AV1.1: Review requirements and design context for AV1
  - [x] AV1.2: Implement AV1 end-to-end (models + repository + tests TDD)
  - [x] AV1.3: Run validation for AV1
  - depends_on: none
  - validation: cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_artifact_lineage.py

- [ ] AV2: Lineage service — get_artifact_lineage()
  - [ ] AV2.1: Review requirements and design context for AV2
  - [ ] AV2.2: Implement AV2 end-to-end (service method + schema + tests)
  - [ ] AV2.3: Run validation for AV2
  - depends_on: AV1
  - validation: cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_artifact_lineage.py

- [ ] AV3: Lineage read endpoint
  - [ ] AV3.1: Review requirements and design context for AV3
  - [ ] AV3.2: Implement AV3 end-to-end (route + regression tests)
  - [ ] AV3.3: Run validation for AV3
  - depends_on: AV1, AV2
  - validation: cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_artifact_lineage.py tests/api/test_project_activity_feed.py tests/api/test_project_runs.py
