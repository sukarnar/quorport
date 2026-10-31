# Quorport

**Secure REST endpoints and data loads over SQL databases, files, upstream APIs and Python callables.**

Quorport turns any data source into an authenticated REST API — no boilerplate, no manual wiring.
Define a source, add an endpoint, serve. Everything lives in one YAML file.

---

## What it does

| Capability | Description |
|---|---|
| **Endpoints** | Expose SQL queries, file data, upstream APIs or Python functions as REST endpoints |
| **Access control** | API keys, JWT, AD/LDAP groups, per-endpoint policies |
| **Data loads** | Pull from any endpoint or source into a database table on a schedule |
| **Reports** | Generate HTML and PDF reports from Jinja2 templates |
| **Studio** | Desktop GUI for everything above — no CLI required |

---

## Quick start

```powershell
# Activate the environment (once per terminal session)
C:\apps\quorport\.venv\Scripts\Activate.ps1

# Create a project
quorport init C:\apps\hr-api --name hr-api
cd C:\apps\hr-api

# Open Studio (desktop window)
quorport studio

# Or open Studio in a browser
quorport studio --web
```

The short alias `qp` works everywhere: `qp serve`, `qp call employees-list`, etc.
The legacy names `portwright`, `pw` and `restforge` are also still available.

---

## Typical workflow

```powershell
# 1. Add a database credential (password prompted securely)
quorport cred add hr_db -t database -f driver=postgresql+psycopg \
  -f host=dbhost -f port=5432 -f database=hr -f username=hr_api

# 2. Add a data source
quorport source add hr -t sql --credential hr_db

# 3. Create CRUD endpoints for a table
quorport endpoint crud employees -s hr --table employees --key employee_id

# 4. Issue an API key
quorport key create reporting-app --scope employees:read

# 5. Test it
quorport call employees-list --limit 5 --table

# 6. Start the server
quorport serve
```

---

## Installation

### Core (REST endpoints + CLI)

```powershell
pip install .
```

### With database drivers

```powershell
pip install ".[postgres]"   # PostgreSQL
pip install ".[mysql]"      # MySQL / MariaDB
pip install ".[mssql]"      # SQL Server
pip install ".[oracle]"     # Oracle
```

### With Studio (desktop GUI)

```powershell
pip install ".[gui]"
quorport studio
```

### With Reports (HTML / PDF generation)

```powershell
pip install ".[reports]"

# WeasyPrint requires GTK on Windows — use xhtml2pdf instead:
pip install xhtml2pdf
```

### Everything

```powershell
pip install ".[postgres,mysql,mssql,oracle,gui,reports]"
```

---

## Credentials

Credentials are stored encrypted (AES-256-GCM) — never in `quorport.yaml`, never in logs.

### Project credentials (per-project)

```powershell
quorport cred init                          # create the master key once
quorport cred add hr_db -t database -f driver=postgresql+psycopg -f host=dbhost -f database=hr -f username=hr_api
quorport cred list
quorport cred test hr_db
quorport cred rotate hr_db                  # change password, live servers pick it up within minutes
quorport cred remove old_login
```

### Global credentials (shared across all projects)

Global credentials live in `~/.quorport/credentials.vault` and are available to every project on this machine. A same-named project credential always takes priority.

```powershell
quorport cred add shared_dw -t database --global    # store in global vault
quorport cred list --global                         # list global credentials
quorport cred promote hr_db                         # move project credential to global vault
quorport cred remove shared_dw --global             # remove from global vault
```

### Deploying to production safely

**Config travels, credentials don't.** `quorport.yaml` contains only credential names — no secrets. Commit and deploy the YAML freely; provision credentials separately on each server.

```gitignore
# .gitignore
.quorport/
.env
*.vault
```

For CI/CD pipelines, use `${ENV:VAR}` references instead of the vault:

```yaml
sources:
  hr:
    type: sql
    url: "postgresql+psycopg://${ENV:HR_DB_USER}:${ENV:HR_DB_PASS}@${ENV:HR_DB_HOST}/hr"
```

For enterprise environments, configure HashiCorp Vault as the provider in `quorport.yaml` and manage secrets there.

---

## Reports & Templates

Reports pull data from a configured endpoint or source and render it through a Jinja2 HTML template.

```powershell
# Run a report
quorport report run my-report

# Run and open the output
quorport report run my-report --open

# List all reports
quorport report list
```

### Built-in templates

| Template | Best for |
|---|---|
| `simple_table` | Any flat data set |
| `summary_dashboard` | Numeric data with KPI cards |
| `grouped_by_category` | Data with a natural category column |
| `invoice` | Line-item billing |
| `audit_log` | Event logs with colour-coded badges |
| `financial_accounting` | General ledger, trial balance, journal entries |

In Studio: **Reports → Templates** to browse, preview, copy and edit templates.

---

## Project file

All configuration lives in `quorport.yaml` in your project folder.
Studio and the CLI read and write the same file.

```yaml
name: hr-api
credentials:
  hr_db:
    type: database
    driver: postgresql+psycopg
    host: dbhost
    database: hr
    username: hr_api
sources:
  hr:
    type: sql
    credential: hr_db
endpoints:
  - name: employees-list
    source: hr
    sql: SELECT * FROM employees
    access: key
reports:
  - name: headcount
    template: templates/simple_table.html
    endpoint: employees-list
    format: pdf
```

---

## CLI reference

```
quorport --help               All commands
quorport docs                 Open the built-in guide
quorport docs <topic>         Jump to a topic (e.g. quorport docs reports)
quorport docs --search <term> Search the guide
quorport <command> --help     Help for a specific command
```

Key command groups:

| Group | Description |
|---|---|
| `cred` | Manage credentials |
| `source` | Manage data sources |
| `endpoint` | Manage endpoints |
| `key` | Manage API keys |
| `load` | Manage and run data loads |
| `report` | Manage and run reports |
| `serve` | Start the REST server |
| `studio` | Launch the desktop GUI |
| `call` | Test an endpoint from the CLI |
| `docs` | Browse the built-in guide |

---

## Requirements

- Python 3.11+
- Windows 10 / 11 (Studio), or any platform (CLI + server)
- Database driver matching your source (see Installation above)

---

## Version history

| Version | Notes |
|---|---|
| 0.8.0 | Reports & Templates — HTML/PDF reports, Jinja2 template editor, template gallery |
| Earlier | REST endpoints, data loads, access control, Studio GUI |

---

## Author

**Sukarna Chinchod**

> *Quorport — a gateway that controls who gets access to what data.*
