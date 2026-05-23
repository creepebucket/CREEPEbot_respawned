def generate_node_status_html(api_data: dict, request_time: int) -> str:
    """
    根据 MCSM API 数据和请求时间生成科幻监控界面的 HTML。

    :param api_data: 包含 MCSM API 响应的字典 (dict)
    :param request_time: 发起请求时的时间戳 (毫秒 ms)
    :return: 渲染好的 HTML 字符串
    """

    # ---------------- 1. 数据解析与处理 ----------------
    status = api_data.get("status", 500)
    response_time = api_data.get("time", request_time)

    # 延迟计算 (毫秒)
    latency = response_time - request_time
    if latency < 0: latency = 0

    # 获取节点数据
    node_list = api_data.get("data", [])
    if not node_list:
        return "<html><body><h1>NO DATA</h1></body></html>"

    data = node_list[0]
    sys_info = data.get("system", {})
    process_info = data.get("process", {})
    instance_info = data.get("instance", {})

    # 系统与版本信息
    hostname = sys_info.get("hostname", "UNKNOWN").upper()
    platform = sys_info.get("platform", "UNKNOWN").upper()
    os_release = sys_info.get("release", "UNKNOWN")
    sys_type = sys_info.get("type", "UNKNOWN").upper()
    daemon_version = data.get("version", "UNKNOWN")
    cwd = sys_info.get("cwd", "UNKNOWN").upper()

    # 实例数量
    inst_running = instance_info.get("running", 0)
    inst_total = instance_info.get("total", 0)

    # 守护进程进程资源
    proc_mem_mb = process_info.get("memory", 0) / (1024 * 1024)
    proc_cpu = process_info.get("cpu", 0)

    # CPU 处理
    cpu_usage_pct = sys_info.get("cpuUsage", 0) * 100

    # 内存处理 (Byte -> GB)
    total_mem = sys_info.get("totalmem", 0)
    free_mem = sys_info.get("freemem", 0)
    used_mem = total_mem - free_mem

    total_mem_gb = total_mem / (1024 ** 3)
    used_mem_gb = used_mem / (1024 ** 3)
    mem_usage_pct = sys_info.get("memUsage", 0) * 100

    # 运行时长处理 (秒 -> 天/时/分)
    uptime_sec = sys_info.get("uptime", 0)
    days = uptime_sec // 86400
    hours = (uptime_sec % 86400) // 3600
    minutes = (uptime_sec % 3600) // 60
    uptime_str = f"{int(days):02d}D : {int(hours):02d}H : {int(minutes):02d}M"

    # 负载处理
    loadavg = sys_info.get("loadavg", [0, 0, 0])
    loadavg_str = f"{loadavg[0]:.2f} / {loadavg[1]:.2f} / {loadavg[2]:.2f}"
    # ---------------- 2. 静态 CSS 定义 ----------------
    # 单独定义 CSS 避免 f-string 冲突
    css_style = """
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
            background-size: 16px 16px; color: var(--text-main);
            font-family: var(--font-family); font-weight: 300; -webkit-font-smoothing: antialiased;
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
        .data-grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
        .data-item { display: flex; flex-direction: column; gap: 6px; }
        .data-item.full-width { grid-column: span 2; }
        .data-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
        .data-value { font-size: 24px; color: var(--text-title); font-weight: 300; }
        .data-value.small { font-size: 14px; margin-top: 4px; }

        .data-desc { font-size: 11px; color: var(--text-muted); padding: 8px 12px; background: rgba(255,255,255,0.03); border-left: 2px solid var(--text-muted); margin-top: 6px; line-height: 1.4; }
        .data-desc .highlight { color: var(--text-main); font-weight: 400; }

        .progress-bar-bg { width: 100%; height: 2px; background: var(--panel-border); margin-top: 8px; position: relative; }
        .progress-bar-fill { height: 100%; background: var(--accent-cyan); position: relative; }
        .progress-bar-fill::after { content: ''; position: absolute; right: 0; top: -2px; height: 6px; width: 2px; background: #fff; box-shadow: 0 0 4px var(--accent-cyan); }

        .footer { display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); border-top: 1px solid var(--panel-border); padding-top: 16px; text-transform: uppercase; letter-spacing: 1px; }
        .decor-code { position: absolute; top: 24px; right: 24px; text-align: right; font-size: 10px; color: rgba(255, 255, 255, 0.1); line-height: 1.5; text-transform: uppercase; }
    """
    # ---------------- 3. 注入 HTML 模板 ----------------
    html_template = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <style>{css_style}</style>
    </head>
    <body>
        <div class="bot-card">

            <div class="header">
                <div class="header-title">
                    <p class="text-xl-en">NODE.{hostname} // {platform}</p>
                    <h1 class="text-xl-zh">MCSManager 计算节点监控</h1>
                    <p class="text-sm-zh">节点通信链路状态更新。正在输出物理资源与守护进程数据。</p>
                    <p class="text-sm-en">LINK ESTABLISHED. OUTPUTTING SYSTEM METRICS FOR CURRENT NODE.</p>
                </div>
                <div style="font-size: 24px; color: var(--panel-border); font-weight: 100;">#{status}</div>
            </div>
            <!-- 面板 1：硬件指标 -->
            <div class="panel">
                <div class="decor-code">SYS: {sys_type}<br>REL: {os_release}<br>STAT: OK</div>

                <div class="panel-title">System Hardware // 系统硬件指标</div>
                <div class="data-grid">
                    <div class="data-item">
                        <div class="data-label">CPU Workload (处理器负载)</div>
                        <div class="data-value">{cpu_usage_pct:.1f}%</div>
                        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {cpu_usage_pct}%;"></div></div>
                    </div>

                    <div class="data-item">
                        <div class="data-label">RAM Allocation (物理内存)</div>
                        <div class="data-value" style="color: var(--accent-cyan);">{used_mem_gb:.2f} / {total_mem_gb:.2f} GB</div>
                        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {mem_usage_pct}%;"></div></div>
                    </div>

                    <div class="data-item">
                        <div class="data-label">Network Latency (通信延迟)</div>
                        <div class="data-value" style="color: var(--accent-green);">{latency} MS</div>
                    </div>

                    <div class="data-item">
                        <div class="data-label">System Uptime (连续运行)</div>
                        <div class="data-value">{uptime_str}</div>
                    </div>
                    <!-- 独占一行的 LoadAvg 和说明 -->
                    <div class="data-item full-width" style="margin-top: 8px;">
                        <div class="data-label">System LoadAvg (系统平均负载)</div>
                        <div class="data-value">{loadavg_str}</div>
                        <div class="data-desc">
                            代表 <span class="highlight">1分钟 / 5分钟 / 15分钟</span> 内系统队列中等待执行的任务数平均值。
                            <br>
                            * 注：数值越高代表 CPU 积压越严重；Windows 环境下该系统接口通常固定返回 0。
                        </div>
                    </div>
                </div>
            </div>
            <!-- 面板 2：守护进程信息 -->
            <div class="panel">
                <div class="decor-code">PID_MEM: {proc_mem_mb:.1f}MB<br>PID_CPU: {proc_cpu}</div>
                <div class="panel-title">Daemon Status // 守护进程状态</div>
                <div class="data-grid data-grid-cols-3">
                    <div class="data-item">
                        <div class="data-label">Instances (运行/总计)</div>
                        <div class="data-value" style="color: var(--accent-green);">{inst_running:02d} / {inst_total:02d}</div>
                    </div>

                    <div class="data-item">
                        <div class="data-label">Version (核心版本)</div>
                        <div class="data-value">V {daemon_version}</div>
                    </div>

                    <div class="data-item">
                        <div class="data-label">Platform (架构)</div>
                        <div class="data-value">{platform}</div>
                    </div>

                    <div class="data-item full-width" style="grid-column: span 3;">
                        <div class="data-label">Working Directory (工作流目录)</div>
                        <div class="data-value small">{cwd}</div>
                    </div>
                </div>
            </div>
            <div class="footer">
                <span>MCSM_MONITOR_RENDER_ENGINE</span>
                <span>TS: {response_time} // MS</span>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template