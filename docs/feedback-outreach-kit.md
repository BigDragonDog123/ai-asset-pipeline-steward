# Feedback Outreach Kit

Status date: 2026-06-02.

Use this kit to collect the first real public feedback signal for AI Asset Pipeline Steward. The goal is one public URL from someone other than the maintainer that a reviewer can open without exposing private files, credentials, logs, or non-public media.

## Best Reviewer Profiles

Prioritize people who already understand one of these workflows:

- maintaining AI image, audio, video, dataset, benchmark, or review pipelines;
- reviewing generated assets with human ratings plus automated observations;
- turning local experiments into public-safe documentation or fixtures;
- maintaining open-source tools with issue triage, releases, and CI;
- using coding agents to resume long-running project work.

Avoid asking for generic praise. Ask for one concrete usability gap, confusing field, missing validation rule, or reason the workflow does not fit.

## Review Paths

### 10-Minute Skim

1. Open the README.
2. Skim `docs/reviewer-brief.md`.
3. Skim `examples/handoff_resume_manifest.json`.
4. Leave one public feedback issue.

### 20-Minute Quickstart

1. Clone the repository.
2. Run the README quickstart through `asset-pipeline-steward readiness .`.
3. Run `asset-pipeline-steward report examples/handoff_resume_manifest.json`.
4. Leave a public feedback issue with what worked and what was unclear.

### 40-Minute Maintainer Review

1. Run the quickstart.
2. Compare the manifest shape against one real maintenance workflow, without sharing private data.
3. Identify one missing field, validation rule, report section, or handoff rule.
4. Leave a public feedback issue or public comment.

## English Short DM

```text
I published a small public-safe toolkit for AI asset pipeline maintenance:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward

Could you give it a 10-minute skim and leave one public feedback issue if anything is confusing or missing?

Best starting point:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/docs/reviewer-brief.md

Feedback form:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml

Please do not include private paths, logs, credentials, model files, or non-public media.
```

## English Forum Post

```text
I am looking for feedback on AI Asset Pipeline Steward, a small public-safe toolkit for turning local AI asset workflows into repeatable maintainer records:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward

It focuses on synthetic/public-safe manifests, model/workflow readiness, separated human and automated review signals, decision gates, and resumable handoffs.

Useful review paths:
- 10-minute skim: reviewer brief + handoff example
- 20-minute quickstart: run repo-scan, readiness, and one report command
- 40-minute maintainer review: compare the manifest shape against a real workflow without sharing private data

I would value one concrete critique: unclear field, missing validation rule, weak report output, or reason this does not fit your workflow.

Reviewer brief:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/docs/reviewer-brief.md

Feedback form:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml
```

## Chinese Short DM

```text
我做了一个公开安全的小工具，用来把本地 AI 素材/模型评测/人工审核这类流程，整理成可复现、可交接、可公开的维护记录：
https://github.com/BigDragonDog123/ai-asset-pipeline-steward

你方便花 10 分钟看一下 reviewer brief 或 example，然后留一个公开 feedback issue 吗？不用夸，最好指出哪里不清楚、缺哪个字段/校验规则、或者为什么不适合你的流程。

Reviewer brief:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/docs/reviewer-brief.md

Feedback form:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml

不要贴私人路径、日志、密钥、模型文件或非公开素材。
```

## Chinese Public Post

```text
我在征集一个开源小工具的真实反馈：AI Asset Pipeline Steward
https://github.com/BigDragonDog123/ai-asset-pipeline-steward

它的目标是把本地 AI 素材生产、模型/工作流检查、人工审核、VLM 辅助观察、批量任务交接这些重复工作，抽成一个公开安全的维护流程。仓库只放合成示例，不包含模型权重、私人路径、日志、密钥或非公开素材。

希望有做过 AI 图像/音视频/数据集/评测/审核流程的人帮忙看一眼：
- 10 分钟：看 reviewer brief 和 handoff 示例
- 20 分钟：跑 quickstart
- 40 分钟：拿它和你自己的真实维护流程对照，但不要公开私人数据

最有用的是具体批评：哪里不清楚、缺什么字段、缺什么校验规则、report 哪里不好用、为什么不适合你的流程。

Reviewer brief:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/docs/reviewer-brief.md

Feedback form:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml
```

## Valid Evidence Checklist

A feedback link counts when all are true:

- the author is not the maintainer;
- the URL is public or otherwise accessible to an application reviewer;
- the content discusses this repository or its workflow;
- the content does not expose private paths, logs, credentials, local media, model weights, or non-public samples;
- the URL is recorded in `external_feedback_urls` in `docs/adoption-evidence.json`.

## After Feedback Arrives

1. Scan for public feedback candidates:

```bash
asset-pipeline-steward feedback-candidates .
```

2. Record the reviewed public URL:

```bash
asset-pipeline-steward record-feedback https://example.com/public-feedback-url
```

3. The command also refreshes public GitHub metrics when the API is available. If it prints a warning, manually review stars, forks, CI, release, issue, and PR evidence before submitting.
4. Re-run:

```bash
asset-pipeline-steward evidence .
asset-pipeline-steward readiness .
asset-pipeline-steward application .
python -m pytest -q
```

5. Commit and push the evidence update.
6. Close issue #8 only after `asset-pipeline-steward evidence .` reports external feedback as passing.
