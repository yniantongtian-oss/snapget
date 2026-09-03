import re
import json
import urllib.parse
from .base import BaseExtractor
from ..models import ParseResult, MediaItem, MediaType


class DouyinExtractor(BaseExtractor):
    PLATFORM_NAME = "douyin"
    URL_PATTERNS = [
        re.compile(r"douyin\.com", re.IGNORECASE),
        re.compile(r"iesdouyin\.com", re.IGNORECASE),
    ]

    MOBILE_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        )
    }

    def parse(self, raw_text_or_url: str) -> ParseResult:
        clean_url = self.extract_url_from_text(raw_text_or_url) or raw_text_or_url
        redirected_url = self.fetch_redirect_url(clean_url, custom_headers=self.MOBILE_HEADERS)

        # Extract item ID (from /video/123456 or /note/123456 or modal_id=123456)
        id_match = re.search(r"/(?:video|note)/(\d+)", redirected_url)
        if not id_match:
            id_match = re.search(r"modal_id=(\d+)", redirected_url)

        item_id = id_match.group(1) if id_match else None
        if not item_id:
            raise ValueError(f"Could not locate Douyin item ID from URL: {redirected_url}")

        # Try mobile API endpoint first
        api_url = f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={item_id}"
        data = None
        try:
            resp_str = self.http_get(api_url, headers=self.MOBILE_HEADERS)
            json_data = json.loads(resp_str)
            item_list = json_data.get("item_list", [])
            if item_list:
                data = item_list[0]
        except Exception:
            pass

        # Fallback to fetching webpage HTML and parsing _ROUTER_DATA
        if not data:
            web_url = f"https://www.douyin.com/video/{item_id}"
            html = self.http_get(web_url)
            router_match = re.search(r"window\._ROUTER_DATA\s*=\s*(\{.+?\});</script>", html)
            if router_match:
                try:
                    router_data = json.loads(router_match.group(1))
                    loader_data = router_data.get("loaderData", {})
                    for v in loader_data.values():
                        if isinstance(v, dict) and "video" in v:
                            data = v
                            break
                except Exception:
                    pass

        title = "douyin_media"
        author = "douyin_user"
        cover_url = None
        items = []

        if data:
            title = data.get("desc", "").strip() or f"douyin_{item_id}"
            author = data.get("author", {}).get("nickname", "douyin_user")
            cover_list = data.get("video", {}).get("cover", {}).get("url_list", [])
            cover_url = cover_list[0] if cover_list else None

            # Check if this is an image gallery (note)
            images = data.get("images")
            if images and isinstance(images, list):
                # Multiple images
                for idx, img_info in enumerate(images, start=1):
                    url_list = img_info.get("url_list", [])
                    if url_list:
                        raw_img_url = url_list[0]
                        items.append(
                            MediaItem(
                                url=raw_img_url,
                                media_type=MediaType.IMAGE_SET,
                                title=title,
                                filename=f"{author}_{item_id}_img_{idx:02d}.jpg",
                                headers={"Referer": "https://www.douyin.com/"},
                            )
                        )
                return ParseResult(
                    platform=self.PLATFORM_NAME,
                    title=title,
                    author=author,
                    media_type=MediaType.IMAGE_SET,
                    items=items,
                    cover_url=cover_url,
                    raw_url=clean_url,
                )

            # Otherwise, video item
            video_info = data.get("video", {})
            play_addr = video_info.get("play_addr", {}).get("url_list", [])
            if play_addr:
                video_url = play_addr[0].replace("playwm", "play")
                items.append(
                    MediaItem(
                        url=video_url,
                        media_type=MediaType.VIDEO,
                        title=title,
                        filename=f"{author}_{item_id}.mp4",
                        headers={
                            "User-Agent": self.MOBILE_HEADERS["User-Agent"],
                            "Referer": "https://www.douyin.com/",
                        },
                    )
                )

        if not items:
            raise RuntimeError(f"Unable to parse no-watermark media from Douyin item {item_id}")

        return ParseResult(
            platform=self.PLATFORM_NAME,
            title=title,
            author=author,
            media_type=MediaType.VIDEO,
            items=items,
            cover_url=cover_url,
            raw_url=clean_url,
        )
