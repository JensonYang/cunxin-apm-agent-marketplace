import importlib.util
from pathlib import Path
import unittest

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


if __name__ == "__main__":
    unittest.main()
