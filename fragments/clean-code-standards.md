# Clean Code & Architectural Guidelines

## 1. Modularity & Single Responsibility
- Every module, function, and class must have exactly one reason to change.
- Keep functions short (prefer < 30 lines) and focused on a single level of abstraction.
- Avoid premature optimization; prioritize readability, maintainability, and clear naming.

## 2. Type Hints & Explicit Contracts
- Use standard Python type annotations (`from __future__ import annotations`).
- Type all public function parameters and return values.
- Prefer `dataclasses` or `pydantic` models for structured data over untyped nested dictionaries.

## 3. Error Handling
- Never use bare `except:` clauses. Always catch specific exceptions (`OSError`, `ValueError`, `KeyError`).
- Fail early with meaningful, actionable error messages.
