---
mode: "agent"
description: "Break a phase plan into granular tasks and write .github/docs/phaseN-progress.md"
---

Read #file:../docs/features.md and the most recent `.github/docs/phaseN-plan.md` that exists but has no matching `.github/docs/phaseN-progress.md` yet.

Create `.github/docs/phaseN-progress.md` with the following structure:

1. **Header** — link to the plan file, last updated date, legend ([ ] · [~] · [x] · [!])
2. **One Milestone per feature** in the phase plan, numbered M1, M2, …
3. **Inside each milestone** — granular tasks numbered T{milestone}.{n}, each task must:
   - Start with the exact file path to create or edit
   - Describe in one sentence exactly what to implement (function signature, route path, model fields, component props, etc.)
   - Be small enough to complete in under 30 minutes
   - Be independently executable by an AI agent with no ambiguity
4. **Phase Completion Checklist** at the end

Rules:

- Follow all conventions in #file:../copilot-instructions.md
- Tasks must be ordered so each one can be executed without depending on a task that comes later in the list
- Do NOT implement anything — this is task breakdown only
- Use the exact task format: `- [ ] **T{M}.{N}** — \`path/to/file\` — description`
