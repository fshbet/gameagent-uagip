### TD-001

Health Monitor emits:

RuntimeWarning:
coroutine 'HealthMonitor.run_check' was never awaited

Status:
Non-blocking

Impact:
No test failures

Priority:
Medium

Target:
Before production deployment


Health Monitor

Issue:
RuntimeWarning: coroutine HealthMonitor.run_check was never awaited

Impact:
No functional failures currently.
Potential async scheduling issue.

Priority:
Medium

Must be fixed before production release.