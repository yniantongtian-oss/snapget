from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class MediaType(str, Enum):
    VIDEO = "video"
    IMAGE_SET = "image_set"
    AUDIO = "audio"


@dataclass
class MediaItem:
    """Represents a single downloadable resource (video file, single image, or audio)"""
    url: str
    media_type: MediaType
    title: str
    filename: str
    headers: Dict[str, str] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParseResult:
    """Represents the parsed outcome of a social media link"""
    platform: str
    title: str
    author: str
    media_type: MediaType
    items: List[MediaItem] = field(default_factory=list)
    cover_url: Optional[str] = None
    raw_url: str = ""
    description: str = ""
