# 寸心 APM 客诉与行为分析助手

这是一个 Codex 插件，用于基于只读的寸心 APM 查询接口排查“寸心来印”的生产客诉，并汇总客户行为。它结合生产 APM 数据结构和应用全流程埋点字典进行分析。

## 功能说明

- 通过 `POST /api/log/query` 按用户、日期和应用范围查询日志。
- 基于 `trackEvents.fullFlow.js` 关联登录、配置、打印会话、打印任务和退出登录等事件。
- 识别明确失败、接口状态或耗时异常、未完成打印任务、重试/降级/去重信号，以及高频轮询行为。
- 默认生成脱敏的中文 Markdown 客诉排查与行为分析报告，不展示原始事件载荷。
- 本机存在 `cn-saas-printer` 代码时，会以 `origin/dev` 为基线关联页面、接口、队列和打印脚本实现，区分“日志已证实”和“代码上可能发生”的结论。
- 支持直接提供禅道 Bug 链接：智能体会先通过 `zentao-bug-report` MCP 读取 Bug，再结合 `origin/dev` 代码；Bug 中包含明确用户/打印标识和日期时，才会追加有界 APM 查询。

## 隐私与生产安全

- 插件为只读工具，仅调用 `POST /api/log/query`。
- 不会调用 APM 的同步/刷新、账号跳转、项目上传下载、恢复或其他会产生副作用的接口。
- 除非显式传入 `--save-raw`，否则不会保存原始遥测数据。
- 报告会主动隐藏 IP、图片 URL/标识、会话 ID、本地路径、User-Agent 和原始 `data_extra`。
- 不保存、展示或提交 Git 用户名、密码、访问令牌；代码仓库刷新仅使用本机已经配置好的认证。

## 结合本地代码排查

如需同时分析 APM 与客户端实现，请在本机准备以下两个仓库，并保留可读取的 `origin/dev` 引用：

```bash
git clone http://gitlab.artisanstate.com/front/desktop/cn-saas-printer.git
cd cn-saas-printer
git fetch origin dev
git clone http://gitlab.artisanstate.com/yangxy/scripts.git scripts
git -C scripts fetch origin dev
```

智能体不会切换、重置或清理你正在使用的工作分支；它会直接读取 `origin/dev` 的代码进行对照。仓库认证请通过 Git 凭据管理器或 SSH 配置完成，不要把密码写进克隆地址、文档或命令历史。

## 禅道 MCP 接入

先按公司网络环境安装并初始化禅道客户端：

```bash
npm install zentao-debug@2.0.2 --registry=https://nexus.znoinc.com/repository/npm/ --strict-ssl=false
npx -y zentao-debug --target codex --scope user --mcp-url http://172.30.200.247:8018/mcp --yes
```

初始化会在 Codex 用户配置中添加 `zentao-bug-report` MCP 服务和对应技能；重启 Codex 后生效。之后直接粘贴禅道 Bug 链接即可。MCP 服务端负责禅道认证，客户端不要配置、保存或提交禅道账号密码。

## 同事安装

面向 ChatGPT 桌面版个人安装和 ChatGPT 工作空间管理员统一部署的完整说明，见 [ChatGPT 安装与使用指南](docs/ChatGPT安装使用指南.md)。


1. 将此仓库克隆到受信任的本地目录。
2. 在 Codex 中添加该仓库的插件市场：

   ```bash
   codex plugin marketplace add /absolute/path/to/cunxin-apm-agent-marketplace
   ```

3. 在 Codex 的已添加插件市场中安装 `cunxin-apm-support-agent`。之后遇到生产客诉、用户行为、打印 ID 或 APM 分析请求时，`cunxin-apm-support` 技能会自动启用。

本仓库当前为公开仓库。发布前请检查是否包含内部地址、凭据、客户数据或其他不应公开的信息；公开访问者不能直接修改原仓库。

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

