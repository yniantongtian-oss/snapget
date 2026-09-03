import re
import json
import urllib.parse
from .base import BaseExtractor
from ..models import ParseResult, MediaItem, MediaType


class BilibiliExtractor(BaseExtractor):
    PLATFORM_NAME = "bilibili"
    URL_PATTERNS = [
        re.compile(r"bilibili\.com", re.IGNORECASE),
        re.compile(r"b23\.tv", re.IGNORECASE),
    ]

    BILI_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.bilibili.com/",
    }

    def parse(self, raw_text_or_url: str) -> ParseResult:
        clean_url = self.extract_url_from_text(raw_text_or_url) or raw_text_or_url
        redirected_url = self.fetch_redirect_url(clean_url, custom_headers=self.BILI_HEADERS)

        bv_match = re.search(r"(BV[0-9a-zA-Z]{10})", redirected_url)
        if not bv_match:
            # Check for av id
            av_match = re.search(r"av(\d+)", redirected_url, re.IGNORECASE)
            if not av_match:
                raise ValueError(f"Could not find Bilibili BV or AV id from {redirected_url}")
            aid = av_match.group(1)
            bvid = None
        else:
            bvid = bv_match.group(1)
            aid = None

        # 1. Query video view info
        view_api = (
            f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            if bvid
            else f"https://api.bilibili.com/x/web-interface/view?aid={aid}"
        )

        resp_text = self.http_get(view_api, headers=self.BILI_HEADERS)
        view_data = json.loads(resp_text)
        if view_data.get("code") != 0:
            raise RuntimeError(f"Bilibili API error: {view_data.get('message')}")

        data = view_data.get("data", {})
        title = data.get("title", f"bilibili_{bvid or aid}")
        author = data.get("owner", {}).get("name", "bilibili_up")
        cover_url = data.get("pic")
        cid = data.get("cid")

        if not cid:
            pages = data.get("pages", [])
            if pages:
                cid = pages[0].get("cid")

        if not cid:
            raise RuntimeError(f"Unable to locate CID for video {bvid or aid}")

        # 2. Query playurl API for direct stream URL
        play_api = (
            f"https://api.bilibili.com/x/player/playurl?"
            f"bvid={bvid or ''}&cid={cid}&qn=80&fnval=0&fnver=0&fourk=1"
        )
        play_resp_text = self.http_get(play_api, headers=self.BILI_HEADERS)
        play_data = json.loads(play_resp_text)

        durl_list = play_data.get("data", {}).get("durl", [])
        if not durl_list:
            raise RuntimeError(f"Could not retrieve video stream url from Bilibili CID {cid}")

        video_url = durl_list[0].get("url")

        items = [
            MediaItem(
                url=video_url,
                media_type=MediaType.VIDEO,
                title=title,
                filename=f"{author}_{bvid or aid}.mp4",
                headers={
                    "Referer": "https://www.bilibili.com/",
                    "User-Agent": self.BILI_HEADERS["User-Agent"],
                },
                extra={"cid": cid, "bvid": bvid},
            )
        ]

        return ParseResult(
            platform=self.PLATFORM_NAME,
            title=title,
            author=author,
            media_type=MediaType.VIDEO,
            items=items,
            cover_url=cover_url,
            raw_url=clean_url,
            description=data.get("desc", ""),
        )
