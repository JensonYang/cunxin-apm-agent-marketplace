# Cunxin APM Support Agent

A Codex plugin for investigating Cunxin Printer production complaints and summarizing customer behavior from the read-only Cunxin APM query API. It combines the production APM schema with the application's full-flow event dictionary.

## What it does

- Queries a scoped user/date/app window from `POST /api/log/query`.
- Correlates login, configuration, print-session, print-task, and logout events from `trackEvents.fullFlow.js`.
- Identifies explicit failures, API status/latency problems, unfinished print tasks, retry/fallback/duplicate signals, and high-frequency polling.
- Produces a Chinese markdown support report without exposing raw event payloads by default.

## Privacy and production safety

- The plugin is read-only and only uses `POST /api/log/query`.
- It never calls APM sync/flush, account jump, project download/upload, recovery, or mutation endpoints.
- Raw telemetry is not stored unless `--save-raw` is explicitly supplied.
- Reports intentionally omit IPs, image URLs/identifiers, session IDs, local paths, User-Agents, and raw `data_extra`.

## Install for colleagues

1. Clone this repository to a trusted local directory.
2. Add the repository's marketplace in Codex:

   ```bash
   codex plugin marketplace add /absolute/path/to/cunxin-apm-agent-marketplace
   ```

3. In Codex, install the `cunxin-apm-support-agent` plugin from the added marketplace. The `cunxin-apm-support` skill then activates for production complaint, user behavior, print ID, or APM analysis requests.

Keep the repository private: the event dictionary and the production APM endpoint are internal company assets.

## Direct verification

From the plugin skill directory:

```bash
python3 scripts/apm_support.py report --user-id 1872443 --date 2026-09-14 --app-id 23001
python3 -m unittest discover -s tests -v
```

For a retained, authorized evidence snapshot only:

```bash
python3 scripts/apm_support.py query --user-id 1872443 --date 2026-09-14 --save-raw .apm-snapshots/1872443-2026-09-14
```
