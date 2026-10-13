#!/usr/bin/env python3
"""Check and bootstrap the user-scoped zentao-debug MCP integration."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Any


MCP_SERVER_NAME = "zentao-bug-report"
DEFAULT_PACKAGE = "zentao-debug@2.0.2"
DEFAULT_MCP_URL = "http://172.30.200.247:8018/mcp"
NEXUS_NPM_REGISTRY = "https://nexus.znoinc.com/repository/npm/"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def has_registered_mcp(codex_binary: str) -> bool:
    result = run([codex_binary, "mcp", "list", "--json"])
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "未知错误"
        raise RuntimeError(f"无法读取 Codex MCP 配置：{detail}")

    try:
        servers: Any = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("Codex MCP 配置返回了无效 JSON。") from error

    if not isinstance(servers, list):
        raise RuntimeError("Codex MCP 配置格式不符合预期。")
    return any(isinstance(server, dict) and server.get("name") == MCP_SERVER_NAME for server in servers)


def install_mcp(npm_binary: str, package: str, mcp_url: str) -> None:
    result = run(
        [
            npm_binary,
            "exec",
            "--yes",
            f"--registry={NEXUS_NPM_REGISTRY}",
            f"--package={package}",
            "--",
            "zentao-debug",
            "--target",
            "codex",
            "--scope",
            "user",
            "--mcp-url",
            mcp_url,
            "--yes",
        ]
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "未知错误"
        raise RuntimeError(f"zentao-debug 安装失败：{detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description="检测并安装 zentao-debug MCP。")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="仅检测，不安装。")
    mode.add_argument("--ensure", action="store_true", help="缺失时自动安装（默认）。")
    args = parser.parse_args()

    codex_binary = os.environ.get("CODEX_BINARY", "codex")
    npm_binary = os.environ.get("NPM_BINARY", "npm")
    package = os.environ.get("ZENTAO_DEBUG_PACKAGE", DEFAULT_PACKAGE)
    mcp_url = os.environ.get("ZENTAO_MCP_URL", DEFAULT_MCP_URL)

    try:
        if has_registered_mcp(codex_binary):
            print("zentao-debug 已安装并已注册 zentao-bug-report MCP。")
            return 0

        if args.check:
            print("未检测到 zentao-debug；可运行本脚本的 --ensure 自动安装。")
            return 1

        print("未检测到 zentao-debug，正在为当前用户安装并注册禅道 MCP...")
        install_mcp(npm_binary, package, mcp_url)
        if not has_registered_mcp(codex_binary):
            raise RuntimeError("安装命令已完成，但未注册 zentao-bug-report MCP。")
    except (OSError, RuntimeError) as error:
        print(f"zentao-debug 初始化失败：{error}", file=sys.stderr)
        return 2

    print("zentao-debug 安装完成，已注册 zentao-bug-report MCP；请重新打开聊天后读取禅道 Bug。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
