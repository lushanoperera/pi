# Prompt for Claude Code: integrate Pi collaboration via Obsidian Brain

Paste this into Claude Code from any working directory, preferably `~/.claude` or the project where you want the collaboration protocol installed.

---

You are Claude Code running on Lushano's machine. Your task is to audit and update the Claude Code setup so it can collaborate cleanly with Pi (`@earendil-works/pi-coding-agent`) through the shared Obsidian Brain vault, including structured handoff pair sessions.

## Hard constraints

- Do **not** install a Pi MCP server or invent a new sync backend. Pi core intentionally has no MCP.
- Use the existing Obsidian Brain vault as the shared source of truth.
- Keep changes minimal and tier-aware: update existing rules/skills where appropriate; only create a new skill/rule if it reduces duplication.
- Do **not** store secrets in Obsidian, `.claude`, or `.pi` git repos.
- Preserve existing memory routing conventions and temporal markers.
- Read before editing every file you modify.
- Show a short plan before edits if changes touch more than 2 files.

## Shared-memory facts already established

Pi has been configured at:

- Pi config repo: `/Users/disconnesso/.pi/agent`
- Pi collaboration skill: `/Users/disconnesso/.pi/agent/skills/obsidian-collab-memory/SKILL.md`
- Pi helper CLI: `/Users/disconnesso/.pi/agent/skills/obsidian-collab-memory/scripts/obsidian_memory.py`
- Pi git remote: `https://github.com/lushanoperera/pi.git`

Claude Code MCP memory roots:

- Memory Bank root: `/Users/disconnesso/Obsidian/Brain/projects`
- Knowledge Graph AIM JSONL: `/Users/disconnesso/Obsidian/Brain/.aim`
- KG Obsidian mirror: `/Users/disconnesso/Obsidian/Brain/knowledge-graph/entities`
- Research / LLM wiki: `/Users/disconnesso/Obsidian/Brain/research`
- Handoff template: `/Users/disconnesso/.claude/templates/session-handoff.md`

Existing Pi setup notes:

- Session: `/Users/disconnesso/Obsidian/Brain/projects/pi-config/session-2026-05-20-pi-obsidian-collab.md`
- Handoff: `/Users/disconnesso/Obsidian/Brain/projects/pi-config/handoff-2026-05-20-pi-obsidian-collab.md`
- KG entities: `ProjectPiConfig`, `DecisionPiObsidianCollabMemory`

## Files to study first

Read these before proposing edits:

1. `/Users/disconnesso/.pi/agent/skills/obsidian-collab-memory/SKILL.md`
2. `/Users/disconnesso/.pi/agent/skills/obsidian-collab-memory/references/memory-systems.md`
3. `/Users/disconnesso/.claude/rules/memory-context.md`
4. `/Users/disconnesso/.claude/rules/workflow.md`
5. `/Users/disconnesso/.claude/rules/mcp-efficiency.md`
6. `/Users/disconnesso/.claude/skills/context-load/SKILL.md`
7. `/Users/disconnesso/.claude/skills/session-summary/SKILL.md`
8. `/Users/disconnesso/.claude/skills/recall/SKILL.md`
9. `/Users/disconnesso/.claude/skills/remember/SKILL.md`
10. `/Users/disconnesso/.claude/skills/revise-claude-setup/SKILL.md`
11. `/Users/disconnesso/.claude/templates/session-handoff.md`

Then inspect `~/.claude/CLAUDE.md` only to decide whether it needs an index pointer.

## Desired collaboration model

### Shared source of truth

Claude Code should continue to use MCP tools where available:

- Memory Bank MCP for `projects/<slug>/*.md`
- Knowledge Graph MCP for AIM entities/relations
- Research wiki files for external-content knowledge

Pi reads and writes the same files directly because Pi has no MCP. Therefore Claude Code should treat Pi as a peer agent that may leave Markdown handoffs and AIM/KG facts in the vault.

### Pair-session protocol

When the user says any of:

- “handoff to Pi”
- “let Pi continue”
- “prepare pair session with Pi”
- “Claude ↔ Pi handoff”
- “resume from Pi”

Claude Code should use this protocol.

#### Accepting a handoff from Pi

1. Detect project slug from cwd/user request, or ask if ambiguous.
2. Load current memory context:
   - L0/L1 via `auto-memory/MEMORY.md` already available in global context.
   - Read the newest relevant `projects/<slug>/handoff-*.md` with `agent: pi` if present.
   - Read latest `projects/<slug>/session-*.md` only if handoff is insufficient.
   - Search KG for project decisions/blockers if needed.
3. Follow “Next Session Should”.
4. Respect “Do NOT Re-Read” unless the file is needed for correctness.
5. If the Pi handoff is stale/conflicting, use temporal markers or write an explicit correction note rather than silently overwriting.

#### Handing off to Pi

Write a Claude-compatible handoff to Memory Bank:

- Path: `/Users/disconnesso/Obsidian/Brain/projects/<slug>/handoff-YYYY-MM-DD-<sessionid>.md`
- Include either YAML frontmatter or body marker: `agent: claude-code`
- Use the existing template sections exactly:
  - Goal
  - Outcome with `STATUS: COMPLETED | PARTIAL | BLOCKED`
  - Files Modified
  - Decisions in `IF/THEN/BECAUSE` or `IF/THEN/BUT` form
  - Open Items with `CONFIRMED`, `ASSUMED`, `OPEN`
  - Do NOT Re-Read
  - Next Session Should
- Add precise first action for Pi.
- Keep it compact and operational; no verbose transcript summary.

Also persist durable facts:

- Decisions/blockers/patterns → KG via `aim_memory_store`/`aim_memory_link` using project context.
- Project continuity/session state → Memory Bank Markdown.
- External research → Research wiki only, following `research/CLAUDE.md`.

### Conflict and write safety

- Prefer append-only dated notes over rewriting another agent’s notes.
- If both agents worked on the same file, document actual file state and commit/hash if available.
- If a handoff contradicts current code, mark it `ASSUMED` or `OPEN`; verify before acting.
- Before broad Obsidian edits, check `git -C /Users/disconnesso/Obsidian/Brain status --short`.
- Avoid full KG mirror sync unless necessary; it can dirty many generated Markdown files. MCP writes plus existing hooks are preferred.

## Audit and adjustment task

After studying the files, decide the smallest correct changes. Likely candidates:

1. `rules/memory-context.md`
   - Add Pi as a peer/client of the same Obsidian-backed memory stack.
   - Add pair-handoff trigger language and collision-safety rules.

2. `skills/session-summary/SKILL.md`
   - Ensure handoff generation includes `agent: claude-code` and is explicitly Pi-readable.
   - Add “handoff to Pi” as a trigger/use-case if missing.
   - Ensure “Do NOT Re-Read” and “Next Session Should” are treated as mandatory for pair handoffs.

3. `skills/context-load/SKILL.md`
   - Add handling for `agent: pi` handoff files.
   - Prioritize latest handoff over generic session summaries when resuming pair sessions.

4. `skills/recall/SKILL.md`
   - Mention Pi-authored Memory Bank/KG entries are first-class search results.
   - Avoid duplicate retrieval paths if recall-engine already covers them.

5. `skills/revise-claude-setup/SKILL.md`
   - Add Pi collaboration setup as a known workflow/process target if relevant.

6. Optional: create `~/.claude/skills/pi-collaboration/SKILL.md`
   - Only if this is cleaner than spreading too much into existing skills.
   - It should be short and should delegate to existing `/context-load`, `/session-summary`, `/recall`, `/remember`.

7. Optional: update `~/.claude/CLAUDE.md`
   - Only add a one-line pointer if a new rule/skill needs discoverability.

## Expected output from you

1. Brief audit summary: what already supports Pi collaboration and what was missing.
2. Proposed edit plan with exact target files.
3. Apply the approved/minimal edits.
4. Run lightweight validation:
   - No secrets added.
   - Skill frontmatter valid enough for Claude Code.
   - `rg -n "Pi|pi-collaboration|agent: pi|handoff to Pi" ~/.claude/rules ~/.claude/skills ~/.claude/CLAUDE.md` shows the installed hooks/instructions.
5. Persist a session note and handoff in Memory Bank project `pi-config` summarizing what changed.
6. Store any durable decision in KG context `pi-config`.

## Acceptance criteria

- Claude Code can accept a Pi handoff without needing explanation from the user.
- Claude Code can prepare a Pi handoff at session end using the established template.
- Existing `/context-load`, `/session-summary`, `/recall`, `/remember`, and `/revise-claude-setup` behavior remains intact.
- No new secret-bearing files are tracked or exposed.
- The protocol is documented in one obvious place and referenced from existing memory/session skills.

Start now by reading the files listed above and producing the audit + edit plan.
