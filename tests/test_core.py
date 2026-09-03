import sys
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.downloader import sanitize_filename
from core.extractors.base import BaseExtractor
from core.extractors.douyin import DouyinExtractor
from core.extractors.xiaohongshu import XiaohongshuExtractor
from core.extractors.bilibili import BilibiliExtractor
from core.extractors import get_extractor


class TestSnapGet(unittest.TestCase):
    def test_sanitize_filename(self):
        raw = '视频/标题: "测试" <非法字符>? * 123 | 换行\n'
        cleaned = sanitize_filename(raw)
        self.assertNotIn("/", cleaned)
        self.assertNotIn(":", cleaned)
        self.assertNotIn('"', cleaned)
        self.assertNotIn("<", cleaned)
        self.assertNotIn(">", cleaned)
        self.assertNotIn("?", cleaned)
        self.assertNotIn("*", cleaned)
        self.assertNotIn("|", cleaned)
        self.assertNotIn("\n", cleaned)

    def test_extract_url_from_messy_text(self):
        text = "7.20 复制打开抖音，看看【小猫咪的作品】 https://v.douyin.com/iABC123/ 复制此链接"
        url = BaseExtractor.extract_url_from_text(text)
        self.assertEqual(url, "https://v.douyin.com/iABC123/")

    def test_extractor_matching(self):
        dy_text = "https://v.douyin.com/iABC123/"
        xhs_text = "74 探索发现 http://xhslink.com/a/ABCDEF 复制本条信息"
        bili_text = "【名场面】https://www.bilibili.com/video/BV1xx411c7mD 爽！"

        self.assertIsInstance(get_extractor(dy_text), DouyinExtractor)
        self.assertIsInstance(get_extractor(xhs_text), XiaohongshuExtractor)
        self.assertIsInstance(get_extractor(bili_text), BilibiliExtractor)


if __name__ == "__main__":
    unittest.main()
