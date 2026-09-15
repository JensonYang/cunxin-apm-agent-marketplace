#!/usr/bin/env python3
"""Read-only Cunxin APM query and complaint-analysis helper."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

DEFAULT_BASE_URL = "https://apm.cunxin.com"
DEFAULT_APP_ID = "23001"
DEFAULT_PAGE_SIZE = 100
DEFAULT_MAX_PAGES = 5
DEFAULT_WINDOW_MINUTES = 60
DEFAULT_MAX_REQUESTS = 240
DEFAULT_EVENT_TYPES = [
    "error",
    "user_behav",
    "api",
    "network",
    "performance",
    "paint",
    "server_error",
    "footprint",
    "server_api",
]
SHANGHAI = ZoneInfo("Asia/Shanghai")
SUCCESS_BIZ_CODES = {"0", "200", "2000", "200000", "success", "ok"}
PRINT_ID_PATTERN = re.compile(r"[\"']?print_id[\"']?\s*:\s*[\"']?([A-Za-z0-9_-]+)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query Cunxin APM logs and generate a redacted support report."
    )
    parser.add_argument("command", choices=("report", "query"), help="report analyzes results; query only saves raw results")
    parser.add_argument("--user-id", required=True, help="Cunxin user ID")
    parser.add_argument("--date", required=True, help="Shanghai date in YYYY-MM-DD")
    parser.add_argument("--app-id", default=DEFAULT_APP_ID, help="APM app ID (default: 寸心来印 / 23001)")
    parser.add_argument("--bizline-id", default=None, help="Optional APM business-line ID")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="APM site origin")
    parser.add_argument("--type", dest="types", action="append", choices=DEFAULT_EVENT_TYPES, help="Event type to query; repeat to select types")
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE, help="Rows per request, 1-10000 (default: 100)")
    parser.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES, help="Safety cap per event type and time window (default: 5)")
    parser.add_argument("--window-minutes", type=int, default=DEFAULT_WINDOW_MINUTES, help="Split the query into this many minutes per request window (default: 60)")
    parser.add_argument("--max-requests", type=int, default=DEFAULT_MAX_REQUESTS, help="Safety cap for all APM requests in one run (default: 240)")
    parser.add_argument("--save-raw", type=Path, help="Explicitly save raw APM responses to this directory")
    parser.add_argument("--full-day", action="store_true", help="For today, query through 23:59:59 instead of the current Shanghai time")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    try:
        date = datetime.strptime(args.date, "%Y-%m-%d").date()
    except ValueError as error:
        raise SystemExit("--date must use YYYY-MM-DD") from error
    if date > datetime.now(SHANGHAI).date():
        raise SystemExit("--date cannot be in the future")
    if not args.user_id.strip():
        raise SystemExit("--user-id cannot be empty")
    if not 1 <= args.page_size <= 10000:
        raise SystemExit("--page-size must be between 1 and 10000")
    if args.max_pages < 1:
        raise SystemExit("--max-pages must be at least 1")
    if not 1 <= args.window_minutes <= 24 * 60:
        raise SystemExit("--window-minutes must be between 1 and 1440")
    if args.max_requests < 1:
        raise SystemExit("--max-requests must be at least 1")


def query_bounds(date_value: str, full_day: bool) -> tuple[str, str, bool]:
    date = datetime.strptime(date_value, "%Y-%m-%d").date()
    now = datetime.now(SHANGHAI)
    start = datetime.combine(date, time.min, tzinfo=SHANGHAI)
    is_in_progress = date == now.date() and not full_day
    end = now.replace(microsecond=0) if is_in_progress else datetime.combine(date, time.max, tzinfo=SHANGHAI).replace(microsecond=0)
    return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"), is_in_progress


def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": DEFAULT_BASE_URL,
            "Referer": f"{DEFAULT_BASE_URL}/monitor-ui",
            "User-Agent": "Cunxin-APM-Support-Agent/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"APM returned HTTP {error.code}: {detail}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"APM request failed: {error.reason}") from error


def iter_time_windows(start: str, end: str, window_minutes: int) -> Iterable[tuple[str, str]]:
    """Yield adjacent inclusive windows so each request has a bounded time range."""
    cursor = datetime.strptime(start, "%Y-%m-%d %H:%M:%S").replace(tzinfo=SHANGHAI)
    cutoff = datetime.strptime(end, "%Y-%m-%d %H:%M:%S").replace(tzinfo=SHANGHAI)
    span = timedelta(minutes=window_minutes)
    while cursor <= cutoff:
        window_end = min(cursor + span - timedelta(seconds=1), cutoff)
        yield cursor.strftime("%Y-%m-%d %H:%M:%S"), window_end.strftime("%Y-%m-%d %H:%M:%S")
        cursor = window_end + timedelta(seconds=1)


def save_response(root: Path, event_type: str, window_start: str, page: int, response: dict[str, Any]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    window_tag = window_start.replace("-", "").replace(" ", "T").replace(":", "")
    output = root / f"{event_type}-{window_tag}-page-{page}.json"
    output.write_text(json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8")


def query_logs(args: argparse.Namespace) -> tuple[dict[str, list[dict[str, Any]]], list[str], dict[str, Any]]:
    start, end, in_progress = query_bounds(args.date, args.full_day)
    event_types = args.types or DEFAULT_EVENT_TYPES
    all_rows: dict[str, list[dict[str, Any]]] = {}
    warnings: list[str] = []
    request_count = 0
    request_limit_reached = False

    for event_type in event_types:
        rows: list[dict[str, Any]] = []
        for window_start, window_end in iter_time_windows(start, end, args.window_minutes):
            if request_limit_reached:
                break
            for page in range(1, args.max_pages + 1):
                if request_count >= args.max_requests:
                    warnings.append(f"已达到 --max-requests={args.max_requests}；剩余时间片未查询，不能据此认定无日志")
                    request_limit_reached = True
                    break
                payload: dict[str, Any] = {
                    "page": page,
                    "pageSize": args.page_size,
                    "order": "ASC",
                    "app_id": args.app_id,
                    "item_id": args.user_id,
                    "type": event_type,
                    "log_time_start": window_start,
                    "log_time_end": window_end,
                }
                if args.bizline_id:
                    payload["bizline_id"] = args.bizline_id
                request_count += 1
                try:
                    response = post_json(f"{args.base_url.rstrip('/')}/api/log/query", payload)
                except RuntimeError as error:
                    warnings.append(f"{event_type}: `{window_start}` 至 `{window_end}` 查询失败：{error}")
                    break
                if args.save_raw:
                    save_response(args.save_raw, event_type, window_start, page, response)
                if not response.get("success"):
                    warnings.append(f"{event_type}: `{window_start}` 至 `{window_end}` APM returned success=false")
                    break
                data = response.get("data") or {}
                page_rows = data.get("result") or []
                if not isinstance(page_rows, list):
                    warnings.append(f"{event_type}: `{window_start}` 至 `{window_end}` result is not a list")
                    break
                rows.extend(row for row in page_rows if isinstance(row, dict))
                if len(page_rows) < args.page_size:
                    break
                pagination = data.get("pagination") or {}
                total = pagination.get("total")
                if isinstance(total, int) and page * args.page_size >= total:
                    break
            else:
                warnings.append(f"{event_type}: `{window_start}` 至 `{window_end}` stopped at --max-pages={args.max_pages}；该时间片数据可能不完整")
        all_rows[event_type] = rows

    metadata = {
        "user_id": args.user_id,
        "app_id": args.app_id,
        "date": args.date,
        "start": start,
        "end": end,
        "in_progress": in_progress,
        "event_types": event_types,
        "query_strategy": {
            "page_size": args.page_size,
            "max_pages": args.max_pages,
            "window_minutes": args.window_minutes,
            "request_count": request_count,
            "max_requests": args.max_requests,
        },
    }
    return all_rows, warnings, metadata


def log_time(row: dict[str, Any]) -> str:
    return str(row.get("log_time") or "")


def normalized_url(value: Any) -> str:
    raw = str(value or "")
    if not raw:
        return "(unknown endpoint)"
    try:
        parsed = urlsplit(raw)
        return parsed.path or raw.split("?", 1)[0]
    except ValueError:
        return raw.split("?", 1)[0]


def numeric_value(row: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = row.get(key)
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def percentile(values: Iterable[float], fraction: float) -> int | None:
    ordered = sorted(values)
    if not ordered:
        return None
    index = max(0, math.ceil(len(ordered) * fraction) - 1)
    return round(ordered[index])


def event_name(row: dict[str, Any]) -> str:
    return str(row.get("data_name") or "")


def extract_print_id(row: dict[str, Any]) -> str | None:
    extra = row.get("data_extra")
    if isinstance(extra, dict):
        value = extra.get("print_id")
        return str(value) if value is not None else None
    if not isinstance(extra, str):
        return None
    try:
        parsed = json.loads(extra)
        value = parsed.get("print_id") if isinstance(parsed, dict) else None
        if value is not None:
            return str(value)
    except json.JSONDecodeError:
        pass
    match = PRINT_ID_PATTERN.search(extra)
    return match.group(1) if match else None


def is_api_failure(row: dict[str, Any]) -> bool:
    status = numeric_value(row, "data_http_status")
    if status is not None and status >= 400:
        return True
    business = str(row.get("data_biz_status") or "").strip().lower()
    return bool(business and business not in SUCCESS_BIZ_CODES)


def print_task_summary(behavior_rows: list[dict[str, Any]]) -> dict[str, Any]:
    task_events: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in behavior_rows:
        print_id = extract_print_id(row)
        if print_id:
            task_events[print_id].append(row)

    starts = {"cx_main_print_start", "cx_main_print_exec_start", "cx_print_task_execute_start"}
    terminals = {
        "cx_main_print_finish_success",
        "cx_main_print_finish_failed",
        "cx_main_print_exec_failed",
        "cx_main_print_exec_timeout",
        "cx_print_task_execute_success",
        "cx_print_task_execute_failed",
    }
    unresolved: list[dict[str, str]] = []
    for print_id, rows in task_events.items():
        names = {event_name(row) for row in rows}
        if names & starts and not names & terminals:
            unresolved.append(
                {
                    "print_id": print_id,
                    "first": min(filter(None, (log_time(row) for row in rows)), default=""),
                    "last": max(filter(None, (log_time(row) for row in rows)), default=""),
                }
            )
    unresolved.sort(key=lambda item: item["last"], reverse=True)
    return {
        "task_count": len(task_events),
        "unresolved": unresolved,
        "route_fallback": sum(event_name(row) == "cx_print_task_route_fallback" for row in behavior_rows),
        "duplicate_skip": sum(event_name(row) == "cx_print_task_skipped_duplicate" for row in behavior_rows),
        "retry_success": sum(event_name(row) == "cx_print_task_retry_success" for row in behavior_rows),
        "start": sum(event_name(row) == "cx_main_print_start" for row in behavior_rows),
        "finish_success": sum(event_name(row) == "cx_main_print_finish_success" for row in behavior_rows),
        "exec_success": sum(event_name(row) == "cx_main_print_exec_success" for row in behavior_rows),
    }


def render_report(rows_by_type: dict[str, list[dict[str, Any]]], warnings: list[str], meta: dict[str, Any]) -> str:
    behavior = rows_by_type.get("user_behav", [])
    api_rows = rows_by_type.get("api", [])
    perf_rows = rows_by_type.get("performance", [])
    error_rows = rows_by_type.get("error", [])
    task = print_task_summary(behavior)
    behavior_names = Counter(filter(None, (event_name(row) for row in behavior)))
    explicit_failures = [row for row in behavior if re.search(r"(failed|error|timeout)", event_name(row), re.I)]
    api_failures = [row for row in api_rows if is_api_failure(row)]
    api_latencies = [numeric_value(row, "data_cost") for row in api_rows]
    api_latencies = [value for value in api_latencies if value is not None]
    perf_latencies = [numeric_value(row, "data_resource_cost", "data_cost", "data_duration") for row in perf_rows]
    perf_latencies = [value for value in perf_latencies if value is not None]
    endpoints = Counter(normalized_url(row.get("data_url")) for row in api_rows)
    status_counts = Counter(str(row.get("data_http_status") or "(missing)") for row in api_rows)
    session_starts = sum(event_name(row) == "cx_print_session_start_success" for row in behavior)
    session_stops = sum(event_name(row) == "cx_print_session_stop_success" for row in behavior)
    latest = max((log_time(row) for rows in rows_by_type.values() for row in rows if log_time(row)), default="No records")

    lines = [
        "# Cunxin APM 客诉与行为分析",
        "",
        f"- 范围：用户 `{meta['user_id']}`，应用 `{meta['app_id']}`，上海时间 `{meta['start']}` 至 `{meta['end']}`。",
        f"- 数据截止：`{latest}`。" + (" 当天仍在进行，结论仅覆盖当前快照。" if meta["in_progress"] else ""),
        "- 原始 `data_extra`、IP、图片 URL、会话 ID、设备路径和 User-Agent 默认未输出。",
        "",
        "## 结论",
        f"- 共读取行为 `{len(behavior)}` 条、API `{len(api_rows)}` 条、前端错误 `{len(error_rows)}` 条、性能 `{len(perf_rows)}` 条。",
        f"- 显式失败/超时行为 `{len(explicit_failures)}` 条；API 非成功 `{len(api_failures)}` 条。",
        f"- 打印主流程启动 `{task['start']}` 次，执行成功 `{task['exec_success']}` 次，完成成功 `{task['finish_success']}` 次。",
    ]
    strategy = meta.get("query_strategy")
    if isinstance(strategy, dict):
        lines.insert(
            4,
            (
                "- 查询策略："
                f"每个时间片 `{strategy['window_minutes']}` 分钟，"
                f"每页 `{strategy['page_size']}` 条，"
                f"每类每片最多 `{strategy['max_pages']}` 页；"
                f"本次已发起 `{strategy['request_count']}`/`{strategy['max_requests']}` 个只读请求。"
            ),
        )

    if task["unresolved"]:
        evidence = "、".join(f"`{item['print_id']}`（最后 `{item['last']}`）" for item in task["unresolved"][:10])
        lines.append(f"- 未解析完成的打印任务 `{len(task['unresolved'])}` 个：{evidence}。它们可能仍在执行或发生完成事件漏报，应优先核对打印机队列与后续日志。")
    else:
        lines.append("- 未发现已开始但缺少终态事件的打印任务。")

    lines.extend(["", "## 会话与行为"])
    lines.append(f"- 打印会话成功启动 `{session_starts}` 次、成功停止 `{session_stops}` 次。" + (" 启停数不一致时，可能存在仍在运行的会话；需结合最后记录判断。" if session_starts != session_stops else ""))
    for name, count in behavior_names.most_common(8):
        lines.append(f"- `{name}`：`{count}` 次")
    lines.append(f"- 路由回退 `{task['route_fallback']}` 次、重复任务跳过 `{task['duplicate_skip']}` 次、重试成功 `{task['retry_success']}` 次；这些是排查信号，不能单独视为故障。")

    lines.extend(["", "## API 与性能"])
    if api_rows:
        lines.append(f"- API HTTP 状态：{', '.join(f'`{status}` {count}' for status, count in status_counts.most_common())}。")
        lines.append(
            "- 接口耗时："
            f"P50 `{percentile(api_latencies, 0.50) or 'N/A'}ms`，"
            f"P95 `{percentile(api_latencies, 0.95) or 'N/A'}ms`，"
            f"P99 `{percentile(api_latencies, 0.99) or 'N/A'}ms`，"
            f"最大 `{round(max(api_latencies)) if api_latencies else 'N/A'}ms`。"
        )
        lines.append("- 高频接口：" + "；".join(f"`{url}` {count} 次" for url, count in endpoints.most_common(5)) + "。")
    if perf_rows:
        lines.append(
            "- 资源性能："
            f"{len(perf_rows)} 条，P50 `{percentile(perf_latencies, 0.50) or 'N/A'}ms`，"
            f"P95 `{percentile(perf_latencies, 0.95) or 'N/A'}ms`，"
            f"最大 `{round(max(perf_latencies)) if perf_latencies else 'N/A'}ms`。"
        )

    lines.extend(["", "## 建议"])
    recommendations: list[str] = []
    if explicit_failures or api_failures:
        recommendations.append("先按失败时间与 `print_id` 关联前后事件，区分本地打印故障、路由问题和接口问题。")
    if task["unresolved"]:
        recommendations.append("核对未解析任务的本地打印机队列、脚本执行结果和更晚时间段的终态埋点。")
    if task["route_fallback"] or task["duplicate_skip"]:
        recommendations.append("检查二维码类型解析、打印机绑定、队列去重和本地回退策略是否符合预期。")
    if endpoints.get("/cloudapi/album_live/position_printer/list_print_queue", 0) > 1000:
        recommendations.append("评估空闲会话的队列轮询退避和心跳采样，避免高频成功请求推高服务与埋点成本。")
    if not (explicit_failures or api_failures or task["unresolved"]):
        recommendations.append("当前窗口未见明确失败证据；如客诉仍存在，请补充具体打印任务 ID、客户操作时间和现象。")
    lines.extend(f"{index}. {recommendation}" for index, recommendation in enumerate(recommendations, start=1))
    if warnings:
        lines.extend(["", "## 查询告警"])
        lines.extend(f"- {warning}" for warning in warnings)
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    validate_args(args)
    try:
        rows_by_type, warnings, meta = query_logs(args)
    except RuntimeError as error:
        print(f"APM query failed: {error}", file=sys.stderr)
        return 1
    if args.command == "query":
        if not args.save_raw:
            print("query requires --save-raw so raw telemetry has an explicit destination", file=sys.stderr)
            return 2
        print(f"Saved raw APM responses to {args.save_raw}")
        return 0
    print(render_report(rows_by_type, warnings, meta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
