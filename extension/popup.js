document.addEventListener("DOMContentLoaded", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const statusEl = document.getElementById("statusInfo");
  const triggerBtn = document.getElementById("triggerBtn");
  const openLocalBtn = document.getElementById("openLocalBtn");

  if (tab && tab.url) {
    const url = new URL(tab.url);
    if (url.hostname.includes("xiaohongshu.com")) {
      statusEl.textContent = "检测到【小红书】网页，可直接一键提取无水印原图图集与视频。";
    } else if (url.hostname.includes("douyin.com")) {
      statusEl.textContent = "检测到【抖音】网页，可直接一键提取高清无水印视频。";
    } else if (url.hostname.includes("bilibili.com")) {
      statusEl.textContent = "检测到【B站】网页，可直接提取当前视频流与高清封面。";
    } else {
      statusEl.textContent = `当前站点: ${url.hostname}，支持提取通用媒体文件。`;
    }
  }

  triggerBtn.addEventListener("click", async () => {
    if (tab && tab.id) {
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          const btn = document.getElementById("snapget-float-btn");
          if (btn) {
            btn.click();
          } else {
            alert("请刷新当前页面后再次尝试！");
          }
        },
      });
      window.close();
    }
  });

  openLocalBtn.addEventListener("click", () => {
    chrome.tabs.create({ url: "http://127.0.0.1:8080" });
  });
});
