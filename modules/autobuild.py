from datetime import date
import re
import threading
import time

from urllib.request import Request, urlopen


STATUS_URL = "http://builds.kolibrios.org/status.html"
STATUS_SEC = 300  # refetch each 5 minutes
DOWNLOAD_LANGS = ("en_US", "ru_RU", "es_ES")
DOWNLOAD_EXTS = ("img", "iso", "distr", "raw")

VER_RE = re.compile(r"\b(\d+\.\d+\.\d+\.\d+\+\d{3,8}-[0-9a-fA-F]{7,40})\b")
DATE_RE = re.compile(r"\b(\d{4})\.(\d{2})\.(\d{2})\s+\d{2}:\d{2}:\d{2}\b")
ROW_RE = re.compile(r"(<tr\b[^>]*>.*?</tr>)", flags=re.I | re.S)

autobuild_date = date.today()
autobuild_vers = "0.0.0.0+0000-0000000"
autobuild_sizes = {
    lang: {ext: "?" for ext in DOWNLOAD_EXTS}
    for lang in DOWNLOAD_LANGS
}

_started = False
_updater_lock = threading.Lock()


def _refresh_build_sizes():
    for lang in DOWNLOAD_LANGS:
        for ext in DOWNLOAD_EXTS:
            url = f"http://builds.kolibrios.org/{lang}/latest-{ext}.7z"
            req = Request(
                url,
                method="HEAD",
                headers={"User-Agent": "Mozilla/5.0"},
            )
            with urlopen(req, timeout=10) as r:
                content_length = r.headers.get("Content-Length")
                if not content_length:
                    continue
                autobuild_sizes[lang][ext] = f"{int(content_length) / 1048576:.1f} MB"


def _refresh_autobuild_once():
    global autobuild_date, autobuild_vers
    try:
        req = Request(
            STATUS_URL,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        with urlopen(req, timeout=10) as r:
            html = r.read().decode(
                r.headers.get_content_charset() or "utf-8", "replace"
            )

        last_ver = None

        for row in ROW_RE.findall(html):
            cls = re.search(r'class\s*=\s*"([^"]*)"', row, flags=re.I)
            classes = cls.group(1).lower() if cls else ""
            if "commit" in classes:
                mver = VER_RE.search(row)
                if mver:
                    last_ver = mver.group(1)
                continue
            if "success" not in classes:
                continue
            text = re.sub(r"<[^>]+>", " ", row)
            mts = DATE_RE.search(text)
            if mts:
                autobuild_date = date(*map(int, mts.groups()))
            if last_ver:
                autobuild_vers = last_ver
                _refresh_build_sizes()
            return

    except Exception:
        pass


def _updater_loop():
    while True:
        _refresh_autobuild_once()
        time.sleep(STATUS_SEC)


def ensure_started():
    global _started
    with _updater_lock:
        if _started:
            return
        threading.Thread(target=_updater_loop, daemon=True).start()
        _started = True


_refresh_autobuild_once()
