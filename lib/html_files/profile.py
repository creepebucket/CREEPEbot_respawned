import time
from typing import List


def get_profile_html(qid: int, gid: int, perm: int, global_perm: str, tags: List[str]) -> str:
    """
    生成用户的个人档案 HTML 渲染代码
    :param qid: 用户 QQ 号
    :param gid: 当前群号
    :param perm: 当前群权限 (0-10，0为普通，3为管理，5为群主，10为系统)
    :param global_perm: 全局账户状态 (如 "USER", "ADMIN", "SUPER_ADMIN")
    :param tags: 用户的标签列表
    :return: 完整的 HTML 字符串
    """

    # --- 1. 预处理动态数据 ---
    current_ts = int(time.time())

    # 处理全局权限颜色与中文翻译
    g_perm_upper = global_perm.upper()
    if "SUPER" in g_perm_upper:
        g_color = "var(--accent-red)"
        g_zh = "/ 超级管理员"
    elif "ADMIN" in g_perm_upper:
        g_color = "var(--accent-yellow)"
        g_zh = "/ 管理员"
    else:
        g_color = "var(--text-main)"
        g_zh = "/ 普通用户"
    # 处理群权限数值与进度条宽度 (限制在 0-10 之间)
    perm_clamped = max(0, min(perm, 10))
    perm_width = (perm_clamped / 10.0) * 100

    # 根据权限级别动态给予颜色
    if perm_clamped >= 10:
        p_color = "var(--accent-red)"
    elif perm_clamped >= 5:
        p_color = "var(--accent-yellow)"
    elif perm_clamped >= 3:
        p_color = "var(--accent-cyan)"
    else:
        p_color = "var(--accent-green)"
    # 判断哪个刻度应该被高亮 (Active)
    mk_user = " active" if perm_clamped == 0 else ""
    mk_admin = " active" if perm_clamped == 3 else ""
    mk_owner = " active" if perm_clamped == 5 else ""
    mk_sys = " active" if perm_clamped == 10 else ""
    # 处理标签列表
    if tags:
        tags_html = "".join([
            f"""
            <div class="tag-row">
                <span class="tag-idx">0x{i:02X}</span>
                <span class="tag-name">{tag}</span>
            </div>""" for i, tag in enumerate(tags, 1)
        ])
    else:
        tags_html = """
            <div class="tag-row">
                <span class="tag-idx">0x00</span>
                <span class="tag-name" style="color: var(--text-muted);">// NO_TAGS_ALLOCATED</span>
            </div>"""
    # --- 2. CSS 样式 (纯文本，防止 f-string {} 冲突) ---
    css_content = """
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
            --accent-yellow: #FFB000;
            --font-family: 'JetBrains Mono', 'Noto Sans CJK SC', 'Source Han Sans CN', 'WenQuanYi Micro Hei', sans-serif;
        }
        body {
            margin: 0; padding: 0; width: 800px;
            background-color: var(--bg-base);
            background-image: radial-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px);
            background-size: 16px 16px;
            color: var(--text-main); font-family: var(--font-family);
            font-weight: 300; -webkit-font-smoothing: antialiased;
        }
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
        .panel-title { font-size: 12px; color: var(--text-title); margin-bottom: 24px; text-transform: uppercase; letter-spacing: 2px; display: flex; align-items: center; gap: 8px; }
        .panel-title::before { content: '■'; font-size: 10px; color: var(--accent-cyan); }
        .data-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px 32px; }
        .data-item { display: flex; flex-direction: column; gap: 6px; }
        .data-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; display: flex; gap: 6px;}
        .data-label .tag { color: var(--bg-base); background: var(--text-muted); padding: 0 4px; font-weight: 400; }
        .data-value { font-size: 24px; color: var(--text-title); font-weight: 300; display: flex; align-items: baseline; gap: 8px;}
        .data-value-sub { font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
        .meter-container { margin-top: 12px; position: relative; padding-bottom: 36px; }
        .meter-bar-bg { width: 100%; height: 4px; background: var(--panel-border); position: relative; }

        /* 动态背景颜色的进度条 */
        .meter-bar-fill { height: 100%; position: absolute; left: 0; top: 0; }
        .meter-bar-fill::after {
            content: ''; position: absolute; right: 0; top: -3px; height: 10px; width: 2px; background: #fff;
            /* 读取行内样式传递的变量 */
            box-shadow: 0 0 6px var(--fill-color, #FFF);
        }

        .meter-markers { position: absolute; width: 100%; top: 4px; height: 100%; }
        .marker { position: absolute; top: 0; transform: translateX(-50%); display: flex; flex-direction: column; align-items: center; font-size: 10px; color: var(--text-muted); line-height: 1.4; font-weight: 400; }
        .marker.first { transform: translateX(0); align-items: flex-start; }
        .marker.last { transform: translateX(-100%); align-items: flex-end; }
        .marker::before { content: ''; width: 1px; height: 6px; background: var(--text-muted); margin-bottom: 4px; }
        .marker.active { color: var(--text-title); font-weight: 400; }
        .marker.active::before { background: var(--text-title); width: 2px; }

        .tag-list-container { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 24px; }
        .tag-row { display: flex; align-items: center; padding: 8px 12px; background: rgba(0, 240, 255, 0.03); border: 1px solid rgba(0, 240, 255, 0.1); font-size: 13px; }
        .tag-idx { color: var(--text-muted); font-size: 10px; margin-right: 12px; }
        .tag-name { color: var(--text-main); font-weight: 400; letter-spacing: 0.5px; }
        .footer { display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); border-top: 1px solid var(--panel-border); padding-top: 16px; text-transform: uppercase; letter-spacing: 1px; }
        .decor-code { position: absolute; top: 24px; right: 24px; text-align: right; font-size: 10px; color: rgba(255, 255, 255, 0.1); line-height: 1.5; }
    </style>
    """
    # --- 3. HTML 结构 (注入数据) ---
    html_content = f"""
    <body>
        <div class="bot-card">
            <div class="header">
                <div class="header-title">
                    <p class="text-xl-en">SYS.AUTH_MATRIX</p>
                    <h1 class="text-xl-zh">用户安全凭证矩阵</h1>
                    <p class="text-sm-zh">终端权限解译完成。正在映射全局状态与节点独立操作许可。</p>
                    <p class="text-sm-en">CREDENTIALS DECODED. MAPPING GLOBAL STATE AND NODE INDEPENDENT PERMISSIONS.</p>
                </div>
                <div style="font-size: 24px; color: var(--panel-border); font-weight: 100;">PRM</div>
            </div>
            <div class="panel">
                <div class="decor-code">ENC: SHA-256<br>STATUS: VALID</div>
                <div class="panel-title">Identity & Privilege // 身份与权限层级</div>

                <div class="data-grid">
                    <div class="data-item">
                        <div class="data-label"><span class="tag">GLOBAL</span> User ID (全局标识)</div>
                        <div class="data-value">{qid}</div>
                    </div>
                    <div class="data-item">
                        <div class="data-label"><span class="tag">GLOBAL</span> Account State (账户状态)</div>
                        <div class="data-value" style="color: {g_color};">{g_perm_upper} <span class="data-value-sub" style="color: {g_color};">{g_zh}</span></div>
                    </div>
                    <div class="data-item" style="margin-top: 16px;">
                        <div class="data-label"><span class="tag" style="background: var(--accent-cyan); color: var(--bg-base);">LOCAL</span> Current Node (当前群组)</div>
                        <div class="data-value" style="color: var(--accent-cyan);">{gid}</div>
                    </div>

                    <div class="data-item" style="margin-top: 16px;">
                        <div class="data-label"><span class="tag" style="background: var(--accent-cyan); color: var(--bg-base);">LOCAL</span> Auth Level (当前群权限)</div>
                        <div class="data-value" style="color: {p_color};">{perm_clamped:02d} <span class="data-value-sub">/ 10</span></div>

                        <div class="meter-container">
                            <div class="meter-bar-bg">
                                <div class="meter-bar-fill" style="width: {perm_width}%; background: {p_color}; --fill-color: {p_color};"></div>
                            </div>
                            <div class="meter-markers">
                                <div class="marker first{mk_user}" style="left: 0%;"><span>0</span><span>USER</span></div>
                                <div class="marker{mk_admin}" style="left: 30%;"><span>3</span><span>ADMIN</span></div>
                                <div class="marker{mk_owner}" style="left: 50%;"><span>5</span><span>OWNER</span></div>
                                <div class="marker last{mk_sys}" style="left: 100%;"><span>10</span><span>SYS</span></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="panel">
                <div class="decor-code">STR_CNT: {len(tags)}<br>MEM_ADDR: 0x0A</div>
                <div class="panel-title">Semantic Tags // 分配特征标签</div>
                <div class="tag-list-container">
                    {tags_html}
                </div>
            </div>
            <div class="footer">
                <span>CREEPEBOT_RESPAWNED // SECURE_VIEW</span>
                <span>TS: {current_ts} // UTC+8</span>
            </div>
        </div>
    </body>
    """
    return f"""<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n<title>User Auth Render</title>\n{css_content}\n</head>\n{html_content}\n</html>"""
