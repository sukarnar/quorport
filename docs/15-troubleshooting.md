---
title: Troubleshooting
screen: dashboard
---
| Message | What to do |
|---|---|
| *The filename, directory name or volume label syntax is incorrect* | a file source path contains a full path or bad characters. Use only the file name inside `data\` (e.g. `transfers.csv`). |
| *File … is outside the data folder* | copy the file into the project's `data` folder and use just its name |
| *vault is locked / master key missing* | `.env` lacks `QUORPORT_MASTER_KEY` – restore `.env` from backup, or `quorport cred init` for a new project |
| *401 Unauthorized* | no or wrong `X-API-Key`; check `quorport key list` (expired? revoked?) |
| *403 Forbidden* | the key lacks the endpoint's scope – create a key with that scope |
| *422* | a parameter is missing or invalid; the response says which |
| *source … is read-only* | edit the source and switch on **Allow writes** (`--read-write`) |
| load *skipped – source unchanged* | the same file was loaded already; replace the file, or **Run anyway** / `--force` |
| load *columns changed* | the file's header changed; check the mapping, then **Run anyway** / `--force` |
| load *n row(s) rejected* | open **View rejected rows** / `quorport load rejects <run>`; fix the data or raise Max rejects |
| Studio shows an old screen after an update | close every Studio window (and browser tab), check `pip show quorport`, start it again |
| A list shows only some rows | list endpoints are paged; use `limit`/`offset`, or `quorport call ... --limit 10000` |

**Renamed from Portwright (and earlier restforge).** Projects created before the renames work unchanged:
an existing `portwright.yaml` or `restforge.yaml` is used when there is no `quorport.yaml`,
`PORTWRIGHT_*` / `RESTFORGE_*` variables in `.env` are read, the vault in `.portwright\` or
`.restforge\` is found, API keys starting `pw_` or `rf_` stay valid (new ones start `qp_`), and the
`portwright`, `pw` and `restforge` commands still run. An install in `C:\apps\portwright` or
`C:\apps\restforge` can stay there.

<!-- studio -->
## In Studio

* **Dashboard > Validate project** lists configuration problems with the exact reason.
* **Sources > Test** and **Credentials > Test** check connections one by one.
* A yellow bar at the top means `quorport.yaml` was changed elsewhere – press **Reload**.

<!-- cli -->
## With the CLI

```powershell
quorport --help                       # is the command found? (activate the venv first)
qp --version                            # short alias, same command
where.exe quorport                    # which installation is used
pip show quorport                     # installed version
quorport validate
quorport source test hr
quorport cred test hr_oracle
quorport call employees-list --limit 1
Get-Content C:\apps\hr-api\logs\audit.jsonl -Tail 20
```
