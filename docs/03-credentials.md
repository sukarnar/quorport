---
title: Credentials
screen: credentials
---
Credentials hold logins and tokens that Quorport uses to reach your systems. They are encrypted
(AES-256-GCM) in the project vault, never written to `quorport.yaml`, never shown again after saving,
and removed from log lines automatically.

| Type | Fields | Used for |
|---|---|---|
| `database` | driver, host, port, service_name / sid / dsn / database, username, password, schema | SQL sources |
| `basic` | username, password | upstream APIs |
| `bearer` | token | upstream APIs |
| `api_key` | header, key | upstream APIs |
| `oauth2` | token_url, client_id, client_secret, scope | upstream APIs (token fetched and refreshed for you) |
| `generic` | any name=value pairs | `${CRED:name.field}` in headers, or Python functions |

---

## Project vs global credentials

| | Project vault | Global vault |
|---|---|---|
| **Location** | `<project>/.quorport/credentials.vault` | `~/.quorport/credentials.vault` |
| **Scope** | This project only | All projects on this machine |
| **Master key env** | `QUORPORT_MASTER_KEY` | `QUORPORT_GLOBAL_KEY` (falls back to `QUORPORT_MASTER_KEY`) |
| **Priority** | Wins when same name exists in both | Used when no project credential matches |

Use the **global vault** for credentials shared across multiple projects — a shared analytics database, a corporate API key, an LDAP service account.
Use the **project vault** for credentials specific to one project or environment.

---

<!-- studio -->
## In Studio

### Project credentials

1. **Credentials > Add credential**. If the vault is locked, press **Create master key** first.
2. Choose the type. For a database choose the driver first – the form shows the fields that driver needs.
3. Optionally choose **Rotate after** to get a reminder before the password expires.
4. **Save**, then the **Test** (▶) button logs in and reports success or the database error.
5. **Rotate / edit** changes a password; running servers pick it up within a few minutes.
6. **Used by** shows which sources use the credential; it cannot be deleted while in use.
7. **Promote** (globe icon) moves the credential to the global vault so all projects can use it.

### Global credentials

- Click **Add global credential** to store a credential in `~/.quorport/credentials.vault`.
- Global credentials appear in a separate section at the bottom of the Credentials screen.
- A project credential with the same name always takes priority over the global one.
- Use **Delete** (🗑) to remove a global credential — this will break any project that relies on it.

---

<!-- cli -->
## With the CLI

### Project credentials

```powershell
quorport cred init                                   # create the master key (once per project)
quorport cred types                                  # fields of every type

# Oracle – password prompted (hidden input)
quorport cred add hr_oracle -t database -f driver=oracle+oracledb -f host=dbhost.corp.local `
  -f port=1521 -f service_name=HRPDB -f username=hr_api --expires-days 90

# SQL Server, PostgreSQL
quorport cred add dw -t database -f driver=mssql+pyodbc -f host=sqlhost -f database=DW -f username=etl
quorport cred add pg -t database -f driver=postgresql+psycopg -f host=pghost -f database=app -f username=app

# Upstream APIs
quorport cred add crm_token -t bearer
quorport cred add erp -t oauth2 -f token_url=https://login.corp.local/oauth2/token -f client_id=quorport

# Non-interactive (CI / scheduler): read the secret from an environment variable
quorport cred add hr_oracle -t database -f driver=oracle+oracledb -f host=dbhost -f service_name=HRPDB `
  -f username=hr_api --secret-from-env password=HR_DB_PASSWORD

quorport cred list
quorport cred test hr_oracle
quorport cred rotate hr_oracle                       # new password, prompted
quorport cred show hr_oracle                         # secrets masked
quorport cred remove old_login
quorport cred rekey                                  # new master key, re-encrypts the vault
```

### Global credentials

```powershell
# Store a credential in the global vault (shared across all projects)
quorport cred add shared_dw -t database -f driver=mssql+pyodbc -f host=sqlhost `
  -f database=DW -f username=etl --global

# List global credentials
quorport cred list --global

# Remove from the global vault
quorport cred remove shared_dw --global

# Promote an existing project credential to the global vault
quorport cred promote hr_oracle
```

---

## Deploying to production safely

**The golden rule: config travels, credentials don't.**

`quorport.yaml` contains only credential *names* (e.g. `credential: hr_db`) — no secrets. It is safe to commit and deploy. The vault file is environment-specific and must never be copied across environments.

### Recommended approach

**1. Gitignore the vault**

```gitignore
.quorport/
.env
*.vault
```

**2. Use credential names as contracts**

Keep the same credential name across all environments. Each environment's vault holds a different value for the same name:

```yaml
# quorport.yaml — identical in dev, test and production
sources:
  hr:
    type: sql
    credential: hr_db        # name only — no secrets here
```

```powershell
# Dev — points at dev DB
quorport cred add hr_db -t database -f host=dev-db ...

# Production — ops runs this once on the prod server
quorport cred add hr_db -t database -f host=prod-db ...
```

**3. Use `${ENV:VAR}` for CI/CD pipelines**

For containers and pipelines where interactive prompts are not possible, reference environment variables directly:

```yaml
sources:
  hr:
    type: sql
    url: "postgresql+psycopg://${ENV:HR_DB_USER}:${ENV:HR_DB_PASS}@${ENV:HR_DB_HOST}/hr"
```

Inject the variables as CI secrets or container env vars — no vault file needed.

**4. Use a secrets manager in production**

For enterprise environments, point the provider chain at HashiCorp Vault or AWS Parameter Store:

```yaml
security:
  credentials:
    providers: [hashicorp, env]
    hashicorp:
      url: https://vault.internal
      token: ${ENV:VAULT_TOKEN}
```

**5. Safe migration script**

```powershell
# deploy.ps1 — deploys config only, never touches credentials
git pull origin main
quorport migrate apply          # schema/config changes only
quorport cred list              # verify expected credentials are present
quorport serve
```

### Environment summary

| | Dev | Test | Production |
|---|---|---|---|
| `quorport.yaml` | git | git | git (same file) |
| `.quorport/credentials.vault` | local | local | provisioned by ops |
| `QUORPORT_MASTER_KEY` | `.env` file | CI secret | server env var |
| Credential values | dev DB | test DB | prod DB |

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `The vault is locked` | `QUORPORT_MASTER_KEY` not set | Add it to `.env` or the server's environment |
| `credential 'x' not found` | Not provisioned in this environment | Run `quorport cred add x …` |
| `credential 'x' expired` | Past the rotation deadline | Run `quorport cred rotate x` |
| `no writable provider` | All providers are read-only (env, hashicorp) | Add `vault` to `providers` list |
