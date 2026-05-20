# Prompt for Claude Code: Pi + Claude parallel worktrees and PR/MR workflow

Paste this into Claude Code when you want it to update its setup for parallel work with Pi.

---

You are Claude Code on Lushano's machine. Update/audit the Claude Code setup so Claude Code and Pi can work in parallel on the same project using git worktrees, shared Obsidian Brain handoffs, and GitHub/GitLab PR/MR workflows.

## Intent

Lushano wants two complementary coding agents:

- **Claude Code / Opus 4.7**: strongest for frontend, UI polish, design systems, browser flows, visual QA, React/Next/Tailwind, WordPress theme UI.
- **Pi / selected model gpt-5.5**: strongest for backend/staff-engineer coding work, APIs, data models, infra, migrations, integration contracts, refactors, tests.

They should be able to work concurrently on separate branches/worktrees, then reconcile through PR/MR or a local integration branch.

## Hard constraints

- Do not let both agents modify the same working tree concurrently.
- Do not let both agents edit the same files unless an explicit contract/handoff says so.
- Use git worktrees for parallel work.
- Use Obsidian Brain Memory Bank handoffs for cross-agent coordination.
- Keep changes minimal and compatible with existing Claude rules/skills.
- No secrets in handoffs, commits, PRs, logs, `.claude`, `.pi`, or Obsidian.
- Read before editing every file you modify.

## Existing shared-memory setup

Pi config:

- `/Users/disconnesso/.pi/agent`
- Pi collaboration skill: `/Users/disconnesso/.pi/agent/skills/obsidian-collab-memory/SKILL.md`
- Pi helper CLI: `/Users/disconnesso/.pi/agent/skills/obsidian-collab-memory/scripts/obsidian_memory.py`
- Existing Claude↔Pi prompt: `/Users/disconnesso/.pi/agent/prompts/claude-code-pi-collaboration.md`

Shared Obsidian Brain:

- Memory Bank: `/Users/disconnesso/Obsidian/Brain/projects`
- Knowledge Graph/AIM: `/Users/disconnesso/Obsidian/Brain/.aim`
- KG mirror: `/Users/disconnesso/Obsidian/Brain/knowledge-graph/entities`
- Research wiki: `/Users/disconnesso/Obsidian/Brain/research`

Tools available on this machine:

- `git`
- `gh` for GitHub PRs
- `glab` for GitLab MRs

## Collaboration workflow to encode

### 1. Task split

Before spawning parallel work, create a clear split:

- **Backend/API/data/infra/tests** → Pi worktree.
- **Frontend/UI/design/browser QA** → Claude Code worktree.
- Shared contract files, routes, types, schemas, env names, and API payloads must be decided first.

If the split is unclear, stop and propose a contract before coding.

### 2. Worktree layout

Use a sibling worktree directory by default:

```bash
<repo>/.worktrees/<agent>-<slug>
```

Examples:

```bash
git worktree add .worktrees/pi-api feature/pi-api-contract
git worktree add .worktrees/claude-ui feature/claude-ui-polish
```

If the repo or tooling dislikes nested `.worktrees`, use sibling paths:

```bash
../<repo-name>-pi-api
../<repo-name>-claude-ui
```

Always record exact worktree paths in the handoff.

### 3. Branch naming

Use predictable branch names:

- Pi: `feat/pi/<scope>` or `fix/pi/<scope>`
- Claude: `feat/claude/<scope>` or `fix/claude/<scope>`
- Integration: `integrate/pi-claude/<scope>` if needed

### 4. Contract-first handoff

Before concurrent coding, write a Memory Bank handoff in the project slug:

```text
/Users/disconnesso/Obsidian/Brain/projects/<project>/handoff-YYYY-MM-DD-parallel-<scope>.md
```

It must include:

- Goal
- Agent split
- Worktree paths
- Branch names
- Files each agent owns
- Shared contract/interface
- Test commands
- Conflict boundaries
- PR/MR target branch
- Reconcile plan

### 5. During parallel work

Each agent must:

- Work only in its assigned worktree.
- Commit coherent changes on its branch.
- Keep a concise session note/handoff when pausing.
- Avoid broad formatting across files owned by the other agent.
- Run relevant tests before handing off.

Claude Code should expect Pi to leave handoffs with `agent: pi`. Claude should leave handoffs with `agent: claude-code`.

### 6. Reconciliation

Preferred reconciliation options:

1. **PR/MR per agent branch** into the project’s normal target branch if independent.
2. **Integration branch** if branches depend on each other:
   - Create `integrate/pi-claude/<scope>` from target branch.
   - Merge/cherry-pick Pi branch.
   - Merge/cherry-pick Claude branch.
   - Resolve conflicts.
   - Run full test/build suite.
   - Open one PR/MR from integration branch.

Use `gh` for GitHub and `glab` for GitLab when authenticated. If not authenticated, push branches and print exact PR/MR URL/commands for the user.

### 7. PR/MR content

PR/MR description must include:

- Agent roles:
  - Pi: backend/API/etc.
  - Claude Code: frontend/UI/etc.
- Worktree/branch summary.
- Contract decisions.
- Tests run.
- Known risks/open items.
- Handoff link/path in Obsidian Brain.

### 8. Conflict prevention rules

- If Claude needs backend changes, ask Pi or write an explicit backend request in the handoff.
- If Pi needs UI changes, ask Claude or write an explicit UI request in the handoff.
- If a shared file must be edited by both agents, nominate one owner and require the other to edit through a patch/request.
- Lockfiles are high-conflict: one agent owns dependency changes unless explicitly coordinated.
- Migrations/schema changes are backend-owned by default.
- Component styling/design tokens are frontend-owned by default.

## Files to audit/update

Read first:

1. `/Users/disconnesso/.claude/rules/workflow.md`
2. `/Users/disconnesso/.claude/rules/memory-context.md`
3. `/Users/disconnesso/.claude/rules/multi-model.md`
4. `/Users/disconnesso/.claude/skills/using-git-worktrees/SKILL.md`
5. `/Users/disconnesso/.claude/skills/parallel-orchestrator/SKILL.md`
6. `/Users/disconnesso/.claude/skills/session-summary/SKILL.md`
7. `/Users/disconnesso/.claude/templates/session-handoff.md`
8. `/Users/disconnesso/.pi/agent/prompts/claude-code-pi-collaboration.md`

Then decide minimal edits. Likely targets:

- `using-git-worktrees/SKILL.md`: add Pi/Claude ownership and branch naming.
- `parallel-orchestrator/SKILL.md`: distinguish subagents vs external peer agent Pi; require worktrees for peer parallelism.
- `memory-context.md`: add parallel pair-session handoff protocol.
- `session-summary/SKILL.md`: include worktree/branch/PR-MR info in pair handoffs.
- Optional new skill: `pi-parallel-worktrees` if the workflow is too large for existing files.

## Expected output

1. Audit summary: what already supports worktrees/parallelism, what is missing for Pi.
2. Minimal edit plan.
3. Apply approved/minimal edits.
4. Validate:
   - No secrets added.
   - `rg -n "Pi|worktree|PR|MR|agent: pi|parallel" ~/.claude/rules ~/.claude/skills ~/.claude/templates` shows intended instructions.
   - Skill frontmatter is valid.
5. Persist a `pi-config` Memory Bank session note and handoff summarizing changes.
6. Store durable decisions in KG context `pi-config`.

## Acceptance criteria

- Claude Code can intentionally split a task with Pi by backend/frontend ownership.
- Both agents use separate worktrees and branches.
- Claude Code can open GitHub PRs or GitLab MRs when `gh`/`glab` auth is available.
- Handoffs capture branch, worktree, ownership, test, and reconciliation state.
- The protocol does not disrupt existing Claude subagent/team workflows.

Start by reading the files above, then produce the audit and edit plan.
