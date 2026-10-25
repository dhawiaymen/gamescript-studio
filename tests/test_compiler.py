import json
import shutil
import subprocess
import pytest
from gamescript_studio.model import (
    default_project,
    validate,
    save_project,
    load_project,
    ProjectError,
)
from gamescript_studio.compiler import export_game
from gamescript_studio.cli import main


@pytest.mark.parametrize("mode", ["tap", "catch", "dodge"])
def test_roundtrip(tmp_path, mode):
    project = default_project(mode)
    save_project(project, tmp_path / "p.json")
    assert load_project(tmp_path / "p.json") == project


@pytest.mark.parametrize(
    "key,value",
    [
        ("width", 0),
        ("seed", -1),
        ("duration", float("nan")),
        ("lives", True),
        ("background", "red"),
        ("mode", "platformer"),
        ("version", True),
        ("spawn_interval", 0),
    ],
)
def test_reject_bad_fields(key, value):
    p = default_project()
    p[key] = value
    with pytest.raises(ProjectError):
        validate(p)


def test_unknown_rules_rejected():
    p = default_project()
    p["rules"][0]["action"] = "eval"
    with pytest.raises(ProjectError):
        validate(p)


def test_no_shared_mutation():
    p = default_project()
    other = validate(p)
    other["rules"].clear()
    assert p["rules"]


def test_export_escaping_and_non_overwrite(tmp_path):
    p = default_project()
    p["title"] = '</title><script>alert("x")</script>'
    out = tmp_path / "game"
    page = export_game(p, out)
    assert "&lt;script&gt;" in page.read_text()
    assert "<script>alert" not in page.read_text()
    assert (out / "LICENSE").exists()
    original = (out / "game.js").read_bytes()
    with pytest.raises(FileExistsError):
        export_game(p, out)
    assert (out / "game.js").read_bytes() == original


def test_cli_errors(tmp_path):
    assert main(["new", str(tmp_path / "p.json")]) == 0
    assert main(["new", str(tmp_path / "p.json")]) == 2
    assert main(["validate", str(tmp_path / "p.json")]) == 0
    assert main(["export", str(tmp_path / "missing"), "out"]) == 2


def run_js(tmp_path, project, body):
    if not shutil.which("node"):
        pytest.skip("Node.js is required for generated-runtime tests")
    path = export_game(project, tmp_path / "game").parent / "game.js"
    program = (
        'const assert=require("node:assert/strict");const {createGame,config}=require('
        + json.dumps(str(path))
        + ");const g=createGame(config);\n"
        + body
    )
    result = subprocess.run(["node", "-e", program], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr


def test_tap_win_reset_and_terminal_state(tmp_path):
    p = default_project("tap")
    p["target_score"] = 3
    run_js(
        tmp_path,
        p,
        """
for(let i=0;i<3;i++)g.step({tap:true},.1);
assert.equal(g.snapshot().status,'won');assert.equal(g.snapshot().score,3);
g.step({tap:true},1);assert.equal(g.snapshot().score,3);
assert.equal(g.reset().score,0);assert.equal(g.snapshot().status,'running');
""",
    )


def test_time_expires_and_no_negative_time(tmp_path):
    p = default_project("tap")
    p["duration"] = 1
    run_js(
        tmp_path,
        p,
        "g.step({},2);assert.equal(g.snapshot().status,'lost');assert.equal(g.snapshot().time,0);",
    )


def test_seed_reproducibility_and_snapshot_copy(tmp_path):
    run_js(
        tmp_path,
        default_project(),
        """
g.reset(13);g.step({},2);const a=g.snapshot();g.reset(13);g.step({},2);
assert.deepEqual(g.snapshot(),a);a.items[0].x=-9;assert.notEqual(g.snapshot().items[0].x,-9);
g.reset(14);g.step({},2);assert.notDeepEqual(g.snapshot().items,a.items);
""",
    )


def test_catch_lose_and_greedy_win(tmp_path):
    p = default_project("catch")
    p.update(duration=60, target_score=3, lives=1, speed=500)
    run_js(
        tmp_path,
        p,
        """
for(let i=0;i<1000&&g.snapshot().status==='running';i++){
 const s=g.snapshot(),item=s.items[0];g.step({x:item?item.x:240},.05);
}
assert.equal(g.snapshot().status,'won');g.reset();
for(let i=0;i<1000&&g.snapshot().status==='running';i++){
 const item=g.snapshot().items[0];g.step({x:item&&item.x<240?450:30},.05);
}
assert.equal(g.snapshot().status,'lost');assert.equal(g.snapshot().lives,0);
""",
    )


def test_rule_order_and_conditions(tmp_path):
    p = default_project("tap")
    p["rules"].append(
        {"event": "tap", "field": "score", "op": ">=", "value": 2, "action": "win", "amount": 0}
    )
    run_js(
        tmp_path,
        p,
        "g.step({tap:true},0);assert.equal(g.snapshot().status,'running');g.step({tap:true},0);assert.equal(g.snapshot().status,'won');",
    )


def test_bad_simulation_inputs(tmp_path):
    run_js(
        tmp_path,
        default_project(),
        "assert.throws(()=>g.step({},NaN));assert.throws(()=>g.reset(-1));assert.throws(()=>g.step({x:Infinity},.1));",
    )


@pytest.mark.gui
def test_gui_form_and_rules():
    import tkinter as tk
    from gamescript_studio.gui import Studio

    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("No graphical display available")
    try:
        app = Studio(root)
        root.update()
        app.vars["title"].set("GUI roundtrip")
        assert app.collect()["title"] == "GUI roundtrip"
        app.change("add")
        assert len(app.project["rules"]) == 3
        app.undo()
        assert len(app.project["rules"]) == 2
    finally:
        root.destroy()
