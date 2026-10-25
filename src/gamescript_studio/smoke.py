"""Exercise the packaged app on a real Windows runner, including Tk startup."""
import json
import platform
from pathlib import Path
import tempfile
import traceback
import tkinter as tk


def run(result_path):
    result = {"status": "failed", "platform": platform.platform(), "checks": []}
    root = None
    try:
        with tempfile.TemporaryDirectory(prefix="portable smoke ") as temporary:
            work = Path(temporary)
            from .model import default_project, save_project, load_project
            from .compiler import export_game
            from .gui import Studio
            project = default_project("tap")
            save_project(project, work / "project.json")
            assert load_project(work / "project.json") == project
            page = export_game(project, work / "playable game")
            assert page.is_file() and (page.parent / "game.js").is_file()
            result["checks"] += ["project roundtrip", "packaged templates export"]
            root = tk.Tk()
            app = Studio(root)
            root.update()
            app.example("dodge")
            assert app.collect()["mode"] == "dodge"
            app.change("add")
            assert len(app.project["rules"]) == 3
            app.undo()
            assert len(app.project["rules"]) == 2
            result["checks"].append("native Tk editor and rule actions")
            root.destroy()
            root = None
        result["status"] = "passed"
    except Exception:
        result["error"] = traceback.format_exc()
    finally:
        if root is not None:
            root.destroy()
        Path(result_path).write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0 if result["status"] == "passed" else 1
