import time
from typing import List, Any


def get_command_list_html(enabled_commands: List[Any], all_commands: List[Any]) -> str:
    """
    根据传入的指令列表渲染终端风格的 HTML
    :param enabled_commands: 当前已启用的指令对象列表
    :param all_commands: 所有注册的指令对象列表
    """

    # 提取已启用的指令对象（通过比较 id 或对象本身）
    # 假设对象有 id 属性，如果没有则回退到通过对象在列表中的引用判断
    enabled_ids = {getattr(cmd, 'id', id(cmd)) for cmd in enabled_commands}
    # ================= 动态生成指令列表 =================
    list_rows_html = ""
    for i, cmd in enumerate(all_commands):
        # 获取属性，如果没有 id 属性则默认使用索引
        cmd_id = getattr(cmd, 'id', i)
        cmd_name = getattr(cmd, 'name', 'UNKNOWN_CMD')
        cmd_desc = getattr(cmd, 'desc', 'No description available.')

        # 判断是否被启用
        is_enabled = getattr(cmd, 'id', id(cmd)) in enabled_ids

        if is_enabled:
            row_class = "list-row active"
            status_class = "cell-status status-enabled"
            status_text = "ENABLED"
        else:
            row_class = "list-row inactive"
            status_class = "cell-status status-disabled"
            status_text = "DISABLED"

        # 格式化 ID 为两位数（例如 "0" 变成 "00"），增强机器感
        formatted_id = str(cmd_id)

        list_rows_html += f"""
                <div class="{row_class}">
                    <div class="cell-id">{formatted_id}</div>
                    <div class="cell-name">{cmd_name}</div>
                    <div class="cell-desc">{cmd_desc}</div>
                    <div class="{status_class}">{status_text}</div>
                </div>"""
    # ================= 时间戳处理 =================
    current_ts = int(time.time())
    # ================= HTML 模板拼接 =================
    # 使用常量字符串避免 CSS 中大量大括号导致 f-string 解析错误
    HTML_HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Command Manager Terminal</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@100;300;400&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #040507;
            --panel-bg: rgba(255, 255, 255, 0.015);
            --panel-border: rgba(255, 255, 255, 0.15);
            --text-title: #FFFFFF;
            --text-main: #D1D5DB;
            --text-muted: #5E6572;
            --accent-cyan: #00F0FF;
            --accent-red: #FF003C;
            --accent-green: #00FF66;
            --accent-yellow: #FFB300;
            --font-family: 'JetBrains Mono', 'Noto Sans CJK SC', 'Source Han Sans CN', 'WenQuanYi Micro Hei', sans-serif;
        }
        body { margin: 0; padding: 0; width: 800px; background-color: var(--bg-base); background-image: radial-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px); background-size: 16px 16px; color: var(--text-main); font-family: var(--font-family); font-weight: 300; -webkit-font-smoothing: antialiased; }
        .bot-card { padding: 48px; box-sizing: border-box; display: flex; flex-direction: column; gap: 32px; border: 1px solid rgba(255, 255, 255, 0.05); }
        .header { display: flex; justify-content: space-between; align-items: flex-start; padding-bottom: 24px; border-bottom: 1px solid var(--panel-border); position: relative; }
        .header::after { content: ''; position: absolute; left: 0; bottom: -1px; width: 120px; height: 1px; background-color: var(--accent-cyan); }
        .header-title { display: flex; flex-direction: column; gap: 10px; }
        .text-xl-en { font-size: 36px; font-weight: 100; color: var(--text-title); letter-spacing: -1px; margin: 0; line-height: 1; }
        .text-xl-zh { font-size: 20px; font-weight: 300; color: var(--accent-cyan); margin: 0; letter-spacing: 2px; }
        .text-sm-en { font-size: 12px; color: var(--text-muted); margin: 0; text-transform: uppercase; letter-spacing: 0.5px; }
        .text-sm-zh { font-size: 13px; color: var(--text-muted); margin: 0; }

        .panel { background: var(--panel-bg); border: 1px solid var(--panel-border); padding: 24px; position: relative; backdrop-filter: blur(4px); }
        .panel::before, .panel::after { content: ''; position: absolute; width: 8px; height: 8px; border: 1px solid var(--accent-cyan); }
        .panel::before { top: -1px; left: -1px; border-right: none; border-bottom: none; }
        .panel::after { bottom: -1px; right: -1px; border-left: none; border-top: none; }
        .panel-title { font-size: 12px; color: var(--text-title); margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px; display: flex; align-items: center; gap: 8px; }
        .panel-title::before { content: '■'; font-size: 10px; color: var(--accent-cyan); }
        .decor-code { position: absolute; top: 24px; right: 24px; text-align: right; font-size: 10px; color: rgba(255, 255, 255, 0.1); line-height: 1.5; }
        .manual-box { display: flex; flex-direction: column; gap: 16px; }
        .manual-meta { display: flex; gap: 24px; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; padding-bottom: 16px; border-bottom: 1px dashed rgba(255, 255, 255, 0.1); }
        .meta-item { display: flex; gap: 8px; align-items: center; }
        .meta-label { color: var(--text-muted); }
        .meta-value { color: var(--accent-yellow); font-weight: 400; }
        .cmd-hint-container { display: flex; gap: 16px; flex-wrap: wrap; }
        .cmd-hint { display: flex; align-items: center; gap: 8px; padding: 8px 16px; background: rgba(0, 240, 255, 0.05); border: 1px solid rgba(0, 240, 255, 0.2); font-size: 12px; color: var(--text-main); letter-spacing: 1px; }
        .cmd-hint .prefix { color: var(--text-muted); }
        .cmd-hint .cmd-code { color: var(--accent-cyan); font-weight: 400; text-transform: lowercase; }
        .cmd-note { font-size: 12px; color: var(--text-muted); line-height: 1.6; }
        .list-container { display: flex; flex-direction: column; gap: 8px; }
        .list-header { display: grid; grid-template-columns: 60px 140px 1fr 100px; gap: 16px; padding: 8px 16px; font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid var(--panel-border); }
        .list-row { display: grid; grid-template-columns: 60px 140px 1fr 100px; gap: 16px; align-items: center; padding: 12px 16px; background: rgba(255, 255, 255, 0.02); border: 1px solid transparent; }
        .list-row:nth-child(even) { background: transparent; }
        .list-row.active { border-left: 2px solid var(--accent-green); }
        .list-row.inactive { border-left: 2px solid var(--accent-red); opacity: 0.7; }
        .cell-id { font-size: 14px; color: var(--text-muted); }
        .cell-id::before { content: 'ID:'; font-size: 10px; opacity: 0.5; margin-right: 2px; }
        .cell-name { font-size: 14px; color: var(--text-title); font-weight: 400; letter-spacing: 1px; }
        .cell-desc { font-size: 12px; color: var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .cell-status { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; display: flex; align-items: center; gap: 6px; }
        .status-enabled { color: var(--accent-green); }
        .status-enabled::before { content: '■'; font-size: 10px; }
        .status-disabled { color: var(--accent-red); }
        .status-disabled::before { content: '■'; font-size: 10px; }
        .footer { display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); border-top: 1px solid var(--panel-border); padding-top: 16px; text-transform: uppercase; letter-spacing: 1px; }
    </style>
</head>
<body>
    <div class="bot-card">
        <div class="header">
            <div class="header-title">
                <p class="text-xl-en">SYS.CMD_REGISTRY</p>
                <h1 class="text-xl-zh">模块状态管理中心</h1>
                <p class="text-sm-zh">当前显示该会话下的模块装载情况。仅授权管理员可操作。</p>
                <p class="text-sm-en">DISPLAYING CURRENT SESSION MODULE STATUS. ADMIN CLEARANCE REQUIRED.</p>
            </div>
            <div style="font-size: 24px; color: var(--panel-border); font-weight: 100;">02</div>
        </div>
        <div class="panel">
            <div class="decor-code">HEX: 0xCF12<br>ROOT: REQUIRED</div>
            <div class="panel-title">Operation Manual // 操作指南</div>
            <div class="manual-box">
                <div class="manual-meta">
                    <div class="meta-item"><span class="meta-label">AUTH_LEVEL (权限):</span> <span class="meta-value">LVL 1+</span></div>
                    <div class="meta-item"><span class="meta-label">SCOPE (作用域):</span> <span class="meta-value">CURRENT SESSION (当前会话)</span></div>
                </div>
                <div class="cmd-note">
                    通过指定指令的 3 位字母 ID 进行批量开启或关闭。<br>
                    参数 [ <span style="color:var(--accent-green)">-e</span> ] 为装载 (Enable)，参数 [ <span style="color:var(--accent-red)">-d</span> ] 为卸载 (Disable)。
                    关键字 <span style="color:var(--accent-yellow)">all</span> 表示全部指令。
                </div>
                <div class="cmd-hint-container">
                    <div class="cmd-hint">
                        <span class="prefix">&gt; 启用指令示例：</span>
                        <span class="cmd-code">/cmd -e hlp ech prf</span>
                    </div>
                    <div class="cmd-hint" style="border-color: rgba(255, 0, 60, 0.2); background: rgba(255, 0, 60, 0.05);">
                        <span class="prefix">&gt; 禁用指令示例：</span>
                        <span style="color: var(--accent-red); font-weight: 400; text-transform: lowercase;">/cmd -d all</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="panel">
            <div class="panel-title">Module Registry // 已注册模块列表</div>
            <div class="list-container">
                <div class="list-header">
                    <div>UID</div>
                    <div>CMD_NAME</div>
                    <div>DESCRIPTION</div>
                    <div>STATUS</div>
                </div>"""
    HTML_TAIL = f"""
            </div>
        </div>
        <div class="footer">
            <span>CREEPEBOT_RESPAWNED</span>
            <span>TS: {current_ts} // UTC+8</span>
        </div>
    </div>
</body>
</html>"""
    # 组装返回最终 HTML
    return HTML_HEAD + list_rows_html + HTML_TAIL
