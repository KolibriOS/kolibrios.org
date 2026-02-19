import re
import threading
import time


STATUS_URL = "http://builds.kolibrios.org/status.html"
STATUS_SEC = 300  # refetch each 5 minutes

autobuild_date = {"YYYY": "YYYY", "MM": "MM", "DD": "DD"}
autobuild_vers = "0.0.0.0+0000-0000000"

_started = False
_updater_lock = threading.Lock()


def _refresh_build_date_once():
    global autobuild_date, autobuild_vers
    try:
        from urllib.request import Request, urlopen
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

        ver_re = re.compile(
            r"\b(\d+\.\d+\.\d+\.\d+\+\d{3,8}-[0-9a-fA-F]{7,40})\b"
        )
        last_ver = None

        rows = re.findall(r"(<tr\b[^>]*>.*?</tr>)", html, flags=re.I | re.S)
        for row in rows:
            cls = re.search(r'class\s*=\s*"([^"]*)"', row, flags=re.I)
            classes = cls.group(1).lower() if cls else ""
            if "commit" in classes:
                mver = ver_re.search(row)
                if mver:
                    last_ver = mver.group(1)
                continue
            if "success" not in classes:
                continue
            text = re.sub(r"<[^>]+>", " ", row)
            mts = re.search(
                r"\b(\d{4})\.(\d{2})\.(\d{2})\s+\d{2}:\d{2}:\d{2}\b", text
            )
            if mts:
                autobuild_date["YYYY"], autobuild_date["MM"], autobuild_date["DD"] = mts.groups()
            else:
                mds = re.search(r"\b(\d{2})\.(\d{2})\.(\d{4})\b", text)
                if not mds:
                    return
                autobuild_date["YYYY"], autobuild_date["MM"], autobuild_date["DD"] = (
                    mds.group(3),
                    mds.group(2),
                    mds.group(1),
                )
            if last_ver:
                autobuild_vers = last_ver
            return

        # Fallback for plain-text log format (no HTML table)
        # Example: 2025.09.20 20:45:10 user 💚 Build processing completed successfully. Thank you.
        log_line_re = re.compile(
            r"^(\d{4})\.(\d{2})\.(\d{2})\s+\d{2}:\d{2}:\d{2}\s+(.*)$"
        )
        for raw in html.splitlines():
            mline = log_line_re.match(raw.strip())
            if not mline:
                continue
            yyyy, mm, dd, rest = mline.groups()
            mver = ver_re.search(rest)
            if mver:
                last_ver = mver.group(1)
            if "Build processing completed successfully" in rest:
                autobuild_date["YYYY"], autobuild_date["MM"], autobuild_date["DD"] = yyyy, mm, dd
                if last_ver:
                    autobuild_vers = last_ver
                return

    except Exception:
        pass


def _updater_loop():
    while True:
        _refresh_build_date_once()
        time.sleep(STATUS_SEC)


def ensure_started():
    global _started
    with _updater_lock:
        if _started:
            return
        threading.Thread(target=_updater_loop, daemon=True).start()
        _started = True


_refresh_build_date_once()
