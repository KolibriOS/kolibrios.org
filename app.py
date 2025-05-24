from os import path, listdir
from datetime import date
from configparser import ConfigParser

from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

cp = ConfigParser()
app = Flask(__name__)


def load_all_locales():
    locales = {}
    locales_dir = "locales"

    for filename in listdir(locales_dir):
        if filename.endswith(".ini"):
            lang = path.splitext(filename)[0]
            cp = ConfigParser()
            with open(path.join(locales_dir, filename), encoding="utf-8") as f:
                cp.read_file(f)
            locales[lang] = {section: dict(cp[section]) for section in cp.sections()}
    
    return locales


locales = load_all_locales()


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        app.static_folder,
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon"
    )


@app.route("/")
def home():
    return redirect(url_for("index", lang="en"))


@app.route("/<lang>")
def index(lang):

    if lang not in locales:
        abort(404)

    return render_template(
        f"{lang}.html",
        locale=locales[lang],
        lang=lang,
        year=date.today().year,
        current=request.endpoint,
    )


@app.route("/<lang>/download")
def download_page(lang):

    if lang not in locales:
        abort(404)

    return render_template(
        "tmpl/download.htm",
        locale=locales[lang],
        lang=lang,
        year=date.today().year,
        current=request.endpoint,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
