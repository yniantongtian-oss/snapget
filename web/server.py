import json
import os
import sys
import webbrowser
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any

try:
    from ..core import (
        get_extractor,
        MediaDownloader,
        ParseResult,
        MediaType,
        MediaItem,
        search_media,
        SearchResultItem,
    )
except (ImportError, ValueError):
    from core import (
        get_extractor,
        MediaDownloader,
        ParseResult,
        MediaType,
        MediaItem,
        search_media,
        SearchResultItem,
    )

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SnapGet - 自媒体全网聚合搜索与无水印抓取工具</title>
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: #151d2f;
            --card-hover: #1e2942;
            --accent: #38bdf8;
            --accent-hover: #0284c7;
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
            --border: #24324a;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --tag-bg: rgba(56, 189, 248, 0.12);
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
            padding: 30px 20px;
        }

        .container {
            max-width: 1000px;
            width: 100%;
        }

        header {
            text-align: center;
            margin-bottom: 25px;
        }

        .logo {
            font-size: 2.3rem;
            font-weight: 800;
            letter-spacing: -1px;
            background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
        }

        .subtitle {
            color: var(--text-sub);
            margin-top: 6px;
            font-size: 0.95rem;
        }

        .tabs {
            display: flex;
            gap: 10px;
            background: #111827;
            padding: 6px;
            border-radius: 12px;
            border: 1px solid var(--border);
            margin-bottom: 22px;
        }

        .tab-btn {
            flex: 1;
            padding: 10px 16px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 600;
            background: transparent;
            color: var(--text-sub);
            transition: all 0.2s;
        }

        .tab-btn.active {
            background: var(--card-bg);
            color: var(--accent);
            border: 1px solid var(--border);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            margin-bottom: 24px;
        }

        .search-bar-wrap {
            display: flex;
            gap: 12px;
            align-items: center;
        }

        input[type="text"] {
            flex: 1;
            height: 48px;
            background: #090d16;
            border: 1px solid var(--border);
            border-radius: 10px;
            color: var(--text-main);
            padding: 0 16px;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.2s;
        }

        input[type="text"]:focus {
            border-color: var(--accent);
        }

        textarea {
            width: 100%;
            height: 85px;
            background: #090d16;
            border: 1px solid var(--border);
            border-radius: 10px;
            color: var(--text-main);
            padding: 12px;
            font-size: 0.95rem;
            resize: vertical;
            outline: none;
            transition: border-color 0.2s;
        }

        textarea:focus {
            border-color: var(--accent);
        }

        .quick-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 14px;
            align-items: center;
        }

        .tag-label {
            font-size: 0.85rem;
            color: var(--text-sub);
        }

        .tag {
            background: var(--tag-bg);
            color: var(--accent);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid rgba(56, 189, 248, 0.2);
        }

        .tag:hover {
            background: var(--accent);
            color: #0b0f19;
        }

        button.btn-main {
            padding: 0 24px;
            height: 48px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 600;
            background: var(--accent);
            color: #0b0f19;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            white-space: nowrap;
            transition: all 0.2s;
        }

        button.btn-main:hover {
            background: var(--accent-hover);
            color: #fff;
        }

        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 18px;
            margin-top: 20px;
        }

        .result-card {
            background: #0d1424;
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s, border-color 0.2s;
        }

        .result-card:hover {
            transform: translateY(-3px);
            border-color: var(--accent);
        }

        .thumb-box {
            position: relative;
            width: 100%;
            height: 130px;
            background: #000;
        }

        .thumb-img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .duration-badge {
            position: absolute;
            bottom: 6px;
            right: 6px;
            background: rgba(0, 0, 0, 0.75);
            color: #fff;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.75rem;
        }

        .card-body {
            padding: 12px;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .card-title {
            font-size: 0.9rem;
            font-weight: 600;
            line-height: 1.4;
            margin-bottom: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
            color: var(--text-main);
        }

        .card-meta {
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: var(--text-sub);
            margin-bottom: 12px;
        }

        .author-name {
            color: var(--accent);
            max-width: 110px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .card-actions {
            display: flex;
            gap: 6px;
        }

        .btn-card-action {
            flex: 1;
            padding: 6px 0;
            border-radius: 6px;
            border: 1px solid var(--border);
            background: #151d2f;
            color: var(--text-main);
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            text-align: center;
        }

        .btn-card-action.primary {
            background: var(--accent);
            color: #0b0f19;
            border-color: var(--accent);
            font-weight: 600;
        }

        .btn-card-action:hover {
            opacity: 0.9;
        }

        /* Detail Modal / Parse Result View */
        #detail-view {
            display: none;
            margin-top: 20px;
        }

        .detail-header {
            display: flex;
            gap: 16px;
            align-items: flex-start;
            margin-bottom: 16px;
        }

        .detail-cover {
            width: 120px;
            height: 120px;
            object-fit: cover;
            border-radius: 10px;
        }

        .toast {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #1e2942;
            color: #fff;
            padding: 12px 20px;
            border-radius: 8px;
            border-left: 4px solid var(--accent);
            box-shadow: 0 10px 25px rgba(0,0,0,0.6);
            display: none;
            z-index: 1000;
        }

        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(0,0,0,0.3);
            border-radius: 50%;
            border-top-color: currentColor;
            animation: spin 0.8s linear infinite;
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
            <p class="subtitle">全网自媒体搜索、无水印原画视频/图集批量高速提取器</p>
        </header>

        <div class="tabs">
            <button class="tab-btn active" id="tabSearchBtn" onclick="switchTab('search')">🔍 UP主 / 关键词搜索发现</button>
            <button class="tab-btn" id="tabParseBtn" onclick="switchTab('parse')">🔗 粘贴直链无水印提取</button>
        </div>

        <!-- Tab 1: Search Module -->
        <div id="tab-search" class="card">
            <div class="search-bar-wrap">
                <input type="text" id="searchKeyword" placeholder="输入UP主名称、视频标题或关键词 (例如：老番茄、罗翔、科技、搞笑)..." onkeydown="if(event.key==='Enter') executeSearch()">
                <button class="btn-main" id="searchBtn" onclick="executeSearch()">
                    <span id="searchSpinner" style="display:none;" class="spinner"></span>
                    <span>立即搜索</span>
                </button>
            </div>
            <div class="quick-tags">
                <span class="tag-label">热门搜索推荐：</span>
                <span class="tag" onclick="quickSearch('罗翔说刑法')">罗翔说刑法</span>
                <span class="tag" onclick="quickSearch('老番茄')">老番茄</span>
                <span class="tag" onclick="quickSearch('影视飓风')">影视飓风</span>
                <span class="tag" onclick="quickSearch('黑神话悟空')">黑神话悟空</span>
                <span class="tag" onclick="quickSearch('AI人工智能')">AI人工智能</span>
                <span class="tag" onclick="quickSearch('短剧')">热门短剧</span>
            </div>

            <div id="search-status" style="margin-top:16px; font-size: 0.9rem; color: var(--text-sub); display:none;"></div>
            <div class="results-grid" id="searchResultsGrid"></div>
        </div>

        <!-- Tab 2: Direct URL Parser -->
        <div id="tab-parse" class="card" style="display: none;">
            <div style="display:flex; flex-direction:column; gap:12px;">
                <textarea id="urlInput" placeholder="直接粘贴手机端复制的抖音、小红书、B站分享内容或网页链接，支持包含多余中文，自动过滤..."></textarea>
                <div style="display:flex; justify-content:flex-end; gap:10px;">
                    <button class="btn-card-action" style="padding: 10px 16px; width:auto;" onclick="document.getElementById('urlInput').value=''">清空</button>
                    <button class="btn-main" id="parseBtn" onclick="executeParse()">
                        <span id="parseSpinner" style="display:none;" class="spinner"></span>
                        <span>开始无水印解析</span>
                    </button>
                </div>
            </div>
        </div>

        <!-- Shared Detail / Parse View -->
        <div class="card" id="detail-view">
            <div class="detail-header">
                <img id="detailCover" class="detail-cover" src="" alt="封面">
                <div style="flex:1;">
                    <h3 id="detailTitle" style="font-size:1.1rem; margin-bottom:8px;"></h3>
                    <p id="detailAuthor" style="color:var(--accent); font-size:0.9rem; margin-bottom:6px;"></p>
                    <p id="detailDesc" style="color:var(--text-sub); font-size:0.85rem; max-height:50px; overflow-y:auto;"></p>
                </div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px;">
                <span id="detailCount" style="color:var(--text-sub); font-size:0.85rem;"></span>
                <button class="btn-main" style="height:36px; padding:0 16px; background:var(--success); color:#fff;" onclick="downloadAllCurrent()">一键打包全部下载</button>
            </div>
            <div class="results-grid" id="detailItemsGrid"></div>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        let currentDetailResult = null;

        function showToast(msg, isSuccess = true) {
            const toast = document.getElementById('toast');
            toast.textContent = msg;
            toast.style.borderLeftColor = isSuccess ? 'var(--success)' : 'var(--danger)';
            toast.style.display = 'block';
            setTimeout(() => { toast.style.display = 'none'; }, 3500);
        }

        function switchTab(tab) {
            document.getElementById('tab-search').style.display = tab === 'search' ? 'block' : 'none';
            document.getElementById('tab-parse').style.display = tab === 'parse' ? 'block' : 'none';
            document.getElementById('tabSearchBtn').className = 'tab-btn ' + (tab === 'search' ? 'active' : '');
            document.getElementById('tabParseBtn').className = 'tab-btn ' + (tab === 'parse' ? 'active' : '');
        }

        function quickSearch(kw) {
            document.getElementById('searchKeyword').value = kw;
            executeSearch();
        }

        async function executeSearch() {
            const kw = document.getElementById('searchKeyword').value.trim();
            if (!kw) {
                showToast("请输入想要搜索的UP主名称或关键词！", false);
                return;
            }

            const btn = document.getElementById('searchBtn');
            const spinner = document.getElementById('searchSpinner');
            const statusEl = document.getElementById('search-status');
            const grid = document.getElementById('searchResultsGrid');

            btn.disabled = true;
            spinner.style.display = 'inline-block';
            statusEl.style.display = 'block';
            statusEl.textContent = `正在搜索与「${kw}」相关的精彩视频与UP主作品...`;
            grid.innerHTML = '';

            try {
                const resp = await fetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ keyword: kw, platform: 'bilibili' })
                });
                const res = await resp.json();
                if (!res.success) {
                    showToast(res.error || "搜索出现异常", false);
                    statusEl.textContent = "搜索失败: " + (res.error || "未知异常");
                    return;
                }

                const items = res.results || [];
                statusEl.textContent = `共搜索到 ${items.length} 条相关作品，点击即可直接下载或提取直链：`;

                items.forEach((it) => {
                    const card = document.createElement('div');
                    card.className = 'result-card';
                    card.innerHTML = `
                        <div class="thumb-box">
                            <img class="thumb-img" src="${it.cover}" loading="lazy" referrerpolicy="no-referrer">
                            <span class="duration-badge">${it.duration || '视频'}</span>
                        </div>
                        <div class="card-body">
                            <div class="card-title" title="${it.title}">${it.title}</div>
                            <div class="card-meta">
                                <span class="author-name" title="${it.author}">@${it.author}</span>
                                <span>${it.play_count > 10000 ? (it.play_count / 10000).toFixed(1) + '万播放' : it.play_count + '次播放'}</span>
                            </div>
                            <div class="card-actions">
                                <button class="btn-card-action primary" onclick="parseAndDownloadDirectly('${it.url}')">一键下载</button>
                                <button class="btn-card-action" onclick="parseAndShowDetail('${it.url}')">提取直链</button>
                            </div>
                        </div>
                    `;
                    grid.appendChild(card);
                });
                showToast(`搜索成功！已呈现 ${items.length} 个结果`);
            } catch (err) {
                showToast("网络通信异常: " + err.message, false);
            } finally {
                btn.disabled = false;
                spinner.style.display = 'none';
            }
        }

        async function parseAndDownloadDirectly(targetUrl) {
            showToast("正在解析并自动开启高速下载通道...");
            try {
                const parseResp = await fetch('/api/parse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: targetUrl })
                });
                const parseData = await parseResp.json();
                if (!parseData.success) {
                    showToast(parseData.error || "直链解析失败", false);
                    return;
                }
                showToast(`解析完成：${parseData.data.title.substring(0, 15)}... 开始写入硬盘`);

                const dlResp = await fetch('/api/download_all', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ result: parseData.data })
                });
                const dlData = await dlResp.json();
                if (dlData.success) {
                    showToast(`下载完成！已保存到本地 downloads 目录`, true);
                } else {
                    showToast(`下载遇到错误: ${dlData.error}`, false);
                }
            } catch (e) {
                showToast("请求失败: " + e.message, false);
            }
        }

        async function parseAndShowDetail(targetUrl) {
            showToast("正在提取原画直链与图集...");
            try {
                const resp = await fetch('/api/parse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: targetUrl })
                });
                const res = await resp.json();
                if (!res.success) {
                    showToast(res.error || "解析失败", false);
                    return;
                }
                currentDetailResult = res.data;
                renderDetailView(currentDetailResult);
                showToast("无水印原画直链提取完毕，已展现于下方卡片！");
                document.getElementById('detail-view').scrollIntoView({ behavior: 'smooth' });
            } catch (err) {
                showToast("解析出错: " + err.message, false);
            }
        }

        async function executeParse() {
            const text = document.getElementById('urlInput').value.trim();
            if (!text) {
                showToast("请先粘贴分享内容或链接！", false);
                return;
            }
            const btn = document.getElementById('parseBtn');
            const spinner = document.getElementById('parseSpinner');
            btn.disabled = true;
            spinner.style.display = 'inline-block';
            try {
                await parseAndShowDetail(text);
            } finally {
                btn.disabled = false;
                spinner.style.display = 'none';
            }
        }

        function renderDetailView(data) {
            const view = document.getElementById('detail-view');
            view.style.display = 'block';
            document.getElementById('detailTitle').textContent = data.title;
            document.getElementById('detailAuthor').textContent = `@${data.author} (${data.platform.toUpperCase()})`;
            document.getElementById('detailDesc').textContent = data.description || '无详细介绍';
            document.getElementById('detailCover').src = data.cover_url || '';
            document.getElementById('detailCount').textContent = `共提取出 ${data.items.length} 个无水印资源文件`;

            const grid = document.getElementById('detailItemsGrid');
            grid.innerHTML = '';

            data.items.forEach((item, idx) => {
                const card = document.createElement('div');
                card.className = 'result-card';

                let previewHtml = '';
                if (item.media_type === 'image_set' || item.url.match(/\\.(jpe?g|png|webp)/i)) {
                    previewHtml = `<img class="thumb-img" style="height:120px;" src="${item.url}" loading="lazy" referrerpolicy="no-referrer">`;
                } else {
                    previewHtml = `<div style="height:120px; background:#000; display:flex; align-items:center; justify-content:center; color:var(--accent); font-weight:bold;">🎬 视频 #${idx + 1}</div>`;
                }

                card.innerHTML = `
                    ${previewHtml}
                    <div class="card-body" style="padding:8px;">
                        <span style="font-size:0.75rem; color:var(--text-sub); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${item.filename}">${item.filename}</span>
                        <div class="card-actions" style="margin-top:8px;">
                            <button class="btn-card-action" onclick="copyLink('${item.url}')">复制直链</button>
                            <button class="btn-card-action primary" onclick="downloadSingleFile(${idx})">立即下载</button>
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

        async function downloadSingleFile(index) {
            if (!currentDetailResult || !currentDetailResult.items[index]) return;
            const item = currentDetailResult.items[index];
            showToast(`正在下载 ${item.filename}...`);
            try {
                const resp = await fetch('/api/download_single', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ item, folder: `${currentDetailResult.platform}_${currentDetailResult.title}` })
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

        async function downloadAllCurrent() {
            if (!currentDetailResult) return;
            showToast(`开始批量下载共 ${currentDetailResult.items.length} 个文件...`);
            try {
                const resp = await fetch('/api/download_all', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ result: currentDetailResult })
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

        if self.path == "/api/search":
            self.handle_search(data)
        elif self.path == "/api/parse":
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

    def handle_search(self, data: dict):
        kw = data.get("keyword", "").strip()
        platform = data.get("platform", "bilibili")
        if not kw:
            self._json_response({"success": False, "error": "关键词不能为空"}, 400)
            return

        try:
            results = search_media(kw, platform=platform)
            res_list = [
                {
                    "platform": it.platform,
                    "title": it.title,
                    "author": it.author,
                    "url": it.url,
                    "cover": it.cover,
                    "duration": it.duration,
                    "play_count": it.play_count,
                    "bvid": it.bvid,
                    "description": it.description,
                }
                for it in results
            ]
            self._json_response({"success": True, "results": res_list})
        except Exception as e:
            self._json_response({"success": False, "error": str(e)}, 500)

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
