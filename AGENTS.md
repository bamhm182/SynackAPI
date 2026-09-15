# SynackAPI Project Guide

## Overview

SynackAPI is a community-maintained Python library that provides Synack Red Team members a programmatic interface to Synack's Penetration Testing as a Service (PTaaS) platform. It has no official affiliation with Synack.

**Package name:** `SynackAPI` | **Importable as:** `synack` | **Exposes:** `Handler`, `State`

---

## Directory Layout

```
synackapi/
├── src/synack/              # Library source (the actual Python package)
│   ├── __init__.py          # Exports Handler and State
│   ├── _handler.py          # Main Handler class (entry point for users)
│   ├── _state.py            # Centralized State configuration object
│   ├── plugins/             # Plugin system — one file per plugin
│   │   ├── base.py          # Plugin base class and auto-registry
│   │   ├── alerts.py
│   │   ├── api.py
│   │   ├── auth.py
│   │   ├── db.py
│   │   ├── debug.py
│   │   ├── duo.py
│   │   ├── missions.py
│   │   ├── notifications.py
│   │   ├── scratchspace.py
│   │   ├── targets.py
│   │   ├── templates.py
│   │   ├── transactions.py
│   │   ├── users.py
│   │   └── utils.py
│   └── db/                  # SQLite database layer
│       ├── alembic/         # Schema migration versions (do not edit manually)
│       └── models/          # SQLAlchemy ORM models
├── test/                    # Unit tests (no real API calls, mocked)
│   └── test_<plugin>.py     # One test file per plugin/component
├── docs/                    # mdBook documentation (GitHub Pages)
│   └── src/
│       └── usage/
│           └── plugins/     # One .md file per plugin
│               └── <plugin>.md
├── tools/check_docs.py      # Verifies plugin docs match public plugin methods
├── setup.py                 # Package metadata and dependencies
├── pyproject.toml           # Build backend config (setuptools)
└── .flake8                  # Flake8 config (max-line-length=119)
```

---

## Architecture

### Handler (`_handler.py`)
The user-facing entry point. On init it creates a `State` object, auto-instantiates every registered plugin, and exposes each as an attribute:

```python
from synack import Handler
h = Handler(login=True, email="user@example.com", password="pass")
h.missions.get()
h.targets.get_registered()
```

### State (`_state.py`)
Holds all configuration. Properties cascade: runtime override → database value → default. Key categories:
- **Auth**: `email`, `password`, `otp_secret`, `otp_count`, `api_token`
- **Config**: `config_dir` (~/.config/synack), `synack_domain` (default: `synack.com`, can be overridden to e.g. `synack.us`)
- **Files**: `template_dir`, `scratchspace_dir`
- **Notifications**: `notifications_token`, `slack_app_token`, `slack_channel`, `slack_url`
- **SMTP**: `smtp_server`, `smtp_port`, `smtp_username`, `smtp_password`, `smtp_email_from`, `smtp_email_to`, `smtp_starttls`
- **Proxies**: `use_proxies`, `http_proxy`, `https_proxy`
- **Flags**: `debug`, `login`, `use_scratchspace`

### Plugin System (`plugins/base.py`)
`Plugin` base class uses `__init_subclass__` to auto-register all subclasses. Each plugin receives the shared `State` object. Handler discovers and instantiates all registered plugins at startup.

Some plugins (e.g. `Duo`, `Auth`) instantiate other plugins internally to access their methods. This is a known architectural limitation — plugins receive only `State`, not the handler, so they cannot reference the handler's shared plugin instances.

### Database (`db/`)
SQLite at `~/.config/synack/synackapi.db`. Managed by SQLAlchemy ORM + Alembic migrations. Models: `Target`, `IP`, `Port`, `Url`, `Category`, `Organization`, `Config`.

Several `Db` properties prompt the user for input when the value is unset (e.g. `email`, `password`, `otp_secret`, `otp_count`, `slack_app_token`, `slack_channel`). `synack_domain` does not prompt — it defaults to `synack.com` and can be overridden.

---

## Generated Files

At runtime, SynackAPI creates and manages files under `~/.config/synack/`:

### `synackapi.db`
SQLite database storing persistent settings (credentials, tokens, config) and cached API data (targets, IPs, ports, URLs). Alembic migrations are applied automatically on startup via `db.set_migration()`. Contains sensitive information — keep it protected.

### `login.js`
JavaScript file written by `auth.set_login_script()` after a successful login. Intended for use with a TamperMonkey userscript to:
1. Detect navigation to `https://login.<synack_domain>/`
2. Wait 60 seconds, then redirect to `https://platform.<synack_domain>/`
3. Inject the current API token into the browser session

See `docs/src/usage/main-components/files.md` for the TamperMonkey script template.

---

## Plugins Reference

| Plugin | Attribute on Handler | Purpose |
|---|---|---|
| Alerts | `h.alerts` | Email/Slack alerts and message sanitization |
| Api | `h.api` | Core HTTP wrapper for all Synack endpoints |
| Auth | `h.auth` | Full authentication flow (CSRF → credentials → Duo → token) |
| Db | `h.db` | SQLite access, schema migrations, ORM queries |
| Debug | `h.debug` | Timestamp-based debug logging |
| Duo | `h.duo` | Duo Security MFA (HOTP OTP and push approval) |
| Missions | `h.missions` | Mission retrieval, sorting, summaries |
| Notifications | `h.notifications` | Notification polling and state |
| Scratchspace | `h.scratchspace` | File saving for mission assets, Burp configs, attachments |
| Targets | `h.targets` | Target listing, scope building for web/host testing |
| Templates | `h.templates` | Mission templates with variable substitution |
| Transactions | `h.transactions` | Payout/balance querying |
| Users | `h.users` | User profile retrieval |
| Utils | `h.utils` | HTML parsing utilities |

---

## Code Quality Rules

Before committing, run the same checks used by CI:

```bash
flake8 src test tools
python tools/check_docs.py
coverage run --source=src --omit='src/synack/db/alembic/env.py,src/synack/db/alembic/versions/*.py' -m unittest discover test
coverage report --fail-under=100
```

`tools/check_docs.py` verifies that every public non-property plugin method has matching documentation, that documented plugin methods still exist, that required parameters are documented, and that plugin doc headings are alphabetical.

**Summary:** when adding or renaming a public plugin method, also add/update the matching `## <plugin>.<method>` section in `docs/src/usage/plugins/<plugin>.md` and add/update tests in `test/test_<plugin>.py`.

---

## Testing

### Unit Tests
```bash
coverage run --source=src --omit=src/synack/db/alembic/env.py,src/synack/db/alembic/versions/*.py -m unittest discover test
coverage report
```
No real credentials needed — all external calls are mocked.

### CI (GitHub Actions)
- `.github/workflows/test-build.yml` — flake8 lint, documentation checks, coverage-enforced unit tests, and package builds.
- `.github/workflows/mdbook.yml` — builds and deploys docs to GitHub Pages.
- `.github/workflows/release.yml` — automated release.

---

## Documentation

Built with [mdBook](https://rust-lang.github.io/mdBook/). Source lives in `docs/src/`. Plugin reference pages are at `docs/src/usage/plugins/<plugin>.md`.

Notable non-plugin doc pages:
- `docs/src/usage/main-components/files.md` — documents runtime-generated files (`synackapi.db`, `login.js`)
- `docs/src/usage/main-components/state.md` — explains the State object and database vs. state override behavior
- `docs/src/usage/examples/` — usage examples (mission bot, templates, target registration, invisible missions)

To build locally:
```bash
cd docs && mdbook build
```

Each plugin doc file must have `## <plugin>.<method>` headings for all public non-property methods (checked by `tools/check_docs.py`).

---

## Dependencies

Production (from `setup.py`):
- `alembic` — DB migrations
- `netaddr` — network address parsing
- `pathlib2` — path utilities
- `pyaml` — YAML parsing
- `pyotp` — HOTP/TOTP for Duo
- `requests` — HTTP client
- `SQLAlchemy` — ORM
- `urllib3` — URL utilities

Dev: `coverage`, `flake8`, `pytest`; docs require `mdbook`

Install for development: `pip install -e '.[dev]'`

---

## Important Constraints

- **Rate limits**: Do not poll missions more than once every 30 seconds. Do not exceed 200 requests in any 5-minute window. Violations risk account bans.
- **Unofficial**: This library reverse-engineers an undocumented API. Breaking changes can occur any time Synack updates their platform.
- **Python version**: Requires Python 3.6+ per package metadata; CI currently runs Python 3.12.
