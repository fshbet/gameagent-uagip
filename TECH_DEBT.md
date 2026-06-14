# Technical Debt Register

This document tracks known issues, limitations, architectural concerns, and deferred improvements.

---

# Closed Technical Debt

## TD-001 - Health Monitor Async Warning

### Component

Health Monitoring System

### Status

Resolved

### Priority

Medium

### Severity

Low

### Category

Async / Resource Management

### Original Issue

```text
RuntimeWarning:
coroutine 'HealthMonitor.run_check' was never awaited
```

Observed during test execution.

### Resolution

The async lifecycle issue was corrected and verified.

Validation completed using:

```powershell
python -X tracemalloc -m pytest tests/ -v
```

### Verification Result

```text
133 passed
0 failed
0 warnings
```

### Closed In

Phase 3B - Dataset Management Platform

### Notes

No functional regressions detected after fix.


---

# TD-002 - Emulator Support Missing

## Component

Capture Layer

## Status

Planned

## Priority

Medium

## Severity

Low

## Category

Feature Gap

## Description

Capture subsystem currently supports:

* Desktop Capture
* Android ADB Capture

Missing support for:

* BlueStacks
* LDPlayer
* MuMu
* Android Studio Emulator

## Impact

Development and testing currently rely on physical Android devices.

## Target Phase

Phase 4A - Emulator Adapter

---

# TD-003 - YOLO Infrastructure Not Implemented

## Component

Vision Layer

## Status

Planned

## Priority

High

## Severity

Medium

## Category

Missing Capability

## Description

Current Vision Engine supports:

* Image preprocessing
* OCR
* Template matching
* Detector abstraction

Missing:

* YOLO model management
* Dataset training
* Inference pipeline
* Model versioning

## Impact

Object detection cannot yet be trained or deployed.

## Target Phase

Phase 3C - Phase 3E

---

# TD-004 - Dataset Annotation Tooling Missing

## Component

Dataset Platform

## Status

Planned

## Priority

Medium

## Severity

Low

## Category

Tooling

## Description

Dataset management exists but annotation tooling is not yet available.

Missing:

* Bounding box editor
* Polygon editor
* Dataset review workflow
* Label validation tools

## Target Phase

Phase 4B

---

# Debt Management Rules

1. Every warning must be tracked.
2. Every deferred fix must receive a TD identifier.
3. Technical debt must never be silently ignored.
4. Critical debt must be resolved before production deployment.
5. Closed items should be moved to a historical section rather than deleted.

---

# Summary

| ID     | Component           | Priority | Status   |
|--------|---------------------|----------|----------|
| TD-002 | Emulator Support    | Medium   | Planned  |
| TD-003 | YOLO Infrastructure | High     | Planned  |
| TD-004 | Annotation Tooling  | Medium   | Planned  |


# Current Technical Debt Status

Open Items: 3

Resolved Items: 1

Production Blockers: 0

Current Project Health:

* Tests Passing: 133
* Test Failures: 0
* Runtime Warnings: 0
* Known Critical Defects: 0
