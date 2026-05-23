import statistics
import time
from collections import Counter
from typing import List


def get_roll_html(values: List[int], info: str) -> str:
    # 抽离静态的 CSS 样式，避免 f-string 大括号冲突
    CSS_STYLE = """
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
    /* Header */
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
    /* Panel */
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
    /* Dice Matrix */
    .dice-matrix { display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 8px; }
    .dice-block {
        width: 72px; height: 72px; border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.03); display: flex; justify-content: center; align-items: center; position: relative;
    }
    .dice-block::before {
        content: ''; position: absolute; top: 0; left: 0; width: 6px; height: 6px; background: rgba(255, 255, 255, 0.2);
    }
    .dice-index { position: absolute; top: 4px; right: 6px; font-size: 9px; color: var(--text-muted); }
    .dice-value { font-size: 32px; font-weight: 300; color: var(--text-title); }

    .dice-block.max { border-color: var(--accent-green); background: rgba(0, 255, 102, 0.05); }
    .dice-block.max::before { background: var(--accent-green); }
    .dice-block.max .dice-value { color: var(--accent-green); font-weight: 400; }

    .dice-block.min { border-color: var(--accent-red); background: rgba(255, 0, 60, 0.05); }
    .dice-block.min::before { background: var(--accent-red); }
    .dice-block.min .dice-value { color: var(--accent-red); font-weight: 400; }
    /* Data Grid & Others */
    .data-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px 16px; }
    .data-item { display: flex; flex-direction: column; gap: 6px; }
    .data-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
    .data-value { font-size: 28px; color: var(--text-title); font-weight: 300; }
    .controls-flex { display: flex; flex-wrap: wrap; gap: 16px; align-items: center; }
    .status-indicator { font-size: 12px; color: var(--text-main); letter-spacing: 1px; display: flex; align-items: center; gap: 6px; }
    .status-indicator::before { content: ''; display: inline-block; width: 6px; height: 6px; background: var(--accent-green); }
    .cmd-hint {
        display: flex; align-items: center; gap: 8px; padding: 8px 16px;
        background: rgba(0, 240, 255, 0.05); border: 1px solid rgba(0, 240, 255, 0.2);
        font-size: 12px; color: var(--text-main); letter-spacing: 1px;
    }
    .cmd-hint .prefix { color: var(--text-muted); }
    .cmd-hint .cmd-code { color: var(--accent-cyan); font-weight: 400; text-transform: lowercase; }
    .footer {
        display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted);
        border-top: 1px solid var(--panel-border); padding-top: 16px; text-transform: uppercase; letter-spacing: 1px;
    }
    .decor-code {
        position: absolute; top: 24px; right: 24px; text-align: right;
        font-size: 10px; color: rgba(255, 255, 255, 0.1); line-height: 1.5;
    }
    .divider { width: 100%; height: 1px; background: var(--panel-border); margin: 24px 0; position: relative; }
    .divider::before { content: ''; position: absolute; left: 0; top: -2px; width: 32px; height: 5px; background: rgba(255,255,255,0.1); }
</style>
    """

    if not values:
        return "<div style='color:red;'>Error: 没有任何投掷数据</div>"
    # --- 1. 数据统计运算 ---
    total_sum = sum(values)
    mean_val = total_sum / len(values)
    median_val = statistics.median(values)

    # 计算众数（避免 statistics.multimode 在全不重复时返回“全部值”）
    counter = Counter(values)
    max_freq = max(counter.values())

    if max_freq == 1 and len(values) > 1:
        mode_str = "N/A"
    else:
        modes = sorted([val for val, freq in counter.items() if freq == max_freq])
        mode_str = ", ".join(map(str, modes))
        if max_freq > 1:
            mode_str = f"{mode_str} (x{max_freq})"
    max_val = max(values)
    min_val = min(values)
    # --- 2. 生成骰子方块的 HTML ---
    dice_html_list = []
    for i, val in enumerate(values, 1):
        class_str = "dice-block"
        # 仅在非所有骰子点数全一样的情况下，高亮最大最小值
        if max_val != min_val:
            if val == max_val:
                class_str += " max"
            elif val == min_val:
                class_str += " min"

        dice_html_list.append(f"""
            <div class="{class_str}">
                <span class="dice-index">D{i}</span>
                <span class="dice-value">{val}</span>
            </div>""")

    dice_matrix_html = "".join(dice_html_list)
    # --- 3. 获取真实时间戳 ---
    current_ts = int(time.time())
    # --- 4. 构建完整的 HTML 模板 ---
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SYS.QUANTUM_RNG</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@100;300;400&display=swap" rel="stylesheet">
    {CSS_STYLE}
</head>
<body>
    <div class="bot-card">
        <div class="header">
            <div class="header-title">
                <p class="text-xl-en">SYS.QUANTUM_RNG</p>
                <h1 class="text-xl-zh">量子概率演算终端</h1>
                <p class="text-sm-zh">{info}</p>
                <p class="text-sm-en">RANDOM NUMBER GENERATION COMPLETE. WAITING FOR NEXT COMMAND.</p>
            </div>
            <div style="font-size: 24px; color: var(--panel-border); font-weight: 100;">RNG</div>
        </div>
        <div class="panel">
            <div class="decor-code">SEED: {hex(current_ts)[-4:].upper().zfill(4)}<br>ENTROPY: HIGH<br>SEQ: 0014</div>

            <div class="panel-title">Raw Data Matrix // 原始数据矩阵</div>
            <div class="dice-matrix">
                {dice_matrix_html}
            </div>
            <div class="divider"></div>
            <div class="panel-title">Statistical Analysis // 统计学分析</div>
            <div class="data-grid">
                <div class="data-item">
                    <div class="data-label">Total Sum (总计)</div>
                    <div class="data-value" style="color: var(--accent-cyan);">{total_sum}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Mean (平均)</div>
                    <div class="data-value">{mean_val:.2f}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Median (中位数)</div>
                    <div class="data-value">{median_val:g}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Mode (众数)</div>
                    <div class="data-value">{mode_str}</div>
                </div>
            </div>
        </div>
        <div class="panel">
            <div class="panel-title">Command Center // 指令中心</div>
            <div class="controls-flex">
                <span class="status-indicator">CALC_DONE (演算完成)</span>
                <div style="flex-grow: 1;"></div>
                <div class="cmd-hint">
                    <span class="prefix">&gt; 发送</span>
                    <span class="cmd-code">/roll</span>
                    <span>重新抛掷</span>
                </div>
            </div>
        </div>
        <div class="footer">
            <span>CREEPEBOT_RESPAWNED // RNG_MODULE</span>
            <span>TS: {current_ts}</span>
        </div>
    </div>
</body>
</html>
"""
    return html_template
