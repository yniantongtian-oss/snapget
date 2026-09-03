import argparse
import sys
from pathlib import Path

try:
    from .core import get_extractor, MediaDownloader, ParseResult, search_media
except (ImportError, ValueError):
    from core import get_extractor, MediaDownloader, ParseResult, search_media

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn
    console = Console()
    HAS_RICH = True
except ImportError:
    console = None
    HAS_RICH = False


def print_info(msg: str):
    if HAS_RICH:
        console.print(f"[cyan]ℹ {msg}[/cyan]")
    else:
        print(f"[*] {msg}")


def print_success(msg: str):
    if HAS_RICH:
        console.print(f"[green]✔ {msg}[/green]")
    else:
        print(f"[+] {msg}")


def print_error(msg: str):
    if HAS_RICH:
        console.print(f"[bold red]✖ {msg}[/bold red]")
    else:
        print(f"[!] {msg}")


def cli_main():
    parser = argparse.ArgumentParser(
        description="SnapGet - 全网主流自媒体无水印音视频/图集批量抓取工具"
    )
    parser.add_argument("url", nargs="?", help="目标网页链接或手机端复制的完整分享口令")
    parser.add_argument("-o", "--output", default="downloads", help="下载保存路径 (默认: downloads)")
    parser.add_argument("-s", "--search", help="直接按关键词或UP主搜索视频并列出")
    parser.add_argument("-w", "--web", action="store_true", help="启动本地 Web 交互页面")
    parser.add_argument("-p", "--port", type=int, default=8080, help="Web 服务监听端口 (默认: 8080)")
    parser.add_argument("--info-only", action="store_true", help="仅解析媒体直链，不执行下载")

    args = parser.parse_args()

    if args.search:
        print_info(f"正在全网搜索关键词/UP主: [bold]{args.search}[/bold] ...")
        results = search_media(args.search)
        if not results:
            print_error("未搜索到相关作品")
            return
        if HAS_RICH:
            table = Table(title=f"「{args.search}」搜索结果 (前 {len(results)} 条)", border_style="green")
            table.add_column("序号", style="cyan")
            table.add_column("标题", style="white")
            table.add_column("UP主/作者", style="yellow")
            table.add_column("时长", style="magenta")
            table.add_column("链接", style="blue")
            for idx, it in enumerate(results, 1):
                table.add_row(str(idx), it.title[:35], f"@{it.author}", it.duration, it.url)
            console.print(table)
        else:
            for idx, it in enumerate(results, 1):
                print(f"[{idx}] @{it.author} - {it.title} ({it.duration}) -> {it.url}")
        return

    if args.web or not args.url:
        from .web import run_web_server
        print_info(f"正在启动 SnapGet 本地可视化 Web 服务 (端口: {args.port})...")
        run_web_server(port=args.port)
        return

    # CLI download mode
    print_info("正在分析链接并识别目标平台...")
    try:
        extractor = get_extractor(args.url)
        print_info(f"匹配到解析器: [bold]{extractor.PLATFORM_NAME.upper()}[/bold]")

        res: ParseResult = extractor.parse(args.url)

        if HAS_RICH:
            table = Table(title="解析结果概览", border_style="cyan")
            table.add_column("字段", style="bold yellow")
            table.add_column("内容", style="white")
            table.add_row("所属平台", res.platform.upper())
            table.add_row("标题", res.title)
            table.add_row("作者", f"@{res.author}")
            table.add_row("媒体类型", res.media_type.value)
            table.add_row("资源总数", str(len(res.items)))
            console.print(table)
        else:
            print(f"平台: {res.platform} | 作者: {res.author} | 标题: {res.title} | 资源: {len(res.items)} 个")

        if args.info_only:
            print_info("提取到的直链清单:")
            for idx, item in enumerate(res.items, 1):
                print(f"  [{idx}] {item.filename} -> {item.url}")
            return

        print_info(f"开始下载至目录: {args.output} ...")
        downloader = MediaDownloader(output_dir=args.output)

        if HAS_RICH:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                console=console,
            ) as progress:
                for item in res.items:
                    task = progress.add_task(f"下载 {item.filename[:25]}...", total=None)
                    def cb(dl, total):
                        progress.update(task, completed=dl, total=total)
                    downloader.download_item(item, folder_name=f"{res.platform}_{res.title}", progress_callback=cb)
        else:
            downloader.download_all(res, item_callback=lambda it, p: print(f"  ✔ {it.filename} 完成"))

        print_success(f"全部任务下载完成！保存在 {args.output} 目录下。")

    except Exception as e:
        print_error(f"处理失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
