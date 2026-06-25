import os
import re
import datetime

import click
from sass import compile as compile_sass
from flask import Flask, redirect, request, url_for, g, Response
from flask.cli import run_command

from modules import autobuild, locales, helpers


# ---------- APP CONFIG ------------------------------------------------------


app = Flask(__name__)

locales.ensure_loaded()

# CSS Compilation and minification
if app.debug:
    css = compile_sass(filename="static/style.scss", output_style="compressed")
    with open("static/style.css", "w", encoding="utf-8") as f:
        f.write(css)

# JS minification
with open("static/script.js", encoding="utf-8") as f:
    js = f.read()
js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
js = re.sub(r"//.*", "", js)
js = re.sub(r"\s+", " ", js).strip()
with open("static/script.min.js", "w", encoding="utf-8") as f:
    f.write(js)


@app.before_request
def _ensure_updater_started():
    autobuild.ensure_started()


@app.before_request
def before_request():
    if args := request.view_args:
        g.locale = args.get("lang", "en")
        g.translations = locales.translations.get(g.locale, helpers.get_best_lang())
        g.locales_name = locales.locales_name


@app.context_processor
def _inject_autobuild_vers():
    return {
        "autobuild_vers": autobuild.autobuild_vers,
        "autobuild_sizes": autobuild.autobuild_sizes,
        "autobuild_files": autobuild.autobuild_files,
    }


@app.context_processor
def _inject_autobuild_date():
    return {
        "autobuild_date": autobuild.autobuild_date.strftime(
            g.translations.get("downloads", {})
            .get("date-format", "{DD}.{MM}.{YYYY}")
            .replace("{YYYY}", "%Y")
            .replace("{MM}", "%m")
            .replace("{DD}", "%d")
        )
    }


@app.context_processor
def inject_translations():
    def translate(text, **kwargs):
        section, key = text.split(":", 1)

        template = (
            g.translations.get(section, {})
            .get(key, f"${section}: {key}$")
        )

        try:
            return template.format(**kwargs)
        except Exception:
            return template

    return {"_": translate}


# ---------- ROUTES -------------------------------------------------------


@app.route("/")
def home():
    return redirect(url_for("index", lang=helpers.get_best_lang()))


@app.route("/download", strict_slashes=False)
def download_home():
    return redirect(url_for("download", lang=helpers.get_best_lang()))


@app.route("/<lang>", strict_slashes=False)
def index(lang):
    return helpers.render_localized_template(lang, "index.html")


@app.route("/<lang>/download", strict_slashes=False)
def download(lang):
    return helpers.render_localized_template(lang, "download.html")


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
    today = datetime.date.today().isoformat()

    urls = []
    for lang in locales.locales_code:
        urls.append(f"{base_url}/{lang}")
        urls.append(f"{base_url}/{lang}/download")

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc in urls:
        xml_lines.extend(
            [
                f"    <url>",
                f"        <loc>{loc}</loc>",
                f"        <lastmod>{today}</lastmod>",
                f"        <changefreq>monthly</changefreq>",
                f"        <priority>0.8</priority>",
                f"    </url>",
            ]
        )
    xml_lines.append("</urlset>")

    return Response("\n".join(xml_lines), mimetype="application/xml")


# ---------- CLI -------------------------------------------------------------


@app.cli.command("preview")
@click.option("--nocss", is_flag=True, help="Render pages without CSS")
@click.option("--nojs", is_flag=True, help="Render pages without JS")
@click.pass_context
def preview(ctx, nocss, nojs):
    """Run the dev server without CSS/JS to preview the KolibriOS WebView look."""
    app.config["NOCSS"] = nocss
    app.config["NOJS"] = nojs
    # Delegate to the built-in `flask run` instead of app.run() (which the
    # Flask CLI ignores). FLASK_DEBUG enables the reloader/debugger so the
    # command behaves like `flask run --debug`.
    os.environ["FLASK_DEBUG"] = "1"
    ctx.invoke(run_command, host="0.0.0.0")


# ---------- APP ENTRY -------------------------------------------------------


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
