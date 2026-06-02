# Starter Issues

Create these issues after the repository is public. They are designed to produce visible, useful maintenance activity instead of empty project noise.

Machine-readable source:

```text
docs/starter-issues.json
```

Render them with:

```bash
asset-pipeline-steward starter-issues .
```

## 1. Add handoff-heavy batch resume manifest example

Labels: `enhancement`, `documentation`

Body:

```text
Add a synthetic manifest example that demonstrates resuming a paused batch without private outputs or copyrighted samples.

Acceptance criteria:
- Example manifest lives under examples/.
- It includes progress, blocker, known-unknown, and next-action handoff fields.
- It keeps synthetic assets and public-safe paths only.
- It passes asset-pipeline-steward validation.
- README or terminal examples link to it.
```

## 2. Add handoff completeness validation rules

Labels: `enhancement`

Body:

```text
Extend validation so manifests can declare handoff-ready fields before a maintainer resumes work.

Acceptance criteria:
- Validator checks goal, current status, next action, blockers, and known unknowns.
- Tests cover valid and invalid handoff examples.
- docs/terminal-examples.md shows the new behavior.
```

## 3. Extend maintainer report with handoff sections

Labels: `enhancement`

Body:

```text
Extend asset-pipeline-steward report so it can render a handoff-ready summary.

Acceptance criteria:
- Report includes goal, current status, next action, blockers, and known unknowns.
- Tests cover the new report sections.
- Output remains readable in plain terminal logs.
```

## 4. Add public extraction tutorial

Labels: `documentation`

Body:

```text
Write a tutorial showing how to convert a private local AI asset workflow into a public-safe synthetic fixture.

Acceptance criteria:
- Tutorial explains keep/replace/exclude decisions.
- No private or copyrighted samples are used.
- Tutorial links to docs/public-extraction-checklist.md.
```

## 5. Prepare v0.1.0 release

Labels: `release`

Body:

```text
Prepare the first public release after CI passes on GitHub.

Acceptance criteria:
- CHANGELOG.md has v0.1.0 notes.
- README quickstart has been verified from a fresh clone.
- GitHub Actions CI is green.
- Release notes link to terminal examples and Codex for OSS readiness docs.
```
