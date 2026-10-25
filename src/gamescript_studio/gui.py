"""Tkinter visual rule editor; usable with the keyboard as well as the mouse."""

import copy
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from pathlib import Path
import webbrowser
from .model import (
    default_project,
    validate,
    load_project,
    save_project,
    EVENTS,
    ACTIONS,
    FIELDS,
    OPS,
)
from .compiler import compile_script, export_game


class Studio(ttk.Frame):
    def __init__(self, root):
        super().__init__(root, padding=16)
        self.pack(fill="both", expand=True)
        self.root = root
        self.project = default_project()
        self.path = None
        self.history = []
        self.vars = {}
        root.title("GameScript Studio · Visual mini-game compiler")
        root.geometry("1180x830")
        root.minsize(960, 700)
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 14))
        for label, command in [
            ("New", self.new),
            ("Open", self.open),
            ("Save", self.save),
            ("Undo rule edit", self.undo),
            ("Preview game", self.preview),
            ("Export HTML + JS", self.export),
        ]:
            ttk.Button(toolbar, text=label, command=command).pack(side="left", padx=3)
        ttk.Label(self, text="GameScript Studio", font=("Segoe UI", 22, "bold")).pack(anchor="w")
        ttk.Label(
            self, text="Configure your game. Build rules visually. Export code you own."
        ).pack(anchor="w", pady=(2, 14))
        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True)
        settings = ttk.Frame(body, padding=10)
        body.add(settings, weight=1)
        ttk.Label(settings, text="GAME SETTINGS", font=("Segoe UI", 11, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=8
        )
        for row, key in enumerate([k for k in self.project if k not in ("rules", "version")], 1):
            ttk.Label(settings, text=key.replace("_", " ").title()).grid(
                row=row, column=0, sticky="w", pady=4
            )
            v = tk.StringVar()
            self.vars[key] = v
            if key == "mode":
                entry = ttk.Combobox(
                    settings,
                    textvariable=v,
                    values=["tap", "catch", "dodge"],
                    state="readonly",
                    width=18,
                )
            else:
                entry = ttk.Entry(settings, textvariable=v, width=21)
            entry.grid(row=row, column=1, sticky="ew", padx=8, pady=4)
            if key in ("background", "accent"):
                ttk.Button(settings, text="…", width=3, command=lambda k=key: self.color(k)).grid(
                    row=row, column=2
                )
        ttk.Label(
            settings,
            text="Changing mode preserves your rules.\nUse New for mode-specific defaults.",
            wraplength=270,
        ).grid(row=20, column=0, columnspan=3, pady=14)
        right = ttk.Notebook(body)
        body.add(right, weight=4)
        rules = ttk.Frame(right, padding=10)
        right.add(rules, text="Visual rules")
        self.tree = ttk.Treeview(
            rules,
            columns=("event", "condition", "action"),
            show="headings",
            height=8,
            selectmode="browse",
        )
        for name, width in [("event", 90), ("condition", 180), ("action", 200)]:
            self.tree.heading(name, text=name.title())
            self.tree.column(name, width=width)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.select)
        edit = ttk.Frame(rules)
        edit.pack(fill="x", pady=10)
        self.rule_vars = {}
        for col, (name, values) in enumerate(
            [
                ("event", EVENTS),
                ("field", FIELDS),
                ("op", OPS),
                ("value", None),
                ("action", ACTIONS),
                ("amount", None),
            ]
        ):
            ttk.Label(edit, text=name.title()).grid(row=0, column=col, sticky="w")
            v = tk.StringVar(value=(values[0] if values else "1"))
            self.rule_vars[name] = v
            widget = (
                ttk.Combobox(edit, textvariable=v, values=values, state="readonly", width=11)
                if values
                else ttk.Entry(edit, textvariable=v, width=7)
            )
            widget.grid(row=1, column=col, padx=2)
        buttons = ttk.Frame(rules)
        buttons.pack(fill="x")
        for label, fn in [
            ("Add rule", lambda: self.change("add")),
            ("Update selected", lambda: self.change("update")),
            ("Delete", lambda: self.change("delete")),
            ("Move up", lambda: self.change("up")),
            ("Move down", lambda: self.change("down")),
        ]:
            ttk.Button(buttons, text=label, command=fn).pack(side="left", padx=2)
        ttk.Label(
            rules,
            text="Rules run from top to bottom. Conditions see changes made by earlier rules.",
            wraplength=650,
        ).pack(anchor="w", pady=10)
        self.graph = tk.Canvas(rules, height=180, background="#15223b", highlightthickness=0)
        self.graph.pack(fill="x")
        code = ttk.Frame(right, padding=10)
        right.add(code, text="Generated JavaScript")
        ttk.Button(code, text="Refresh code from settings", command=self.code).pack(
            anchor="w", pady=5
        )
        self.code_text = tk.Text(code, wrap="none", font=("Consolas", 10))
        self.code_text.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(code, command=self.code_text.yview)
        self.code_text.configure(yscrollcommand=scroll.set)
        self.status = tk.StringVar(value="Ready — source is editable, offline, and MIT licensed.")
        ttk.Label(self, textvariable=self.status).pack(anchor="w", pady=(12, 0))
        root.bind("<Control-s>", lambda e: self.save())
        root.bind("<Control-o>", lambda e: self.open())
        self.populate()

    def color(self, key):
        c = colorchooser.askcolor(self.vars[key].get(), parent=self.root)[1]
        if c:
            self.vars[key].set(c)

    def collect(self):
        data = copy.deepcopy(self.project)
        for k, v in self.vars.items():
            value = v.get()
            if k in ("width", "height", "target_score", "lives", "seed"):
                value = int(value)
            elif k in ("duration", "speed", "spawn_interval"):
                value = float(value)
            data[k] = value
        return validate(data)

    def populate(self):
        for k, v in self.vars.items():
            v.set(str(self.project[k]))
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for i, r in enumerate(self.project["rules"]):
            cond = "Always" if r["field"] == "always" else f"{r['field']} {r['op']} {r['value']}"
            self.tree.insert(
                "", "end", iid=str(i), values=(r["event"], cond, f"{r['action']} ({r['amount']})")
            )
        self.graph.delete("all")
        self.graph.create_text(
            18, 18, text="SELECT A RULE TO INSPECT ITS FLOW", anchor="w", fill="#b5c8e1"
        )

    def select(self, event=None):
        selection = self.tree.selection()
        if not selection:
            return
        r = self.project["rules"][int(selection[0])]
        for k, v in self.rule_vars.items():
            v.set(str(r[k]))
        self.graph.delete("all")
        labels = [
            f"WHEN\n{r['event']}",
            f"IF\n{r['field']} {r['op']} {r['value']}" if r["field"] != "always" else "IF\nalways",
            f"DO\n{r['action']} {r['amount']}",
        ]
        for i, label in enumerate(labels):
            x = 15 + i * 210
            self.graph.create_rectangle(
                x, 45, x + 175, 130, fill="#263e60", outline="#58e0ae", width=2
            )
            self.graph.create_text(
                x + 87, 87, text=label, fill="white", font=("Segoe UI", 12, "bold")
            )
            if i < 2:
                self.graph.create_line(
                    x + 175, 87, x + 205, 87, arrow="last", fill="#58e0ae", width=2
                )

    def change(self, kind):
        try:
            data = self.collect()
            selection = self.tree.selection()
            index = int(selection[0]) if selection else None
            if kind != "add" and index is None:
                raise ValueError("Select a rule first.")
            previous = copy.deepcopy(data)
            if kind in ("add", "update"):
                rule = {k: v.get() for k, v in self.rule_vars.items()}
                for k in ("value", "amount"):
                    rule[k] = float(rule[k])
                if kind == "add":
                    data["rules"].append(rule)
                else:
                    data["rules"][index] = rule
            elif kind == "delete":
                del data["rules"][index]
            else:
                target = index + (-1 if kind == "up" else 1)
                if not 0 <= target < len(data["rules"]):
                    return
                data["rules"][index], data["rules"][target] = (
                    data["rules"][target],
                    data["rules"][index],
                )
            self.project = validate(data)
            self.history.append(previous)
            self.history = self.history[-50:]
            self.refresh()
            self.status.set("Rules updated. Save your project to keep changes.")
        except (ValueError, TypeError) as exc:
            messagebox.showerror("Invalid rule", str(exc))

    def undo(self):
        if self.history:
            self.project = self.history.pop()
            self.populate()

    def new(self):
        if messagebox.askyesno("New project", "Start a new project? Save any changes first."):
            self.project = default_project(self.vars["mode"].get())
            self.path = None
            self.history = []
            self.populate()

    def open(self):
        path = filedialog.askopenfilename(filetypes=[("GameScript projects", "*.json")])
        if not path:
            return
        try:
            data = load_project(path)
            if not messagebox.askyesno(
                "Open project", "Replace the editor contents? Save any changes first."
            ):
                return
            self.project = data
            self.path = path
            self.history = []
            self.populate()
            self.status.set(path)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Open failed", str(exc))

    def save(self):
        try:
            data = self.collect()
            path = self.path or filedialog.asksaveasfilename(
                defaultextension=".json", filetypes=[("GameScript projects", "*.json")]
            )
            if path:
                save_project(data, path)
                self.path = path
                self.project = data
                self.status.set(f"Saved: {path}")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Save failed", str(exc))

    def code(self):
        try:
            source = compile_script(self.collect())
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", source)
        except ValueError as exc:
            messagebox.showerror("Invalid settings", str(exc))

    def preview(self):
        try:
            folder = Path(tempfile.mkdtemp(prefix="gamescript-preview-")) / "game"
            page = export_game(self.collect(), folder)
            webbrowser.open(page.as_uri())
            self.status.set(f"Preview: {folder}")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Preview failed", str(exc))

    def export(self):
        folder = filedialog.asksaveasfilename(title="New output folder name", initialfile="my-game")
        if not folder:
            return
        try:
            page = export_game(self.collect(), folder)
            self.status.set(f"Exported: {page}")
            messagebox.showinfo(
                "Export complete", f"Open {page} in a browser.\nAll source files are included."
            )
        except (OSError, ValueError) as exc:
            messagebox.showerror("Export failed", str(exc))


def main():
    root = tk.Tk()
    ttk.Style().theme_use("clam")
    Studio(root)
    root.mainloop()
