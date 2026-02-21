---
mode: "agent"
description: "Plan the next Phase from features.md and write docs/phaseN-plan.md"
---

Read #file:../docs/features.md carefully.

Identify the **next phase that has no plan file yet** by checking which of these files exist:

- `docs/phase1-plan.md`
- `docs/phase2-plan.md`
- `docs/phase3-plan.md`

For that phase, create `docs/phaseN-plan.md` (where N is the phase number) containing:

1. **Header** — phase name, goal, timeline, status (🟡 Planning)
2. **What We Are Building** — one paragraph + a flow diagram in plain text showing how the pieces connect
3. **Feature Breakdown** — one section per feature in that phase, each containing:
   - What it is (1–2 sentences)
   - The exact files to create or modify (with paths relative to repo root)
   - The key functions/classes/routes to implement
   - Any new npm or Python packages required
4. **Dependencies** — full list of new packages for backend and frontend
5. **Build Order** — numbered critical path (what must be done before what)
6. **Definition of Done** — checkbox list of acceptance criteria

Rules:

- Follow all conventions in #file:../copilot-instructions.md
- Do NOT start implementing anything — this is planning only
- Keep each feature section concise; defer implementation details to the progress file
- If a feature depends on a previous phase feature not yet built, call it out explicitly as a prerequisite
- Do Not assume or take any decisions not explicitly stated in the features.md — if something is ambiguous, ask the user for clarification before writing the plan file
