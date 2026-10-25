import argparse
import json
import sys
from .model import default_project, load_project, save_project
from .compiler import export_game


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Visual mini-game compiler: export portable HTML/JavaScript."
    )
    sub = p.add_subparsers(dest="command")
    sub.add_parser("gui", help="Open the visual editor")
    new = sub.add_parser("new", help="Write a starter project")
    new.add_argument("path")
    new.add_argument("--mode", choices=["tap", "catch", "dodge"], default="catch")
    check = sub.add_parser("validate")
    check.add_argument("project")
    export = sub.add_parser("export")
    export.add_argument("project")
    export.add_argument("output")
    args = p.parse_args(argv)
    try:
        if args.command in (None, "gui"):
            from .gui import main as gui

            gui()
        elif args.command == "new":
            from pathlib import Path

            if Path(args.path).exists():
                raise FileExistsError("Project already exists")
            save_project(default_project(args.mode), args.path)
        elif args.command == "validate":
            print(json.dumps({"valid": True, "title": load_project(args.project)["title"]}))
        elif args.command == "export":
            print(export_game(load_project(args.project), args.output))
        return 0
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
