import re
import json
from .base import BaseExtractor
from ..models import ParseResult, MediaItem, MediaType


class XiaohongshuExtractor(BaseExtractor):
    PLATFORM_NAME = "xiaohongshu"
    URL_PATTERNS = [
        re.compile(r"xhslink\.com", re.IGNORECASE),
        re.compile(r"xiaohongshu\.com", re.IGNORECASE),
    ]

    WEB_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.xiaohongshu.com/",
    }

    def parse(self, raw_text_or_url: str) -> ParseResult:
        clean_url = self.extract_url_from_text(raw_text_or_url) or raw_text_or_url
        redirected_url = self.fetch_redirect_url(clean_url, custom_headers=self.WEB_HEADERS)

        note_id_match = re.search(r"/(?:explore|discovery/item)/([0-9a-fA-F]+)", redirected_url)
        note_id = note_id_match.group(1) if note_id_match else "xhs_note"

        html = self.http_get(redirected_url, headers=self.WEB_HEADERS)

        # Parse window.__INITIAL_STATE__
        state_match = re.search(r"window\.__INITIAL_STATE__\s*=\s*(\{.+?\})</script>", html)
        if not state_match:
            # Alternate format: undefined or assignment
            state_match = re.search(r"window\.__INITIAL_STATE__\s*=\s*(\{.+?\});", html)

        note_data = None
        if state_match:
            try:
                state_json_str = state_match.group(1)
                # Replace undefined with null
                state_json_str = re.sub(r"\bundefined\b", "null", state_json_str)
                state = json.loads(state_json_str)
                note_dict = state.get("note", {}).get("noteDetailMap", {})
                if note_id in note_dict:
                    note_data = note_dict[note_id].get("note", {})
                elif note_dict:
                    first_key = list(note_dict.keys())[0]
                    note_data = note_dict[first_key].get("note", {})
            except Exception:
                pass

        title = "xhs_note"
        author = "xhs_user"
        cover_url = None
        items = []

        if note_data:
            title = (note_data.get("title") or note_data.get("desc") or f"xhs_{note_id}").strip()
            author = note_data.get("user", {}).get("nickname", "xhs_user")

            # Check for video
            video_info = note_data.get("video")
            if video_info and isinstance(video_info, dict):
                stream_dict = video_info.get("media", {}).get("stream", {})
                h264_list = stream_dict.get("h264", []) or stream_dict.get("av1", [])
                video_url = None
                if h264_list and isinstance(h264_list, list):
                    video_url = h264_list[0].get("masterUrl")

                if video_url:
                    items.append(
                        MediaItem(
                            url=video_url,
                            media_type=MediaType.VIDEO,
                            title=title,
                            filename=f"{author}_{note_id}.mp4",
                            headers=self.WEB_HEADERS,
                        )
                    )
                    return ParseResult(
                        platform=self.PLATFORM_NAME,
                        title=title,
                        author=author,
                        media_type=MediaType.VIDEO,
                        items=items,
                        cover_url=note_data.get("imageList", [{}])[0].get("urlDefault"),
                        raw_url=clean_url,
                    )

            # Check for images
            image_list = note_data.get("imageList", [])
            for idx, img in enumerate(image_list, start=1):
                # Prefer original / default high resolution without watermark parameters
                img_url = (
                    img.get("urlOriginal")
                    or img.get("urlDefault")
                    or img.get("infoList", [{}])[-1].get("url")
                )
                if img_url:
                    # Strip watermark and formatting query params to get uncompressed original image
                    clean_img_url = img_url.split("?")[0]
                    items.append(
                        MediaItem(
                            url=clean_img_url,
                            media_type=MediaType.IMAGE_SET,
                            title=title,
                            filename=f"{author}_{note_id}_img_{idx:02d}.jpg",
                            headers=self.WEB_HEADERS,
                        )
                    )

        # Fallback regex extraction directly from HTML if initial_state failed
        if not items:
            raw_img_urls = re.findall(
                r'https?://[a-zA-Z0-9\-\.]+\.xhscdn\.com/[^\s"\'<>]+', html
            )
            valid_images = []
            for u in raw_img_urls:
                clean_u = u.split("?")[0].split("!")[0]
                if clean_u not in valid_images and ("sns-webpic" in clean_u or "spectrum" in clean_u):
                    valid_images.append(clean_u)

            for idx, img_u in enumerate(valid_images[:30], start=1):
                items.append(
                    MediaItem(
                        url=img_u,
                        media_type=MediaType.IMAGE_SET,
                        title=title,
                        filename=f"{author}_{note_id}_img_{idx:02d}.jpg",
                        headers=self.WEB_HEADERS,
                    )
                )

        if not items:
            raise RuntimeError(f"Failed to extract media items from Xiaohongshu note: {redirected_url}")

        return ParseResult(
            platform=self.PLATFORM_NAME,
            title=title,
            author=author,
            media_type=MediaType.IMAGE_SET if items[0].media_type == MediaType.IMAGE_SET else MediaType.VIDEO,
            items=items,
            cover_url=cover_url or (items[0].url if items else None),
            raw_url=clean_url,
        )
