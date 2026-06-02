# Manifest Schema

The manifest schema is available in two forms:

```text
schemas/asset-pipeline-manifest.schema.json
```

and:

```bash
asset-pipeline-steward schema
```

The CLI-generated schema is tested against the checked-in schema file, so maintainers should update both together.

## Required Top-Level Sections

- `project`
- `assets`
- `models`
- `workflows`
- `review_signals`
- `decision_gate`
- `handoff`

## Intent

The schema describes the public shape of a manifest. The Python validator adds safety checks that JSON Schema alone does not cover, such as private local path detection, sensitive marker detection, and model-weight path blocking.

Use both:

```bash
asset-pipeline-steward schema
asset-pipeline-steward examples/fixture_manifest.json
```
