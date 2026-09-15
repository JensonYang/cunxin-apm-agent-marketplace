/**
 * 全流程埋点事件清单（登录 -> 配置 -> 打印 -> 退出登录）。
 *
 * 设计目标：
 * - 在一个文件里统一管理所有事件名，避免散落字符串；
 * - 可作为“事件字典”给产品/测试/后端共同对齐。
 *
 * 建议调用方式：
 *   trackFn({ name: TRACK_EVENTS.LOGIN_SUBMIT, login_type: 'sms' });
 */

/** 打印任务级埋点通用字段 */
export const PRINT_TASK_CORE_FIELDS = Object.freeze([
    'print_id',
    'album_id',
    'image_id',
    'qr_type',
]);

export const TRACK_EVENTS = Object.freeze({
    // 登录流程
    LOGIN_MODAL_SHOW: 'cx_login_modal_show', // 显示登录弹窗
    LOGIN_SEND_SMS_CLICK: 'cx_login_send_sms_click', // 点击发送短信验证码
    LOGIN_SEND_SMS_SUCCESS: 'cx_login_send_sms_success', // 发送短信验证码成功
    LOGIN_SEND_SMS_FAILED: 'cx_login_send_sms_failed', // 发送短信验证码失败
    LOGIN_SUBMIT: 'cx_login_submit', // 提交登录
    LOGIN_SUCCESS: 'cx_login_success', // 登录成功
    LOGIN_FAILED: 'cx_login_failed', // 登录失败
    LOGIN_REMEMBER_PASSWORD_TOGGLE: 'cx_login_remember_password_toggle', // 记住密码开关变更
    LOGIN_SWITCH_TYPE: 'cx_login_switch_type', // 切换登录方式（快捷/密码）

    // 配置流程 - 点位配置
    CONFIG_POINT_MODAL_SHOW: 'cx_config_point_modal_show', // 打开点位配置弹窗
    CONFIG_POINT_TOGGLE: 'cx_config_point_toggle', // 勾选/取消勾选点位
    CONFIG_POINT_TEMPLATE_TOGGLE: 'cx_config_point_template_toggle', // 勾选/取消勾选点位模板
    CONFIG_POINT_TEMPLATE_CHANGE: 'cx_config_point_template_change', // 选择点位模板值
    CONFIG_POINT_PRINTER_TOGGLE: 'cx_config_point_printer_toggle', // 勾选/取消勾选点位关联打印机
    CONFIG_POINT_PRINTER_SIZE_CHANGE: 'cx_config_point_printer_size_change', // 修改点位关联打印机尺寸
    CONFIG_POINT_SAVE_SUBMIT: 'cx_config_point_save_submit', // 提交点位配置
    CONFIG_POINT_SAVE_SUCCESS: 'cx_config_point_save_success', // 点位配置保存成功
    CONFIG_POINT_SAVE_FAILED: 'cx_config_point_save_failed', // 点位配置保存失败
    CONFIG_POINT_AUTO_PRINT_TOGGLE: 'cx_config_point_auto_print_toggle', // 点位自动打印开关变更
    CONFIG_POINT_POSTCARD_TOGGLE: 'cx_config_point_postcard_toggle', // 点位明信片模版开关变更
    CONFIG_POINT_POSTCARD_TEMPLATE_CHANGE: 'cx_config_point_postcard_template_change', // 选择明信片模版

    // 配置流程 - 打印机配置
    CONFIG_PRINTER_MODAL_SHOW: 'cx_config_printer_modal_show', // 打开打印机配置弹窗
    CONFIG_PRINTER_PAPER_OPTIONS_LOAD: 'cx_config_printer_paper_options_load', // 加载打印机纸张选项
    CONFIG_PRINTER_SAVE_SUBMIT: 'cx_config_printer_save_submit', // 提交打印机配置
    CONFIG_PRINTER_SAVE_SUCCESS: 'cx_config_printer_save_success', // 打印机配置保存成功
    CONFIG_PRINTER_SAVE_FAILED: 'cx_config_printer_save_failed', // 打印机配置保存失败
    CONFIG_PRINTER_QR_TOGGLE: 'cx_config_printer_qr_toggle', // 打印机二维码开关变更
    CONFIG_PRINTER_OVERLAY_PANEL_OPEN: 'cx_config_printer_overlay_panel_open', // 打开打印机照片叠印设置
    CONFIG_PRINTER_QR_TYPE_CHANGE: 'cx_config_printer_qr_type_change', // 修改打印机照片叠印类型
    CONFIG_PRINTER_SIZE_CHANGE: 'cx_config_printer_size_change', // 修改打印机纸张尺寸
    CONFIG_PRINT_LAYOUT_CHANGE: 'cx_config_print_layout_change', // 打印排版设置变更
    CONFIG_PRINT_MARGIN_CHANGE: 'cx_config_print_margin_change', // 打印边距设置变更

    // 打印流程 - 会话级事件
    PRINT_SESSION_START_CLICK: 'cx_print_session_start_click', // 点击开启打印
    PRINT_SESSION_START_BLOCKED: 'cx_print_session_start_blocked', // 开启打印被拦截（配置不满足）
    PRINT_SESSION_START_SUCCESS: 'cx_print_session_start_success', // 开启打印成功
    PRINT_SESSION_START_FAILED: 'cx_print_session_start_failed', // 开启打印失败
    PRINT_SESSION_STOP_CLICK: 'cx_print_session_stop_click', // 点击结束打印
    PRINT_SESSION_STOP_SUCCESS: 'cx_print_session_stop_success', // 结束打印成功
    PRINT_SESSION_STOP_FAILED: 'cx_print_session_stop_failed', // 结束打印失败
    PRINT_SESSION_PERIOD_INFORM: 'cx_print_session_period_inform', // 打印会话心跳上报
    PRINT_CONNECT_STATUS_CHECK: 'cx_print_connect_status_check', // 检查客户端连接状态
    PRINT_CONNECT_STATUS_FAILED: 'cx_print_connect_status_failed', // 连接状态检查失败

    // 打印流程 - 队列与任务级事件
    PRINT_QUEUE_PULL_START: 'cx_print_queue_pull_start', // 开始拉取打印队列（请求前先记录，有数据才上报）
    PRINT_QUEUE_PULL_SUCCESS: 'cx_print_queue_pull_success', // 拉取打印队列成功（有数据才上报）
    PRINT_QUEUE_PULL_FAILED: 'cx_print_queue_pull_failed', // 拉取打印队列失败
    PRINT_TASK_ENQUEUE: 'cx_print_task_enqueue', // 任务加入本地打印队列
    PRINT_TASK_SKIPPED_DUPLICATE: 'cx_print_task_skipped_duplicate', // 任务重复被跳过
    PRINT_TASK_METADATA_INVALID: 'cx_print_task_metadata_invalid', // 任务元数据不完整
    PRINT_TASK_ROUTE_POINT: 'cx_print_task_route_point', // 任务按点位路由打印机
    PRINT_TASK_ROUTE_FALLBACK: 'cx_print_task_route_fallback', // 任务点位路由兜底
    PRINT_TASK_ASSIGN_PRINTER: 'cx_print_task_assign_printer', // 任务分配打印机
    PRINT_TASK_QR_TYPE_RESOLVED: 'cx_print_task_qr_type_resolved', // 解析实际使用的二维码类型
    PRINT_TASK_EXECUTE_START: 'cx_print_task_execute_start', // 任务开始执行打印
    PRINT_TASK_EXECUTE_SUCCESS: 'cx_print_task_execute_success', // 任务打印成功
    PRINT_TASK_EXECUTE_FAILED: 'cx_print_task_execute_failed', // 任务打印失败
    PRINT_TASK_STATUS_NOTIFY: 'cx_print_task_status_notify', // 上报打印状态变更
    PRINT_TASK_RETRY_SUBMIT: 'cx_print_task_retry_submit', // 从完成列表重新发起打印
    PRINT_TASK_RETRY_SUCCESS: 'cx_print_task_retry_success', // 从完成列表重新发起打印成功
    PRINT_TASK_RETRY_FAILED: 'cx_print_task_retry_failed', // 从完成列表重新发起打印失败

    // 打印流程 - 主进程执行事件
    MAIN_PRINT_START: 'cx_main_print_start', // 主进程收到打印请求
    MAIN_PRINT_DOWNLOAD_START: 'cx_main_print_download_start', // 主进程开始下载图片资源
    MAIN_PRINT_DOWNLOAD_SUCCESS: 'cx_main_print_download_success', // 主进程下载图片成功
    MAIN_PRINT_OVERLAY_COMPOSED: 'cx_main_print_overlay_composed', // 主进程完成照片叠印合成
    MAIN_PRINT_OVERLAY_COMPOSE_FAILED: 'cx_main_print_overlay_compose_failed', // 主进程照片叠印合成失败
    MAIN_PRINT_SCRIPT_SELECTED: 'cx_main_print_script_selected', // 主进程选择打印脚本
    MAIN_PRINT_EXEC_START: 'cx_main_print_exec_start', // 主进程开始执行打印命令
    MAIN_PRINT_EXEC_SUCCESS: 'cx_main_print_exec_success', // 主进程执行打印命令成功
    MAIN_PRINT_EXEC_FAILED: 'cx_main_print_exec_failed', // 主进程执行打印命令失败
    MAIN_PRINT_EXEC_TIMEOUT: 'cx_main_print_exec_timeout', // 主进程执行打印超时
    MAIN_PRINT_FINISH_SUCCESS: 'cx_main_print_finish_success', // 主进程打印流程完成（成功）
    MAIN_PRINT_FINISH_FAILED: 'cx_main_print_finish_failed', // 主进程打印流程完成（失败）

    // 退出登录流程
    LOGOUT_CLICK: 'cx_logout_click', // 点击退出登录入口
    LOGOUT_CONFIRM: 'cx_logout_confirm', // 确认退出登录
    LOGOUT_SUCCESS: 'cx_logout_success', // 退出登录成功
    LOGOUT_FAILED: 'cx_logout_failed', // 退出登录失败
    AUTH_FORCED_LOGOUT: 'cx_auth_forced_logout', // 鉴权失效导致被动登出
});

/**
 * 事件定义表（用于文档化）：
 * - name: 事件名（与 TRACK_EVENTS 对齐）
 * - stage: 所属流程阶段（login/config/print/logout）
 * - trigger: 触发时机说明
 * - requiredFields: 建议的必传字段（用于保证分析可用性）
 */
export const FULL_FLOW_TRACK_EVENT_DEFINITIONS = [
    // 登录流程
    {
        name: TRACK_EVENTS.LOGIN_MODAL_SHOW,
        stage: 'login',
        trigger: 'login modal opens',
        requiredFields: [],
    },
    {
        name: TRACK_EVENTS.LOGIN_SEND_SMS_CLICK,
        stage: 'login',
        trigger: 'user clicks send sms code',
        requiredFields: ['mobile_masked'],
    },
    {
        name: TRACK_EVENTS.LOGIN_SEND_SMS_SUCCESS,
        stage: 'login',
        trigger: 'sms code sent successfully',
        requiredFields: ['mobile_masked'],
    },
    {
        name: TRACK_EVENTS.LOGIN_SEND_SMS_FAILED,
        stage: 'login',
        trigger: 'sms code send failed',
        requiredFields: ['mobile_masked', 'error_message'],
    },
    {
        name: TRACK_EVENTS.LOGIN_SUBMIT,
        stage: 'login',
        trigger: 'user submits login',
        requiredFields: ['login_type'],
    },
    {
        name: TRACK_EVENTS.LOGIN_SUCCESS,
        stage: 'login',
        trigger: 'login success',
        requiredFields: ['login_type', 'user_id'],
    },
    {
        name: TRACK_EVENTS.LOGIN_FAILED,
        stage: 'login',
        trigger: 'login failed',
        requiredFields: ['login_type', 'error_message'],
    },
    {
        name: TRACK_EVENTS.LOGIN_REMEMBER_PASSWORD_TOGGLE,
        stage: 'login',
        trigger: 'remember password toggled',
        requiredFields: ['enabled'],
    },
    {
        name: TRACK_EVENTS.LOGIN_SWITCH_TYPE,
        stage: 'login',
        trigger: 'switch between sms/password login tab',
        requiredFields: ['from_type', 'to_type'],
    },

    // 配置流程
    {
        name: TRACK_EVENTS.CONFIG_POINT_MODAL_SHOW,
        stage: 'config',
        trigger: 'point modal opens',
        requiredFields: ['source'],
    },
    {
        name: TRACK_EVENTS.CONFIG_POINT_TOGGLE,
        stage: 'config',
        trigger: 'toggle point selection',
        requiredFields: ['enc_position_id', 'point_name', 'enabled'],
    },
    {
        name: TRACK_EVENTS.CONFIG_POINT_TEMPLATE_TOGGLE,
        stage: 'config',
        trigger: 'toggle point template selection',
        requiredFields: ['enc_position_id', 'point_name', 'template_type', 'enabled'],
    },
    {
        name: TRACK_EVENTS.CONFIG_POINT_TEMPLATE_CHANGE,
        stage: 'config',
        trigger: 'change point template option',
        requiredFields: [
            'enc_position_id',
            'point_name',
            'template_type',
            'template_id',
            'template_name',
        ],
    },
    {
        name: TRACK_EVENTS.CONFIG_POINT_PRINTER_TOGGLE,
        stage: 'config',
        trigger: 'toggle point printer selection',
        requiredFields: ['enc_position_id', 'point_name', 'printer_name', 'selected_size', 'enabled'],
    },
    {
        name: TRACK_EVENTS.CONFIG_POINT_PRINTER_SIZE_CHANGE,
        stage: 'config',
        trigger: 'change point printer size',
        requiredFields: ['enc_position_id', 'point_name', 'printer_name', 'selected_size'],
    },
    {
        name: TRACK_EVENTS.CONFIG_POINT_SAVE_SUBMIT,
        stage: 'config',
        trigger: 'submit point config',
        requiredFields: ['selected_count', 'auto_print_count', 'selected_points'],
    },
    {
        name: TRACK_EVENTS.CONFIG_POINT_SAVE_SUCCESS,
        stage: 'config',
        trigger: 'save point config success',
        requiredFields: ['selected_count', 'auto_print_count', 'selected_points'],
    },
    {
        name: TRACK_EVENTS.CONFIG_POINT_SAVE_FAILED,
        stage: 'config',
        trigger: 'save point config failed',
        requiredFields: ['error_message', 'selected_points'],
    },
    {
        name: TRACK_EVENTS.CONFIG_POINT_AUTO_PRINT_TOGGLE,
        stage: 'config',
        trigger: 'toggle auto print on point',
        requiredFields: ['enc_position_id', 'point_name', 'printer_name', 'selected_size', 'enabled'],
    },
    {
        name: TRACK_EVENTS.CONFIG_POINT_POSTCARD_TOGGLE,
        stage: 'config',
        trigger: 'toggle postcard template on point printer',
        requiredFields: ['enc_position_id', 'point_name', 'printer_name', 'enabled'],
    },
    {
        name: TRACK_EVENTS.CONFIG_POINT_POSTCARD_TEMPLATE_CHANGE,
        stage: 'config',
        trigger: 'change postcard template on point printer',
        requiredFields: ['enc_position_id', 'point_name', 'printer_name', 'template_id', 'template_name'],
    },
    {
        name: TRACK_EVENTS.CONFIG_PRINTER_MODAL_SHOW,
        stage: 'config',
        trigger: 'printer modal opens',
        requiredFields: ['source'],
    },
    {
        name: TRACK_EVENTS.CONFIG_PRINTER_PAPER_OPTIONS_LOAD,
        stage: 'config',
        trigger: 'load printer paper options',
        requiredFields: ['printer_name'],
    },
    {
        name: TRACK_EVENTS.CONFIG_PRINTER_SAVE_SUBMIT,
        stage: 'config',
        trigger: 'submit printer config',
        requiredFields: ['selected_printer_count'],
    },
    {
        name: TRACK_EVENTS.CONFIG_PRINTER_SAVE_SUCCESS,
        stage: 'config',
        trigger: 'save printer config success',
        requiredFields: ['selected_printer_count', 'selected_sizes'],
    },
    {
        name: TRACK_EVENTS.CONFIG_PRINTER_SAVE_FAILED,
        stage: 'config',
        trigger: 'save printer config failed',
        requiredFields: ['error_message'],
    },
    {
        name: TRACK_EVENTS.CONFIG_PRINTER_QR_TOGGLE,
        stage: 'config',
        trigger: 'toggle print qr on printer',
        requiredFields: ['printer_name', 'enabled', 'qr_type'],
    },
    {
        name: TRACK_EVENTS.CONFIG_PRINTER_OVERLAY_PANEL_OPEN,
        stage: 'config',
        trigger: 'open a printer photo overlay settings panel',
        requiredFields: ['printer_name', 'qr_type', 'photo_overlay_enabled'],
    },
    {
        name: TRACK_EVENTS.CONFIG_PRINTER_QR_TYPE_CHANGE,
        stage: 'config',
        trigger: 'change a printer photo overlay type',
        requiredFields: ['printer_name', 'previous_qr_type', 'qr_type'],
    },
    {
        name: TRACK_EVENTS.CONFIG_PRINTER_SIZE_CHANGE,
        stage: 'config',
        trigger: 'change a printer paper size',
        requiredFields: ['printer_name', 'previous_selected_size', 'selected_size'],
    },
    {
        name: TRACK_EVENTS.CONFIG_PRINT_LAYOUT_CHANGE,
        stage: 'config',
        trigger: 'change print layout',
        requiredFields: ['layout'],
    },
    {
        name: TRACK_EVENTS.CONFIG_PRINT_MARGIN_CHANGE,
        stage: 'config',
        trigger: 'change print margin',
        requiredFields: ['margin_mm'],
    },

    // 打印流程
    {
        name: TRACK_EVENTS.PRINT_SESSION_START_CLICK,
        stage: 'print',
        trigger: 'click start print session',
        requiredFields: ['selected_printer_count', 'selected_sizes'],
    },
    {
        name: TRACK_EVENTS.PRINT_SESSION_START_BLOCKED,
        stage: 'print',
        trigger: 'start blocked by invalid config',
        requiredFields: ['reason', 'missing_items'],
    },
    {
        name: TRACK_EVENTS.PRINT_SESSION_START_SUCCESS,
        stage: 'print',
        trigger: 'print session start success',
        requiredFields: ['selected_printer_count', 'selected_sizes'],
    },
    {
        name: TRACK_EVENTS.PRINT_SESSION_START_FAILED,
        stage: 'print',
        trigger: 'print session start failed',
        requiredFields: ['error_message'],
    },
    {
        name: TRACK_EVENTS.PRINT_QUEUE_PULL_START,
        stage: 'print',
        trigger: 'record before queue pull request, report only when records exist',
        requiredFields: [
            'record_count',
            'pull_params',
            'api_response',
            'pull_started_at',
            'queue_tasks',
        ],
    },
    {
        name: TRACK_EVENTS.PRINT_QUEUE_PULL_SUCCESS,
        stage: 'print',
        trigger: 'queue pull success, report only when records exist',
        requiredFields: [
            'record_count',
            'pull_params',
            'api_response',
            'pull_started_at',
            'queue_tasks',
        ],
    },
    {
        name: TRACK_EVENTS.PRINT_QUEUE_PULL_FAILED,
        stage: 'print',
        trigger: 'queue poll failed',
        requiredFields: ['error_message'],
    },
    {
        name: TRACK_EVENTS.PRINT_TASK_ENQUEUE,
        stage: 'print',
        trigger: 'task added to local print queue',
        requiredFields: ['print_id', 'print_size', 'copies', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.PRINT_TASK_SKIPPED_DUPLICATE,
        stage: 'print',
        trigger: 'task skipped because duplicate',
        requiredFields: [...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.PRINT_TASK_METADATA_INVALID,
        stage: 'print',
        trigger: 'task metadata incomplete and marked failed',
        requiredFields: [...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.PRINT_TASK_ROUTE_POINT,
        stage: 'print',
        trigger: 'route task printers by point config',
        requiredFields: [
            'position_id',
            'point_name',
            'auto_print',
            'candidate_printers',
            'matched_printers',
            ...PRINT_TASK_CORE_FIELDS,
        ],
    },
    {
        name: TRACK_EVENTS.PRINT_TASK_ROUTE_FALLBACK,
        stage: 'print',
        trigger: 'fallback because point route cannot be applied strictly',
        requiredFields: ['reason', 'position_id', 'auto_print', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.PRINT_TASK_ASSIGN_PRINTER,
        stage: 'print',
        trigger: 'task assigned to a printer',
        requiredFields: ['printer_name', 'selected_size', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.PRINT_TASK_QR_TYPE_RESOLVED,
        stage: 'print',
        trigger: 'resolve QR type used for actual print',
        requiredFields: ['qr_type_source', 'queue_qr_type', 'printer_qr_type', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.PRINT_TASK_EXECUTE_START,
        stage: 'print',
        trigger: 'task starts actual print call',
        requiredFields: ['printer_name', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.PRINT_TASK_EXECUTE_SUCCESS,
        stage: 'print',
        trigger: 'task print success',
        requiredFields: ['printer_name', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.PRINT_TASK_EXECUTE_FAILED,
        stage: 'print',
        trigger: 'task print failed',
        requiredFields: ['printer_name', 'error_message', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.PRINT_TASK_STATUS_NOTIFY,
        stage: 'print',
        trigger: 'notify backend print status change',
        requiredFields: ['print_status', 'printer_name', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.PRINT_TASK_RETRY_SUBMIT,
        stage: 'print',
        trigger: 'submit retry from completed list',
        requiredFields: ['retry_source', 'requested_print_size', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.PRINT_TASK_RETRY_SUCCESS,
        stage: 'print',
        trigger: 'retry from completed list succeeds',
        requiredFields: ['retry_source', 'requested_print_size', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.PRINT_TASK_RETRY_FAILED,
        stage: 'print',
        trigger: 'retry from completed list fails',
        requiredFields: ['retry_source', 'error_message', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.MAIN_PRINT_START,
        stage: 'print',
        trigger: 'main process receives print request',
        requiredFields: ['printer_name', 'paper_size', 'copies', 'layout', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.MAIN_PRINT_DOWNLOAD_START,
        stage: 'print',
        trigger: 'main process starts downloading image',
        requiredFields: ['printer_name', 'paper_size', 'copies', 'layout', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.MAIN_PRINT_DOWNLOAD_SUCCESS,
        stage: 'print',
        trigger: 'main process download image success',
        requiredFields: ['printer_name', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.MAIN_PRINT_OVERLAY_COMPOSED,
        stage: 'print',
        trigger: 'main process completes photo overlay composition',
        requiredFields: ['printer_name', 'photo_overlay_enabled', 'overlay_rendered', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.MAIN_PRINT_OVERLAY_COMPOSE_FAILED,
        stage: 'print',
        trigger: 'main process fails photo overlay composition',
        requiredFields: ['printer_name', 'photo_overlay_enabled', 'error_message', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.MAIN_PRINT_SCRIPT_SELECTED,
        stage: 'print',
        trigger: 'main process selects print script',
        requiredFields: ['printer_name', 'script', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.MAIN_PRINT_EXEC_START,
        stage: 'print',
        trigger: 'main process executes print command',
        requiredFields: ['printer_name', 'script', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.MAIN_PRINT_EXEC_SUCCESS,
        stage: 'print',
        trigger: 'main process print command success',
        requiredFields: ['printer_name', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.MAIN_PRINT_EXEC_FAILED,
        stage: 'print',
        trigger: 'main process print command failed',
        requiredFields: ['printer_name', 'error_message', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.MAIN_PRINT_EXEC_TIMEOUT,
        stage: 'print',
        trigger: 'main process print command timeout',
        requiredFields: ['printer_name', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.MAIN_PRINT_FINISH_SUCCESS,
        stage: 'print',
        trigger: 'main process print flow finished successfully',
        requiredFields: ['printer_name', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.MAIN_PRINT_FINISH_FAILED,
        stage: 'print',
        trigger: 'main process print flow failed',
        requiredFields: ['printer_name', 'error_message', ...PRINT_TASK_CORE_FIELDS],
    },
    {
        name: TRACK_EVENTS.PRINT_SESSION_STOP_CLICK,
        stage: 'print',
        trigger: 'click stop print session',
        requiredFields: ['pending_count', 'printing_count'],
    },
    {
        name: TRACK_EVENTS.PRINT_SESSION_STOP_SUCCESS,
        stage: 'print',
        trigger: 'stop print session success',
        requiredFields: [],
    },
    {
        name: TRACK_EVENTS.PRINT_SESSION_STOP_FAILED,
        stage: 'print',
        trigger: 'stop print session failed',
        requiredFields: ['error_message'],
    },
    {
        name: TRACK_EVENTS.PRINT_SESSION_PERIOD_INFORM,
        stage: 'print',
        trigger: 'periodic heartbeat report',
        requiredFields: [],
    },
    {
        name: TRACK_EVENTS.PRINT_CONNECT_STATUS_CHECK,
        stage: 'print',
        trigger: 'check connect status with server',
        requiredFields: ['status'],
    },
    {
        name: TRACK_EVENTS.PRINT_CONNECT_STATUS_FAILED,
        stage: 'print',
        trigger: 'connect status check failed',
        requiredFields: ['error_message'],
    },

    // 退出登录流程
    {
        name: TRACK_EVENTS.LOGOUT_CLICK,
        stage: 'logout',
        trigger: 'click logout entry',
        requiredFields: [],
    },
    {
        name: TRACK_EVENTS.LOGOUT_CONFIRM,
        stage: 'logout',
        trigger: 'confirm logout in modal',
        requiredFields: ['printing_count', 'pending_count'],
    },
    {
        name: TRACK_EVENTS.LOGOUT_SUCCESS,
        stage: 'logout',
        trigger: 'logout completed',
        requiredFields: [],
    },
    {
        name: TRACK_EVENTS.LOGOUT_FAILED,
        stage: 'logout',
        trigger: 'logout request failed',
        requiredFields: ['error_message'],
    },
    {
        name: TRACK_EVENTS.AUTH_FORCED_LOGOUT,
        stage: 'logout',
        trigger: 'forced logout from AUTH_LOGOUT event',
        requiredFields: ['reason'],
    },
];

/** @type {{ pullParams: object, startedAt: number } | null} */
let pendingPrintQueuePull = null;

/**
 * 打印队列拉取：接口请求前先本地记录 START，不立即上报。
 */
export function recordPrintQueuePullStart(pullParams = {}) {
    pendingPrintQueuePull = {
        pullParams,
        startedAt: Date.now(),
    };
}

/**
 * 打印队列拉取：仅当接口返回有数据时，才上报 START + SUCCESS。
 */
export function reportPrintQueuePullIfHasData({
    apiResponse,
    recordCount,
    pullParams,
    queueTasks = [],
} = {}) {
    if (!recordCount || recordCount <= 0) {
        pendingPrintQueuePull = null;
        return;
    }

    const startedAt = pendingPrintQueuePull?.startedAt ?? Date.now();
    const resolvedPullParams = pullParams ?? pendingPrintQueuePull?.pullParams ?? {};
    pendingPrintQueuePull = null;
    const payload = {
        record_count: recordCount,
        pull_params: resolvedPullParams,
        api_response: apiResponse,
        pull_started_at: startedAt,
        queue_tasks: queueTasks,
    };

    trackFn({
        name: TRACK_EVENTS.PRINT_QUEUE_PULL_START,
        ...payload,
    });
    trackFn({
        name: TRACK_EVENTS.PRINT_QUEUE_PULL_SUCCESS,
        ...payload,
        pull_finished_at: Date.now(),
    });
}

export function clearPrintQueuePullPending() {
    pendingPrintQueuePull = null;
}

/**
 * 渲染进程埋点上报包装函数。
 *
 * 约定：
 * - 入参必须包含 name；
 * - 其余字段会透传到 data；
 * - 自动追加 timestamp（毫秒时间戳）；
 * - best-effort，不允许因埋点失败影响主业务流程。
 */
export function trackFn(payload = {}) {
    if (!payload || typeof payload !== 'object') return;
    const { name, ...ext } = payload;
    if (!name) return;

    try {
        window.logger?.track?.({
            data: {
                name,
                ...ext,
                timestamp: Date.now(),
            },
        });
    } catch (_error) {
        // 埋点失败时静默处理，避免影响业务流程
    }
}
