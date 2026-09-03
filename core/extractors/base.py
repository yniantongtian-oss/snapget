import re
import urllib.request
import urllib.parse
from abc import ABC, abstractmethod
from typing import Optional
from ..models import ParseResult


class BaseExtractor(ABC):
    """Abstract base class for all platform extractors."""

    PLATFORM_NAME: str = "generic"
    URL_PATTERNS: list[re.Pattern] = []

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        )
    }

    @classmethod
    def matches(cls, url: str) -> bool:
        """Determines whether the given URL belongs to this extractor."""
        for pattern in cls.URL_PATTERNS:
            if pattern.search(url):
                return True
        return False

    @staticmethod
    def extract_url_from_text(text: str) -> Optional[str]:
        """Extracts the first HTTP/HTTPS link from mixed copy/paste text."""
        url_match = re.search(r"https?://[^\s\u4e00-\u9fa5]+", text)
        if url_match:
            return url_match.group(0).rstrip("，。！？,.!?")
        return None

    def fetch_redirect_url(self, short_url: str, custom_headers: Optional[dict] = None) -> str:
        """Resolves short link redirect (e.g., v.douyin.com, b23.tv, xhslink.com)."""
        headers = {**self.DEFAULT_HEADERS, **(custom_headers or {})}
        req = urllib.request.Request(short_url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.geturl()
        except urllib.error.HTTPError as e:
            if 300 <= e.code < 400 and "Location" in e.headers:
                return e.headers["Location"]
            return short_url
        except Exception:
            return short_url

    def http_get(self, url: str, headers: Optional[dict] = None) -> str:
        """Helper to make an HTTP GET and return decoded string."""
        req_headers = {**self.DEFAULT_HEADERS, **(headers or {})}
        req = urllib.request.Request(url, headers=req_headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content_type = resp.headers.get("Content-Type", "")
            encoding = "utf-8"
            if "charset=" in content_type:
                encoding = content_type.split("charset=")[-1].strip()
            return resp.read().decode(encoding, errors="replace")

    @abstractmethod
    def parse(self, raw_text_or_url: str) -> ParseResult:
        """Parses the input string and returns a structured ParseResult."""
        pass
