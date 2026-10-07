# Pytest & Automated Verification Guidelines

## 1. Test Determinism & Isolation
- Tests must be strictly deterministic; never rely on external network calls or system clocks without mocking.
- Use `tempfile.TemporaryDirectory` or pytest's `tmp_path` fixture for disk operations.
- Clean up all scratch files and resources after test completion.

## 2. Coverage & Edge Case Verification
- Ensure 100% coverage on critical path functions (parsers, validators, serialization).
- Explicitly test boundary conditions, path traversal attempts, and encoding edge cases (BOM, Unicode normalization).
