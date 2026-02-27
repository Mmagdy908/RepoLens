---
mode: "agent"
description: "Review progress, fix any broken tasks, and update the progress file"
---

Read #file:../docs/phase1-progress.md (or the most recently updated phaseN-progress.md).

For every task marked `[x]` (done):

1. Verify the file(s) mentioned in the task actually exist at the stated path
2. Do a quick sanity check: does the file contain the function/route/model described?
3. If a file is missing or the implementation doesn't match the description, mark the task `[!]` and add a note explaining what's wrong

For every task marked `[!]` (blocked):

1. Read the error note
2. Fix the underlying issue
3. Mark the task `[x]` once fixed

Report at the end:

- ✅ Tasks verified OK
- 🔧 Tasks fixed
- ❌ Tasks still broken (with reason)
- Overall milestone completion percentage
