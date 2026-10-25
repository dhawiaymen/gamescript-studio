# GameScript Studio

**Build small browser games with visual rules. Export readable JavaScript you own.**

GameScript Studio is a Windows-oriented desktop tool for developers, educators,
and game-jam creators who need a small, understandable starting point instead
of a complete game engine. It combines a settings form, an ordered rule editor,
a visual event → condition → action diagram, and a code viewer.

Version **0.1.0**, initial release candidate. MIT licensed. No account, API key,
subscription, telemetry, or runtime CDN is required.

## What works

- Tap, catch, and dodge game templates with configurable timing, lives, scoring,
  colors, dimensions, spawning, and deterministic random seeds.
- Add, edit, reorder, delete, and undo rule edits. Each rule handles an event,
  checks a condition, and updates game state.
- Save/load validated JSON projects, inspect generated JavaScript, and preview
  a playable game in your browser.
- Export a new folder containing `index.html`, `game.js`, `project.json`, and
  the MIT runtime license. Open the HTML file directly; no server is needed.
- Mouse, touch, and keyboard controls; a deterministic adapter for GameTest AI.

## Start on Windows

1. Install **Python 3.11+** from [python.org](https://www.python.org/downloads/windows/),
   including the Python launcher and Tcl/Tk (standard installer options).
2. Extract this repository to a normal folder, such as `D:\DevTools\gamescript-studio`.
3. Double-click **`Setup.cmd`** once. It creates a local virtual environment.
4. Double-click **`Start.cmd`** whenever you want to use the editor.

Setup needs internet access to install Python packaging dependencies. The
installed application and exported games work offline.

Alternative PowerShell setup:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m gamescript_studio gui
```

## First game in two minutes

Open the editor and keep the Catch template. Set the title and target score.
Select the `collect` rule to inspect its flow: collecting an object adds one
point. A `miss` removes one life. Click **Preview game**, then move the catcher
under the falling targets. Save your project and choose **Export HTML + JS**.
Choose a **new folder name** for each export; existing folders are protected.

To switch templates, select a mode and click **New**. Merely changing the mode
preserves your custom rules. Rules execute in list order, and conditions see
the state changes of previous rules. `lose_life` accepts positive integers.
When lives reach zero the game loses; otherwise reaching the target wins;
otherwise the time limit ends the game. Explicit `win`/`lose` rules take priority.

## Command-line workflow

```powershell
python -m gamescript_studio new my-game.json --mode tap
python -m gamescript_studio validate my-game.json
python -m gamescript_studio export my-game.json exported-game
```

Starter projects are in [`examples/`](examples/). See
[`docs/PROJECT_FORMAT.md`](docs/PROJECT_FORMAT.md) for the schema and
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the compiler design.

## Testing and building

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m build
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

Install **Node.js 20+** to run the generated-JavaScript behavioral tests.
GUI tests run when a display is available. The GitHub workflow targets Windows
and Ubuntu with Python 3.11–3.13 and produces a Windows folder build. A workflow
file is not evidence of a successful hosted run; see the supplied validation
record for checks actually performed. No prebuilt Windows executable is included
in this source release.

## Scope and limitations

This release generates **2D HTML Canvas games**, not native executables, Roblox
Luau, Unity projects, or TikTok Effect House/APJS scripts. It does not import
arbitrary JavaScript. The visual editor is an ordered rule system, not a general
graph engine. There is no asset importer, physics editor, multiplayer backend,
or TypeScript exporter. Preview folders are stored in the system temporary
directory and may be removed after the browser is closed.

The display surface is Canvas: the surrounding controls support keyboard use,
but this is not a fully screen-reader-playable game framework. Time is simulated;
background browser tabs may progress more slowly than wall time.

## Contributing and license

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and
[LICENSE](LICENSE). Maintainer account: [dhawiaymen](https://github.com/dhawiaymen).
This initial implementation was AI-assisted and includes reproducible tests.
No user counts, stars, downloads, or community adoption are claimed.
