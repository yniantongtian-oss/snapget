# ⚡ SnapGet (全网主流自媒体无水印抓取工具)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License" />
  <img src="https://img.shields.io/badge/Platform-Windows%20|%20macOS%20|%20Linux-blue" alt="Platform" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" alt="Status" />
</p>

一款极轻量、开箱即用的多平台自媒体无水印原画视频/图集批量抓取器。自带现代暗黑风格本地 Web 交互界面与终端 CLI 工具，支持直接从手机端复制杂乱分享口令一键解析。

---

## ✨ 核心特性

- **无水印原画直提取**：
  - **抖音**：支持手机分享口令识别、自动重定向短链、提取 1080P/720P 无水印 MP4 真实流以及图集高清图片列表。
  - **小红书**：自动清洗分享短链接，突破平台压缩限制，提取无水印超清原图图集与视频。
  - **哔哩哔哩 (Bilibili)**：支持 `b23.tv` 短链与 `BV/AV` 号解析，获取封面、UP主信息及分块视频流。
  - **通用扩展支持**：集成 yt-dlp 引擎，作为兜底扩展支持主流国外平台（YouTube、X/Twitter 等）与其它国内视频站点。
- **开箱即用可视化 WebUI**：
  - 无需任何复杂前端环境或 Node.js 构建，零多余依赖，单命令自启本地轻量服务。
  - 暗黑极客质感，支持资源卡片式预览、一键复制直链、单文件下载与全选一键下载。
- **高效 CLI 终端工具**：
  - 基于 `rich` 打造美观终端交互：状态面板、实时多任务下载进度条与测速。
- **健壮工程化实现**：
  - 自动过滤与纠正 Windows 非法文件名字符（`\/*?:"<>|`），防止保存异常。
  - 解析器高度解耦（BaseExtractor），平台接口变动时单文件即可快速维护。

---

## 🚀 快速上手

### 1. 克隆仓库

```bash
git clone https://github.com/yniantongtian-oss/snapget.git
cd snapget
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 浏览器扩展插件 / 油猴脚本 (最爽玩法)

小红书、抖音等平台搜索往往有严格的网页反爬和登录风控。直接在浏览器里刷视频/图集，配合插件一键抓取最省心：

- **Chrome / Edge 扩展插件安装**：
  1. 打开浏览器扩展管理页面（Edge 输 `edge://extensions`，Chrome 输 `chrome://extensions`）。
  2. 开启右上角 **「开发者模式 (Developer mode)」**。
  3. 点击 **「加载解压缩的扩展 (Load unpacked)」**，选择本项目下的 `extension/` 文件夹即可。
  4. 之后无论是刷小红书还是刷抖音，右下角会自动悬浮 **「⚡ 提取无水印素材」** 按钮，点一下直接把屏幕上的原图、原画视频通通打包！
- **油猴脚本 (Tampermonkey)**：
  - 如果装了油猴插件，直接把根目录的 `snapget.user.js` 导入即可使用。

直接双击运行或在命令行敲入：

```bash
python -m snapget.main
```

启动后会自动在浏览器中弹出 `http://127.0.0.1:8080` 交互界面：
1. 直接把手机端或电脑端复制的内容粘进输入框（哪怕包含前后中文描述也无所谓，程序会自动正则筛选提取合法链接）。
2. 点击 **「开始解析」**。
3. 预览解析出的视频或无水印高清图集，点击 **「一键下载全部到本地」** 或单独下载。

#### 方式 B：终端命令行极速下载

```bash
# 自动解析并下载到默认 downloads 目录
python -m snapget.cli "https://v.douyin.com/xxxxx/"

# 指定保存路径
python -m snapget.cli "https://www.bilibili.com/video/BVxxxxxx" -o my_videos/

# 仅查看解析出的无水印直链清单，不执行下载
python -m snapget.cli "http://xhslink.com/a/xxxxx" --info-only
```

---

## 📂 项目结构

```text
snapget/
├── core/
│   ├── extractors/            # 平台独立解析层
│   │   ├── base.py            # 解析器基类与短链重定向
│   │   ├── douyin.py          # 抖音视频/图集解析器
│   │   ├── xiaohongshu.py     # 小红书原图/视频解析器
│   │   ├── bilibili.py        # B站音视频解析器
│   │   └── generic.py         # 通用 yt-dlp 扩展解析器
│   ├── downloader.py          # 流式分块下载引擎
│   └── models.py              # 数据结构与类型定义
├── web/
│   └── server.py              # 轻量原生可视化 Web 服务
├── tests/
│   └── test_core.py           # 核心用例单元测试
├── cli.py                     # CLI 命令行交互逻辑
├── main.py                    # 入口启动引导脚本
├── requirements.txt           # 核心依赖说明
├── pyproject.toml             # 打包配置文件
├── LICENSE                    # MIT 开源授权协议
└── README.md
```

---

## ⚠️ 免责声明 (Disclaimer)

1. 本项目仅供编程学习、技术交流以及个人合理备份使用。
2. 请勿将本项目用于任何商业牟利、批量侵权搬运或破坏平台正常运营秩序的行为。
3. 用户使用本项目下载的任何音视频、图文素材，其知识产权均归原作者所有，若因侵权产生任何纠纷，由使用者自行承担全部责任。

---

## 📄 开源许可

本项目基于 [MIT License](LICENSE) 协议发布，欢迎 Star、提 Issue 或发起 PR 共同完善！
