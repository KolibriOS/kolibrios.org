from os import path, listdir
from datetime import date
from configparser import ConfigParser

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
    Response
)


# ---------- APP CONFIG ------------------------------------------------------


cp = ConfigParser()
app = Flask(__name__)


# ---------- LOCALES FUNCTIONS -----------------------------------------------


def load_all_locales():
    locales_list = []
    locales_dict = {}
    locales_dir = "locales"

    for filename in listdir(locales_dir):
        if filename.endswith(".ini"):
            lang = path.splitext(filename)[0]
            with open(path.join(locales_dir, filename), encoding="utf-8") as f:
                cp.read_file(f)
            locales_dict[lang] = {
                section: dict(cp[section]) for section in cp.sections()
            }

    for code, data in locales_dict.items():
        full_name = data.get("title", {}).get("language", code)
        locales_list.append({"code": code, "name": full_name})

    priority = ["en", "ru", "es"]
    locales_list.sort(
        key=lambda loc: (0, priority.index(loc["code"]))
        if loc["code"] in priority
        else (1, loc["code"])
    )

    locales_code = [loc["code"] for loc in locales_list]

    return locales_list, locales_dict, locales_code


locales_list, locales_dict, locales_code = load_all_locales()


# ---------- HELPER FUNCTIONS ------------------------------------------------


def get_best_lang():
    return request.accept_languages.best_match(locales_code) or "en"


def render_localized_template(lang, template_name):
    if lang not in locales_dict:
        return redirect(url_for("index", lang=get_best_lang()))

    return render_template(
        template_name,
        loc_list=locales_list,
        locale=locales_dict[lang],
        lang=lang,
        year=date.today().year,
        current=request.endpoint,
    )


# ---------- MAIN PAGES ------------------------------------------------------


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        app.static_folder, "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


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
                "  <url>",
                f"    <loc>{loc}</loc>",
                f"    <lastmod>{today}</lastmod>",
                "    <changefreq>monthly</changefreq>",
                "    <priority>0.8</priority>",
                "  </url>",
            ]
        )
    xml_lines.append("</urlset>")

    return Response("\n".join(xml_lines), mimetype="application/xml")


# ---------- APP ENTRY -------------------------------------------------------


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
