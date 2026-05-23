import html
import re
import time
from datetime import datetime


def render_instance_list(instances: list[dict]) -> str:
    """
    根据 MCSM 实例数据列表生成硬核科幻风 HTML 渲染字符串
    """

    # ==================== 静态 CSS ====================
    CSS = """
    :root {
        --bg-base: #040507;
        --panel-bg: rgba(255, 255, 255, 0.015);
        --panel-border: rgba(255, 255, 255, 0.15);
        --panel-border-light: rgba(255, 255, 255, 0.05);
        --text-title: #FFFFFF;
        --text-main: #D1D5DB;
        --text-muted: #5E6572;
        --accent-cyan: #00F0FF;
        --accent-red: #FF003C;
        --accent-green: #00FF66;
        --accent-yellow: #FFD700;
        --font-family: 'JetBrains Mono', 'Noto Sans CJK SC', 'Source Han Sans CN', 'WenQuanYi Micro Hei', sans-serif;
    }
    body {
        margin: 0; padding: 0; width: 800px; background-color: var(--bg-base);
        background-image: radial-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px);
        background-size: 16px 16px; color: var(--text-main);
        font-family: var(--font-family); font-weight: 300; -webkit-font-smoothing: antialiased;
    }
    .bot-card { padding: 48px; box-sizing: border-box; display: flex; flex-direction: column; gap: 24px; border: 1px solid var(--panel-border-light); }
    .header { display: flex; justify-content: space-between; align-items: flex-start; padding-bottom: 24px; border-bottom: 1px solid var(--panel-border); position: relative; }
    .header::after { content: ''; position: absolute; left: 0; bottom: -1px; width: 120px; height: 1px; background-color: var(--accent-cyan); }
    .header-title { display: flex; flex-direction: column; gap: 10px; }
    .text-xl-en { font-size: 36px; font-weight: 100; color: var(--text-title); letter-spacing: -1px; margin: 0; line-height: 1; }
    .text-xl-zh { font-size: 20px; font-weight: 300; color: var(--accent-cyan); margin: 0; letter-spacing: 2px; }
    .text-sm-en { font-size: 12px; color: var(--text-muted); margin: 0; text-transform: uppercase; letter-spacing: 0.5px; }
    .text-sm-zh { font-size: 13px; color: var(--text-muted); margin: 0; }

    .panel { background: var(--panel-bg); border: 1px solid var(--panel-border); padding: 24px; position: relative; backdrop-filter: blur(4px); display: flex; flex-direction: column; gap: 20px; }
    .panel::before, .panel::after { content: ''; position: absolute; width: 8px; height: 8px; border: 1px solid var(--accent-cyan); }
    .panel::before { top: -1px; left: -1px; border-right: none; border-bottom: none; }
    .panel::after { bottom: -1px; right: -1px; border-left: none; border-top: none; }
    .panel-title { font-size: 12px; color: var(--text-title); text-transform: uppercase; letter-spacing: 2px; display: flex; align-items: center; gap: 8px; }
    .panel-title::before { content: '■'; font-size: 10px; color: var(--accent-cyan); }
    .decor-code { position: absolute; top: 24px; right: 24px; text-align: right; font-size: 10px; color: rgba(255, 255, 255, 0.1); line-height: 1.5; text-transform: uppercase; }

    .instance-header { display: flex; align-items: flex-start; justify-content: space-between; border-bottom: 1px solid var(--panel-border-light); padding-bottom: 16px; }
    .instance-name-box { display: flex; flex-direction: column; gap: 4px; }
    .instance-name { font-size: 24px; color: var(--text-title); font-weight: 300; letter-spacing: 1px; }
    .instance-uuid { font-size: 11px; color: var(--text-muted); letter-spacing: 1px; text-transform: uppercase; }

    .status-badge { display: flex; align-items: center; gap: 8px; padding: 6px 12px; font-size: 12px; letter-spacing: 2px; text-transform: uppercase; }
    .status-badge::before { content: ''; width: 6px; height: 6px; }
    .status-running { border: 1px solid var(--accent-green); background: rgba(0, 255, 102, 0.05); color: var(--accent-green); }
    .status-running::before { background: var(--accent-green); }
    .status-stopped { border: 1px solid var(--text-muted); background: rgba(255, 255, 255, 0.02); color: var(--text-muted); }
    .status-stopped::before { background: var(--text-muted); }
    .status-busy { border: 1px solid var(--accent-yellow); background: rgba(255, 215, 0, 0.05); color: var(--accent-yellow); }
    .status-busy::before { background: var(--accent-yellow); }

    .data-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px 24px; }
    .data-item { display: flex; flex-direction: column; gap: 6px; }
    .data-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
    .data-value { font-size: 18px; color: var(--text-title); font-weight: 300; }

    .progress-bar-bg { width: 100%; height: 2px; background: var(--panel-border-light); margin-top: 4px; position: relative; }
    .progress-bar-fill { height: 100%; background: var(--accent-cyan); position: relative; transition: width 0s; }
    .progress-bar-fill.active::after { content: ''; position: absolute; right: 0; top: -2px; height: 6px; width: 2px; background: #fff; box-shadow: 0 0 4px var(--accent-cyan); }

    .global-cmd-panel { background: rgba(0, 240, 255, 0.02); border: 1px solid rgba(0, 240, 255, 0.2); margin-top: 16px; }
    .cmd-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 24px; }
    .cmd-hint { display: flex; align-items: baseline; gap: 8px; padding: 8px 12px; background: rgba(255, 255, 255, 0.03); border: 1px solid var(--panel-border-light); font-size: 12px; color: var(--text-main); letter-spacing: 1px; }
    .cmd-hint .cmd-code { color: var(--accent-cyan); font-weight: 400; flex-shrink: 0; }
    .cmd-hint .cmd-desc { color: var(--text-muted); font-size: 11px; }
    .cmd-hint.danger .cmd-code { color: var(--accent-red); }

    .example-box { background: #000; border: 1px solid var(--panel-border); padding: 16px; font-size: 12px; color: var(--text-muted); display: flex; flex-direction: column; gap: 8px; letter-spacing: 0.5px; }
    .example-box .ex-line span.user { color: var(--accent-green); }
    .example-box .ex-line span.cmd { color: var(--text-title); }
    .footer { display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); border-top: 1px solid var(--panel-border); padding-top: 16px; text-transform: uppercase; letter-spacing: 1px; }
    """

    # ==================== 生成实例卡片列表 ====================
    instances_html = ""
    for inst in instances:
        config = inst.get("config", {})
        proc_info = inst.get("processInfo", {})

        name = config.get("nickname", "Unknown")
        uuid = inst.get("instanceUuid", "UNKNOWN_UUID")
        status_code = inst.get("status", 0)

        # CPU和内存格式化
        cpu = proc_info.get("cpu", 0.0)
        mem_bytes = proc_info.get("memory", 0)
        mem_mb = mem_bytes / (1024 * 1024)

        # 防止 CPU 过高撑爆进度条
        progress_width = min(cpu, 100)

        # 状态判定
        if status_code == 3:
            status_class = "status-running"
            status_text = "RUNNING // 运行中"
            p_bar_class = "active"
            val_color = ""
        elif status_code == 0:
            status_class = "status-stopped"
            status_text = "STOPPED // 已停止"
            p_bar_class = ""
            val_color = "color: var(--text-muted);"
        else:
            status_class = "status-busy"
            status_text = f"BUSY ({status_code}) // 忙碌中"
            p_bar_class = "active"
            val_color = ""

        # RCON 处理
        rcon_enabled = config.get("enableRcon", False)
        if rcon_enabled:
            rcon_str = f"{config.get('rconIp', '127.0.0.1')}:{config.get('rconPort', 25575)}"
            rcon_color = "color: var(--accent-cyan);"
        else:
            rcon_str = "DISABLED"
            rcon_color = "color: var(--text-muted);"

        # 时间戳处理 (到期时间)
        end_ts = config.get("endTime", 0)
        if end_ts and end_ts > 0:
            # 假设来源数据为毫秒级时间戳，除以1000转换为秒
            exp_time = datetime.fromtimestamp(end_ts / 1000).strftime('%Y-%m-%d %H:%M')
        else:
            exp_time = "PERMANENT (永久)"

        # 实例标签数据
        ins_type = config.get("type", "UNKNOWN")
        ins_env = config.get("processType", "UNKNOWN")

        instances_html += f"""
        <div class="panel">
            <div class="decor-code">TYPE: {ins_type}<br>ENV: {ins_env}</div>
            <div class="instance-header">
                <div class="instance-name-box">
                    <div class="instance-name">{name}</div>
                    <div class="instance-uuid">UUID: {uuid}</div>
                </div>
                <div class="status-badge {status_class}">{status_text}</div>
            </div>

            <div class="data-grid">
                <div class="data-item">
                    <div class="data-label">CPU / RAM</div>
                    <div class="data-value" style="{val_color}">{cpu:.1f}% / {mem_mb:.1f}M</div>
                    <div class="progress-bar-bg"><div class="progress-bar-fill {p_bar_class}" style="width: {progress_width}%;"></div></div>
                </div>
                <div class="data-item">
                    <div class="data-label">RCON Interface</div>
                    <div class="data-value" style="{rcon_color} font-size: 14px; margin-top: 4px;">{rcon_str}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Expiration</div>
                    <div class="data-value" style="font-size: 14px; margin-top: 4px;">{exp_time}</div>
                </div>
            </div>
        </div>
        """

    # ==================== 全局指令中心 ====================
    # 使用 Python 获取当前生成页面的准确时间
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    instance_count = len(instances)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>MCSM Render</title>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@100;300;400&display=swap" rel="stylesheet">
        <style>{CSS}</style>
    </head>
    <body>
        <div class="bot-card">
            <div class="header">
                <div class="header-title">
                    <p class="text-xl-en">MCSM.INSTANCE_LIST</p>
                    <h1 class="text-xl-zh">实例节点矩阵阵列</h1>
                    <p class="text-sm-zh">已连接至守护进程。共探测到 {instance_count} 个注册实例对象。</p>
                </div>
                <div style="font-size: 24px; color: var(--panel-border); font-weight: 100;">{instance_count:02d}</div>
            </div>

            {instances_html}

            <div class="panel global-cmd-panel">
                <div class="panel-title">Global Operation Center // 全局指令中心</div>

                <div class="cmd-grid">
                    <div class="cmd-hint">
                        <span class="cmd-code">/start &lt;名称&gt;</span>
                        <span class="cmd-desc">- 启动目标实例</span>
                    </div>
                    <div class="cmd-hint danger">
                        <span class="cmd-code">/stop &lt;名称&gt;</span>
                        <span class="cmd-desc">- 安全停止实例</span>
                    </div>
                    <div class="cmd-hint">
                        <span class="cmd-code">/restart &lt;名称&gt;</span>
                        <span class="cmd-desc">- 重新启动实例</span>
                    </div>
                    <div class="cmd-hint danger">
                        <span class="cmd-code">/kill &lt;名称&gt;</span>
                        <span class="cmd-desc">- 强制终止进程</span>
                    </div>
                    <div class="cmd-hint">
                        <span class="cmd-code">/send &lt;名称&gt; &lt;指令&gt;</span>
                        <span class="cmd-desc">- 向后台发送命令</span>
                    </div>
                    <div class="cmd-hint">
                        <span class="cmd-code">/log &lt;名称&gt; &lt;行数&gt;</span>
                        <span class="cmd-desc">- 获取实例日志</span>
                    </div>
                </div>

                <div class="data-label" style="margin-bottom: 8px;">Execution Examples // 执行示例</div>
                <div class="example-box">
                    <div class="ex-line">[SYS] 等待标准输入...</div>
                    <div class="ex-line"><span class="user">root@qq_bot:~$</span> <span class="cmd">/start new_name</span></div>
                    <div class="ex-line"><span class="user">root@qq_bot:~$</span> <span class="cmd">/send new_name list</span></div>
                    <div class="ex-line"><span class="user">root@qq_bot:~$</span> <span class="cmd">/log lobby 100</span></div>
                </div>
            </div>

            <div class="footer">
                <span>CREEPEBOT_RESPAWNED</span>
                <span>TS: {current_time_str} // UTC+8</span>
            </div>
        </div>
    </body>
    </html>
    """

    return html_content


def get_log_html(log: str, name: str) -> str:
    log_lines_html = []

    # 按行解析日志
    for line in log.strip().splitlines():
        line = line.strip()
        if not line:
            continue

        # 转义 HTML 字符，防止日志中的 < > 破坏 DOM 结构
        safe_line = html.escape(line)

        # 正则匹配行首所有的 [xxx] 序列及其伴随的空格
        prefix_match = re.match(r'^(?:\[.*?\]\s*)+', safe_line)

        if prefix_match:
            prefix = prefix_match.group(0)
            message = safe_line[len(prefix):]

            # 提取具体的 [xxx] 块和空白符，按彩虹颜色顺序高亮
            blocks = re.findall(r'\[.*?\]|\s+', prefix)
            formatted_prefix = ""
            color_idx = 1

            for block in blocks:
                if block.startswith('['):
                    # 取余循环 1~6 颜色
                    c_idx = ((color_idx - 1) % 6) + 1
                    formatted_prefix += f'<span class="b{c_idx}">{block}</span>'
                    color_idx += 1
                else:
                    formatted_prefix += block
            message = re.sub(r'\[.*?\]', lambda m, it=iter(range(color_idx, 10**9)): f'<span class="b{((next(it) - 1) % 6) + 1}">{m.group(0)}</span>', message)

            # 对消息正文做基础的高亮区分 (WARN/ERROR)
            msg_class = "log-msg"
            if "[ERROR]" in prefix or "Exception" in safe_line:
                msg_class += " error"
            elif "[WARN]" in prefix:
                msg_class += " warn"

            log_lines_html.append(
                f'<div class="log-line">{formatted_prefix}<span class="{msg_class}">{message}</span></div>')
        else:
            # 如果行首没有 [xxx]，当作纯文本输出
            log_lines_html.append(f'<div class="log-line"><span class="log-msg">{safe_line}</span></div>')

    # 拼接所有日志行
    log_content = "\n                ".join(log_lines_html)

    # 获取当前时间戳
    current_ts = int(time.time())

    # HTML 基准模板 (使用 __XXX__ 作为占位符，避免 f-string 语法和 CSS 的 {} 冲突)
    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MC Server Log Render</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@100;300;400&display=swap" rel="stylesheet">

    <style>
        :root {
            var(--bg-base): #040507;
            --bg-base: #040507;
            --panel-bg: rgba(255, 255, 255, 0.015);
            --panel-border: rgba(255, 255, 255, 0.15);
            --text-title: #FFFFFF;
            --text-main: #D1D5DB;
            --text-muted: #5E6572;
            --accent-cyan: #00F0FF;
            --accent-red: #FF003C;
            --accent-green: #00FF66;

            /* 彩虹高亮色序列 */
            --rb-1: #FF003C; /* 荧光红 */
            --rb-2: #FF9900; /* 琥珀橙 */
            --rb-3: #F1FA8C; /* 终端黄 */
            --rb-4: #00FF66; /* 矩阵绿 */
            --rb-5: #00F0FF; /* 节点青 */
            --rb-6: #BD93F9; /* 虚空紫 */

            --font-family: 'JetBrains Mono', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei', sans-serif;
        }

        body {
            margin: 0; padding: 0; width: 800px;
            background-color: var(--bg-base);
            background-image: radial-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px);
            background-size: 16px 16px;
            color: var(--text-main); font-family: var(--font-family);
            font-weight: 300; -webkit-font-smoothing: antialiased;
        }

        .bot-card {
            padding: 48px; box-sizing: border-box;
            display: flex; flex-direction: column; gap: 32px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        /* 头部排版 */
        .header {
            display: flex; justify-content: space-between; align-items: flex-start;
            padding-bottom: 24px; border-bottom: 1px solid var(--panel-border); position: relative;
        }
        .header::after {
            content: ''; position: absolute; left: 0; bottom: -1px; width: 120px; height: 1px; background-color: var(--accent-cyan);
        }
        .header-title { display: flex; flex-direction: column; gap: 10px; }
        .text-xl-en { font-size: 36px; font-weight: 100; color: var(--text-title); letter-spacing: -1px; margin: 0; line-height: 1; }
        .text-xl-zh { font-size: 20px; font-weight: 300; color: var(--accent-cyan); margin: 0; letter-spacing: 2px; }
        .text-sm-en { font-size: 12px; color: var(--text-muted); margin: 0; text-transform: uppercase; letter-spacing: 0.5px; }
        .text-sm-zh { font-size: 13px; color: var(--text-muted); margin: 0; }

        /* 面板容器 */
        .panel {
            background: var(--panel-bg); border: 1px solid var(--panel-border);
            padding: 24px; position: relative; backdrop-filter: blur(4px);
        }
        .panel::before, .panel::after {
            content: ''; position: absolute; width: 8px; height: 8px; border: 1px solid var(--accent-cyan);
        }
        .panel::before { top: -1px; left: -1px; border-right: none; border-bottom: none; }
        .panel::after { bottom: -1px; right: -1px; border-left: none; border-top: none; }

        .panel-title {
            font-size: 12px; color: var(--text-title); margin-bottom: 16px;
            text-transform: uppercase; letter-spacing: 2px; display: flex; align-items: center; gap: 8px;
        }
        .panel-title::before { content: '■'; font-size: 10px; color: var(--accent-cyan); }

        /* 日志终端显示区 (移除强制对齐) */
        .log-terminal {
            background-color: rgba(0, 0, 0, 0.6); border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 16px; font-size: 13px; line-height: 1.6; display: flex; flex-direction: column; gap: 6px;
            position: relative; box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.8);
        }
        .log-terminal::after { content: ''; position: absolute; right: 4px; top: 4px; bottom: 4px; width: 2px; background: rgba(255, 255, 255, 0.1); }
        .log-terminal::before { content: ''; position: absolute; right: 4px; bottom: 20%; height: 30px; width: 2px; background: var(--accent-cyan); z-index: 2; }

        .log-line { word-break: break-all; }

        .b1 { color: var(--rb-1); } .b2 { color: var(--rb-2); } .b3 { color: var(--rb-3); }
        .b4 { color: var(--rb-4); } .b5 { color: var(--rb-5); } .b6 { color: var(--rb-6); }

        .log-msg { color: var(--text-main); }
        .log-msg.warn { color: var(--rb-2); }
        .log-msg.error { color: var(--accent-red); background: rgba(255, 0, 60, 0.1); padding: 0 4px; }

        /* 底部信息 */
        .footer {
            display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted);
            border-top: 1px solid var(--panel-border); padding-top: 16px; text-transform: uppercase; letter-spacing: 1px;
        }
        .decor-code { position: absolute; top: 16px; right: 24px; text-align: right; font-size: 10px; color: rgba(255, 255, 255, 0.15); line-height: 1.5; }
    </style>
</head>
<body>
    <div class="bot-card">
        <div class="header">
            <div class="header-title">
                <p class="text-xl-en">SERVER.LOG_STREAM</p>
                <h1 class="text-xl-zh">__SERVER_NAME__</h1>
                <p class="text-sm-zh">数据流已接入。当前正在捕获节点控制台标准输出。</p>
                <p class="text-sm-en">STREAM CONNECTED. CAPTURING STDOUT FROM DAEMON.</p>
            </div>
            <div style="font-size: 24px; color: var(--panel-border); font-weight: 100;">LOG</div>
        </div>

        <div class="panel">
            <div class="decor-code">MODE: TAIL -F<br>ENCODING: UTF-8</div>
            <div class="panel-title">Console Stream // 控制台实时输出</div>

            <div class="log-terminal">
                __LOG_CONTENT__
            </div>
        </div>

        <div class="footer">
            <span>CREEPEBOT_RESPAWNED</span>
            <span>TS: __TIMESTAMP__ // UTC+8</span>
        </div>
    </div>
</body>
</html>"""

    # 替换数据占位符并返回最终 HTML
    return html_template.replace("__SERVER_NAME__", html.escape(name)) \
        .replace("__LOG_CONTENT__", log_content) \
        .replace("__TIMESTAMP__", str(current_ts))
