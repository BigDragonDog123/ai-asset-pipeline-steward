# Reviewer Request Pack

Use this when asking one real reviewer to leave public feedback. The goal is one concrete, public-safe issue or comment from someone other than the maintainer.

Repository:

```text
https://github.com/BigDragonDog123/ai-asset-pipeline-steward
```

## English Short DM

```text
I published a small public-safe toolkit for AI asset pipeline maintenance:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward

Could you give it a 10-minute skim and leave one public feedback issue? The useful answer is one concrete blocker, unclear field, missing validation rule, or reason it does not fit your workflow.

Start here:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/REVIEW.md

Feedback form:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml

Please do not include private paths, logs, credentials, model files, or non-public media.
```

## Chinese Short DM

```text
我做了一个公开安全的小工具，用来把本地 AI 素材、模型评测、人工审核这类流程，整理成可复现、可交接、可公开的维护记录：
https://github.com/BigDragonDog123/ai-asset-pipeline-steward

你方便花 10 分钟看一下 reviewer brief 或 example，然后留一个公开 feedback issue 吗？不用夸，最好指出哪里不清楚、缺哪个字段/校验规则、有什么采用阻碍，或者为什么不适合你的流程。

Review landing:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/REVIEW.md

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

最有用的是具体批评：哪里不清楚、缺什么字段、缺什么校验规则、report 哪里不好用、有什么采用阻碍、为什么不适合你的流程。

Review landing:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/blob/main/REVIEW.md

Feedback form:
https://github.com/BigDragonDog123/ai-asset-pipeline-steward/issues/new?template=feedback.yml
```

## Valid Feedback Rules

- The reviewer is not the repository maintainer.
- The feedback URL is public or reviewer-accessible.
- The feedback includes one concrete blocker, unclear field, missing rule, or fit concern.
- The feedback does not expose private paths, logs, credentials, model files, or non-public media.
- The reviewer confirms the public issue URL may be recorded as external feedback evidence.

## After Feedback

```bash
asset-pipeline-steward feedback-candidates .
asset-pipeline-steward record-feedback <public-feedback-url>
asset-pipeline-steward feedback-response-playbook .
asset-pipeline-steward evidence .
asset-pipeline-steward submission-ready . --manual-ready
```

The same request pack can be printed from a clone:

```bash
asset-pipeline-steward reviewer-request .
```
