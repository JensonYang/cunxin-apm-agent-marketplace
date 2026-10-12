# 结合 `cn-saas-printer` dev 代码排查

当客诉涉及客户端页面、队列、接口调用、打印流程、重试或脚本执行，并且本机存在 `cn-saas-printer` 代码时，结合代码与 APM 日志给出结论。代码基线固定为 `origin/dev`，避免把本地功能分支或未提交改动当作生产依据。

## 代码发现与基线

1. 优先使用当前工作目录或其父目录中的 `cn-saas-printer` Git 仓库；也可以使用用户明确提供的本地路径。
2. 确认仓库可读取 `origin/dev`。若该引用不存在或明显过期，只有在获得网络访问授权且本机已配置认证时才执行 `git fetch origin dev`。
3. 不要切换、重置或清理用户当前工作树。直接读取 `origin/dev`，例如：

   ```bash
   git -C <cn-saas-printer> show origin/dev:src/renderer/constants/trackEvents.fullFlow.js
   git -C <cn-saas-printer> grep -n "list_print_queue" origin/dev -- src
   ```

4. 如 `<cn-saas-printer>/scripts` 是 Git 仓库，对下载、打印、驱动或脚本问题也使用其 `origin/dev` 内容。不要为了分析而修改脚本仓库当前分支。

`cn-saas-printer` 的主仓库地址为 `http://gitlab.artisanstate.com/front/desktop/cn-saas-printer.git`，脚本仓库地址为 `http://gitlab.artisanstate.com/yangxy/scripts.git`。这些地址仅用于识别和在用户已配置认证后刷新代码；不得将用户名、密码或令牌写入命令、配置、报告或 Git remote。

## 关联方法

- 从 APM 的事件名、接口路径、时间和 `print_id` 出发，使用 `git grep origin/dev` 找到埋点定义、调用位置、请求发起处与状态更新/组件渲染处。
- 先说明日志事实，再说明代码中该事实可能经过的分支、异步边界、去重、重试、节流或错误处理；不要把代码存在的一个分支表述为该用户已实际触发。
- 对“接口有数据但页面没有显示”，至少核对：请求成功后的响应校验、状态写入、列表筛选/去重、组件条件渲染、错误捕获，以及是否有后续请求覆盖前一次响应。
- 对打印问题，继续关联队列拉取、入队、路由回退、重复跳过、下载、脚本执行和终态事件；必要时查看 `scripts` 的对应打印机脚本参数和退出码处理。
- 只引用诊断所需的文件路径、函数/事件名和代码行为。不要在报告中粘贴客户数据、密钥、机器路径或大段内部源代码。

## 报告要求

在“相关 dev 代码路径”小节中说明：使用的代码基线（`origin/dev`）、检查的文件/函数、日志与代码一致的部分、仍无法由现有埋点证明的部分。若本机没有可用代码或无法读取 `origin/dev`，明确说明“本次为仅日志结论”，不要猜测实现细节。
