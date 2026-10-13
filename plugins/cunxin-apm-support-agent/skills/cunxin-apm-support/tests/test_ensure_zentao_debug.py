"""Behavior tests for the Zentao MCP bootstrap helper."""

from __future__ import annotations

import json
import os
import pathlib
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest


SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
ENSURE_SCRIPT = SKILL_DIR / "scripts" / "ensure_zentao_debug.py"
DEFAULT_MCP_URL = "http://172.30.200.247:8018/mcp"
NEXUS_NPM_REGISTRY = "https://nexus.znoinc.com/repository/npm/"


class EnsureZentaoDebugTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp_dir.name)
        self.state_file = self.root / "zentao-ready"
        self.npm_args_file = self.root / "npm-args.json"
        self.codex = self._write_executable(
            "codex",
            """
            #!/usr/bin/env python3
            import json
            import os
            import pathlib
            import sys

            state = pathlib.Path(os.environ["STATE_FILE"])
            if sys.argv[1:] == ["mcp", "list", "--json"]:
                servers = [{"name": "zentao-bug-report"}] if state.exists() else []
                print(json.dumps(servers))
                raise SystemExit(0)
            raise SystemExit(64)
            """,
        )
        self.npm = self._write_executable(
            "npm",
            """
            #!/usr/bin/env python3
            import json
            import os
            import pathlib
            import sys

            pathlib.Path(os.environ["NPM_ARGS_FILE"]).write_text(
                json.dumps(sys.argv[1:]), encoding="utf-8"
            )
            pathlib.Path(os.environ["STATE_FILE"]).touch()
            """,
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_executable(self, name: str, body: str) -> pathlib.Path:
        path = self.root / name
        path.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ | {
            "CODEX_BINARY": str(self.codex),
            "NPM_BINARY": str(self.npm),
            "STATE_FILE": str(self.state_file),
            "NPM_ARGS_FILE": str(self.npm_args_file),
        }
        return subprocess.run(
            [sys.executable, str(ENSURE_SCRIPT), *args],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    def test_check_succeeds_without_install_when_mcp_is_registered(self) -> None:
        self.state_file.touch()

        result = self._run("--check")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.npm_args_file.exists())
        self.assertIn("已安装", result.stdout)

    def test_ensure_registers_missing_mcp_without_project_dependency(self) -> None:
        result = self._run("--ensure")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(self.npm_args_file.read_text(encoding="utf-8")),
            [
                "exec",
                "--yes",
                f"--registry={NEXUS_NPM_REGISTRY}",
                "--package=zentao-debug@2.0.2",
                "--",
                "zentao-debug",
                "--target",
                "codex",
                "--scope",
                "user",
                "--mcp-url",
                DEFAULT_MCP_URL,
                "--yes",
            ],
        )
        self.assertIn("安装完成", result.stdout)


if __name__ == "__main__":
    unittest.main()
