# Feedback Response Playbook

Use this playbook after a real public, non-maintainer feedback URL appears.

The goal is not only to record the URL. The goal is to turn the feedback into visible maintenance evidence before Codex for OSS submission.

Repository:

```text
https://github.com/BigDragonDog123/ai-asset-pipeline-steward
```

## Response Rules

- Do not quote or record private paths, credentials, logs, model files, or non-public media.
- Do not count maintainer-authored text as external feedback.
- Record the feedback URL only after checking that it is public-safe and reviewer-accessible.
- Respond publicly with either a shipped change, a linked issue, or a clear roadmap decision.
- Keep the response small enough that tests and `repo-scan` can verify it before submission.

## Response Sequence

1. Screen the feedback for public-safety problems before quoting or linking it.
2. Record the URL with `asset-pipeline-steward record-feedback <public-feedback-url>`.
3. Classify the critique as docs clarification, validation rule, CLI ergonomics, roadmap decision, or out-of-scope.
4. Open or update one public issue that links the feedback URL and states the maintainer decision.
5. Ship the smallest docs, validation, test, or roadmap change that addresses the critique.
6. Reply publicly with what changed, what will change later, or why the feedback is out of scope.
7. Rerun evidence, readiness, status, and submission gates before the official form.

## Response Options

### Docs Clarification

- Use when: the reviewer was blocked by unclear instructions or missing examples.
- Evidence: docs diff, test if applicable, and public maintainer reply.

### Validation Rule

- Use when: the reviewer found a manifest field or safety rule that should be enforced.
- Evidence: validator change, focused test, and public maintainer reply.

### CLI Ergonomics

- Use when: the reviewer found command output, next actions, or error recovery unclear.
- Evidence: CLI output change, test, terminal example update, and public maintainer reply.

### Roadmap Decision

- Use when: the feedback is valid but too large for the current release.
- Evidence: roadmap or issue update with scope, reason, and next milestone.

### Out Of Scope

- Use when: the request would require private assets, large model files, or unsafe publishing.
- Evidence: public reply explaining the boundary and any safe alternative.

## Public Reply Template

```text
Thanks for the concrete feedback. I recorded this as external feedback evidence because it is public-safe and not maintainer-authored.

Maintainer response:
- Decision: <docs clarification | validation rule | CLI ergonomics | roadmap decision | out-of-scope>
- Action: <link issue, docs change, PR, release note, or roadmap item>
- Verification: <tests/checks run>

I avoided private paths, logs, credentials, model files, and non-public media.
```

## Commands

```bash
asset-pipeline-steward feedback-candidates .
asset-pipeline-steward record-feedback <public-feedback-url>
asset-pipeline-steward evidence .
asset-pipeline-steward readiness .
asset-pipeline-steward codex-oss-status . --manual-ready
asset-pipeline-steward submission-ready . --manual-ready
```

The same playbook can be printed from a clone:

```bash
asset-pipeline-steward feedback-response-playbook .
```

## Links

- Evidence file: `docs/adoption-evidence.json`
- Growth plan: `docs/maintainer-growth-plan.md`
- Submission runbook: `docs/codex-for-oss-submission-runbook.md`
