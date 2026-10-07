# Security Directives: Zero-Trust & Read-Only Guarantees

## 1. Secrets & Credentials Isolation
- Never log, print, or commit passwords, API tokens, bearer keys, or database credentials.
- Read credentials exclusively from secure environment variables or OS-level keychains.
- Never write credentials to temporary scratch files or transcripts.

## 2. Least Privilege & Dangerous Operation Guards
- Default to read-only mode on all database connections and filesystems.
- Destructive commands (`DROP`, `DELETE`, `rm -rf`, format, schema mutation) strictly require explicit user confirmation.
- Sanitize and validate all external inputs against path traversal attacks (`../`).
