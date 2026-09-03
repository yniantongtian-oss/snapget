import re
import json
import urllib.request
import urllib.parse
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SearchResultItem:
    platform: str
    title: str
    author: str
    url: str
    cover: str
    duration: str
    play_count: int
    bvid: Optional[str] = None
    description: str = ""


class BilibiliSearcher:
    """Public searcher for Bilibili videos, creators, and topics."""

    SEARCH_API = "https://api.bilibili.com/x/web-interface/search/type"
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.bilibili.com/",
    }

    @staticmethod
    def _clean_html_tags(text: str) -> str:
        """Removes HTML highlighting tags like <em class="keyword">."""
        return re.sub(r"<[^>]+>", "", text).strip()

    def search(self, keyword: str, page: int = 1, page_size: int = 20) -> List[SearchResultItem]:
        query_params = urllib.parse.urlencode({
            "keyword": keyword,
            "search_type": "video",
            "page": page,
            "page_size": page_size,
        })
        full_url = f"{self.SEARCH_API}?{query_params}"

        req = urllib.request.Request(full_url, headers=self.HEADERS)
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("code") != 0:
            raise RuntimeError(f"Bilibili search error: {data.get('message')}")

        raw_results = data.get("data", {}).get("result", [])
        items: List[SearchResultItem] = []

        for item in raw_results:
            title = self._clean_html_tags(item.get("title", ""))
            author = item.get("author", "未知UP主")
            bvid = item.get("bvid", "")
            video_url = f"https://www.bilibili.com/video/{bvid}" if bvid else item.get("arcurl", "")
            
            cover = item.get("pic", "")
            if cover.startswith("//"):
                cover = "https:" + cover

            duration = item.get("duration", "")
            play = item.get("play", 0)
            desc = self._clean_html_tags(item.get("description", ""))

            items.append(
                SearchResultItem(
                    platform="bilibili",
                    title=title,
                    author=author,
                    url=video_url,
                    cover=cover,
                    duration=duration,
                    play_count=play,
                    bvid=bvid,
                    description=desc,
                )
            )

        return items


def search_media(keyword: str, platform: str = "bilibili") -> List[SearchResultItem]:
    """Unified search entry point."""
    if platform.lower() in ("bilibili", "bili"):
        searcher = BilibiliSearcher()
        return searcher.search(keyword)
    
    # Fallback to Bilibili default
    searcher = BilibiliSearcher()
    return searcher.search(keyword)
