# MASTER PROMPT: Universal Autonomous Gaming Intelligence Platform (UAGIP)

## Mission

Build a production-grade, plugin-based, AI-powered gaming intelligence platform capable of autonomously playing Android, Windows, Browser, and future game types.

This is NOT a simple game bot.

The objective is to create a self-improving gaming ecosystem that can:

* Play games autonomously
* Learn from successes and failures
* Learn from human gameplay
* Learn from community knowledge
* Learn from videos
* Learn from patch notes
* Learn from web searches
* Create and maintain a knowledge base
* Record gameplay
* Generate highlights
* Upload videos automatically
* Generate AI commentary
* Support multiple games without modifying core code

---

# CORE DESIGN PRINCIPLES

## Principle 1

No game-specific logic inside the core framework.

All game-specific logic must reside inside plugins.

---

## Principle 2

Every module must be independently deployable.

---

## Principle 3

Every module must expose APIs.

---

## Principle 4

Every module must support future replacement.

Example:

OpenCV → YOLO

SQLite → PostgreSQL

Local LLM → Cloud LLM

Without rewriting the system.

---

## Principle 5

Everything must be configurable.

No hardcoded coordinates.

No hardcoded screen resolutions.

No hardcoded actions.

---

# TECHNOLOGY STACK

Backend:

* Python 3.12+

AI:

* Ollama
* Qwen3
* Gemma
* DeepSeek

Vision:

* OpenCV
* YOLO
* EasyOCR

Learning:

* Stable Baselines3
* PPO
* DQN
* A2C

Database:

* SQLite
* PostgreSQL
* pgvector

Messaging:

* Redis
* RabbitMQ

APIs:

* FastAPI

UI:

* Streamlit

Automation:

* ADB
* Scrcpy
* PyAutoGUI
* Pynput

Video:

* FFmpeg

Speech:

* Whisper

Containerization:

* Docker

Monitoring:

* Prometheus
* Grafana

---

# PROJECT STRUCTURE

Create:

/core
/plugins
/vision
/actions
/learning
/memory
/research
/video
/analytics
/dashboard
/api
/tests
/docs
/deployments

---

# DEVELOPMENT PHASES

The implementation must be completed in the following phases.

Each phase must be independently runnable.

Each phase must contain:

* Source code
* Tests
* Documentation
* Configuration
* Example implementation

---

# PHASE 1 - CORE FOUNDATION

## Deliverables

Create:

Core framework

Plugin loader

Configuration manager

Logging framework

Dependency injection

Event bus

State manager

Task scheduler

Error handler

Health monitoring

### Requirements

Support:

YAML configs

JSON configs

Environment variables

Runtime overrides

### Output

Provide:

Folder structure

Source code

Unit tests

README

Docker files

---

# PHASE 2 - CAPTURE ENGINE

## Objective

Capture game screen data.

### Android

Support:

Scrcpy

ADB

USB

Wireless

### Windows

Support:

MSS

DXCam

Multi-monitor

### Features

Frame capture

Video capture

Screenshot capture

Region capture

Performance metrics

### API

capture.get_frame()

capture.start_recording()

capture.stop_recording()

---

# PHASE 3 - VISION ENGINE

## Objective

Convert pixels into structured information.

### Support

OpenCV

YOLO

OCR

Template matching

### Detect

Buttons

Characters

Health bars

Mana bars

Energy bars

Enemies

Rewards

Menus

Text

Icons

Animations

### Output

Structured JSON state.

---

# PHASE 4 - INPUT ENGINE

## Objective

Control devices.

### Android

ADB

Tap

Swipe

Long press

Multi-touch

### Windows

Mouse

Keyboard

Controller support

### API

action.tap()

action.swipe()

action.press_key()

action.execute()

---

# PHASE 5 - STATE ENGINE

## Objective

Convert detections into game states.

Examples:

MENU

FIGHT

LOADING

REWARD

INVENTORY

BOSS

CUTSCENE

SHOP

GAME_OVER

Must support custom state registration.

---

# PHASE 6 - RULE ENGINE

## Objective

Rule-based gameplay.

Example:

IF hp < 20%

THEN retreat

Create visual rule editor.

Create YAML rule definitions.

---

# PHASE 7 - LLM DECISION ENGINE

## Objective

Use LLM reasoning.

### Supported Models

Qwen

Gemma

DeepSeek

Llama

### Inputs

Current state

Historical memory

Community knowledge

### Output

Strict JSON actions.

### Features

Tool calling

Memory retrieval

Reflection

Planning

---

# PHASE 8 - MEMORY SYSTEM

## Objective

Persistent memory.

Store:

States

Actions

Rewards

Failures

Strategies

Videos

Knowledge

### Support

SQLite

PostgreSQL

Vector DB

Semantic search

---

# PHASE 9 - RESEARCH ENGINE

## Objective

Search internet for strategies.

### Sources

Official Wiki

Official Guides

Patch Notes

Community Wiki

Forums

Reddit

YouTube

Steam Discussions

Blogs

Discord exports

### Trigger Events

Boss encountered

Repeated failures

Low win rate

New chapter

New enemy

Patch detected

### Outputs

Strategies

Weaknesses

Counters

Equipment suggestions

Combo suggestions

Store confidence scores.

---

# PHASE 10 - YOUTUBE LEARNING ENGINE

## Objective

Learn from videos.

### Input

YouTube URLs

Recorded gameplay

Tournament videos

### Pipeline

Download video

Extract frames

Extract audio

Generate transcript

Analyze strategy

Extract action sequences

Build knowledge entries

### Output

Winning patterns database

---

# PHASE 11 - REINFORCEMENT LEARNING ENGINE

## Objective

Self-learning.

### Algorithms

PPO

DQN

A2C

### Features

Reward shaping

Experience replay

Checkpointing

Training analytics

Model versioning

---

# PHASE 12 - STRATEGY VALIDATION ENGINE

## Objective

Verify internet advice.

### Workflow

Research Strategy
↓
Apply Strategy
↓
Measure Results
↓
Update Confidence

Store:

Success rate

Failure rate

Patch relevance

Last validation date

---

# PHASE 13 - SELF REFLECTION ENGINE

After every match:

Generate:

Why won

Why lost

Mistakes

Best actions

Worst actions

Improvement opportunities

Store reflection permanently.

---

# PHASE 14 - GAME SDK

Create SDK for onboarding new games.

Developer only needs:

States

Actions

Vision mappings

Strategy file

Config

Everything else handled automatically.

---

# PHASE 15 - SHADOW FIGHT 3 PLUGIN

Implement complete plugin.

States:

MENU

FIGHT

VICTORY

DEFEAT

REWARD

Actions:

MOVE_LEFT

MOVE_RIGHT

JUMP

DUCK

PUNCH

KICK

BLOCK

SHADOW_POWER

Detect:

Player HP

Enemy HP

Distance

Shadow Energy

Round State

Create starter strategies.

---

# PHASE 16 - ANALYTICS PLATFORM

Create dashboards.

Metrics:

Win Rate

Loss Rate

Rewards

Match Duration

Boss Success Rate

Strategy Success Rate

Learning Progress

Model Accuracy

---

# PHASE 17 - VIDEO RECORDING ENGINE

## Objective

Record everything.

### Record

Entire match

Boss fights

Rewards

Achievements

Failures

Training sessions

### Output

MP4

WebM

Highlights

Thumbnails

---

# PHASE 18 - AI VIDEO EDITOR

## Objective

Automatically create videos.

### Detect

Victory moments

Boss kills

Rare rewards

High scores

Near defeats

Funny moments

### Generate

Highlight reels

Daily summaries

Weekly summaries

Boss guides

Training progress videos

---

# PHASE 19 - AI COMMENTARY GENERATOR

## Objective

Create video descriptions.

### Inputs

Match statistics

Strategies used

Boss defeated

Rewards earned

Win/Loss result

### Outputs

YouTube Description

Example:

"Today the AI defeated Titan using a medium-range counterattack strategy learned from previous encounters and community research. The match lasted 3 minutes and resulted in a flawless victory with 82% remaining health."

Generate:

Title

Description

Tags

Hashtags

Chapter markers

---

# PHASE 20 - SOCIAL MEDIA PUBLISHER

## Objective

Upload content automatically.

### Platforms

YouTube

TikTok

Instagram Reels

Facebook

X

Telegram

Discord

### Features

OAuth authentication

Scheduled uploads

Auto-generated descriptions

Auto-generated hashtags

Auto-generated thumbnails

Upload retry logic

---

# PHASE 21 - KNOWLEDGE GRAPH

Create relationships:

Bosses

Weapons

Strategies

Enemies

Maps

Skills

Equipment

Community Tips

Use graph relationships for advanced reasoning.

---

# PHASE 22 - MULTI-AGENT SYSTEM

Agent 1:
Vision

Agent 2:
Decision

Agent 3:
Research

Agent 4:
Learning

Agent 5:
Memory

Agent 6:
Video

Agent 7:
Publishing

Agent 8:
Analytics

Agents communicate through queues.

---

# PHASE 23 - CONTINUOUS IMPROVEMENT LOOP

Observe
↓
Play
↓
Record
↓
Analyze
↓
Reflect
↓
Research
↓
Learn
↓
Validate
↓
Update Knowledge
↓
Improve Strategy
↓
Play Again

Forever.

---

# FINAL DELIVERABLES

Generate:

1. Complete source code
2. Docker deployment
3. Kubernetes deployment
4. FastAPI APIs
5. Streamlit dashboard
6. PostgreSQL schema
7. SQLite schema
8. Vector database integration
9. Plugin SDK
10. Shadow Fight 3 implementation
11. Unit tests
12. Integration tests
13. CI/CD pipeline
14. Monitoring
15. Documentation
16. Architecture diagrams
17. API documentation
18. Video generation pipeline
19. Social publishing pipeline
20. Installation guide
21. Developer guide
22. User guide

The system must be production-ready, extensible, modular, self-improving, and capable of supporting any future game by adding only a new plugin.
