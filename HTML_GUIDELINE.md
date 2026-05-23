# 🤖 QQ Bot 图像渲染器 HTML/CSS 设计规范

## 1. 核心设计意图 (Core Intent)
本项目用于 QQ 机器人的卡片回复。由于 QQ 环境不支持复杂的交互式 HTML 元素，我们将 HTML 渲染为静态图片发送。
*   **信息密度与易读性**：在手机端和电脑端均需保持高对比度和清晰的阅读体验。
*   **静态交互**：图片无法点击，所有传统的“按钮”必须转换为“指令提示”（告知用户发送什么命令来触发后续操作）。
*   **无头浏览器友好**：代码需针对 Puppeteer / Playwright 等无头浏览器优化，确保瞬间渲染完毕，不出白边、不丢字体。

## 2. 视觉风格基准：科幻终端 / 硬核 HUD (Sci-Fi / Hardcore HUD)
整体视觉必须严格遵循以下风格特征：
1.  **绝对锐利 (Sharp Edges)**：**全局禁用任何 `border-radius`**。所有容器、进度条、边框必须是纯直角。
2.  **深色主题与高对比度 (Dark Theme)**：背景采用极暗色（如 `#040507`），辅以微弱的点阵/网格背景。文本使用高亮白/灰。
3.  **强调色 (Accents)**：主强调色为荧光青色（Cyan `#00F0FF`），警告/错误使用荧光红（Red `#FF003C`），正常/在线使用荧光绿（Green `#00FF66`）。
4.  **微型装饰 (Micro-Decorations)**：
    *   使用双斜杠 `//` 作为中英文分隔符（如 `Hardware // 硬件`）。
    *   面板四角使用 `::before` 和 `::after` 伪类绘制“十字定位准星 / 直角边框”。
    *   增加无意义的十六进制占位符（如 `HEX: 0x8F9A`）提升终端质感。
5.  **排版 (Typography)**：
    *   英文/数字：要求使用全大写（Uppercase），配合较宽的字间距（`letter-spacing`）。
    *   字体字重：大量使用细体（Light `300` / Thin `100`），产生冷峻的工业感。

## 3. 代码与渲染规范 (Coding Guidelines)
后续 LLM 在生成 HTML/CSS 时，必须遵循以下规则：
1.  **固定尺寸**：`body` 必须设定固定宽度（标准为 `width: 800px;`），高度由内容自动撑开。禁止使用 `vw/vh` 等相对视口单位，全部使用 `px`，以确保截图 API (`element.screenshot()`) 比例恒定。
2.  **字体栈 (Font Stack) 限制**：
    *   代码需首选 `JetBrains Mono`（建议服务端预装）。
    *   中文字体必须 fallback 到 Ubuntu 常用字体：`'Noto Sans CJK SC', 'WenQuanYi Micro Hei'`，防止无头浏览器渲染出默认的宋体。
3.  **禁用动画**：禁止使用 `transition`, `animation` 或 `@keyframes`。截图是瞬间发生的，处于中间态的动画会导致截图模糊或元素不完整。
4.  **单文件结构**：CSS 必须内联写在 `<style>` 标签中，**禁止引入外部 CSS 文件**，减少无头浏览器的网络请求阻塞。
5.  **图文无缝集成**：如果必须使用图标，优先使用纯 CSS 几何图形（如 `■`, `▲`, `●`）或内联 SVG，避免加载外部图片。

## 4. 交互控件的处理方式
因为图片无法点击，原有的 `<button>` 必须渲染为**“指令提示框 (Command Hint)”**：
*   **设计原则**：清晰地指示用户在聊天框输入什么指令。
*   **展现形式**：终端输入框样式，包含前缀（如 `>`）和高亮的命令（如 `/reboot`）。

---

## 5. 基准 HTML 模板参考代码
*(以下代码作为后续所有面板生成的 Base 模板，请直接复用其 CSS 变量与结构逻辑)*

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Bot Render</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@100;300;400&display=swap" rel="stylesheet">
  
    <style>
        :root {
            /* 极暗背景色 */
            --bg-base: #040507;
            /* 极简透明填充 */
            --panel-bg: rgba(255, 255, 255, 0.015);
            --panel-border: rgba(255, 255, 255, 0.15);
          
            /* 文字颜色 */
            --text-title: #FFFFFF;
            --text-main: #D1D5DB;
            --text-muted: #5E6572;
          
            /* 高级终端强调色 */
            --accent-cyan: #00F0FF;
            --accent-red: #FF003C;
            --accent-green: #00FF66;
          
            /* 字体栈：要求适配 Ubuntu 环境 */
            --font-family: 'JetBrains Mono', 'Noto Sans CJK SC', 'Source Han Sans CN', 'WenQuanYi Micro Hei', sans-serif;
        }

        body {
            margin: 0;
            padding: 0;
            width: 800px; /* 固定宽度，适应截图 */
            background-color: var(--bg-base);
            /* 终端暗点背景 */
            background-image: radial-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px);
            background-size: 16px 16px;
            color: var(--text-main);
            font-family: var(--font-family);
            font-weight: 300;
            -webkit-font-smoothing: antialiased;
        }

        .bot-card {
            padding: 48px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            gap: 32px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        /* ================= 头部排版 ================= */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--panel-border);
            position: relative;
        }

        .header::after {
            content: '';
            position: absolute;
            left: 0;
            bottom: -1px;
            width: 120px;
            height: 1px;
            background-color: var(--accent-cyan);
        }

        .header-title { display: flex; flex-direction: column; gap: 10px; }
      
        .text-xl-en { font-size: 36px; font-weight: 100; color: var(--text-title); letter-spacing: -1px; margin: 0; line-height: 1; }
        .text-xl-zh { font-size: 20px; font-weight: 300; color: var(--accent-cyan); margin: 0; letter-spacing: 2px; }
        .text-sm-en { font-size: 12px; color: var(--text-muted); margin: 0; text-transform: uppercase; letter-spacing: 0.5px; }
        .text-sm-zh { font-size: 13px; color: var(--text-muted); margin: 0; }

        /* ================= 面板容器与边框修饰 ================= */
        .panel {
            background: var(--panel-bg);
            border: 1px solid var(--panel-border);
            padding: 24px;
            position: relative;
            backdrop-filter: blur(4px);
        }

        /* 四角定位符 (Corner Brackets) */
        .panel::before, .panel::after {
            content: '';
            position: absolute;
            width: 8px;
            height: 8px;
            border: 1px solid var(--accent-cyan);
        }
        .panel::before { top: -1px; left: -1px; border-right: none; border-bottom: none; }
        .panel::after { bottom: -1px; right: -1px; border-left: none; border-top: none; }

        .panel-title {
            font-size: 12px;
            color: var(--text-title);
            margin-bottom: 24px;
            text-transform: uppercase;
            letter-spacing: 2px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .panel-title::before { content: '■'; font-size: 10px; color: var(--accent-cyan); }

        /* ================= 数据展示 ================= */
        .data-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px 32px; }
        .data-item { display: flex; flex-direction: column; gap: 6px; }
        .data-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
        .data-value { font-size: 24px; color: var(--text-title); font-weight: 300; }

        /* ================= 进度条 ================= */
        .progress-bar-bg {
            width: 100%; height: 2px; background: var(--panel-border); margin-top: 8px; position: relative;
        }
        .progress-bar-fill { height: 100%; background: var(--accent-cyan); position: relative; }
        .progress-bar-fill::after {
            content: ''; position: absolute; right: 0; top: -2px; height: 6px; width: 2px;
            background: #fff; box-shadow: 0 0 4px var(--accent-cyan);
        }
        .progress-bar-fill.warning { background: var(--accent-red); }
        .progress-bar-fill.warning::after { box-shadow: 0 0 4px var(--accent-red); }

        /* ================= 控制台与指令引导 ================= */
        .controls-flex { display: flex; flex-wrap: wrap; gap: 16px; align-items: center; }

        .status-indicator {
            font-size: 12px; color: var(--text-main); letter-spacing: 1px;
            display: flex; align-items: center; gap: 6px;
        }
        .status-indicator::before { content: ''; display: inline-block; width: 6px; height: 6px; background: var(--accent-green); }
        .status-indicator.error::before { background: var(--accent-red); }

        /* 专门适配 Bot 图片交互的指令框 */
        .cmd-hint {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(0, 240, 255, 0.05);
            border: 1px solid rgba(0, 240, 255, 0.2);
            font-size: 12px;
            color: var(--text-main);
            letter-spacing: 1px;
        }
        .cmd-hint .prefix { color: var(--text-muted); }
        .cmd-hint .cmd-code { color: var(--accent-cyan); font-weight: 400; text-transform: lowercase; }

        /* ================= 装饰与底部信息 ================= */
        .footer {
            display: flex; justify-content: space-between; font-size: 11px;
            color: var(--text-muted); border-top: 1px solid var(--panel-border);
            padding-top: 16px; text-transform: uppercase; letter-spacing: 1px;
        }
        .decor-code {
            position: absolute; top: 24px; right: 24px; text-align: right;
            font-size: 10px; color: rgba(255, 255, 255, 0.1); line-height: 1.5;
        }
    </style>
</head>
<body>

    <div class="bot-card">
        <div class="header">
            <div class="header-title">
                <p class="text-xl-en">SYS.MONITOR_NODE_A</p>
                <h1 class="text-xl-zh">底层资源监控终端</h1>
                <p class="text-sm-zh">系统自检完成。正在输出当前计算节点的物理分配信息。</p>
                <p class="text-sm-en">DIAGNOSTIC COMPLETE. OUTPUTTING PHYSICAL ALLOCATION METRICS FOR CURRENT NODE.</p>
            </div>
            <div style="font-size: 24px; color: var(--panel-border); font-weight: 100;">01</div>
        </div>

        <div class="panel">
            <div class="decor-code">HEX: 0x8F9A<br>AUTH: GRANTED<br>PORT: 443</div>
          
            <div class="panel-title">Hardware Metrics // 硬件指标</div>
            <div class="data-grid">
                <div class="data-item">
                    <div class="data-label">CPU Workload (核心负载)</div>
                    <div class="data-value">38.4%</div>
                    <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 38.4%;"></div></div>
                </div>
                <div class="data-item">
                    <div class="data-label">RAM Allocation (物理内存)</div>
                    <div class="data-value" style="color: var(--accent-red);">28.5 / 32.0 GB</div>
                    <div class="progress-bar-bg"><div class="progress-bar-fill warning" style="width: 89%;"></div></div>
                </div>
                <div class="data-item">
                    <div class="data-label">Network Ping (网络延时)</div>
                    <div class="data-value" style="color: var(--accent-green);">08 MS</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Uptime (运行时长)</div>
                    <div class="data-value">14D : 08H : 32M</div>
                </div>
            </div>
        </div>

        <div class="panel">
            <div class="panel-title">Operation Center // 指令中心</div>
            <div class="controls-flex">
                <span class="status-indicator">SECURE (安全)</span>
                <span class="status-indicator error">MEM_WARN (内存告警)</span>
              
                <div style="flex-grow: 1;"></div>
              
                <!-- 修改点：将不可点击的按钮替换为指令发送提示 -->
                <div class="cmd-hint">
                    <span class="prefix">&gt; 发送</span>
                    <span class="cmd-code">/force_kill</span>
                    <span>强制终止</span>
                </div>
                <div class="cmd-hint">
                    <span class="prefix">&gt; 发送</span>
                    <span class="cmd-code">/flush</span>
                    <span>清理缓存</span>
                </div>
            </div>
        </div>

        <div class="footer">
            <span>CREEPEBOT_RESPAWNED</span>
            <span>TS: 1698249000 // UTC+8</span>
        </div>
    </div>

</body>
</html>
```