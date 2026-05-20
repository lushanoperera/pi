---
name: obsidian-collab-memory
description: Use for Obsidian Brain vault access, Claude Code handoffs, memory-bank/project memory, knowledge graph/AIM memory, research wiki/LLM wiki, remember/recall workflows, and collaborative pair sessions with Claude Code.
---

# Obsidian Collaborative Memory

Pi has no built-in MCP, but Claude Code's MCP memory systems are file-backed in the Obsidian Brain vault. Use the same canonical files directly so Pi and Claude Code collaborate safely.

## Canonical locations

- Vault: `/Users/disconnesso/Obsidian/Brain`
- Memory Bank MCP root: `/Users/disconnesso/Obsidian/Brain/projects`
- Knowledge Graph MCP root: `/Users/disconnesso/Obsidian/Brain/.aim`
- Knowledge Graph Obsidian mirror: `/Users/disconnesso/Obsidian/Brain/knowledge-graph/entities`
- Research / LLM wiki: `/Users/disconnesso/Obsidian/Brain/research`
- Auto memory index: `/Users/disconnesso/Obsidian/Brain/auto-memory/MEMORY.md`
- Claude handoff template: `/Users/disconnesso/.claude/templates/session-handoff.md`
- KG mirror sync hook: `/Users/disconnesso/.claude/hooks/kg-to-obsidian.js --sync`

## Load order

When user asks to recall context, resume a Claude Code session, accept a handoff, or work with memory:

1. Read `auto-memory/MEMORY.md` for L0/L1 context and active-project pointers.
2. Determine project slug from user/cwd. Prefer existing folder names under `projects/`.
3. Read the latest relevant `projects/<slug>/handoff-*.md` and/or `session-*.md`.
4. Search KG mirrors in `knowledge-graph/entities/` for durable decisions/blockers/patterns.
5. For external-content knowledge, read `research/CLAUDE.md`, then `research/index.md`, then follow `[[backlinks]]`.

Token discipline: use `rg`/file lists first, then `read` only targeted files.

## Memory routing

- **Memory Bank / project continuity**: write Markdown in `projects/<slug>/`.
  - Sessions: `session-YYYY-MM-DD-<id>.md`
  - Handoffs: `handoff-YYYY-MM-DD-<id>.md`
- **Knowledge Graph / durable structured facts**: append JSONL records in `.aim/memory-<context>.jsonl`, then update the KG Markdown mirror (helper does targeted sync by default).
- **Research / LLM wiki**: external source knowledge only. Read `research/CLAUDE.md` before edits. Update `research/index.md` + `research/log.md`; commit vault changes if requested or after meaningful ingest.
- **Auto-memory index**: do not edit casually. Only curate when explicitly asked or when consolidating stable global facts.

## Knowledge Graph file format

Each `.aim/*.jsonl` file starts with:

```json
{"type":"_aim","source":"mcp-knowledge-graph"}
```

Entity record:

```json
{"type":"entity","name":"DecisionExample","entityType":"decision","observations":["[valid_from:2026-05-20] Chose X over Y because ..."]}
```

Relation record:

```json
{"type":"relation","from":"DecisionExample","to":"ProjectPiConfig","relationType":"part_of"}
```

After writing KG JSONL with the helper, it updates only the touched `knowledge-graph/entities/*.md` pages. For full regeneration only, run:

```bash
bun /Users/disconnesso/.claude/hooks/kg-to-obsidian.js --sync
```

Prefer not to hand-edit generated entity Markdown.

## Handoff protocol with Claude Code

When asked to accept a handoff:

1. Find newest handoff for project: `ls -t /Users/disconnesso/Obsidian/Brain/projects/<slug>/handoff-*.md | head`.
2. Read it and follow “Next Session Should”.
3. Avoid files listed in “Do NOT Re-Read” unless needed.
4. Add a Pi session note while working if decisions are made.

When ending a pair session or preparing Claude Code to continue, write a handoff with:

- Goal
- Outcome with status: `COMPLETED`, `PARTIAL`, or `BLOCKED`
- Files Modified
- Decisions in IF/THEN/BECAUSE form
- Open Items: CONFIRMED / ASSUMED / OPEN
- Do NOT Re-Read
- Next Session Should

Include `agent: pi` in frontmatter or body so Claude Code knows source.

## Collaborative safety

- Be append-friendly: add dated notes instead of overwriting Claude Code's work.
- Preserve Obsidian `[[wikilinks]]` and YAML frontmatter.
- Resolve contradictions with temporal markers: `[valid_from:YYYY-MM-DD]` and `[ended:YYYY-MM-DD]`.
- Never put secrets into Obsidian notes or git-tracked Pi config.
- Before destructive edits in the vault, check git status in `/Users/disconnesso/Obsidian/Brain`.

## Helper CLI

Use the bundled helper for common operations:

```bash
python3 /Users/disconnesso/.pi/agent/skills/obsidian-collab-memory/scripts/obsidian_memory.py latest --project pi-config
python3 /Users/disconnesso/.pi/agent/skills/obsidian-collab-memory/scripts/obsidian_memory.py search "DecisionMemoryConvention"
python3 /Users/disconnesso/.pi/agent/skills/obsidian-collab-memory/scripts/obsidian_memory.py kg-store --context pi-config --name DecisionFoo --type decision --obs "[valid_from:2026-05-20] Foo"
python3 /Users/disconnesso/.pi/agent/skills/obsidian-collab-memory/scripts/obsidian_memory.py kg-link --context pi-config --from DecisionFoo --to ProjectPiConfig --type part_of
```

See `references/memory-systems.md` for tool-equivalent semantics.
