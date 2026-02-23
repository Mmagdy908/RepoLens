---
mode: agent
description: Execute all pending tasks in a single milestone from the progress file
---

Read #file:../docs/phase1-progress.md (or the most recently updated phaseN-progress.md).

Ask the user: "Which milestone number do you want to execute? (e.g. M1, M2, …)"

Then execute **all `[ ]` tasks in that milestone**, one by one in order:

For each task:
1. Read any existing files the task touches before editing
2. Implement exactly what the task description says
3. Follow all conventions in #file:../copilot-instructions.md
4. Mark the task `[x]` in the progress file immediately after completing it
5. If a task adds a dependency, note it — but continue; the user will rebuild after the milestone

After completing the milestone:
- Print a summary table: Task ID | File(s) changed | Status
- List any Docker rebuild commands needed (only once, at the end)
- Confirm the milestone is fully `[x]` in the progress file
- State the next milestone name and its first task
