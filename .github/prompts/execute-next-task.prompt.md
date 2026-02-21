---
mode: "agent"
description: "Execute the next pending task from the current phase progress file"
---

Read #file:../docs/phase1-progress.md (or the most recently updated phaseN-progress.md).

Find the **first task marked `[ ]`** (not started).

Execute that single task:

1. Read any existing files that the task touches before editing them
2. Implement exactly what the task description says — no more, no less
3. Follow all conventions in #file:../copilot-instructions.md
4. After implementing, verify the change compiles / has no syntax errors
5. Mark the task as `[x]` in the progress file
6. If the task requires a Docker rebuild (new dependency added), print the exact command to run:
   ```
   docker compose build backend
   ```
   or
   ```
   docker compose build frontend
   ```

After completing the task, report:

- ✅ What was done
- 📁 Files created or modified
- 🔜 What the next task is (just the task ID and title)

Do NOT execute more than one task per run.
