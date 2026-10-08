# SnapGet — Media Retrieval and Source Inspection

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white" alt="Python version" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT license" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue" alt="Platform support" />
</p>

A lightweight local Web and command-line tool for inspecting shared media URLs and downloading media that you are entitled to access, preserve, or reuse. It supports platform-specific extractors and an optional general-purpose downloader integration.

The tool can assist an authorized video-production asset workflow, but downloading content does not grant copyright, redistribution rights, or permission to bypass platform controls.

## Features

- Extractors for shared links to Douyin, Xiaohongshu, and Bilibili; a general `yt-dlp` fallback supports other compatible sources where permitted.
- Media metadata, available streams, image-gallery assets, and source URLs when the relevant platform exposes them.
- Local Web interface with previews, resource cards, and download actions.
- Rich-based terminal output, transfer status, and progress reporting.
- Windows-compatible filename sanitation and modular extractor classes.
- Browser extension and optional userscript integrations where the platform and your permissions allow them.

Availability depends on live site behavior and authorization; a working offline test does not guarantee that an external platform remains accessible.

## Installation

Requires Python 3.9 or newer.

```bash
git clone https://github.com/yniantongtian-oss/snapget.git
cd snapget
python -m pip install .
```

## Local Web interface

```bash
snapget --web
```

The interface is normally available at `http://127.0.0.1:8080`. Paste an authorized shared URL, inspect the available assets, and select the files you want to retain.

## Command line

```bash
# Download an authorized public media item
snapget "https://www.bilibili.com/video/BVxxxxxx" -o my_videos/

# Display a source inspection result without downloading files
snapget "https://example.com/authorized-media" --info-only
```

Actual supported sources and availability should be verified against the installed extractor implementations.

## Optional browser integration

A browser extension is provided under `extension/`, and a userscript may be present at the repository root. Load only code that you have reviewed and only on websites where you are authorized to retrieve the content.

For Chromium browsers, open the extension management page, enable developer mode, and load the unpacked `extension/` directory. Disable browser integration when it is not needed.

## Architecture

```text
core/
  extractors/
    base.py           Shared interface and redirect handling
    douyin.py         Douyin extractor
    xiaohongshu.py    Xiaohongshu extractor
    bilibili.py       Bilibili extractor
    generic.py        Optional general extractor
  downloader.py       Chunked transfer implementation
  models.py           Data contracts
web/server.py         Local web service
tests/test_core.py    Core regression tests
cli.py                Terminal interface
main.py               Startup integration
pyproject.toml        Package build configuration
requirements.txt      Dependency list
LICENSE               Repository license
```

## Validation

```bash
python -m unittest discover -s tests -v
```

The offline suite covers extractor routing, filename handling, and loopback HTTP behavior. Linux and Windows CI also build distribution artifacts, install the wheel outside the source directory, and check core module imports. The HTTP interface rejects malformed or oversized JSON requests.

These checks do not establish ongoing compatibility with all external websites or prove rights to access a particular asset.

## Responsible use

- Download, copy, and publish only media for which you have the necessary permissions.
- Respect content creator rights, licenses, usage restrictions, and applicable law.
- Do not use the project to evade access controls, authentication barriers, paywalls, or DRM.
- Do not interpret a file lacking a watermark as permission to redistribute it.
- Review source provenance and attribution before using assets in a public or commercial video.

## License

MIT. See [LICENSE](LICENSE). Third-party media and services remain subject to their own terms.
