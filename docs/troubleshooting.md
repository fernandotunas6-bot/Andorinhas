# Troubleshooting

## Troubleshooting

**`command not found: andorinha`** — `source .venv/bin/activate` first.

**`ModuleNotFoundError: No module named 'andorinha'` after install (macOS)** — Python 3.13 silently ignores `.pth` files carrying the macOS hidden flag, and some Macs propagate that flag into `.venv`. Run `andorinha install` again (it auto-fixes), or: `ln -s "$(pwd)/andorinha" .venv/lib/python3.13/site-packages/andorinha`

**`externally-managed-environment`** — Use a venv, not system Python.

**`SyntaxError` or odd `ImportError`s right after install (macOS)** — Your venv is Python 3.9. `python3 -m venv` builds from `/usr/bin/python3`, which macOS keeps at 3.9. Check with `.venv/bin/python -V`, then rebuild: `rm -rf .venv && python3.13 -m venv .venv && source .venv/bin/activate && pip install -e .`

**Claude headless mode fails** — `claude login`, and confirm the subscription is active. Test with `claude -p "say hi"`. In Docker, mount `~/.claude` into the container (writable: the CLI refreshes its login there). If the log says the Claude CLI "lacks --safe-mode" (or another flag), run `claude update` (in Docker, rebuild the image); Andorinha resumes on its own. If your Claude login depends on `env` or `apiKeyHelper` entries in your Claude settings files, set those variables in Andorinha's environment instead: Andorinha's calls don't read settings files. `andorinha status --check` confirms the CLI without sending a prompt.

**Dashboard says "locked"** — Open the link `andorinha dashboard` printed (or `andorinha dashboard --url`). If it says the token file can't be used, follow the message: usually delete `data/dashboard-token` and restart the dashboard. Visit it as `127.0.0.1` or `localhost`; other host names are refused.

**Codex calls fail** — Read the log line; every Codex error says what to do. "Not logged in" or "expired or is due for renewal" → use Codex once or run `codex login` with ChatGPT. "Hasn't been verified with Andorinha" → install the supported Codex version named in the message. "Isolation could not be verified" → a Codex config layer outside your `~/.codex` (for example a managed or `/etc/codex` config) forces a tool, hook, MCP server, instructions or custom endpoint back on; Andorinha refuses to send prompts until it's gone. Model catalog errors → choose an available model ID from the catalog shown in the message, or leave `brain.model` blank to select a listed model. Andorinha never switches to Claude on its own.

**Discovery finds nothing** — Confirm signals first (`andorinha signals --confirm free`); nothing is collected until you do. If you're on the free OpenStreetMap source, it only covers mapped trades and is thin for service-area businesses — `andorinha discover --providers` shows the alternatives.

**Overpass is throttling** — It's free volunteer infrastructure. Andorinha walks three mirrors before giving up. Wait a few minutes, or use a paid provider for bulk work.

**Emails land in spam** — Almost always the domain, not the copy. Check SPF/DKIM/DMARC, confirm warmup ran ([TrulyInbox](https://trulyinbox.com/?via=andorinha) shows the inbox rate; `andorinha warmup` reads it once connected), halve your volume.

**Andorinha does nothing during the day** — Check `quiet_hours` and whether it hit `max_daily_claude_percent`. `andorinha status` shows current state; the `actions` table logs every decision.

**How do I stop it right now?** — `Ctrl+C`, or `andorinha sending pause` to stop outbound while leaving the loop running. State is in SQLite, so it resumes cleanly.

**Where does my data live?** — All local: `data/andorinha.db`, `.env`, `andorinha.yaml`. Nothing goes anywhere except the APIs you configured.
