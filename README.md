# ⚡ AgentPresets

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Dependencies-Zero%20(Stdlib)-success?style=for-the-badge" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge" alt="Cross Platform">
  <img src="https://img.shields.io/badge/Agents-Claude%20%7C%20Gemini%20%7C%20Cursor%20%7C%20Antigravity-orange?style=for-the-badge" alt="Compatible Agents">
</p>

<p align="center">
  <strong>The Git-like Context Composer & Directive Manager for AI Coding Agents.</strong><br>
  <em>Stop pasting 4,000-line monolithic <code>AGENTS.md</code> / <code>GEMINI.md</code> files into every repo.<br>
  Compose, version, and auto-harvest modular Markdown directives with zero dependencies.</em>
</p>

---

## 💥 The Problem: Monolithic Prompt Rot

Every software engineer and team pairing with AI agents (**Claude Code**, **Gemini CLI**, **Cursor**, **GitHub Copilot**, **Antigravity**) hits the same wall:

1. **Context Bloat:** Your `AGENTS.md` or `GEMINI.md` starts with 50 lines. Two weeks later, it's a 3,000-line chaotic behemoth.
2. **Attention Degradation:** When LLMs are fed bloated context files, reasoning degrades, instructions conflict, and hallucination rates climb.
3. **Overwrite Catastrophe:** When you or your agent tweak rules inside the project root, pulling updates from your central templates obliterates your local modifications.
4. **Dependency Friction:** Most context tools require Node, Docker, heavy Python packages, or cloud subscriptions just to stitch together a few markdown files.

---

## 🚀 The Solution: AgentPresets

**AgentPresets** treats AI agent context like modular code. You break directives down into **atomic Markdown fragments** (`fragments/*.md`) and assemble tailored profiles (`presets/*.json`) per repository, subagent, or project phase.

```
                  ┌──────────────────────┐
                  │ fragments/           │
                  │  ├── clean-code.md   │
                  │  ├── zero-trust.md   │
                  │  └── git-flow.md     │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │ presets/             │
                  │  └── python-dev.json ◄── (Picks & orders fragments)
                  └──────────┬───────────┘
                             │
                 [ AgentPresets Engine ] ◄── (Zero-loss Auto-Harvesting)
                             │
                             ▼
             Compiled Context File (GEMINI.md / AGENTS.md)
```

---

## ✨ Core Pillars

### 1. 🛡️ Inviolable Rule: Fragments Never Get Lost (`auto-harvest`)
AgentPresets is **growth-only** by design:
- It **never** mutates, renames, or deletes existing fragments in `fragments/`.
- **Before every single build**, the engine scans the destination file (`GEMINI.md`, `AGENTS.md`, `CLAUDE.md`).
- If you or your LLM edited a rule directly in the target file, AgentPresets **rescues it automatically** into a new variant (`<fragment>-modificado-<timestamp>.md`).
- If you appended manual rules, it splits them cleanly by headings and imports them into your fragment library.
- Every build creates an immutable, timestamped copy in `backups/salidas/`.

### 2. ⚡ Zero External Dependencies
- Written strictly with the **Python standard library** (`tkinter`, `pathlib`, `json`, `argparse`, `shutil`, `re`).
- **No `pip install`, no virtual environments, no node_modules.**
- Runs natively on any machine with Python 3.8+ out of the box.

### 3. 🖥️ Dual Mode: Visual GUI + Headless CI/CD
- **Desktop GUI:** Visual drag-and-order controls (↑ / ↓), multi-select checkboxes, missing fragment alerts, live preview modal, and preset switching.
- **Headless CLI:** Fast single-command execution for Git pre-commit hooks, Docker builds, and automated multi-agent pipelines.

### 4. 🔍 Traceable Context Markers
Compiled outputs inject HTML comments before each section:
```markdown
<!-- fragment: security-zero-trust.md -->
# Security Directives: Zero-Trust...
```
This enables sub-second provenance auditing, allows your agents to cite which rule they are following, and powers bidirectional harvesting.

---

## 📊 Comparison Matrix

| Feature | Monolithic `AGENTS.md` | Git Submodules | AgentPresets |
| :--- | :---: | :---: | :---: |
| **Atomic Modularity** | ❌ Sprawling file | ⚠️ High overhead | ✅ Independent `.md` fragments |
| **Granular Composition** | ❌ All or nothing | ❌ Clunky | ✅ Instant JSON Presets |
| **Zero-Loss Protection** | ❌ Easily overwritten | ⚠️ Merge conflicts | ✅ Bidirectional `harvest` engine |
| **External Dependencies** | ✅ None | ⚠️ Git setup | ✅ **0 dependencies (Stdlib)** |
| **GUI & CLI Support** | ❌ Text editor only | ❌ CLI only | ✅ **Native GUI + CLI** |
| **Target Flexibility** | ❌ Single file | ❌ Submodule path | ✅ `GEMINI.md`, `AGENTS.md`, `CLAUDE.md` |

---

## ⚡ Quickstart

### 1. Clone & Run (No installation required)

```bash
git clone https://github.com/FranciscoGrandon/agent-presets.git
cd agent-presets
```

### 2. Launch the Desktop GUI

```bash
python agentpresets.py
```
*(Select your fragments, order them with ↑ / ↓, choose a preset, and click **Generar archivo**).*

---

### 3. Or Use the Headless CLI

```bash
# List available presets
python agentpresets.py --list

# Compile a preset to default target (GEMINI.md)
python agentpresets.py --preset full-stack-python

# Compile to a custom target (e.g. AGENTS.md or CLAUDE.md)
python agentpresets.py --preset full-stack-python --destino AGENTS.md

# Compile without trace markers
python agentpresets.py --preset full-stack-python --sin-marcadores

# Import & harvest new sections from target into fragments/ without generating
python agentpresets.py --importar --destino GEMINI.md
```

---

## 📁 Repository Structure

```
agent-presets/
├── agentpresets.py           # Core engine, CLI & Desktop GUI
├── agentpresets_mini.py      # Backward-compatible alias
├── fragments/                # Immutable library of atomic markdown rules
│   ├── clean-code-standards.md
│   ├── git-workflow-conventional.md
│   ├── pytest-testing-guidelines.md
│   └── security-zero-trust.md
├── presets/                  # Presets mapping targets to ordered fragments
│   ├── full-stack-python.json
│   └── minimal-security.json
├── backups/                  # Cumulative immutable backups (created at runtime)
│   ├── salidas/              # Target backups (GEMINI.md.20261007-153012.bak)
│   └── presets/              # Preset backups
├── tests/
│   └── test_agentpresets.py  # Automated verification suite (100% pass)
├── LICENSE                   # MIT License
├── CHANGELOG.md              # Keep a Changelog standard
└── README.md
```

---

## ⚙️ How Presets Work

Presets are simple, version-controllable JSON files stored in `presets/<preset-name>.json`:

```json
{
  "destino": "GEMINI.md",
  "fragmentos": [
    "security-zero-trust.md",
    "clean-code-standards.md",
    "git-workflow-conventional.md",
    "pytest-testing-guidelines.md"
  ]
}
```

- **`destino`**: Output file path (defaults to `GEMINI.md` if omitted; supports relative or absolute paths).
- **`fragmentos`**: Ordered list of fragment filenames defining the exact concatenation hierarchy.

---

## 🧪 Running Tests

AgentPresets includes a comprehensive unit testing suite covering exclusive file creation, path traversal defense, heading parsers, and the 5 harvesting scenarios:

```bash
python -m unittest tests/test_agentpresets.py
```

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for additional fragment libraries (e.g. Rust, Go, TypeScript/React, AWS/Terraform security) or CLI enhancements:

1. Fork the project.
2. Create your feature branch (`git checkout -b feature/awesome-fragments`).
3. Commit your changes (`git commit -m 'feat: add typescript and react best practice fragments'`).
4. Push to the branch (`git push origin feature/awesome-fragments`).
5. Open a Pull Request.

---

## 📄 License & Authorship

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

**Created by Francisco Grandón Vergara**  
*Empowering developers and autonomous AI coding agents with clean, deterministic, and modular context architecture.*
