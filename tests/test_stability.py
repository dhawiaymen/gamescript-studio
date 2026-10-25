import copy
import pytest
from gamescript_studio.model import default_project, validate, ProjectError
from test_compiler import run_js


def test_integer_valued_json_fields_are_normalized():
    project = default_project()
    project["width"] = 480.0
    result = validate(project)
    assert type(result["width"]) is int
    assert project["width"] == 480.0


def test_huge_integer_is_a_user_error():
    project = default_project()
    project["width"] = 10 ** 1000
    with pytest.raises(ProjectError):
        validate(project)


def test_runtime_does_not_retain_mutable_input(tmp_path):
    run_js(tmp_path, default_project("tap"), "config.rules.length=0; g.step({tap:true},0); assert.equal(g.snapshot().score,1);")


@pytest.mark.gui
def test_editor_preserves_changes_and_rule_selection(monkeypatch):
    import tkinter as tk
    from gamescript_studio.gui import Studio
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("No display")
    try:
        app = Studio(root)
        app.vars["title"].set("Unsaved project")
        monkeypatch.setattr("gamescript_studio.gui.messagebox.askyesno", lambda *a, **k: False)
        app.example("tap")
        assert app.vars["title"].get() == "Unsaved project"
        app.change("add")
        assert app.tree.selection() == ("2",)
        app.change("up")
        assert app.tree.selection() == ("1",)
        monkeypatch.setattr("gamescript_studio.gui.messagebox.askyesno", lambda *a, **k: True)
        app.example("tap")
        assert app.collect()["mode"] == "tap"
        app.saved_project = copy.deepcopy(app.collect())
        assert app.confirm_discard()
    finally:
        root.destroy()


@pytest.mark.gui
def test_preview_exports_real_game_and_cleans_up(monkeypatch):
    import tkinter as tk
    from pathlib import Path
    from gamescript_studio.gui import Studio
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("No display")
    opened = []
    monkeypatch.setattr("gamescript_studio.gui.webbrowser.open", lambda u: opened.append(u) or True)
    app = Studio(root)
    app.preview()
    directory = Path(app.previews[0].name)
    assert (directory / "game/game.js").is_file()
    assert opened[0].startswith("file:")
    app.close()
    assert not directory.exists()
