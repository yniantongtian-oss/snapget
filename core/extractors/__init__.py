from typing import Type, List

try:
    from .base import BaseExtractor
    from .douyin import DouyinExtractor
    from .xiaohongshu import XiaohongshuExtractor
    from .bilibili import BilibiliExtractor
    from .generic import GenericExtractor
except (ImportError, ValueError):
    from base import BaseExtractor
    from douyin import DouyinExtractor
    from xiaohongshu import XiaohongshuExtractor
    from bilibili import BilibiliExtractor
    from generic import GenericExtractor

REGISTERED_EXTRACTORS: List[Type[BaseExtractor]] = [
    DouyinExtractor,
    XiaohongshuExtractor,
    BilibiliExtractor,
]


def get_extractor(raw_text_or_url: str) -> BaseExtractor:
    """Auto-detects the matching extractor from URL or raw text."""
    url = BaseExtractor.extract_url_from_text(raw_text_or_url) or raw_text_or_url

    for extractor_cls in REGISTERED_EXTRACTORS:
        if extractor_cls.matches(url):
            return extractor_cls()

    # Fallback to Generic
    return GenericExtractor()


__all__ = [
    "BaseExtractor",
    "DouyinExtractor",
    "XiaohongshuExtractor",
    "BilibiliExtractor",
    "GenericExtractor",
    "get_extractor",
]
