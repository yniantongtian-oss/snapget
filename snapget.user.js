// ==UserScript==
// @name         SnapGet - 全网自媒体无水印素材极速提取助手
// @namespace    https://github.com/yniantongtian-oss/snapget
// @version      1.2.0
// @description  在浏览抖音、小红书、B站等网页时，右下角悬浮一键提取高清无水印原画视频与原图图集！
// @author       yniantongtian-oss
// @match        *://*.douyin.com/*
// @match        *://*.xiaohongshu.com/*
// @match        *://*.bilibili.com/*
// @match        *://*.kuaishou.com/*
// @match        *://*.weibo.com/*
// @grant        GM_setClipboard
// @grant        GM_download
// @run-at       document-idle
// ==/UserScript==

(function () {
  'use strict';

  // Inject CSS
  const style = document.createElement('style');
  style.textContent = `
    #snapget-float-btn {
      position: fixed;
      bottom: 80px;
      right: 24px;
      z-index: 99999999;
      background: linear-gradient(135deg, #38bdf8 0%, #6366f1 100%);
      color: #ffffff;
      padding: 10px 18px;
      border-radius: 50px;
      font-size: 14px;
      font-weight: bold;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      border: 1px solid rgba(255, 255, 255, 0.3);
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      user-select: none;
    }
    #snapget-float-btn:hover {
      transform: scale(1.05);
      box-shadow: 0 12px 28px rgba(56, 189, 248, 0.5);
    }
    #snapget-modal-overlay {
      position: fixed;
      top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(4px);
      z-index: 999999999;
      display: flex; align-items: center; justify-content: center;
    }
    .snapget-modal-box {
      background: #0f172a; color: #f8fafc;
      width: 90%; max-width: 780px; max-height: 85vh;
      border-radius: 16px; border: 1px solid #334155;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
      display: flex; flex-direction: column; overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .snapget-modal-header {
      padding: 16px 20px; background: #1e293b; border-bottom: 1px solid #334155;
      display: flex; justify-content: space-between; align-items: center;
    }
    .snapget-modal-title { font-size: 16px; font-weight: bold; color: #38bdf8; }
    .snapget-close-btn { background: transparent; border: none; color: #94a3b8; font-size: 20px; cursor: pointer; }
    .snapget-modal-body { padding: 20px; overflow-y: auto; flex: 1; }
    .snapget-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; }
    .snapget-thumb-card { background: #1e293b; border-radius: 8px; overflow: hidden; border: 1px solid #334155; }
    .snapget-thumb-card img { width: 100%; height: 120px; object-fit: cover; }
    .snapget-thumb-card .card-action { padding: 8px; display: flex; gap: 6px; }
    .snapget-btn-sm {
      flex: 1; padding: 5px 0; font-size: 12px; border-radius: 4px;
      border: none; cursor: pointer; font-weight: 600; text-align: center;
    }
    .snapget-btn-primary { background: #38bdf8; color: #0f172a; }
  `;
  document.head.appendChild(style);

  // Floating Button
  const floatBtn = document.createElement('div');
  floatBtn.id = 'snapget-float-btn';
  floatBtn.innerHTML = `<span>⚡</span><span>提取无水印素材</span>`;
  document.body.appendChild(floatBtn);

  floatBtn.addEventListener('click', () => {
    extractAndShow();
  });

  function extractMedia() {
    const host = window.location.hostname;
    const mediaList = [];
    const pageTitle = document.title.replace(/[\\/*?:"<>|]/g, '_').trim() || 'media';

    if (host.includes('xiaohongshu.com')) {
      document.querySelectorAll('video').forEach((v, idx) => {
        if (v.src && !v.src.startsWith('blob:')) {
          mediaList.push({ type: 'video', url: v.src, name: `${pageTitle}_video_${idx + 1}.mp4` });
        }
      });
      const seen = new Set();
      document.querySelectorAll('img').forEach((img) => {
        const src = img.currentSrc || img.src;
        if (src && (src.includes('xhscdn.com') || src.includes('spectrum'))) {
          const cleanUrl = src.split('?')[0].split('!')[0];
          if (!cleanUrl.includes('avatar') && !cleanUrl.includes('icon') && !seen.has(cleanUrl)) {
            seen.add(cleanUrl);
            mediaList.push({ type: 'image', url: cleanUrl, name: `${pageTitle}_img_${seen.size}.jpg` });
          }
        }
      });
    } else if (host.includes('douyin.com')) {
      document.querySelectorAll('video').forEach((v, idx) => {
        let src = v.src || (v.querySelector('source') ? v.querySelector('source').src : '');
        if (src) {
          mediaList.push({ type: 'video', url: src.replace('playwm', 'play'), name: `${pageTitle}_douyin_${idx + 1}.mp4` });
        }
      });
    } else if (host.includes('bilibili.com')) {
      document.querySelectorAll('video').forEach((v, idx) => {
        if (v.src && !v.src.startsWith('blob:')) {
          mediaList.push({ type: 'video', url: v.src, name: `${pageTitle}_bilibili_${idx + 1}.mp4` });
        }
      });
    }
    return mediaList;
  }

  function extractAndShow() {
    const media = extractMedia();
    const old = document.getElementById('snapget-modal-overlay');
    if (old) old.remove();

    const overlay = document.createElement('div');
    overlay.id = 'snapget-modal-overlay';

    let bodyHtml = '';
    if (media.length === 0) {
      bodyHtml = '<div style="text-align:center; padding:40px; color:#94a3b8;">当前可视区域暂未探测到媒体素材，请点进具体图文/视频详情后再点击提取。</div>';
    } else {
      bodyHtml = '<div class="snapget-grid">';
      media.forEach((it) => {
        const preview = it.type === 'image'
          ? `<img src="${it.url}" referrerpolicy="no-referrer">`
          : `<div style="height:120px; background:#000; display:flex; align-items:center; justify-content:center; color:#38bdf8; font-weight:bold;">🎬 视频</div>`;
        bodyHtml += `
          <div class="snapget-thumb-card">
            ${preview}
            <div class="card-action">
              <button class="snapget-btn-sm" style="background:#334155; color:#fff;" onclick="navigator.clipboard.writeText('${it.url}').then(()=>alert('直链已复制！'))">复制</button>
              <a class="snapget-btn-sm snapget-btn-primary" href="${it.url}" download="${it.name}" target="_blank">下载</a>
            </div>
          </div>
        `;
      });
      bodyHtml += '</div>';
    }

    overlay.innerHTML = `
      <div class="snapget-modal-box">
        <div class="snapget-modal-header">
          <div class="snapget-modal-title">⚡ SnapGet 探测到 ${media.length} 个媒体素材</div>
          <button class="snapget-close-btn" onclick="document.getElementById('snapget-modal-overlay').remove()">✕</button>
        </div>
        <div class="snapget-modal-body">${bodyHtml}</div>
      </div>
    `;
    document.body.appendChild(overlay);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
  }
})();
