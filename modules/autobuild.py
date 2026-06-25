from datetime import date
import re
import threading
import time

from urllib.request import Request, urlopen


CI_URL = "http://builds.kolibrios.org/ci/"
REFRESH_SEC = 300  # refetch each 5 minutes
DOWNLOAD_LANGS = ("en_US", "ru_RU", "es_ES")
DOWNLOAD_EXTS = ("img", "iso", "raw")

# A build dir under /ci/: 0.7.7.0-9083-g3dd8e618a
BUILD_RE = re.compile(
    r'href="\./?(?P<dir>\d+(?:\.\d+){3}-(?P<build>\d+)-g[0-9a-fA-F]+)/"'
)
# A file row in a build's lang dir: kolibrios-<ver>-<lang>.<ext> + its cells.
# The (?!</tr>) guards confine size/time to this row, so a missing cell fails
# the match instead of stealing the next entry's values.
FILE_RE = re.compile(
    r'(?P<name>kolibrios-[^"]+\.(?P<ext>\w+))"'
    r'(?:(?!</tr>).)*?data-size="(?P<size>\d+)"'
    r'(?:(?!</tr>).)*?datetime="(?P<ts>[^"]+)"',
    re.S | re.I,
)

autobuild_date = date.today()
autobuild_vers = "0.0.0.0-0-g0000000"
autobuild_sizes = {l: {e: "?" for e in DOWNLOAD_EXTS} for l in DOWNLOAD_LANGS}
# Falls back to the /ci/ index until a versioned path is parsed.
autobuild_files = {l: {e: "ci/" for e in DOWNLOAD_EXTS} for l in DOWNLOAD_LANGS}

_started = False
_updater_lock = threading.Lock()


def _fetch(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=10) as r:
        return r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")


def _refresh_autobuild_once():
    global autobuild_date, autobuild_vers
    try:
        ci_html = _fetch(CI_URL)
    except Exception:
        return

    builds = [(int(m["build"]), m["dir"]) for m in BUILD_RE.finditer(ci_html)]
    if not builds:
        return
    _, dirname = max(builds)

    dates = []
    for lang in DOWNLOAD_LANGS:
        try:
            html = _fetch(f"{CI_URL}{dirname}/{lang}/")
        except Exception:
            continue
        for m in FILE_RE.finditer(html):
            ext = m["ext"]
            if ext not in DOWNLOAD_EXTS:
                continue
            autobuild_sizes[lang][ext] = f"{int(m['size']) / 1048576:.1f} MB"
            autobuild_files[lang][ext] = f"ci/{dirname}/{lang}/{m['name']}"
            dates.append(m["ts"][:10])  # ISO "YYYY-MM-DD" prefix, sorts chronologically

    autobuild_vers = dirname
    if dates:
        autobuild_date = date.fromisoformat(max(dates))


def _updater_loop():
    while True:
        _refresh_autobuild_once()
        time.sleep(REFRESH_SEC)


def ensure_started():
    global _started
    with _updater_lock:
        if _started:
            return
        threading.Thread(target=_updater_loop, daemon=True).start()
        _started = True


_refresh_autobuild_once()
