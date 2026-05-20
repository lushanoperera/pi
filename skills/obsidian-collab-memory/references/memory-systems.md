# Memory systems reference

## Claude Code MCP configuration studied

Claude Code global MCP servers in `/Users/disconnesso/.claude.json`:

```json
"knowledge-graph": {
  "type": "stdio",
  "command": "bunx",
  "args": ["--bun", "mcp-knowledge-graph@latest", "--memory-path", "/Users/disconnesso/Obsidian/Brain/.aim"],
  "alwaysLoad": true
}
```

```json
"memory-bank": {
  "type": "stdio",
  "command": "bunx",
  "args": ["--bun", "@allpepper/memory-bank-mcp@latest"],
  "alwaysLoad": true,
  "env": {"MEMORY_BANK_ROOT": "/Users/disconnesso/Obsidian/Brain/projects"}
}
```

Pi core intentionally has no MCP. Equivalent access is direct file operations against the same vault.

## Memory Bank MCP semantics

Root: `/Users/disconnesso/Obsidian/Brain/projects`

MCP tools and Pi equivalents:

- `list_projects` → list directories under `projects/`
- `list_project_files(project)` → `find projects/<project> -maxdepth 1 -type f`
- `memory_bank_read(project, file)` → `read projects/<project>/<file>`
- `memory_bank_write(project, file, content)` → `write` a new Markdown file
- `memory_bank_update(project, file, content)` → `edit` or append to existing Markdown

Conventions:

- Project slug is directory name.
- Session and handoff files are Markdown and safe for both Pi and Claude Code.
- Use project-local notes for state that another agent needs to resume.

## Knowledge Graph MCP semantics

Root: `/Users/disconnesso/Obsidian/Brain/.aim`

MCP tools and Pi equivalents:

- `aim_memory_store({context, entities})` → append `entity` JSONL records to `.aim/memory-<context>.jsonl`
- `aim_memory_add_facts({entityName, facts})` → append another `entity` record with same name and new observations; renderer merges observations
- `aim_memory_link({from,to,relationType})` → append a `relation` JSONL record
- `aim_memory_search(query)` → `rg` in `.aim/*.jsonl` or generated `knowledge-graph/entities/*.md`
- `aim_memory_get(name)` → read exact generated entity Markdown or grep JSONL
- `aim_memory_list_stores()` → list `.aim/memory*.jsonl`
- `aim_memory_forget/remove_facts/unlink` → prefer MCP/Claude Code; if direct edit is necessary, edit JSONL carefully and run sync

Context mapping:

- Default/master: `.aim/memory.jsonl`
- Named context `foo`: `.aim/memory-foo.jsonl`

After writes, use the helper's targeted sync (default). Full regeneration is available when needed:

```bash
python3 /Users/disconnesso/.pi/agent/skills/obsidian-collab-memory/scripts/obsidian_memory.py kg-store --full-sync ...
# or
bun /Users/disconnesso/.claude/hooks/kg-to-obsidian.js --sync
```

## Research / LLM wiki semantics

Root: `/Users/disconnesso/Obsidian/Brain/research`

Read first:

1. `research/CLAUDE.md`
2. `research/index.md`

Rules:

- External-content knowledge only; not user/project memory.
- Navigate by `[[backlinks]]`, not broad crawling.
- New pages require frontmatter: `type`, `source_ref`, `tags`, `related`, `last_updated`.
- Update `index.md` and append to `log.md` for meaningful ingest/query persistence.

## Handoff compatibility

Use Claude's template fields exactly so either agent can resume:

- Goal
- Outcome
- Files Modified
- Decisions
- Open Items
- Do NOT Re-Read
- Next Session Should

Prefer filenames:

- `handoff-YYYY-MM-DD-<shortid>.md`
- `session-YYYY-MM-DD-<shortid>.md`
