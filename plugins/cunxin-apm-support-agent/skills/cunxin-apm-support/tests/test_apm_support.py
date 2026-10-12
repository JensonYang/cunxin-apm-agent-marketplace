import argparse
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "apm_support.py"
SPEC = importlib.util.spec_from_file_location("apm_support", SCRIPT)
apm_support = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(apm_support)


class ApmSupportTests(unittest.TestCase):
    def test_extracts_print_id_from_malformed_payload(self):
        row = {"data_extra": '{"print_id":148857,"script_path":"C:\\broken'}
        self.assertEqual(apm_support.extract_print_id(row), "148857")

    def test_marks_started_print_without_terminal_event_unresolved(self):
        rows = [
            {"data_name": "cx_main_print_start", "log_time": "2026-09-14 10:00:01", "data_extra": '{"print_id": "100"}'},
            {"data_name": "cx_main_print_finish_success", "log_time": "2026-09-14 10:00:02", "data_extra": '{"print_id": "101"}'},
            {"data_name": "cx_main_print_exec_start", "log_time": "2026-09-14 10:00:03", "data_extra": '{"print_id": "102"}'},
            {"data_name": "cx_main_print_finish_success", "log_time": "2026-09-14 10:00:04", "data_extra": '{"print_id": "102"}'},
        ]
        summary = apm_support.print_task_summary(rows)
        self.assertEqual(summary["unresolved"], [{"print_id": "100", "first": "2026-09-14 10:00:01", "last": "2026-09-14 10:00:01"}])

    def test_report_redacts_api_query_parameters(self):
        rows = {
            "user_behav": [],
            "api": [{"log_time": "2026-09-14 10:00:00", "data_url": "/download?image_id=secret", "data_http_status": 200, "data_biz_status": "200000", "data_cost": 100}],
            "performance": [],
            "error": [],
        }
        meta = {"user_id": "1872443", "app_id": "23001", "start": "2026-09-14 00:00:00", "end": "2026-09-14 23:59:59", "in_progress": False}
        report = apm_support.render_report(rows, [], meta)
        self.assertIn("`/download`", report)
        self.assertNotIn("image_id=secret", report)

    def test_time_windows_are_adjacent_without_overlap(self):
        windows = list(
            apm_support.iter_time_windows(
                "2026-09-14 00:00:00",
                "2026-09-14 01:59:59",
                60,
            )
        )
        self.assertEqual(
            windows,
            [
                ("2026-09-14 00:00:00", "2026-09-14 00:59:59"),
                ("2026-09-14 01:00:00", "2026-09-14 01:59:59"),
            ],
        )

    def test_query_bounds_can_limit_to_a_specific_time_range(self):
        self.assertEqual(
            apm_support.query_bounds("2026-09-14", False, "10:05", "10:14:59"),
            ("2026-09-14 10:05:00", "2026-09-14 10:14:59", False),
        )

    def test_query_splits_pages_by_small_time_window(self):
        args = argparse.Namespace(
            date="2026-09-14",
            full_day=False,
            types=["user_behav"],
            page_size=2,
            max_pages=2,
            window_minutes=60,
            max_requests=10,
            app_id="23001",
            user_id="1846136",
            bizline_id=None,
            base_url="https://apm.example.test",
            save_raw=None,
        )
        payloads = []

        def fake_post(_url, payload):
            payloads.append(payload)
            if payload["log_time_start"].endswith("00:00:00") and payload["page"] == 1:
                return {"success": True, "data": {"result": [{"id": "1"}, {"id": "2"}]}}
            if payload["log_time_start"].endswith("00:00:00"):
                return {"success": True, "data": {"result": [{"id": "3"}]}}
            return {"success": True, "data": {"result": []}}

        with patch.object(
            apm_support,
            "query_bounds",
            return_value=("2026-09-14 00:00:00", "2026-09-14 01:59:59", False),
        ), patch.object(apm_support, "post_json", side_effect=fake_post):
            rows_by_type, warnings, meta = apm_support.query_logs(args)

        self.assertEqual([row["id"] for row in rows_by_type["user_behav"]], ["1", "2", "3"])
        self.assertEqual(warnings, [])
        self.assertEqual([(item["log_time_start"], item["page"]) for item in payloads], [
            ("2026-09-14 00:00:00", 1),
            ("2026-09-14 00:00:00", 2),
            ("2026-09-14 01:00:00", 1),
        ])
        self.assertEqual(meta["query_strategy"]["request_count"], 3)

    def test_query_stops_when_request_budget_is_reached(self):
        args = argparse.Namespace(
            date="2026-09-14",
            full_day=False,
            types=["user_behav"],
            page_size=2,
            max_pages=1,
            window_minutes=60,
            max_requests=1,
            app_id="23001",
            user_id="1846136",
            bizline_id=None,
            base_url="https://apm.example.test",
            save_raw=None,
        )

        with patch.object(
            apm_support,
            "query_bounds",
            return_value=("2026-09-14 00:00:00", "2026-09-14 01:59:59", False),
        ), patch.object(apm_support, "post_json", return_value={"success": True, "data": {"result": []}}) as post:
            _, warnings, meta = apm_support.query_logs(args)

        self.assertEqual(post.call_count, 1)
        self.assertTrue(any("--max-requests=1" in warning for warning in warnings))
        self.assertEqual(meta["query_strategy"]["request_count"], 1)

    def test_query_timeout_becomes_a_coverage_warning(self):
        args = argparse.Namespace(
            date="2026-09-14",
            full_day=False,
            types=["user_behav"],
            page_size=100,
            max_pages=1,
            window_minutes=60,
            max_requests=5,
            app_id="23001",
            user_id="1846136",
            bizline_id=None,
            base_url="https://apm.example.test",
            save_raw=None,
        )

        with patch.object(
            apm_support,
            "query_bounds",
            return_value=("2026-09-14 00:00:00", "2026-09-14 00:59:59", False),
        ), patch.object(apm_support, "post_json", side_effect=RuntimeError("APM request failed: timed out")):
            rows_by_type, warnings, _ = apm_support.query_logs(args)

        self.assertEqual(rows_by_type["user_behav"], [])
        self.assertTrue(any("查询失败" in warning for warning in warnings))


if __name__ == "__main__":
    unittest.main()
