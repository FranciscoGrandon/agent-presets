# Git Workflow & Conventional Commits

## 1. Commit Message Convention
- Format commits following the Conventional Commits specification:
  - `feat: ...` for new capabilities or user-facing features.
  - `fix: ...` for bug fixes and patches.
  - `docs: ...` for documentation updates.
  - `chore: ...` for maintenance, tooling, and dependency updates.
  - `test: ...` for adding or refactoring test suites.

## 2. Branching & History Integrity
- Never commit directly to the default `main` branch after repository initialization.
- Create atomic feature branches (`feature/...`, `fix/...`) and deliver via Pull Requests.
- Prohibit force pushes (`git push --force`) on protected or shared branches.
