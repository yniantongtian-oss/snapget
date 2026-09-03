(function () {
  if (window.__snapget_injected__) return;
  window.__snapget_injected__ = true;

  // 1. Create Floating Action Button
  const floatBtn = document.createElement("div");
  floatBtn.id = "snapget-float-btn";
  floatBtn.innerHTML = `<span>⚡</span><span>提取无水印素材</span>`;
  document.body.appendChild(floatBtn);

  floatBtn.addEventListener("click", () => {
    extractMediaAndShowModal();
  });

  // 2. Extract media based on current site
  function extractMedia() {
    const host = window.location.hostname;
    const mediaList = [];
    const pageTitle = document.title.replace(/[\\/*?:"<>|]/g, "_").trim() || "media";

    // --- Xiaohongshu (小红书) ---
    if (host.includes("xiaohongshu.com")) {
      // 1. Check for video
      const videos = document.querySelectorAll("video");
      videos.forEach((v, idx) => {
        if (v.src && !v.src.startsWith("blob:")) {
          mediaList.push({
            type: "video",
            url: v.src,
            name: `${pageTitle}_video_${idx + 1}.mp4`,
          });
        }
      });

      // 2. Check for note images
      const images = document.querySelectorAll("img");
      const seenUrls = new Set();
      images.forEach((img) => {
        let src = img.currentSrc || img.src;
        if (src && (src.includes("xhscdn.com") || src.includes("spectrum"))) {
          // Remove query params to get original HD unwatermarked image
          let cleanUrl = src.split("?")[0].split("!")[0];
          // Filter out tiny icons / avatars
          if (
            !cleanUrl.includes("avatar") &&
            !cleanUrl.includes("icon") &&
            !seenUrls.has(cleanUrl)
          ) {
            seenUrls.add(cleanUrl);
            mediaList.push({
              type: "image",
              url: cleanUrl,
              name: `${pageTitle}_img_${seenUrls.size}.jpg`,
            });
          }
        }
      });
    }

    // --- Douyin (抖音) ---
    else if (host.includes("douyin.com")) {
      const videos = document.querySelectorAll("video");
      videos.forEach((v, idx) => {
        let src = v.src;
        if (!src) {
          const source = v.querySelector("source");
          if (source) src = source.src;
        }
        if (src) {
          // Ensure watermark-free
          let cleanUrl = src.replace("playwm", "play");
          mediaList.push({
            type: "video",
            url: cleanUrl,
            name: `${pageTitle}_douyin_${idx + 1}.mp4`,
          });
        }
      });
    }

    // --- Bilibili (B站) ---
    else if (host.includes("bilibili.com")) {
      const videos = document.querySelectorAll("video");
      videos.forEach((v, idx) => {
        if (v.src && !v.src.startsWith("blob:")) {
          mediaList.push({
            type: "video",
            url: v.src,
            name: `${pageTitle}_bilibili_${idx + 1}.mp4`,
          });
        }
      });
      // Also grab cover if present
      const coverMeta = document.querySelector('meta[property="og:image"]');
      if (coverMeta && coverMeta.content) {
        mediaList.push({
          type: "image",
          url: coverMeta.content,
          name: `${pageTitle}_cover.jpg`,
        });
      }
    }

    // --- Generic Web Media Fallback ---
    else {
      const videos = document.querySelectorAll("video");
      videos.forEach((v, idx) => {
        if (v.src && !v.src.startsWith("blob:")) {
          mediaList.push({
            type: "video",
            url: v.src,
            name: `${pageTitle}_video_${idx + 1}.mp4`,
          });
        }
      });
    }

    return mediaList;
  }

  // 3. Render In-Page Modal Dialog
  function extractMediaAndShowModal() {
    const media = extractMedia();
    const oldOverlay = document.getElementById("snapget-modal-overlay");
    if (oldOverlay) oldOverlay.remove();

    const overlay = document.createElement("div");
    overlay.id = "snapget-modal-overlay";

    let bodyHtml = "";
    if (media.length === 0) {
      bodyHtml = `<div style="text-align:center; padding:40px; color:#94a3b8;">
        未在当前可视区域探测到媒体素材。<br><br>
        提示：请确认您已点进具体的笔记详情或视频播放页，或上下滑动让页面加载出来后再点提取。
      </div>`;
    } else {
      bodyHtml = `<div class="snapget-grid">`;
      media.forEach((it, idx) => {
        let preview = "";
        if (it.type === "image") {
          preview = `<img src="${it.url}" referrerpolicy="no-referrer">`;
        } else {
          preview = `<div style="height:120px; background:#000; display:flex; align-items:center; justify-content:center; color:#38bdf8; font-weight:bold;">🎬 视频</div>`;
        }
        bodyHtml += `
          <div class="snapget-thumb-card">
            ${preview}
            <div class="card-action">
              <button class="snapget-btn-sm" style="background:#334155; color:#fff;" onclick="window.__snapget_copy__('${it.url}')">复制</button>
              <button class="snapget-btn-sm snapget-btn-primary" onclick="window.__snapget_download__('${it.url}', '${it.name}')">下载</button>
            </div>
          </div>
        `;
      });
      bodyHtml += `</div>`;
    }

    overlay.innerHTML = `
      <div class="snapget-modal-box">
        <div class="snapget-modal-header">
          <div class="snapget-modal-title">⚡ SnapGet 探测到 ${media.length} 个媒体素材</div>
          <button class="snapget-close-btn" id="snapget-close">✕</button>
        </div>
        <div class="snapget-modal-body">
          ${bodyHtml}
        </div>
        <div class="snapget-modal-footer">
          <span style="font-size:12px; color:#94a3b8;">原画/原图无损直链直出</span>
          ${
            media.length > 0
              ? `<button class="snapget-btn-sm snapget-btn-primary" style="padding:8px 16px; font-size:13px;" id="snapget-dl-all">一键批量下载全部</button>`
              : ""
          }
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    document.getElementById("snapget-close").addEventListener("click", () => {
      overlay.remove();
    });

    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) overlay.remove();
    });

    const dlAllBtn = document.getElementById("snapget-dl-all");
    if (dlAllBtn) {
      dlAllBtn.addEventListener("click", () => {
        media.forEach((it, i) => {
          setTimeout(() => {
            window.__snapget_download__(it.url, it.name);
          }, i * 300);
        });
      });
    }
  }

  // Global helper functions
  window.__snapget_copy__ = function (url) {
    navigator.clipboard.writeText(url).then(() => {
      alert("直链已复制到剪贴板！");
    });
  };

  window.__snapget_download__ = function (url, filename) {
    fetch(url)
      .then((resp) => resp.blob())
      .then((blob) => {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
      })
      .catch(() => {
        // Fallback direct window download
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        a.target = "_blank";
        document.body.appendChild(a);
        a.click();
        a.remove();
      });
  };
})();
