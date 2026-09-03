#!/usr/bin/env python3
"""
SnapGet 入口脚本
支持直接通过命令行执行或双击启动本地 Web 交互模式。
"""
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    from snapget.cli import cli_main
except ImportError:
    from cli import cli_main

if __name__ == "__main__":
    cli_main()
