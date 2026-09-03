import json
import os
import sys
import webbrowser
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any

try:
    from ..core import get_extractor, MediaDownloader, ParseResult, MediaType
except (ImportError, ValueError):
    from core import get_extractor, MediaDownloader, ParseResult, MediaType

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SnapGet - 全网无水印音视频/图集批量抓取工具</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --card-hover: #273549;
            --accent: #38bdf8;
            --accent-hover: #0284c7;
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
            --border: #334155;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
        }

        .container {
            max-width: 900px;
            width: 100%;
        }

        header {
            text-align: center;
            margin-bottom: 35px;
        }

        .logo {
            font-size: 2.4rem;
            font-weight: 800;
            letter-spacing: -1px;
            background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
        }

        .subtitle {
            color: var(--text-sub);
            margin-top: 8px;
            font-size: 1rem;
        }

        .platform-badges {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-top: 16px;
        }

        .badge {
            background: rgba(56, 189, 248, 0.1);
            color: #38bdf8;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.85rem;
            border: 1px solid rgba(56, 189, 248, 0.25);
            font-weight: 500;
        }

        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            margin-bottom: 24px;
        }

        .input-group {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        textarea {
            width: 100%;
            height: 90px;
            background: #0b1120;
            border: 1px solid var(--border);
            border-radius: 10px;
            color: var(--text-main);
            padding: 14px;
            font-size: 0.95rem;
            resize: vertical;
            outline: none;
            transition: border-color 0.2s;
        }

        textarea:focus {
            border-color: var(--accent);
        }

        .btn-group {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
        }

        button {
            padding: 10px 22px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }

        .btn-primary {
            background: var(--accent);
            color: #0f172a;
        }

        .btn-primary:hover {
            background: var(--accent-hover);
            color: #ffffff;
        }

        .btn-secondary {
            background: transparent;
            color: var(--text-sub);
            border: 1px solid var(--border);
        }

        .btn-secondary:hover {
            background: var(--card-hover);
            color: var(--text-main);
        }

        .btn-download-all {
            background: var(--success);
            color: white;
            padding: 8px 16px;
            font-size: 0.9rem;
        }

        .btn-download-all:hover {
            opacity: 0.9;
        }

        #result-container {
            display: none;
        }

        .result-header {
            display: flex;
            gap: 20px;
            align-items: flex-start;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 20px;
        }

        .cover-preview {
            width: 140px;
            height: 140px;
            object-fit: cover;
            border-radius: 10px;
            border: 1px solid var(--border);
            background: #000;
            flex-shrink: 0;
        }

        .media-meta {
            flex: 1;
        }

        .media-title {
            font-size: 1.15rem;
            font-weight: 700;
            line-height: 1.4;
            margin-bottom: 8px;
        }

        .media-author {
            color: var(--accent);
            font-size: 0.9rem;
            margin-bottom: 8px;
        }

        .media-desc {
            color: var(--text-sub);
            font-size: 0.85rem;
            max-height: 60px;
            overflow-y: auto;
        }

        .items-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }

        .item-card {
            background: #0f172a;
            border: 1px solid var(--border);
            border-radius: 10px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .item-thumb {
            width: 100%;
            height: 140px;
            object-fit: cover;
            background: #000;
        }

        .item-video-placeholder {
            width: 100%;
            height: 140px;
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--accent);
            font-weight: bold;
        }

        .item-actions {
            padding: 10px;
            display: flex;
            gap: 8px;
            justify-content: space-between;
            align-items: center;
        }

        .item-name {
            font-size: 0.8rem;
            color: var(--text-sub);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 110px;
        }

        .btn-sm {
            padding: 4px 10px;
            font-size: 0.8rem;
            border-radius: 6px;
        }

        .toast {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: var(--card-bg);
            color: var(--text-main);
            padding: 12px 20px;
            border-radius: 8px;
            border-left: 4px solid var(--accent);
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            display: none;
            z-index: 100;
        }

        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 0.8s linear infinite;
            margin-right: 8px;
            vertical-align: middle;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">⚡ SnapGet</div>
            <p class="subtitle">全网主流自媒体无水印原画视频/图集极速抓取器</p>
            <div class="platform-badges">
                <span class="badge">抖音 / 剪映</span>
                <span class="badge">小红书原图</span>
                <span class="badge">Bilibili 视频</span>
                <span class="badge">快手 / 通用支持</span>
            </div>
        </header>

        <div class="card">
            <div class="input-group">
                <textarea id="urlInput" placeholder="直接粘贴手机端分享口令或网页链接，支持包含多余文字，自动识别..."></textarea>
                <div class="btn-group">
                    <button class="btn-secondary" onclick="clearInput()">清空</button>
                    <button class="btn-primary" id="parseBtn" onclick="parseUrl()">
                        <span id="btnSpinner" style="display:none;" class="spinner"></span>
                        开始解析
                    </button>
                </div>
            </div>
        </div>

        <div class="card" id="result-container">
            <div class="result-header">
                <img id="resCover" class="cover-preview" src="" alt="封面">
                <div class="media-meta">
                    <div class="media-title" id="resTitle"></div>
                    <div class="media-author" id="resAuthor"></div>
                    <div class="media-desc" id="resDesc"></div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span id="resCount" style="font-size: 0.9rem; color: var(--text-sub);"></span>
                <button class="btn-download-all" onclick="downloadAll()">一键下载全部到本地</button>
            </div>
            <div class="items-grid" id="itemsGrid"></div>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        let currentResult = null;

        function showToast(msg, isSuccess = true) {
            const toast = document.getElementById('toast');
            toast.textContent = msg;
            toast.style.borderLeftColor = isSuccess ? 'var(--success)' : 'var(--danger)';
            toast.style.display = 'block';
            setTimeout(() => { toast.style.display = 'none'; }, 3000);
        }

        function clearInput() {
            document.getElementById('urlInput').value = '';
            document.getElementById('result-container').style.display = 'none';
            currentResult = null;
        }

        async function parseUrl() {
            const text = document.getElementById('urlInput').value.trim();
            if (!text) {
                showToast("请先粘贴分享内容或链接！", false);
                return;
            }

            const btn = document.getElementById('parseBtn');
            const spinner = document.getElementById('btnSpinner');
            btn.disabled = true;
            spinner.style.display = 'inline-block';

            try {
                const resp = await fetch('/api/parse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });
                const res = await resp.json();
                if (!res.success) {
                    showToast(res.error || "解析失败", false);
                    return;
                }

                currentResult = res.data;
                renderResult(currentResult);
                showToast("解析成功！已提取无水印高清直链");
            } catch (err) {
                showToast("网络请求异常: " + err.message, false);
            } finally {
                btn.disabled = false;
                spinner.style.display = 'none';
            }
        }

        function renderResult(data) {
            document.getElementById('result-container').style.display = 'block';
            document.getElementById('resTitle').textContent = data.title;
            document.getElementById('resAuthor').textContent = `@${data.author} (${data.platform.toUpperCase()})`;
            document.getElementById('resDesc').textContent = data.description || '无详细描述';
            
            const coverEl = document.getElementById('resCover');
            if (data.cover_url) {
                coverEl.src = data.cover_url;
                coverEl.style.display = 'block';
            } else {
                coverEl.style.display = 'none';
            }

            const grid = document.getElementById('itemsGrid');
            grid.innerHTML = '';

            document.getElementById('resCount').textContent = `共提取出 ${data.items.length} 个媒体资源 (${data.media_type})`;

            data.items.forEach((item, idx) => {
                const card = document.createElement('div');
                card.className = 'item-card';

                let previewHtml = '';
                if (item.media_type === 'image_set' || item.url.match(/\\.(jpe?g|png|webp)/i)) {
                    previewHtml = `<img class="item-thumb" src="${item.url}" loading="lazy" referrerpolicy="no-referrer">`;
                } else {
                    previewHtml = `<div class="item-video-placeholder">🎬 视频 #${idx + 1}</div>`;
                }

                card.innerHTML = `
                    ${previewHtml}
                    <div class="item-actions">
                        <span class="item-name" title="${item.filename}">${item.filename}</span>
                        <div style="display:flex; gap:4px;">
                            <button class="btn-secondary btn-sm" onclick="copyLink('${item.url}')">复制</button>
                            <button class="btn-primary btn-sm" onclick="downloadSingle(${idx})">下载</button>
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        function copyLink(url) {
            navigator.clipboard.writeText(url).then(() => {
                showToast("直链已复制到剪贴板！");
            });
        }

        async function downloadSingle(index) {
            if (!currentResult || !currentResult.items[index]) return;
            const item = currentResult.items[index];
            showToast(`正在下载 ${item.filename}...`);
            try {
                const resp = await fetch('/api/download_single', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ item, folder: `${currentResult.platform}_${currentResult.title}` })
                });
                const res = await resp.json();
                if (res.success) {
                    showToast(`下载完成: ${res.path}`);
                } else {
                    showToast(`下载失败: ${res.error}`, false);
                }
            } catch (e) {
                showToast("下载出错: " + e.message, false);
            }
        }

        async function downloadAll() {
            if (!currentResult) return;
            showToast(`开始批量下载共 ${currentResult.items.length} 个文件...`);
            try {
                const resp = await fetch('/api/download_all', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ result: currentResult })
                });
                const res = await resp.json();
                if (res.success) {
                    showToast(`全部下载完成！保存在 downloads 目录`);
                } else {
                    showToast(`下载失败: ${res.error}`, false);
                }
            } catch (e) {
                showToast("批量下载出错: " + e.message, false);
            }
        }
    </script>
</body>
</html>
"""


class SnapGetRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence default request logs in console
        pass

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8", errors="replace")
        data = json.loads(body) if body else {}

        if self.path == "/api/parse":
            self.handle_parse(data)
        elif self.path == "/api/download_single":
            self.handle_download_single(data)
        elif self.path == "/api/download_all":
            self.handle_download_all(data)
        else:
            self.send_response(404)
            self.end_headers()

    def _json_response(self, obj: dict, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def handle_parse(self, data: dict):
        text = data.get("text", "").strip()
        if not text:
            self._json_response({"success": False, "error": "Empty text provided"}, 400)
            return

        try:
            extractor = get_extractor(text)
            res = extractor.parse(text)

            res_dict = {
                "platform": res.platform,
                "title": res.title,
                "author": res.author,
                "media_type": res.media_type.value,
                "cover_url": res.cover_url,
                "description": res.description,
                "items": [
                    {
                        "url": item.url,
                        "media_type": item.media_type.value,
                        "title": item.title,
                        "filename": item.filename,
                        "headers": item.headers,
                    }
                    for item in res.items
                ],
            }
            self._json_response({"success": True, "data": res_dict})
        except Exception as e:
            self._json_response({"success": False, "error": str(e)}, 500)

    def handle_download_single(self, data: dict):
        try:
            raw_item = data.get("item", {})
            folder = data.get("folder")
            downloader = MediaDownloader()
            item = MediaItem(
                url=raw_item["url"],
                media_type=MediaType(raw_item.get("media_type", "video")),
                title=raw_item.get("title", ""),
                filename=raw_item.get("filename", "media.mp4"),
                headers=raw_item.get("headers", {}),
            )
            saved_path = downloader.download_item(item, folder_name=folder)
            self._json_response({"success": True, "path": str(saved_path)})
        except Exception as e:
            self._json_response({"success": False, "error": str(e)}, 500)

    def handle_download_all(self, data: dict):
        try:
            raw_res = data.get("result", {})
            downloader = MediaDownloader()
            items = [
                MediaItem(
                    url=it["url"],
                    media_type=MediaType(it.get("media_type", "video")),
                    title=it.get("title", ""),
                    filename=it.get("filename", "media.mp4"),
                    headers=it.get("headers", {}),
                )
                for it in raw_res.get("items", [])
            ]
            res = ParseResult(
                platform=raw_res.get("platform", "generic"),
                title=raw_res.get("title", "media"),
                author=raw_res.get("author", "user"),
                media_type=MediaType(raw_res.get("media_type", "video")),
                items=items,
            )
            saved_paths = downloader.download_all(res)
            self._json_response({"success": True, "paths": [str(p) for p in saved_paths]})
        except Exception as e:
            self._json_response({"success": False, "error": str(e)}, 500)


def run_web_server(host: str = "127.0.0.1", port: int = 8080, open_browser: bool = True):
    server = ThreadingHTTPServer((host, port), SnapGetRequestHandler)
    url = f"http://{host}:{port}"
    print(f"[SnapGet] 本地服务已启动: {url}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[SnapGet] 服务已安全关闭。")
        server.server_close()
