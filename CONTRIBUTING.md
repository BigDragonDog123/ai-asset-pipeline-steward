# Contributing

Thanks for helping improve AI Asset Pipeline Steward.

## Ground Rules

- Keep examples public-safe and synthetic.
- Do not add credentials, private paths, local user folders, model files, caches, logs, or unpublished media.
- Prefer small, reviewable changes.
- Add or update tests when behavior changes.
- Use evidence-first workflow for new tools, dependencies, workflows, or public guidance.

## Local Checks

Run:

```bash
python -m unittest discover -s tests
```

For manifest changes, also run:

```bash
python -m asset_pipeline_steward.cli examples/fixture_manifest.json
```

## Pull Request Expectations

A good pull request should include:

- what changed;
- why it helps maintainers;
- how it was tested;
- any evidence used for tool or workflow choices;
- any remaining uncertainty.

## Dependency Policy

Keep dependencies minimal. If a new dependency is proposed, explain why it should be adopted, extended, composed with existing code, or avoided.
