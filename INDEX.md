# UAGIP — Universal Autonomous Gaming Intelligence Platform

> An AI-powered framework for autonomous game-playing agents: capture the screen, interpret
> it with vision models, decide, act, and learn from the outcome.

**Status:** Active development, `v0.6.1-stable` · 8 release tags · foundation and vision layers complete
**Stack:** Python · FastAPI · PostgreSQL · Redis · OpenCV · EasyOCR · YOLO (ultralytics) · LangChain · Ollama · Streamlit

---

## Architecture

```
Capture → Vision → State → Decision → Actions → Memory → Analytics
```

Capture frames from an Android device over ADB, interpret them with vision models and OCR,
maintain game state, decide on actions, execute them, and learn from what happens.

## Build status

Development runs in tagged phases. Completed, per the commit history:

| Phase | Delivered | Tag |
|---|---|---|
| 1A–1E | Config manager, production logging framework, event bus, scheduler, health monitor | `v0.2-core-foundation` |
| 2A | Capture engine | `v0.3-capture-engine` |
| 2B | Android ADB adapter | `v0.4-adb-adapter` |
| 3A | Vision engine foundation | `v0.5-vision-foundation` |
| 3B | Dataset platform | `v0.6-dataset-platform` |

**In progress on branch `yolo-experimental`** (uncommitted at time of writing): a plugin
framework under `plugins/base/` — plugin manager, lifecycle, context, health, metrics — and
YOLO model management under `vision/yolo/` — model registry, metadata, detector backend,
inference results.

> ⚠️ [`MODULE_STATUS.md`](MODULE_STATUS.md) is **stale** and understates progress: it lists
> capture and vision as "not started" when both shipped in v0.3–v0.5. Trust the tags and
> commit history over that file until it's refreshed.

**Overlap note:** [UGAF](../Simple%20UAIGF/UGAF_Development_Kit) targets the same problem
space from a different angle — a plugin framework with a working web console and data-driven
automation. UAGIP is the more research-oriented design, reaching for vision models, learning,
and gameplay-video mining.

## Getting started

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
python project_bootstrap.py
pytest
```

Copy `.env.example` to `.env` to configure. `pre-commit` hooks are configured in
`.pre-commit-config.yaml`; Docker definitions are included.

## Layout

```
core/          Config, logging, event bus, scheduler, health monitor   ✅
capture/       Screen capture (ADB)                                    ✅
vision/        Vision models and OCR; vision/yolo/ in progress         ✅
datasets/      Dataset platform                                        ✅
plugins/       Per-game plugin framework                          🔨 in progress
actions/       Input execution
memory/        State and history
learning/      Outcome learning
research/      Gameplay video mining (yt-dlp, FFmpeg)
video/         Video processing
analytics/     Metrics
api/           FastAPI service
dashboard/     Streamlit UI
docs/          Module design docs and master PRD
tests/         14 test files
```

## Documentation

65 markdown files. Notable: [`ARCHITECTURE.md`](ARCHITECTURE.md),
[`docs/master_prd.md`](docs/master_prd.md), [`DEVELOPMENT_PLAN.md`](DEVELOPMENT_PLAN.md),
[`ROADMAP.md`](ROADMAP.md), [`TECH_DECISIONS.md`](TECH_DECISIONS.md),
[`LESSONS_LEARNED.md`](LESSONS_LEARNED.md), [`TECH_DEBT.md`](TECH_DEBT.md), and per-module
docs under `docs/` for the capture engine, event bus, plugin framework, dataset manager,
health monitor, and logging framework.

## Codebase

| Metric | Value |
|---|---|
| Total tokens | **95,728** |
| Source code | 79,851 (all Python) |
| Tests | 23,528 tokens across 14 files |
| Documentation | 15,707 tokens across 65 files |
| Files / lines | 148 files · 16,237 lines |

Measured with `cl100k_base`, excluding dependencies and build output.

## Notes

- The active branch is **`yolo-experimental`**, not `master`. Merge before treating `master`
  as current.
- No secrets in the repository; `.env.example` documents the intended configuration.
