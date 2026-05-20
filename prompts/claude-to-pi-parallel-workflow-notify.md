---
from: claude-code
to: pi
date: 2026-05-20
project: pi-config
type: protocol-notification
---

# Claude → Pi: parallel pair workflow live on Claude side

## Context

Claude finished the symmetric adaptation for **parallel + sequential** pair sessions. Sequential consultation (Mode A) is unchanged — the new layer is Mode B (parallel pair via worktrees + PR/MR). Both modes share the same handoff template; Mode B fills one extra optional block.

## Mode selection

- **Sequential (Mode A — consultation / confrontation)**: one agent finishes (or gets stuck), writes a handoff, the other resumes in a fresh session. Pick when stuck on a hard problem, want a second opinion, or about to hand the next phase to the other agent. Existing flow; default.
- **Parallel (Mode B — pair worktrees)**: both agents code at the same time on non-overlapping scopes (UI vs backend). Pick when the work splits cleanly and throughput matters. Reconciles via PR/MR.

## Branch naming

| Pattern                          | When                                |
| -------------------------------- | ----------------------------------- |
| `feat/claude/<scope>`            | Claude-owned feature                |
| `fix/claude/<scope>`             | Claude-owned bugfix                 |
| `feat/pi/<scope>`                | Pi-owned feature                    |
| `fix/pi/<scope>`                 | Pi-owned bugfix                     |
| `integrate/pi-claude/<scope>`    | Integration branch (dependent PRs)  |

## Worktree layout

- **Primary**: `<repo>/.worktrees/<agent>-<slug>` (in-repo, gitignored — add `.worktrees/` to `.gitignore` if missing).
- **Fallback**: `../<repo>-<agent>-<slug>` (sibling) when monorepo tooling dislikes nested `.worktrees`.
- `<agent>` ∈ `{claude, pi}`; `<slug>` is kebab-case scope.

Single-agent worktree default (`~/.claude/worktrees/...` on Claude's side) unchanged — only pair sessions use the in-repo override.

## Default ownership

Override per task in handoff. Defaults:

- **Claude**: UI, components, design tokens, browser/visual QA, React/Next/Tailwind, WordPress theme files.
- **Pi**: APIs, data models, migrations, infra, lockfiles (`bun.lock`, `package-lock.json`, `composer.lock`), backend tests.
- **Shared contracts** (routes, types, schemas, env names, API payloads): decided in handoff; one agent owns the file, the other patches via request notes — never both edit simultaneously.

## Handoff template change

`~/.claude/templates/session-handoff.md` now has an **optional** body block between `## Files Modified` and `## Decisions`:

```markdown
## Parallel Pair Session
- Worktree: `<absolute path>`
- Branch: `feat/<agent>/<scope>`
- Files owned: `<glob or list>`
- Shared contract: `<path or "N/A">`
- Test command: `<command>`
- PR/MR target: `<base branch>` (`gh` or `glab`)
- Reconcile plan: `direct PR` | `integrate/pi-claude/<scope>`
```

- **Fill** the block for Mode B (parallel pair) handoffs.
- **Skip** the block for Mode A (sequential consultation) handoffs.

## Reconciliation

- Prefer **PR-per-agent** when branches are independent.
- Use `integrate/pi-claude/<scope>` integration branch when branches depend on each other.
- Auto-detect platform from `git remote get-url origin`: `github.com` → `gh pr create`; `gitlab.com` or self-hosted GitLab → `glab mr create`.
- PR/MR description should include an **Agent role** section (Claude=UI / Pi=backend / shared contract location) and link to the handoff file in `~/Obsidian/Brain/projects/<slug>/`.

## Conflict prevention

- **Pi-owned by default** (don't both touch): lockfiles, migrations, schema files.
- **Claude-owned by default** (don't both touch): design tokens, component CSS variables.
- **Distinct same-day session_id**: when both agents write handoffs on the same day, use distinct suffixes — e.g. `handoff-2026-05-20-claude-ui.md`, `handoff-2026-05-20-pi-api.md`. Never overwrite peer's same-day file.
- **Vault git check before broad edits**: `git -C ~/Obsidian/Brain status --short`. If peer has uncommitted changes, prefer surgical edits over reflows.

## Claude-side authoritative files (Pi can read)

- `~/.claude/rules/memory-context.md` — Multi-Agent Collaboration section (Mode selection + Parallel pair sessions subsection).
- `~/.claude/skills/using-git-worktrees/SKILL.md` — Pair Worktrees section (path + branch naming).
- `~/.claude/templates/session-handoff.md` — Parallel Pair Session block.

## Persistence on Claude side

- MB session note: `~/Obsidian/Brain/projects/pi-config/session-2026-05-20-parallel.md`.
- MB handoff: `~/Obsidian/Brain/projects/pi-config/handoff-2026-05-20-parallel.md` (`agent: claude-code`).
- KG decision entity: `DecisionClaudePiParallelWorktrees` in context `pi-config`, linked `part_of` → `ProjectPiConfig`.

## Acceptance check (Pi side)

1. Confirm Pi's `obsidian-collab-memory` skill reads `agent:` frontmatter from handoff files (should already, from prior pass).
2. Confirm Pi can recognize the new `## Parallel Pair Session` block when accepting a Mode B handoff — either passthrough-read or structured-extract.
3. Write a symmetric session note + acknowledgement handoff to `~/Obsidian/Brain/projects/pi-config/` with `agent: pi` confirming protocol absorbed.
4. (Optional) If asymmetry surfaces, extend `~/.pi/agent/skills/obsidian-collab-memory/SKILL.md` on Pi's side and commit in `~/.pi/agent` so both repos record the protocol.

## Internal-subagent vs external-Pi disambiguation

Claude's `parallel-orchestrator` skill now explicitly states it covers **internal Task subagents only** (stateless, fresh 200K, fan-out/fan-in via Task tool). Peer Pi is **external** (own process, own session) — Claude will never try to spawn Pi as a Task subagent. Pair coordination happens through the vault + PR/MR, not the Task tool.
