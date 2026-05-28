import html
import time


def generate_help_html(commands: list) -> str:
    """
    根据指令对象列表生成终端风格的帮助页面 HTML。
    修复了表格列的文本对齐问题与基线对齐问题。
    """

    # 1. 动态生成指令列表的 HTML 行
    cmd_rows_html = ""
    for cmd in commands:
        if not hasattr(cmd, 'id'): continue

        rid = cmd.id if hasattr(cmd, 'id') else cmd.get('id', '?')
        name = cmd.name if hasattr(cmd, 'name') else cmd.get('name', 'UNKNOWN')

        usage = cmd.usage if hasattr(cmd, 'usage') else cmd.get('usage', 'UNKNOWN')
        desc = cmd.desc if hasattr(cmd, 'desc') else cmd.get('desc', 'UNKNOWN')

        rid = html.escape(str(rid))
        name = html.escape(str(name))
        usage = html.escape(str(usage))
        desc = html.escape(str(desc))

        cmd_rows_html += f"""
                <div class="cmd-row">
                    <div class="cmd-id">{rid}</div>
                    <div class="cmd-name">{name}</div>
                    <div class="cmd-usage">{usage}</div>
                    <div class="cmd-desc">{desc}</div>
                </div>"""

    record_count = f"{len(commands):02d}"
    current_ts = int(time.time())

    # 2. HTML 基础骨架
    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SYS.HELP_MANUAL</title>
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
            --font-family: 'JetBrains Mono', 'Noto Sans CJK SC', 'Source Han Sans CN', 'WenQuanYi Micro Hei', sans-serif;
        }

        body {
            margin: 0; padding: 0; width: 800px; 
            background-color: var(--bg-base);
            background-image: radial-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px);
            background-size: 16px 16px;
            color: var(--text-main); font-family: var(--font-family); font-weight: 300;
            -webkit-font-smoothing: antialiased;
        }

        .bot-card {
            padding: 48px; box-sizing: border-box; display: flex; flex-direction: column; gap: 32px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

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

        .panel {
            background: var(--panel-bg); border: 1px solid var(--panel-border); padding: 24px;
            position: relative; backdrop-filter: blur(4px);
        }
        .panel::before, .panel::after {
            content: ''; position: absolute; width: 8px; height: 8px; border: 1px solid var(--accent-cyan);
        }
        .panel::before { top: -1px; left: -1px; border-right: none; border-bottom: none; }
        .panel::after { bottom: -1px; right: -1px; border-left: none; border-top: none; }

        .panel-title {
            font-size: 12px; color: var(--text-title); margin-bottom: 24px;
            text-transform: uppercase; letter-spacing: 2px; display: flex; align-items: center; gap: 8px;
        }
        .panel-title::before { content: '■'; font-size: 10px; color: var(--accent-cyan); }

        .decor-code {
            position: absolute; top: 24px; right: 24px; text-align: right;
            font-size: 10px; color: rgba(255, 255, 255, 0.1); line-height: 1.5;
        }

        .syntax-box { display: flex; flex-direction: column; gap: 16px; }
        .cmd-hint {
            display: flex; align-items: center; gap: 12px; padding: 12px 16px;
            background: rgba(0, 240, 255, 0.05); border: 1px solid rgba(0, 240, 255, 0.2);
            font-size: 13px; color: var(--text-main); letter-spacing: 1px;
        }
        .cmd-hint .prefix { color: var(--accent-cyan); font-weight: 400; }
        .cmd-hint .highlight { color: var(--text-title); font-weight: 400; }

        .param-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 8px; }
        .param-item {
            border: 1px solid var(--panel-border); padding: 10px 12px; font-size: 12px;
            display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.02);
        }
        .param-flag { color: var(--accent-cyan); font-weight: 400; background: rgba(0, 240, 255, 0.1); padding: 2px 6px; }
        .param-desc { color: var(--text-muted); letter-spacing: 1px;}
        .param-item.active { border-color: rgba(0, 240, 255, 0.4); }
        .param-item.active .param-desc { color: var(--text-main); }

        /* ================= 修改点：表格对齐优化 ================= */
        .cmd-table { display: flex; flex-direction: column; width: 100%; }

        .cmd-row {
            display: grid; 
            /* 调整列宽占比，保障名字和用法有足够空间 */
            grid-template-columns: 50px 140px 220px 1fr; 
            gap: 24px; /* 增加列间距 */
            padding: 16px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05); 
            /* 关键修改：基线对齐，确保所有列文字的底边在同一条直线上 */
            align-items: baseline; 
        }

        .cmd-row.header-row {
            padding-top: 0; padding-bottom: 12px; border-bottom: 1px solid var(--panel-border);
            text-transform: uppercase; font-size: 11px; color: var(--text-muted); letter-spacing: 1px;
        }
        .cmd-row:last-child { border-bottom: none; padding-bottom: 0; }

        .cmd-name { font-size: 14px; color: var(--text-title); font-weight: 400; }

        /* 关键修改：去除了 padding 和 border，纯文本对齐 */
        .cmd-usage { 
            font-size: 13px; color: var(--accent-cyan); font-family: 'JetBrains Mono', monospace; 
        }

        .cmd-desc { font-size: 13px; color: var(--text-main); line-height: 1.6; }

        .footer {
            display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted);
            border-top: 1px solid var(--panel-border); padding-top: 16px; text-transform: uppercase; letter-spacing: 1px;
        }
    </style>
</head>
<body>
    <div class="bot-card">
        <div class="header">
            <div class="header-title">
                <p class="text-xl-en">SYS.HELP_MANUAL</p>
                <h1 class="text-xl-zh">系统指令注册手册</h1>
                <p class="text-sm-zh">终端已就绪。正在输出可用模块的交互命令集。</p>
                <p class="text-sm-en">TERMINAL READY. OUTPUTTING INTERACTIVE COMMAND SET FOR AVAILABLE MODULES.</p>
            </div>
            <div style="font-size: 24px; color: var(--panel-border); font-weight: 100;">CMD</div>
        </div>

        <div class="panel">
            <div class="decor-code">HEX: 0x1A2B<br>MODE: QUERY<br>STATUS: OK</div>
            <div class="panel-title">Query Syntax // 检索语法</div>

            <div class="syntax-box">
                <div class="cmd-hint">
                    <span>发送指令：</span>
                    <span class="prefix">/help</span>
                    <span class="highlight">[参数] &lt;关键词&gt;</span>
                    <span style="color: var(--text-muted); margin-left: auto;">// 执行全局检索</span>
                </div>
                <div style="font-size: 12px; color: var(--text-title); margin-top: 8px;">TARGET PARAMETERS (可组合使用):</div>
                <div class="param-grid">
                    <div class="param-item active">
                        <span class="param-flag">-n</span><span class="param-desc">匹配 "名称" (默认)</span>
                    </div>
                    <div class="param-item">
                        <span class="param-flag">-u</span><span class="param-desc">匹配 "用法"</span>
                    </div>
                    <div class="param-item">
                        <span class="param-flag">-d</span><span class="param-desc">匹配 "描述"</span>
                    </div>
                </div>
                <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px; display: flex; gap: 8px; align-items: center;">
                    <span style="color: var(--accent-green);">[EXAMPLE]</span>
                    <span>查找用法和描述中包含"骰子"的指令：</span>
                    <span style="color: var(--text-title);">/help -ud 骰子</span>
                </div>
            </div>
        </div>

        <div class="panel">
            <div class="decor-code">RECORDS: __RECORDS__<br>PAGE: 01/01</div>
            <div class="panel-title">Command Registry // 指令注册表</div>

            <div class="cmd-table">
                <div class="cmd-row header-row">
                    <div>ID</div>
                    <div>Module Name // 名称</div>
                    <div>Syntax // 用法</div>
                    <div>Description // 描述与功能说明</div>
                </div>

                <!-- 动态指令列表内容 -->
                __COMMANDS_HTML__

            </div>
        </div>

        <div class="footer">
            <span>CREEPEbot respawned</span>
            <span>TS: __TIMESTAMP__ // UTC+8</span>
        </div>
    </div>
</body>
</html>"""

    # 3. 替换占位符并返回
    final_html = html_template.replace('__COMMANDS_HTML__', cmd_rows_html)
    final_html = final_html.replace('__RECORDS__', record_count)
    final_html = final_html.replace('__TIMESTAMP__', str(current_ts))

    return final_html
