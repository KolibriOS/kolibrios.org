import os
from datetime import date
from configparser import ConfigParser

from flask import Flask, render_template, url_for, redirect


cp = ConfigParser()
app = Flask(__name__)


def load_all_locales():
    locales = {}
    locales_dir = 'locales'
    for filename in os.listdir(locales_dir):
        if filename.endswith('.ini'):
            lang = os.path.splitext(filename)[0]
            cp = ConfigParser()
            with open(os.path.join(locales_dir, filename), encoding='utf-8') as f:
                cp.read_file(f)
            locales[lang] = {section: dict(cp[section]) for section in cp.sections()}
    return locales

locales = load_all_locales()


@app.route("/")
def home():
    return redirect(url_for("index", lang="en"))

@app.route("/<lang>")
def index(lang):
    return render_template(f'{lang}.html', locale=locales[lang], lang=lang, year=date.today().year)  # TODO: Check for vulnerability

@app.route("/<lang>/download")
def download_page(lang):
    return render_template('tmpl/download.htm', locale=locales[lang], lang=lang, year=date.today().year)


if __name__ == "__main__":
    
    app.run(host="0.0.0.0", debug=True)
