# Pi agent config

Personal Pi coding-agent configuration for `disconnesso`.

## Obsidian / Claude Code collaboration

Skill installed:

- `skills/obsidian-collab-memory/` — file-backed access to the Obsidian Brain vault memory systems used by Claude Code MCP:
  - Memory Bank: `/Users/disconnesso/Obsidian/Brain/projects`
  - Knowledge Graph AIM JSONL: `/Users/disconnesso/Obsidian/Brain/.aim`
  - KG Obsidian mirror: `/Users/disconnesso/Obsidian/Brain/knowledge-graph/entities`
  - Research LLM wiki: `/Users/disconnesso/Obsidian/Brain/research`

Use when asked to accept/write Claude Code handoffs, recall or persist memory, or query the LLM wiki.

## Git hygiene

This repo intentionally excludes:

- `auth.json`
- session transcripts
- volatile bridge state
- env/secrets/log/cache files
