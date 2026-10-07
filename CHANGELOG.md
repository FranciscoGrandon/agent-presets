# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-07

### Added
- **Core Context Engine**: Concatenation of atomic Markdown fragments with customizable separators (`\n\n\n`) and trace markers (`<!-- fragment: ... -->`).
- **Zero-Loss Auto-Harvesting (`harvest`)**: Scans target output files before overwriting to rescue manual additions, modified fragment variants (`<name>-modificado-<timestamp>.md`), and lost fragments.
- **Desktop GUI (Tkinter/ttk)**: Visual fragment ordering (up/down buttons), live checkbox selection, missing fragment badges (`(falta)`), preset manager, and read-only preview modal. High-DPI support on Windows.
- **Headless CLI**: Full command-line interface (`--list`, `--importar`, `--preset`, `--destino`, `--sin-marcadores`) designed for automated CI/CD and pre-commit hooks.
- **Cumulative Backup Subsystem**: Automatic immutable timestamped backups in `backups/salidas/` and `backups/presets/` with collision resolution (`-1`, `-2`).
- **Sample Library**: Standard best-practice fragments (`clean-code-standards.md`, `security-zero-trust.md`, `git-workflow-conventional.md`, `pytest-testing-guidelines.md`) and pre-configured presets.
- **Automated Test Suite**: Unit tests covering parsing, fragment compilation, traversal security, and the 5 harvesting scenarios.
