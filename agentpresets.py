#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentPresets
============
The Git-like Context Composer & Directive Manager for AI Coding Agents.
Compiles instructions for AI agents (GEMINI.md, AGENTS.md, CLAUDE.md, ...)
by concatenating selected, ordered Markdown fragments with auto-harvesting.

Creado por Francisco Grandón Vergara
License: MIT

Pure Standard Library (tkinter, pathlib, json, argparse, shutil, re). Python 3.8+.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tkinter as tk
import unicodedata
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

# --------------------------------------------------------------------------
# Constants & Configuration
# --------------------------------------------------------------------------
APP_DIR = Path(__file__).resolve().parent
FRAGMENTS_DIR = APP_DIR / "fragments"
PRESETS_DIR = APP_DIR / "presets"
BACKUPS_DIR = APP_DIR / "backups"   # Cumulative backups (never auto-deleted)
DEFAULT_TARGET = "GEMINI.md"
ENCODING = "utf-8"
SEPARATOR = "\n\n\n"  # Triple newline between compiled fragments
INVALID_NAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
MARKER = re.compile(r"^<!--\s*fragment:\s*(.+?)\s*-->\s*$", re.MULTILINE)
FENCE = re.compile(r"^\s*(```|~~~)")


# --------------------------------------------------------------------------
# Core Engine (Headless / Library)
# --------------------------------------------------------------------------
def ensure_dirs() -> None:
    """Ensures fragments/ and presets/ directories exist."""
    FRAGMENTS_DIR.mkdir(exist_ok=True)
    PRESETS_DIR.mkdir(exist_ok=True)


def write_text(path: Path, content: str) -> None:
    """Writes UTF-8 text with Unix LF newlines (avoids CRLF conversion on Windows)."""
    with open(path, "w", encoding=ENCODING, newline="\n") as fh:
        fh.write(content)


def list_fragments() -> list[str]:
    """Lists sorted fragment filenames in fragments/."""
    ensure_dirs()
    return sorted(p.name for p in FRAGMENTS_DIR.glob("*.md") if p.is_file())


def list_presets() -> list[str]:
    """Lists sorted preset names in presets/."""
    ensure_dirs()
    return sorted(p.stem for p in PRESETS_DIR.glob("*.json"))


def fragment_path(name: str) -> Path | None:
    """Returns safe path inside fragments/ or None if attempting path traversal."""
    p = (FRAGMENTS_DIR / name).resolve()
    return p if p.parent == FRAGMENTS_DIR.resolve() else None


def fragment_exists(name: str) -> bool:
    p = fragment_path(name)
    return p is not None and p.is_file()


def valid_preset_name(name: str) -> bool:
    return bool(name) and not INVALID_NAME.search(name) and name not in (".", "..")


def load_preset(name: str) -> dict:
    """Returns {'destino': str|None, 'fragmentos': [str]}.
    Supports modern format (dict with target and fragments) and legacy format (flat array)."""
    path = PRESETS_DIR / f"{name}.json"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, list):
        return {"destino": None, "fragmentos": [str(x) for x in data]}
    if isinstance(data, dict) and isinstance(data.get("fragmentos"), list):
        return {
            "destino": data.get("destino") or None,
            "fragmentos": [str(x) for x in data["fragmentos"]],
        }
    raise ValueError(f"Formato de preset no reconocido: {path.name}")


def archive_copy(src: Path, subdir: str) -> Path:
    """Copies src to backups/<subdir>/ with timestamp.
    Backups are strictly cumulative: never overwrites nor deletes previous copies."""
    folder = BACKUPS_DIR / subdir
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = folder / f"{src.name}.{stamp}.bak"
    n = 1
    while dest.exists():
        dest = folder / f"{src.name}.{stamp}-{n}.bak"
        n += 1
    shutil.copy2(src, dest)
    return dest


def save_preset(name: str, fragments: list[str], target: str) -> None:
    """Saves preset configuration and creates cumulative backup if preset already existed."""
    ensure_dirs()
    path = PRESETS_DIR / f"{name}.json"
    if path.exists():
        archive_copy(path, "presets")
    payload = {"destino": target, "fragmentos": fragments}
    write_text(
        PRESETS_DIR / f"{name}.json",
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    )


def compile_fragments(names: list[str], markers: bool = True):
    """Concatenates fragments in specified order. Returns (content, missing_names)."""
    parts: list[str] = []
    missing: list[str] = []
    for name in names:
        path = fragment_path(name)
        if path is None or not path.is_file():
            missing.append(name)
            continue
        text = path.read_text(encoding="utf-8-sig").strip("\r\n")
        if markers:
            text = f"<!-- fragment: {name} -->\n{text}"
        parts.append(text)
    return SEPARATOR.join(parts) + "\n", missing


def resolve_target(text: str) -> Path:
    p = Path(text.strip() or DEFAULT_TARGET).expanduser()
    return p if p.is_absolute() else APP_DIR / p


def write_output(target: Path, content: str):
    """Overwrites target file. If previous file existed with different content,
    creates cumulative backup in backups/salidas/. Returns backup Path or None."""
    backup = None
    if target.exists():
        try:
            old = target.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            old = None
        if old != content:
            backup = archive_copy(target, "salidas")
    target.parent.mkdir(parents=True, exist_ok=True)
    write_text(target, content)
    return backup


# --------------------------------------------------------------------------
# Harvesting: Target to fragments/ (Zero-loss Guarantee)
# --------------------------------------------------------------------------
def norm(text: str) -> str:
    """Comparable normalized string without newline or trailing space discrepancies."""
    lines = text.replace("\r\n", "\n").strip().split("\n")
    return "\n".join(line.rstrip() for line in lines)


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:60].strip("-") or "fragmento"


def read_fragment_text(name: str) -> str:
    path = fragment_path(name)
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip("\n")


def create_fragment(stem: str, text: str) -> str:
    """Creates fragments/<stem>.md in exclusive mode ('x').
    If filename is taken, appends -2, -3... Returns created filename."""
    ensure_dirs()
    if INVALID_NAME.search(stem):
        stem = slugify(stem)
    n = 1
    while True:
        name = f"{stem}.md" if n == 1 else f"{stem}-{n}.md"
        try:
            with open(FRAGMENTS_DIR / name, "x", encoding=ENCODING, newline="\n") as fh:
                fh.write(text.strip("\n") + "\n")
            return name
        except FileExistsError:
            n += 1


def parse_segments(text: str):
    """Divides text by <!-- fragment: x.md --> markers.
    Returns [(name|None, body)]; None = text without marker."""
    segs, pos, name = [], 0, None
    for m in MARKER.finditer(text):
        segs.append((name, text[pos:m.start()]))
        name, pos = m.group(1).strip(), m.end()
    segs.append((name, text[pos:]))
    return segs


def split_by_headings(text: str) -> list[str]:
    """Divides into sections by headings. If 2+ '# ' cuts by '# ';
    otherwise cuts by '## ' (single '# ' remains with preamble).
    Ignores '#' inside code fences."""
    lines = text.split("\n")
    in_fence, heads = False, []
    for i, line in enumerate(lines):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        m = None if in_fence else HEADING.match(line)
        if m:
            heads.append((i, len(m.group(1))))
    cut_level = 1 if sum(1 for _, lv in heads if lv == 1) >= 2 else 2
    cuts = [i for i, lv in heads if lv == cut_level]
    if not cuts:
        return [text]
    starts = sorted(set([0] + cuts))
    return ["\n".join(lines[a:b]) for a, b in zip(starts, starts[1:] + [len(lines)])]


def block_title(block: str, default: str) -> str:
    for line in block.split("\n"):
        if line.strip():
            m = HEADING.match(line)
            return m.group(2) if m else default
    return default


def harvest(target: Path) -> list[str]:
    """Reads target file BEFORE overwriting and saves everything not yet in fragments/:
      - Manual additions (unmarked or at fragment end),
      - Modified fragments (saved as <name>-modificado-<timestamp>.md),
      - Lost fragments (restores fragment from target marker),
      - Unmarked target files (split by headings).
    Never mutates or deletes existing fragments. Returns list of created fragment names."""
    if not target.is_file():
        return []
    text = target.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    existing = {n: read_fragment_text(n) for n in list_fragments()}
    known = {norm(t) for t in existing.values() if t}
    created: list[str] = []
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    loose: list[str] = []

    def add(stem: str, body: str) -> None:
        key = norm(body)
        if key and key not in known:
            created.append(create_fragment(stem, body))
            known.add(key)

    for name, body in parse_segments(text):
        body = body.strip("\n")
        if not body.strip():
            continue
        if not name or INVALID_NAME.search(name):
            loose.append(body)
        elif name in existing:
            ftext = existing[name]
            if norm(body) == norm(ftext):
                continue
            if body.startswith(ftext):
                loose.append(body[len(ftext):])
            else:
                add(f"{Path(name).stem}-modificado-{stamp}", body)
        else:
            add(Path(name).stem, body)

    for chunk in loose:
        for ftext in sorted(existing.values(), key=len, reverse=True):
            if ftext:
                chunk = chunk.replace(ftext, "")
        chunk = chunk.strip("\n")
        if not chunk.strip():
            continue
        for block in split_by_headings(chunk):
            add(slugify(block_title(block, f"importado-{stamp}")), block)
    return created


# --------------------------------------------------------------------------
# Desktop GUI (Tkinter)
# --------------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("AgentPresets — AI Context Composer")
        self.geometry("660x600")
        self.minsize(560, 460)

        self.order: list[str] = []
        self.checked: dict[str, tk.BooleanVar] = {}
        self.preset_var = tk.StringVar()
        self.target_var = tk.StringVar(value=DEFAULT_TARGET)
        self.markers_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Listo.")

        self._build_ui()
        self.rescan()
        self.refresh_presets()
        self.after(300, self._offer_initial_import)

    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 4}

        top = ttk.Frame(self)
        top.pack(fill="x", **pad)
        ttk.Label(top, text="Preset:").pack(side="left")
        self.combo = ttk.Combobox(top, textvariable=self.preset_var)
        self.combo.pack(side="left", fill="x", expand=True, padx=6)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.on_load())
        ttk.Button(top, text="Cargar", command=self.on_load).pack(side="left")
        ttk.Button(top, text="Guardar", command=self.on_save).pack(side="left", padx=4)
        ttk.Button(top, text="Eliminar", command=self.on_delete).pack(side="left")

        mid = ttk.LabelFrame(self, text="Fragmentos (el orden de la lista determina el orden del archivo)")
        mid.pack(fill="both", expand=True, **pad)
        self.canvas = tk.Canvas(mid, highlightthickness=0)
        scroll = ttk.Scrollbar(mid, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.rows = ttk.Frame(self.canvas)
        self._win = self.canvas.create_window((0, 0), window=self.rows, anchor="nw")
        self.rows.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind(
            "<Configure>", lambda e: self.canvas.itemconfig(self._win, width=e.width)
        )
        self.canvas.bind("<Enter>", self._bind_wheel)
        self.canvas.bind("<Leave>", self._unbind_wheel)

        tools = ttk.Frame(self)
        tools.pack(fill="x", padx=8)
        ttk.Button(tools, text="Actualizar lista", command=self.rescan).pack(side="left")
        ttk.Button(tools, text="Marcar todos", command=lambda: self.set_all(True)).pack(side="left", padx=4)
        ttk.Button(tools, text="Desmarcar todos", command=lambda: self.set_all(False)).pack(side="left")
        ttk.Button(tools, text="Importar desde destino", command=self.on_import).pack(side="right")

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", **pad)
        ttk.Label(bottom, text="Destino:").pack(side="left")
        ttk.Entry(bottom, textvariable=self.target_var).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(bottom, text="Examinar…", command=self.on_browse).pack(side="left")

        actions = ttk.Frame(self)
        actions.pack(fill="x", **pad)
        ttk.Checkbutton(
            actions, text="Incluir marcadores <!-- fragment: … -->", variable=self.markers_var
        ).pack(side="left")
        ttk.Button(actions, text="Generar archivo", command=self.on_generate).pack(side="right")
        ttk.Button(actions, text="Vista previa", command=self.on_preview).pack(side="right", padx=6)

        ttk.Label(self, textvariable=self.status_var, anchor="w", relief="sunken").pack(
            fill="x", side="bottom"
        )

    def _bind_wheel(self, _e=None) -> None:
        self.bind_all("<MouseWheel>", self._on_wheel)
        self.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _unbind_wheel(self, _e=None) -> None:
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.unbind_all(seq)

    def _on_wheel(self, e) -> None:
        self.canvas.yview_scroll(int(-e.delta / 120), "units")

    def rescan(self) -> None:
        ensure_dirs()
        available = list_fragments()
        self.order = [n for n in self.order if n in available]
        self.order += [n for n in available if n not in self.order]
        for n in self.order:
            self.checked.setdefault(n, tk.BooleanVar(value=False))
        self.rebuild_rows()
        self.status_var.set(f"{len(available)} fragmento(s) disponibles.")

    def rebuild_rows(self) -> None:
        for w in self.rows.winfo_children():
            w.destroy()
        if not self.order:
            ttk.Label(
                self.rows, text="No hay fragmentos .md en la carpeta fragments/."
            ).pack(padx=8, pady=8)
            return
        for i, name in enumerate(self.order):
            row = ttk.Frame(self.rows)
            row.pack(fill="x", padx=4, pady=1)
            var = self.checked.setdefault(name, tk.BooleanVar(value=False))
            ttk.Checkbutton(row, text=name, variable=var).pack(side="left")
            if not fragment_exists(name):
                tk.Label(row, text="  (falta)", fg="#c0392b").pack(side="left")
            down = ttk.Button(row, text="↓", width=3, command=lambda n=name: self.move(n, 1))
            down.pack(side="right", padx=1)
            up = ttk.Button(row, text="↑", width=3, command=lambda n=name: self.move(n, -1))
            up.pack(side="right", padx=1)
            if i == 0:
                up.state(["disabled"])
            if i == len(self.order) - 1:
                down.state(["disabled"])

    def move(self, name: str, delta: int) -> None:
        i = self.order.index(name)
        j = i + delta
        if 0 <= j < len(self.order):
            self.order[i], self.order[j] = self.order[j], self.order[i]
            self.rebuild_rows()

    def set_all(self, value: bool) -> None:
        for n in self.order:
            if fragment_exists(n):
                self.checked[n].set(value)

    def selected(self) -> list[str]:
        return [n for n in self.order if self.checked[n].get()]

    def refresh_presets(self) -> None:
        self.combo["values"] = list_presets()

    def on_load(self) -> None:
        name = self.preset_var.get().strip()
        if not name or not (PRESETS_DIR / f"{name}.json").is_file():
            messagebox.showwarning("Cargar preset", "Seleccione un preset existente.")
            return
        try:
            data = load_preset(name)
        except (OSError, ValueError, UnicodeDecodeError) as exc:
            messagebox.showerror("Cargar preset", f"No se pudo leer el preset:\n{exc}")
            return
        chosen = data["fragmentos"]
        available = list_fragments()
        rest = [n for n in available if n not in chosen]
        self.order = chosen + rest
        for n in self.order:
            var = self.checked.setdefault(n, tk.BooleanVar())
            var.set(n in chosen)
        self.target_var.set(data["destino"] or DEFAULT_TARGET)
        self.rebuild_rows()
        missing = [n for n in chosen if not fragment_exists(n)]
        if missing:
            messagebox.showwarning(
                "Fragmentos faltantes",
                "El preset referencia fragmentos que ya no existen:\n\n- "
                + "\n- ".join(missing)
                + "\n\nSe omitirán al generar el archivo.",
            )
        self.status_var.set(f"Preset «{name}» cargado.")

    def on_save(self) -> None:
        name = self.preset_var.get().strip()
        if not valid_preset_name(name):
            messagebox.showwarning(
                "Guardar preset",
                "Escriba un nombre válido (sin \\ / : * ? \" < > |).",
            )
            return
        names = self.selected()
        if not names:
            messagebox.showwarning("Guardar preset", "Marque al menos un fragmento.")
            return
        if (PRESETS_DIR / f"{name}.json").exists() and not messagebox.askyesno(
            "Guardar preset", f"El preset «{name}» ya existe. ¿Sobrescribir?"
        ):
            return
        try:
            save_preset(name, names, self.target_var.get().strip() or DEFAULT_TARGET)
        except OSError as exc:
            messagebox.showerror("Guardar preset", f"No se pudo guardar:\n{exc}")
            return
        self.refresh_presets()
        self.status_var.set(f"Preset «{name}» guardado ({len(names)} fragmentos).")

    def on_delete(self) -> None:
        name = self.preset_var.get().strip()
        path = PRESETS_DIR / f"{name}.json"
        if not name or not path.is_file():
            messagebox.showwarning("Eliminar preset", "Seleccione un preset existente.")
            return
        if not messagebox.askyesno("Eliminar preset", f"¿Eliminar el preset «{name}»?"):
            return
        try:
            archive_copy(path, "presets")
            path.unlink()
        except OSError as exc:
            messagebox.showerror("Eliminar preset", str(exc))
            return
        self.preset_var.set("")
        self.refresh_presets()
        self.status_var.set(f"Preset «{name}» eliminado (respaldo en backups/presets).")

    def on_browse(self) -> None:
        current = resolve_target(self.target_var.get())
        path = filedialog.asksaveasfilename(
            title="Archivo de destino",
            initialdir=str(current.parent),
            initialfile=current.name,
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("Todos", "*.*")],
            confirmoverwrite=False,
        )
        if path:
            p = Path(path)
            try:
                p = p.relative_to(APP_DIR)
            except ValueError:
                pass
            self.target_var.set(str(p))

    def _build(self):
        names = self.selected()
        if not names:
            messagebox.showwarning("Generar", "Marque al menos un fragmento.")
            return None
        try:
            content, missing = compile_fragments(names, self.markers_var.get())
        except (OSError, UnicodeDecodeError) as exc:
            messagebox.showerror("Generar", f"Error leyendo fragmentos:\n{exc}")
            return None
        if missing:
            if len(missing) == len(names):
                messagebox.showerror("Generar", "Ninguno de los fragmentos marcados existe.")
                return None
            if not messagebox.askyesno(
                "Fragmentos faltantes",
                "Estos fragmentos no existen y se omitirán:\n\n- "
                + "\n- ".join(missing)
                + "\n\n¿Continuar?",
            ):
                return None
        return content

    def on_preview(self) -> None:
        content = self._build()
        if content is None:
            return
        win = tk.Toplevel(self)
        win.title("Vista previa")
        win.geometry("700x520")
        txt = tk.Text(win, wrap="word")
        sb = ttk.Scrollbar(win, command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", content)
        txt.configure(state="disabled")

    def _harvest_ui(self, target: Path, title: str):
        try:
            created = harvest(target)
        except (OSError, UnicodeDecodeError) as exc:
            messagebox.showerror(
                title, f"No se pudo leer el destino; no se modificó nada:\n{exc}"
            )
            return None
        for n in created:
            if n not in self.order:
                self.order.append(n)
        self.rescan()
        return created

    @staticmethod
    def _created_text(created: list[str]) -> str:
        return f"{len(created)} fragmento(s) nuevo(s) guardado(s) en fragments/:\n- " + "\n- ".join(created)

    def on_import(self) -> None:
        target = resolve_target(self.target_var.get())
        if not target.is_file():
            messagebox.showwarning("Importar", f"No existe el archivo:\n{target}")
            return
        created = self._harvest_ui(target, "Importar")
        if created is None:
            return
        if created:
            msg = self._created_text(created)
            self.status_var.set(f"{len(created)} fragmento(s) nuevo(s) importados.")
        else:
            msg = "No hay contenido nuevo: todo ya está en fragments/."
            self.status_var.set(msg)
        messagebox.showinfo("Importar", msg)

    def _offer_initial_import(self) -> None:
        target = resolve_target(self.target_var.get())
        if list_fragments() or not target.is_file():
            return
        if messagebox.askyesno(
            "Importar",
            f"No hay fragmentos todavía y existe:\n{target}\n\n"
            "¿Separarlo en fragmentos ahora? (el archivo no se modifica)",
        ):
            self.on_import()

    def on_generate(self) -> None:
        target = resolve_target(self.target_var.get())
        created = self._harvest_ui(target, "Generar")
        if created is None:
            return
        content = self._build()
        if content is None:
            if created:
                messagebox.showinfo("Contenido nuevo rescatado", self._created_text(created))
            return
        try:
            backup = write_output(target, content)
        except OSError as exc:
            messagebox.showerror("Generar", f"No se pudo escribir el archivo:\n{exc}")
            return
        msg = f"Generado: {target}"
        if backup:
            msg += f"\nRespaldo: backups/salidas/{backup.name}"
        if created:
            msg += "\n\n" + self._created_text(created) + "\n(quedan desmarcados; inclúyalos en un preset si los necesita)"
        self.status_var.set(f"Generado: {target}")
        messagebox.showinfo("Generar", msg)


# --------------------------------------------------------------------------
# CLI Engine
# --------------------------------------------------------------------------
def run_cli(args: argparse.Namespace) -> int:
    ensure_dirs()
    if args.list:
        for name in list_presets():
            print(name)
        return 0
    if args.importar:
        target = resolve_target(args.destino or DEFAULT_TARGET)
        try:
            created = harvest(target)
        except (OSError, UnicodeDecodeError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        for n in created:
            print(f"Fragmento nuevo guardado: {n}")
        if not created:
            print("Sin contenido nuevo.")
        return 0
    try:
        data = load_preset(args.preset)
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    content, missing = compile_fragments(data["fragmentos"], not args.sin_marcadores)
    for name in missing:
        print(f"Aviso: falta el fragmento {name}", file=sys.stderr)
    if len(missing) == len(data["fragmentos"]):
        print("Error: no hay fragmentos válidos para compilar.", file=sys.stderr)
        return 1
    target = resolve_target(args.destino or data["destino"] or DEFAULT_TARGET)
    try:
        for n in harvest(target):
            print(f"Fragmento nuevo guardado: {n}")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Error leyendo el destino, no se sobrescribió: {exc}", file=sys.stderr)
        return 1
    backup = write_output(target, content)
    print(f"Generado: {target}" + (f" (respaldo: {backup.name})" if backup else ""))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AgentPresets: The Git-like Context Composer & Directive Manager for AI Agents"
    )
    parser.add_argument("--preset", help="compila este preset sin abrir la GUI")
    parser.add_argument("--destino", help="archivo de salida (anula el del preset)")
    parser.add_argument("--sin-marcadores", action="store_true",
                        help="no incluir comentarios <!-- fragment: … -->")
    parser.add_argument("--list", action="store_true", help="lista los presets disponibles")
    parser.add_argument("--importar", action="store_true",
                        help="guarda como fragmentos lo nuevo del destino (sin generar)")
    args = parser.parse_args()

    if args.preset or args.list or args.importar:
        return run_cli(args)

    ensure_dirs()
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    App().mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
