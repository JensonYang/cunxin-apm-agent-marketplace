# Cunxin Printer Triage Playbook

Use the bundled `trackEvents.fullFlow.js` as the source of truth for exact names and required fields.

## Flow stages

- **Login:** `cx_login_*` events. A `*_failed` event should be paired with its `error_message`; do not expose masked mobile numbers.
- **Configuration:** `cx_config_point_*` and `cx_config_printer_*` events. A submitted setting without the corresponding success/failure event is unresolved.
- **Print session:** `cx_print_session_start_*`, `cx_print_session_stop_*`, `cx_print_session_period_inform`, and `cx_print_connect_status_*`. A started session without a stop event can explain continued queue polling, but it does not prove a defect.
- **Print task:** task and main-process events share `print_id`, `album_id`, `image_id`, and `qr_type`. Use `print_id` for joins. Evaluate route fallback, duplicate skipping, retries, download, script selection, execution, and finish separately.
- **Logout:** `cx_auth_*` events. Forced logout or logout failure can explain later missing telemetry.

## Complaint signals

| Signal | Interpretation | First follow-up |
|---|---|---|
| `*_failed`, `*_error`, `*_timeout` | Explicit failure signal | Read the matching error field and inspect the same task/session before and after it. |
| Start/exec without a terminal event | Incomplete at the query cutoff | Check whether the requested window is still in progress; then inspect printer queue and later logs. |
| `cx_print_task_route_fallback` | Routing chose a fallback path | Check QR type resolution, printer binding, and local-printer mapping. |
| `cx_print_task_skipped_duplicate` | Duplicate protection activated | Compare repeated queue pulls and task identifiers before treating as a lost job. |
| `cx_print_task_retry_*` | User/system retried a task | Establish whether the retry reaches final success. |
| HTTP/Biz non-success | Remote service failure | Group by endpoint/status and compare latency/retry behavior. |
| High-frequency successful polling | Efficiency or telemetry-volume concern | Check whether idle/backoff behavior is expected for an active print session. |

## Evidence discipline

- Prefer an exact timestamp, event name, and redacted task ID over a long raw payload.
- Include no more than ten unresolved or failed task IDs unless the user requests an export.
- Do not infer a print completion solely from HTTP `200`; use the terminal print-flow event when present.
