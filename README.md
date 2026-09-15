# 寸心 APM 客诉与行为分析助手

这是一个 Codex 插件，用于基于只读的寸心 APM 查询接口排查“寸心来印”的生产客诉，并汇总客户行为。它结合生产 APM 数据结构和应用全流程埋点字典进行分析。

## 功能说明

- 通过 `POST /api/log/query` 按用户、日期和应用范围查询日志。
- 基于 `trackEvents.fullFlow.js` 关联登录、配置、打印会话、打印任务和退出登录等事件。
- 识别明确失败、接口状态或耗时异常、未完成打印任务、重试/降级/去重信号，以及高频轮询行为。
- 默认生成脱敏的中文 Markdown 客诉排查与行为分析报告，不展示原始事件载荷。

## 隐私与生产安全

- 插件为只读工具，仅调用 `POST /api/log/query`。
- 不会调用 APM 的同步/刷新、账号跳转、项目上传下载、恢复或其他会产生副作用的接口。
- 除非显式传入 `--save-raw`，否则不会保存原始遥测数据。
- 报告会主动隐藏 IP、图片 URL/标识、会话 ID、本地路径、User-Agent 和原始 `data_extra`。

## 同事安装

1. 将此仓库克隆到受信任的本地目录。
2. 在 Codex 中添加该仓库的插件市场：

   ```bash
   codex plugin marketplace add /absolute/path/to/cunxin-apm-agent-marketplace
   ```

3. 在 Codex 的已添加插件市场中安装 `cunxin-apm-support-agent`。之后遇到生产客诉、用户行为、打印 ID 或 APM 分析请求时，`cunxin-apm-support` 技能会自动启用。

请保持仓库为私有仓库：埋点字典和生产 APM 地址均属于公司内部资产。

## 直接验证

在插件技能目录中执行：

```bash
python3 scripts/apm_support.py report --user-id 1872443 --date 2026-09-14 --app-id 23001
python3 -m unittest discover -s tests -v
```

仅在已获得授权且确需保留证据快照时执行：

```bash
python3 scripts/apm_support.py query --user-id 1872443 --date 2026-09-14 --save-raw .apm-snapshots/1872443-2026-09-14
```

