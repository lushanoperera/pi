#!/usr/bin/env python3
"""Small file-backed helper for the Obsidian Brain memory systems.

Pi has no MCP; this script performs the safe subset of Memory Bank and
mcp-knowledge-graph operations directly on their canonical files.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

VAULT = Path(os.environ.get("OBSIDIAN_VAULT_ROOT", "/Users/disconnesso/Obsidian/Brain"))
PROJECTS = VAULT / "projects"
AIM = VAULT / ".aim"
KG_MD = VAULT / "knowledge-graph" / "entities"
SYNC_HOOK = Path("/Users/disconnesso/.claude/hooks/kg-to-obsidian.js")


def slugify(value: str) -> str:
    value = value.strip().replace(" ", "-")
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "global"


def context_file(context: str | None) -> Path:
    if not context or context == "default":
        return AIM / "memory.jsonl"
    return AIM / f"memory-{slugify(context)}.jsonl"


def ensure_aim_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    marker = {"type": "_aim", "source": "mcp-knowledge-graph"}
    if not path.exists() or path.stat().st_size == 0:
        path.write_text(json.dumps(marker, separators=(",", ":")) + "\n")
        return
    first = path.read_text(errors="replace").splitlines()[0] if path.exists() else ""
    try:
        data = json.loads(first)
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"Refusing to write {path}: first line is not JSON") from exc
    if data.get("type") != "_aim" or data.get("source") != "mcp-knowledge-graph":
        raise SystemExit(f"Refusing to write {path}: missing _aim safety marker")


def append_jsonl(path: Path, record: dict) -> None:
    ensure_aim_file(path)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def safe_filename(value: str) -> str:
    return re.sub(r"[-]{2,}", "-", re.sub(r"[/\\:?*\"<>|]", "-", value)).strip("-")


def load_graph() -> tuple[dict[str, dict], list[dict]]:
    entities: dict[str, dict] = {}
    relations: list[dict] = []
    for path in AIM.glob("memory*.jsonl"):
        for line in path.read_text(errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            if rec.get("type") == "entity":
                item = entities.setdefault(
                    rec.get("name", "unknown"),
                    {"entityType": rec.get("entityType", "unknown"), "observations": []},
                )
                seen = set(item["observations"])
                for obs in rec.get("observations", []):
                    if obs not in seen:
                        item["observations"].append(obs)
                        seen.add(obs)
            elif rec.get("type") == "relation":
                relations.append(rec)
    return entities, relations


def render_entity(name: str, entity: dict, relations: list[dict]) -> str:
    lines = [
        "---",
        "type: entity",
        f"entityType: {entity.get('entityType', 'unknown')}",
        "source: knowledge-graph",
        f"last_updated: {datetime.now().isoformat()}",
        "---",
        "",
        f"# {name}",
        "",
        "## Observations",
        "",
    ]
    for obs in entity.get("observations", []):
        lines.append(f"- {obs}")
    related = [r for r in relations if r.get("from") == name or r.get("to") == name]
    if related:
        lines.extend(["", "## Relations", ""])
        seen: set[tuple[str, str, str]] = set()
        for rel in related:
            outgoing = rel.get("from") == name
            target = rel.get("to") if outgoing else rel.get("from")
            rtype = rel.get("relationType", "relates_to")
            key = (str(target), str(rtype), "out" if outgoing else "in")
            if key in seen:
                continue
            seen.add(key)
            suffix = "" if outgoing else ", incoming"
            lines.append(f"- [[{safe_filename(str(target))}|{target}]] ({rtype}{suffix})")
    return "\n".join(lines) + "\n"


def sync_kg(targets: list[str] | None = None, full: bool = False) -> None:
    """Sync KG markdown. Targeted by default to avoid dirtying the whole vault."""
    if full:
        if SYNC_HOOK.exists():
            subprocess.run(["bun", str(SYNC_HOOK), "--sync"], check=False)
        return
    if not targets:
        return
    entities, relations = load_graph()
    KG_MD.mkdir(parents=True, exist_ok=True)
    for name in dict.fromkeys(targets):
        entity = entities.get(name)
        if not entity:
            continue
        (KG_MD / f"{safe_filename(name)}.md").write_text(render_entity(name, entity, relations), encoding="utf-8")


def cmd_projects(_args: argparse.Namespace) -> int:
    for p in sorted(PROJECTS.iterdir() if PROJECTS.exists() else []):
        if p.is_dir() and not p.name.startswith("."):
            print(p.name)
    return 0


def cmd_files(args: argparse.Namespace) -> int:
    root = PROJECTS / args.project
    if not root.exists():
        raise SystemExit(f"No project: {args.project}")
    for p in sorted(root.glob("*.md")):
        print(p.name)
    return 0


def cmd_latest(args: argparse.Namespace) -> int:
    root = PROJECTS / args.project
    if not root.exists():
        raise SystemExit(f"No project: {args.project}")
    patterns = [f"{args.kind}-*.md"] if args.kind != "any" else ["handoff-*.md", "session-*.md"]
    files: list[Path] = []
    for pat in patterns:
        files.extend(root.glob(pat))
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    for p in files[: args.limit]:
        print(p)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    paths = [PROJECTS, KG_MD]
    if args.research:
        paths.append(VAULT / "research")
    if args.project:
        paths = [PROJECTS / args.project, KG_MD]
    cmd = ["rg", "-n", "--hidden", "--glob", "!.git", "--glob", "!observations/**", args.query, *map(str, paths)]
    return subprocess.run(cmd, check=False).returncode


def cmd_kg_store(args: argparse.Namespace) -> int:
    observations = args.obs or []
    if args.stdin:
        observations.append(sys.stdin.read().strip())
    if not observations:
        raise SystemExit("kg-store needs --obs or --stdin")
    record = {
        "type": "entity",
        "name": args.name,
        "entityType": args.type,
        "observations": observations,
    }
    append_jsonl(context_file(args.context), record)
    if args.sync:
        sync_kg([args.name], full=args.full_sync)
    print(context_file(args.context))
    return 0


def cmd_kg_link(args: argparse.Namespace) -> int:
    record = {"type": "relation", "from": args.from_, "to": args.to, "relationType": args.type}
    append_jsonl(context_file(args.context), record)
    if args.sync:
        sync_kg([args.from_, args.to], full=args.full_sync)
    print(context_file(args.context))
    return 0


def cmd_handoff(args: argparse.Namespace) -> int:
    project = slugify(args.project)
    root = PROJECTS / project
    root.mkdir(parents=True, exist_ok=True)
    sid = args.id or datetime.now().strftime("%H%M%S")
    path = root / f"handoff-{date.today().isoformat()}-{slugify(sid)}.md"
    body = sys.stdin.read().strip() if args.stdin else ""
    content = f"""---
agent: pi
project: {project}
date: {date.today().isoformat()}
---

# Session Handoff: {date.today().isoformat()} — {project}

## Goal
{args.goal or '[fill]'}

## Outcome
STATUS: {args.status}
{args.outcome or '[fill]'}

## Files Modified
{args.files or '- [fill]'}

## Decisions
{args.decisions or '- [fill]'}

## Open Items
{args.open or '- OPEN: [fill]'}

## Do NOT Re-Read
{args.skip or '[fill]'}

## Next Session Should
{args.next or '1. [fill]'}
"""
    if body:
        content += "\n## Notes\n" + body + "\n"
    path.write_text(content, encoding="utf-8")
    print(path)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("projects", help="List Memory Bank projects")
    s.set_defaults(func=cmd_projects)

    s = sub.add_parser("files", help="List project Markdown files")
    s.add_argument("--project", required=True)
    s.set_defaults(func=cmd_files)

    s = sub.add_parser("latest", help="Show latest handoff/session files for a project")
    s.add_argument("--project", required=True)
    s.add_argument("--kind", choices=["handoff", "session", "any"], default="any")
    s.add_argument("--limit", type=int, default=5)
    s.set_defaults(func=cmd_latest)

    s = sub.add_parser("search", help="Search projects and KG markdown")
    s.add_argument("query")
    s.add_argument("--project")
    s.add_argument("--research", action="store_true")
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("kg-store", help="Append KG entity observations")
    s.add_argument("--context", default="default")
    s.add_argument("--name", required=True)
    s.add_argument("--type", default="fact")
    s.add_argument("--obs", action="append")
    s.add_argument("--stdin", action="store_true")
    s.add_argument("--no-sync", dest="sync", action="store_false", default=True)
    s.add_argument("--full-sync", action="store_true", help="Run Claude's full KG mirror sync hook")
    s.set_defaults(func=cmd_kg_store)

    s = sub.add_parser("kg-link", help="Append KG relation")
    s.add_argument("--context", default="default")
    s.add_argument("--from", dest="from_", required=True)
    s.add_argument("--to", required=True)
    s.add_argument("--type", default="relates_to")
    s.add_argument("--no-sync", dest="sync", action="store_false", default=True)
    s.add_argument("--full-sync", action="store_true", help="Run Claude's full KG mirror sync hook")
    s.set_defaults(func=cmd_kg_link)

    s = sub.add_parser("handoff", help="Create Claude-compatible project handoff")
    s.add_argument("--project", required=True)
    s.add_argument("--id")
    s.add_argument("--status", choices=["COMPLETED", "PARTIAL", "BLOCKED"], default="PARTIAL")
    s.add_argument("--goal")
    s.add_argument("--outcome")
    s.add_argument("--files")
    s.add_argument("--decisions")
    s.add_argument("--open")
    s.add_argument("--skip")
    s.add_argument("--next")
    s.add_argument("--stdin", action="store_true")
    s.set_defaults(func=cmd_handoff)

    return p


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
