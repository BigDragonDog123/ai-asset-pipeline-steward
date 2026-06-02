# AI Asset Pipeline Steward Skill Design

## Purpose

This skill captures a repeated AI asset maintenance pattern: model download and verification, workflow setup, staged benchmarks, VLM-assisted review, human rating workbenches, dataset curation, audit reports, and handoff documents.

The design deliberately avoids framing the project as a niche content workflow. The reusable open-source value is stewardship of AI-generated asset pipelines.

## Evidence From Local Work

- Repeated local work contained model, benchmark, VLM, review, audit, queue, and download artifacts.
- Repo-local skill drafts covered project setup, model inventory, model verification, review workbenches, direct downloads, and VLM feedback loops.
- Dataset-preparation scripts showed repeated patterns for extraction, review, training support, and coverage rescue.
- Handoff documents showed the need for resumable context, skill routing, checkpointed reports, audit briefs, and upload-readiness gates.

## Skill Boundary

The skill should guide process and judgment. It should not become a content-specific or private-material workflow. Public examples must use synthetic fixtures and neutral naming.

## Initial Test Prompts

The companion `test-prompts.json` covers three high-risk situations:

1. Full benchmark pressure before preflight.
2. Over-trusting VLM or tagger scores.
3. Unsafe open-source packaging of local private pipelines.

## Next Step

Use this skill as the basis for the first public-safe OSS direction: an AI asset review and pipeline stewardship kit with a review workbench, synthetic fixture data, clean scripts, documentation, and repo-local Codex skills.
