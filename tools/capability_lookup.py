"""Read-only task-to-repository lookup for every Money HQ coding agent.

This prints candidates. It never installs, executes, or downloads their code.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from assets.web_capability_library.library import search_capabilities  # noqa: E402


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Find repo capabilities by task words")
    parser.add_argument("query", nargs="?", default="", help="E.g. landing, animation, form, QA")
    parser.add_argument("--project", default=None)
    parser.add_argument("--category", default=None)
    args = parser.parse_args()
    matches = search_capabilities(
        query=args.query or None, project=args.project, category=args.category
    )
    for item in matches:
        print(f"{item['id']} | {item['name']} | {item['reuse_mode']}")
        print(f"  {item['url']}")
        print(f"  USE: {item['provides']}")
        print(f"  LIMIT: {item.get('commercial_use', 'Verify before use')}")
    if not matches:
        print("No catalog match. Inspect the task and source directly; do not infer installation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
