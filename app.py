import threading
import time

from os import path, listdir
from datetime import date
from configparser import ConfigParser

import sass

from flask import Flask, redirect, render_template, request, url_for, g, Response


# ---------- ENV VARS --------------------------------------------------------


STATUS_URL = "https://builds.kolibrios.org/status.html"
STATUS_FETCH_DELAY_SEC = 300  # 5 minutes


# ---------- APP CONFIG ------------------------------------------------------


app = Flask(__name__)

if app.debug:
    css = sass.compile(filename="static/style.scss")
    with open("static/style.css", "w", encoding="utf-8") as f:
        f.write(css)


# ---------- LATEST COMMIT DATE (MINIMAL ADD-ON) -----------------------------


autobuild_date = "DD.MM.YYYY"
autobuild_vers = "0.0.0.0+0000-0000000"


def _refresh_build_date_once():
    global autobuild_date, autobuild_vers
    try:
        from urllib.request import Request, urlopen
        import re

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

        rows = re.findall(r"(<tr\b[^>]*>.*?</tr>)", html, flags=re.I | re.S)
        if not rows:
            return

        last_commit_ver = None

        for row in rows:
            cls = re.search(r'class\s*=\s*"([^"]*)"', row, flags=re.I)
            classes = cls.group(1).lower() if cls else ""

            text = re.sub(r"<[^>]+>", " ", row)

            if "commit" in classes:
                mver = re.search(
                    r"\b(\d+\.\d+\.\d+\.\d+\+\d{3,8}-[0-9a-fA-F]{7,40})\b", row
                )
                if mver:
                    last_commit_ver = mver.group(1)

            elif "success" in classes:
                mts = re.search(
                    r"\b(\d{4})\.(\d{2})\.(\d{2})\s+\d{2}:\d{2}:\d{2}\b", text
                )
                if not mts:
                    mds = re.search(r"\b(\d{2})\.(\d{2})\.(\d{4})\b", text)
                    if mds:
                        autobuild_date = f"{mds.group(1)}.{mds.group(2)}.{mds.group(3)}"
                    else:
                        return
                else:
                    y, mo, d = mts.groups()
                    autobuild_date = f"{d}.{mo}.{y}"

                if last_commit_ver:
                    autobuild_vers = last_commit_ver
                return

    except Exception:
        pass


def _updater_loop():
    while True:
        _refresh_build_date_once()
        time.sleep(STATUS_FETCH_DELAY_SEC)


_started = False
_refresh_build_date_once()

# Flask 3.x fix: start updater lazily on first request (since before_first_request is removed)
_updater_lock = threading.Lock()


@app.before_request
def _ensure_updater_started():
    global _started
    if not _started:
        with _updater_lock:
            if not _started:
                _started = True
                threading.Thread(target=_updater_loop, daemon=True).start()


@app.context_processor
def _inject_autobuild_vers():
    return {"autobuild_vers": autobuild_vers}


@app.context_processor
def _inject_autobuild_date():
    return {"autobuild_date": autobuild_date}


# ---------- LOCALES FUNCTIONS -----------------------------------------------


def load_all_locales():
    translations = {}
    locales_dir = "locales"

    locales_code_default = ("en", "ru", "es")
    locales_code_extra = []
    locales_code = ()

    for filename in listdir(locales_dir):
        if filename.endswith(".ini"):
            cp = ConfigParser()
            lang = path.splitext(filename)[0]
            with open(path.join(locales_dir, filename), encoding="utf-8") as f:
                cp.read_file(f)

            if lang not in locales_code_default:
                locales_code_extra.append(lang)

            translations[lang] = {
                section: dict(cp[section]) for section in cp.sections()
            }

    locales_code = locales_code_default + tuple(sorted(locales_code_extra))
    locales_name = {l: translations[l]["title"]["language"] for l in locales_code}

    return translations, locales_name, locales_code


translations, locales_name, locales_code = load_all_locales()


# ---------- HELPER FUNCTIONS ------------------------------------------------


def get_best_lang():
    return request.accept_languages.best_match(locales_code) or "en"


def render_localized_template(lang, template_name):
    if lang not in locales_code:
        return redirect(url_for("index", lang=get_best_lang()))

    return render_template(
        template_name,
        year=date.today().year,
    )


@app.before_request
def before_request():
    if args := request.view_args:
        g.locale = args.get("lang", "en")
        g.translations = translations.get(g.locale, get_best_lang())
        g.locales_name = locales_name


@app.context_processor
def inject_translations():
    def translate(text, **kwargs):
        section, key = text.split(":", 1)

        template = g.translations.get(section, {}).get(key, f"${section}: {key}$")

        try:
            return template.format(**kwargs)
        except Exception:
            return template

    return {"_": translate}


# ---------- MAIN PAGES ------------------------------------------------------


@app.route("/")
def home():
    return redirect(url_for("index", lang=get_best_lang()))


@app.route("/<lang>")
def index(lang):
    return render_localized_template(lang, "index.html")


@app.route("/<lang>/download")
def download(lang):
    return render_localized_template(lang, "download.html")


# ---------- ROBOTS.TXT + SITEMAP.XML ----------------------------------------


@app.route("/robots.txt")
def robots_txt():
    base_url = request.url_root.rstrip("/")
    content = [
        "User-agent: *",
        "Disallow:",
        f"Sitemap: {base_url}/sitemap.xml",
    ]
    return Response("\n".join(content), mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap_xml():
    base_url = request.url_root.rstrip("/")
    today = date.today().isoformat()

    urls = []
    for lang in locales_code:
        urls.append(f"{base_url}/{lang}")
        urls.append(f"{base_url}/{lang}/download")

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc in urls:
        xml_lines.extend(
            [
                f"  <url>",
                f"    <loc>{loc}</loc>",
                f"    <lastmod>{today}</lastmod>",
                f"    <changefreq>monthly</changefreq>",
                f"    <priority>0.8</priority>",
                f"  </url>",
            ]
        )
    xml_lines.append("</urlset>")

    return Response("\n".join(xml_lines), mimetype="application/xml")


# ---------- APP ENTRY -------------------------------------------------------


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
