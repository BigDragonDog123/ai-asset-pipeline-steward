# End-To-End Maintainer Loop

This walkthrough shows the full maintenance shape that AI Asset Pipeline Steward is meant to protect: triage, preflight, human review, automated observations, a release decision, and a resumable handoff.

The example uses only synthetic placeholders:

```text
examples/end_to_end_maintainer_loop_manifest.json
```

## Scenario

A maintainer receives feedback that an AI asset batch has inconsistent quality. The maintainer needs to:

- identify which synthetic assets are accepted, queued, revised, or blocked;
- verify the manifest is public-safe before any broader sharing;
- keep human review as the ground-truth signal;
- preserve automated review notes as supporting evidence only;
- decide whether to release, rerun, or pause;
- leave a handoff another maintainer or coding agent can resume.

## Run It

```bash
asset-pipeline-steward examples/end_to_end_maintainer_loop_manifest.json
asset-pipeline-steward report examples/end_to_end_maintainer_loop_manifest.json
```

The validation command should pass. The report should show:

- inventory counts for synthetic assets, models, workflows, and review signals;
- workflows for issue triage, review smoke gate, and release/rerun decision;
- separated human and automated review signals;
- a decision gate that blocks release until review gaps are resolved;
- a handoff with current status, next action, blockers, and known unknowns.

## Why It Matters

This is the smallest complete example of the maintainer workload behind the repository. It shows why the project is more than a schema checker:

- it protects public extraction by rejecting private paths and sensitive markers;
- it makes review state explicit before scaling a batch;
- it keeps automated observations subordinate to human judgement;
- it turns a paused local workflow into a reusable public maintenance record.

## Public Safety

Do not replace this example with real local assets, private paths, model weights, logs, generated private outputs, or copyrighted media. If you adapt the scenario, keep it synthetic or use publishable fixtures only.
