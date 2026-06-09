from pathlib import Path

ROOT = Path("UAGIP")

# -----------------------------
# FOLDERS
# -----------------------------

folders = [
    "docs/vision",
    "docs/learning",
    "docs/research",
    "docs/plugins",
    "docs/deployment",
    "prompts/opencode",
    "core/config",
    "core/logging",
    "core/scheduler",
    "core/events",
    "core/state",
    "core/health",
    "capture",
    "vision",
    "actions",
    "memory",
    "learning",
    "research",
    "video",
    "analytics",
    "dashboard",
    "api",
    "plugins/shadow_fight_3",
    "plugins/clash_of_clans",
    "plugins/hay_day",
    "plugins/minecraft",
    "datasets/screenshots",
    "datasets/videos",
    "datasets/annotations",
    "datasets/models",
    "tests",
    "deployments/docker",
    "deployments/compose",
    "deployments/kubernetes",
    "scripts",
    "logs",
    "recordings",
]
for folder in folders:
    (ROOT / folder).mkdir(parents=True, exist_ok=True)

# -----------------------------
# FILES WITH CONTENT
# -----------------------------

files = {
    ".gitignore": """# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd

# Virtual Environments
.venv/
venv/
env/

# IDE
.vscode/
.idea/

# Environment Files
.env
.env.*

# Logs
logs/
*.log

# Build
build/
dist/
*.egg-info/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Databases
*.db
*.sqlite
*.sqlite3

# Datasets
datasets/videos/
datasets/screenshots/
datasets/raw/

# YOLO
runs/

# FFmpeg
recordings/

# OS
Thumbs.db
Desktop.ini
.DS_Store
""",

    ".env.example": """APP_ENV=development
LOG_LEVEL=INFO

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/uagip

REDIS_URL=redis://localhost:6379

OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=qwen3-coder:14b

SCREEN_CAPTURE_FPS=5

DATASET_DIR=datasets
VIDEO_OUTPUT_DIR=recordings
PLUGIN_DIR=plugins
""",

    "README.md": """# Universal Autonomous Gaming Intelligence Platform (UAGIP)

AI-powered gaming intelligence framework.
""",

    "ROADMAP.md": """# Roadmap

Phase 1 - Core Framework
Phase 2 - Capture Engine
Phase 3 - Vision Engine
Phase 4 - Input Engine
...
""",

    "ARCHITECTURE.md": """# Architecture

Capture
-> Vision
-> State
-> Decision
-> Actions
-> Memory
-> Analytics
""",

    "DEVELOPMENT_PLAN.md": """# Development Plan

[ ] Phase 1 - Core
[ ] Phase 2 - Capture
[ ] Phase 3 - Vision
[ ] Phase 4 - Input
[ ] Phase 5 - State
""",

    "PROJECT_RULES.md": """# Project Rules

- Plugin architecture only
- No hardcoded coordinates
- YAML driven configuration
- Type hints mandatory
- Tests required
- Docker support required
""",

    "AI_INSTRUCTIONS.md": """# AI Instructions

Always read:
1. ARCHITECTURE.md
2. PROJECT_RULES.md
3. DEVELOPMENT_PLAN.md

Before generating code.
""",

    "CHANGELOG.md": "# Changelog\n\n",

    "CONTRIBUTING.md": """# Contributing

Follow coding standards.
Run tests before commit.
""",

    "SECURITY.md": """# Security Policy

Do not commit secrets.
Use .env files.
""",

    "AGENT_CONTEXT.md": """# Agent Context

Current Phase:
Phase 1

Status:
Repository Setup

Next:
Core Framework
""",

    "MODULE_STATUS.md": """# Module Status

CORE            NOT_STARTED
CAPTURE         NOT_STARTED
VISION          NOT_STARTED
INPUT           NOT_STARTED
MEMORY          NOT_STARTED
LEARNING        NOT_STARTED
RESEARCH        NOT_STARTED
VIDEO           NOT_STARTED
ANALYTICS       NOT_STARTED
""",

    "TECH_DECISIONS.md": """# Technical Decisions

Language: Python

Vision: OpenCV + YOLO

Database: PostgreSQL

Queue: Redis

API: FastAPI

Dashboard: Streamlit

Coding Model: Qwen3-Coder
""",

    "requirements.txt": """fastapi
uvicorn
pydantic
sqlalchemy
alembic
psycopg2-binary
redis
opencv-python
easyocr
ultralytics
numpy
pandas
requests
beautifulsoup4
yt-dlp
ffmpeg-python
langchain
ollama
streamlit
python-dotenv
pyyaml
adbutils
mss
dxcam
pyautogui
""",

    "requirements-dev.txt": """pytest
pytest-cov
black
ruff
mypy
pre-commit
ipykernel
""",

    "pyproject.toml": """[project]
name = "uagip"
version = "0.1.0"
description = "Universal Autonomous Gaming Intelligence Platform"
requires-python = ">=3.12"

[tool.black]
line-length = 100

[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
""",

    ".pre-commit-config.yaml": """repos:
  - repo: https://github.com/psf/black
    rev: 25.1.0
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.12.0
    hooks:
      - id: ruff
""",

    "docker-compose.yml": """version: '3.9'

services:

  postgres:
    image: postgres:16

  redis:
    image: redis:7

""",

    "Dockerfile": """FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
""",
}

# -----------------------------
# CREATE FILES
# -----------------------------

for filename, content in files.items():
    filepath = ROOT / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")

# -----------------------------
# CREATE EMPTY DOC FILES
# -----------------------------

extra_docs = [
    "docs/vision/vision_requirements.md",
    "docs/vision/yolo_training.md",
    "docs/vision/detection_schema.md",
    "docs/learning/rl_design.md",
    "docs/learning/reward_system.md",
    "docs/learning/strategy_validation.md",
    "docs/research/web_research.md",
    "docs/research/youtube_mining.md",
    "docs/research/knowledge_graph.md",
    "docs/plugins/plugin_sdk.md",
    "docs/plugins/onboarding_guide.md",
    "docs/deployment/docker.md",
    "docs/deployment/monitoring.md",
    "docs/deployment/kubernetes.md",
]

for doc in extra_docs:
    path = ROOT / doc
    path.touch(exist_ok=True)

# -----------------------------
# PHASE PROMPTS
# -----------------------------

for i in range(1, 24):
    phase = f"phase_{str(i).zfill(2)}.md"
    phase_path = ROOT / "prompts" / "opencode" / phase
    phase_path.write_text(
        f"# Phase {i}\n\nImplementation instructions go here.\n",
        encoding="utf-8"
    )

print(f"\n✅ UAGIP repository created successfully at:\n{ROOT.resolve()}")