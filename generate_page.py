#!/usr/bin/env python3
"""
generate_page.py - 生成 GitHub Pages 的 index.html
终端风格实时展示训练日志
"""

import json
import os
from datetime import datetime


def generate_html():
    # 读取训练日志
    log_file = "data/training_latest.log"
    logs = ""
    if os.path.exists(log_file):
        with open(log_file, encoding="utf-8", errors="replace") as f:
            logs = f.read()

    # 读取元数据
    metadata = {}
    meta_file = "data/metadata.json"
    if os.path.exists(meta_file):
        with open(meta_file) as f:
            metadata = json.load(f)

    updated_at = metadata.get("updated_at", "unknown")
    hostname = metadata.get("hostname", "unknown")
    wandb_size = metadata.get("wandb_zip_size_mb", "?")

    # HTML 转义
    logs_escaped = (
        logs.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )

    # 控制显示大小 (最多200KB文本)
    max_chars = 200000
    if len(logs_escaped) > max_chars:
        logs_escaped = "... (earlier logs truncated) ...\n\n" + logs_escaped[-max_chars:]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Training Monitor</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', 'Consolas', monospace;
            background: #0d1117;
            color: #c9d1d9;
            padding: 20px;
            min-height: 100vh;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #21262d;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .header h1 {{
            color: #58a6ff;
            font-size: 1.4em;
            font-weight: 600;
        }}
        .meta {{
            color: #8b949e;
            font-size: 0.8em;
            text-align: right;
        }}
        .meta span {{ display: block; }}
        .terminal-wrapper {{
            position: relative;
            border: 1px solid #30363d;
            border-radius: 8px;
            overflow: hidden;
        }}
        .terminal-header {{
            background: #161b22;
            padding: 8px 16px;
            display: flex;
            align-items: center;
            gap: 8px;
            border-bottom: 1px solid #21262d;
        }}
        .dot {{ width: 12px; height: 12px; border-radius: 50%; }}
        .dot-r {{ background: #ff5f56; }}
        .dot-y {{ background: #ffbd2e; }}
        .dot-g {{ background: #27c93f; }}
        .terminal-title {{
            color: #8b949e;
            font-size: 0.8em;
            margin-left: 8px;
        }}
        #terminal {{
            background: #0d1117;
            padding: 16px;
            height: 82vh;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 12.5px;
            line-height: 1.5;
        }}
        #terminal::-webkit-scrollbar {{ width: 8px; }}
        #terminal::-webkit-scrollbar-track {{ background: #161b22; }}
        #terminal::-webkit-scrollbar-thumb {{ background: #30363d; border-radius: 4px; }}
        .controls {{
            margin-top: 12px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .btn {{
            padding: 6px 14px;
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #c9d1d9;
            cursor: pointer;
            font-size: 0.82em;
            font-family: inherit;
            transition: background 0.15s;
        }}
        .btn:hover {{ background: #30363d; }}
        .status-dot {{
            display: inline-block;
            width: 8px; height: 8px;
            border-radius: 50%;
            background: #3fb950;
            margin-right: 6px;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.4; }}
        }}
        .search-box {{
            padding: 6px 12px;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #c9d1d9;
            font-family: inherit;
            font-size: 0.82em;
            width: 200px;
        }}
        .search-box:focus {{ outline: none; border-color: #58a6ff; }}
    </style>
</head>
<body>
    <div class="header">
        <h1><span class="status-dot"></span>Training Monitor</h1>
        <div class="meta">
            <span>Host: {hostname}</span>
            <span>Data updated: {updated_at}</span>
            <span>Page generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            <span>wandb zip: {wandb_size} MB</span>
        </div>
    </div>

    <div class="terminal-wrapper">
        <div class="terminal-header">
            <div class="dot dot-r"></div>
            <div class="dot dot-y"></div>
            <div class="dot dot-g"></div>
            <span class="terminal-title">training_latest.log ({len(logs.splitlines())} lines)</span>
        </div>
        <div id="terminal">{logs_escaped}</div>
    </div>

    <div class="controls">
        <button class="btn" onclick="scrollToBottom()">Bottom</button>
        <button class="btn" onclick="scrollToTop()">Top</button>
        <button class="btn" onclick="toggleWrap()">Toggle Wrap</button>
        <input class="search-box" type="text" placeholder="Search..." oninput="searchLog(this.value)">
    </div>

    <script>
        const term = document.getElementById('terminal');

        function scrollToBottom() {{ term.scrollTop = term.scrollHeight; }}
        function scrollToTop() {{ term.scrollTop = 0; }}
        function toggleWrap() {{
            term.style.whiteSpace = term.style.whiteSpace === 'pre' ? 'pre-wrap' : 'pre';
        }}

        // 简单搜索高亮
        let originalContent = term.innerHTML;
        function searchLog(query) {{
            if (!query) {{
                term.innerHTML = originalContent;
                return;
            }}
            const escaped = query.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
            const re = new RegExp(`(${{escaped}})`, 'gi');
            term.innerHTML = originalContent.replace(re,
                '<mark style="background:#a371f7;color:#fff;padding:0 2px;border-radius:2px">$1</mark>');
        }}

        // 页面加载自动滚到底
        window.onload = scrollToBottom;
    </script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  index.html generated ({len(html)//1024}KB, {len(logs.splitlines())} log lines)")


if __name__ == "__main__":
    generate_html()
