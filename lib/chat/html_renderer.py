from __future__ import annotations

"""
HTML -> PNG 渲染器（用于 QQ Bot 静态卡片回复）。

依赖：
  - playwright: `pip install playwright`
  - 浏览器：`python -m playwright install chromium`

默认行为：
  - 按 HTML_GUIDELINE 的固定宽度（800px）截图（可配置）
  - 默认禁用网络请求，避免外链资源导致渲染阻塞/不一致
"""

from dataclasses import dataclass
from typing import Literal, Optional


@dataclass(frozen=True)
class HtmlRenderOptions:
    viewport_width: int = 800
    device_scale_factor: float = 2.0
    wait_until: Literal['load', 'domcontentloaded', 'networkidle'] = 'load'
    timeout_ms: int = 10_000
    selector: str = 'body'
    block_network: bool = True
    base_url: Optional[str] = None
    enforce_guideline_layout: bool = True


class HtmlRenderError(RuntimeError):
    pass


def _ensure_playwright():
    try:
        from playwright.async_api import async_playwright  # type: ignore
    except Exception as e:
        raise HtmlRenderError(
            'playwright 未安装，无法渲染 HTML 为图片。请安装依赖：\n'
            '  pip install playwright\n'
            '  python -m playwright install firefox'
        ) from e
    return async_playwright


def _inject_base_tag(html: str, base_url: str) -> str:
    if '<base' in html.lower():
        return html
    base_tag = f'<base href="{base_url}">'
    lower = html.lower()
    head_idx = lower.find('<head')
    if head_idx != -1:
        head_close = lower.find('>', head_idx)
        if head_close != -1:
            return html[:head_close + 1] + base_tag + html[head_close + 1:]
    return base_tag + html


def _needs_wrap(html: str) -> bool:
    lower = html.lstrip().lower()
    return not (lower.startswith('<!doctype') or '<html' in lower or '<body' in lower)


def _wrap_html_fragment(fragment: str, *, width: int) -> str:
    return (
        '<!DOCTYPE html>'
        '<html lang="zh-CN">'
        '<head>'
        '<meta charset="UTF-8">'
        '<style>'
        'html,body{margin:0;padding:0;}'
        f'body{{width:{width}px;}}'
        '</style>'
        '</head>'
        f'<body>{fragment}</body>'
        '</html>'
    )

async def render_html_to_png(html: str, *, options: HtmlRenderOptions = HtmlRenderOptions()) -> bytes:
    """将 HTML 字符串渲染为 PNG bytes。"""
    async_playwright = _ensure_playwright()
    if options.base_url:
        html = _inject_base_tag(html, options.base_url)
    if _needs_wrap(html):
        html = _wrap_html_fragment(html, width=options.viewport_width)

    try:
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            try:
                context = await browser.new_context(
                    viewport={'width': options.viewport_width, 'height': 720},
                    device_scale_factor=options.device_scale_factor,
                )
                page = await context.new_page()

                if options.block_network:
                    async def _route(route):
                        url = route.request.url
                        if url.startswith('data:') or url.startswith('blob:'):
                            await route.continue_()
                            return
                        if url.startswith('file:'):
                            await route.continue_()
                            return
                        await route.abort()
                    await page.route('**/*', _route)

                await page.set_content(
                    html,
                    wait_until=options.wait_until,
                    timeout=options.timeout_ms,
                )

                if options.enforce_guideline_layout:
                    await page.add_style_tag(
                        content=(
                            'html,body{margin:0;padding:0;}*{box-sizing:border-box;}'
                            f'body{{width:{options.viewport_width}px;}}'
                        )
                    )

                locator = page.locator(options.selector).first
                png = await locator.screenshot(type='png', animations='disabled')
                await context.close()
                return png
            finally:
                await browser.close()
    except HtmlRenderError:
        raise
    except Exception as e:
        raise HtmlRenderError(f'渲染失败: {e}') from e


async def render(html: str, *, options: HtmlRenderOptions = HtmlRenderOptions()):
    """将 HTML 字符串渲染为 OneBot v11 的图片消息段（MessageSegment.image）。"""
    try:
        from nonebot.adapters.onebot.v11 import MessageSegment
    except Exception as e:
        raise HtmlRenderError('nonebot onebot v11 未安装，无法生成图片消息段。') from e

    png = await render_html_to_png(html, options=options)
    return MessageSegment.image(png)
