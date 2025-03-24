from flask import Flask, render_template, request, url_for, redirect
from datetime import date
from configparser import ConfigParser

locale = ConfigParser()
with open('locale.ini', encoding='utf-8') as f:
    locale.read_file(f)

app = Flask(__name__)

print(locale)

@app.route("/")
def home():
    return redirect(url_for("index", lang="en"))

@app.route("/<lang>")
def index(lang):
    return render_template(f'{lang}.html', locale=locale, lang=lang, year=date.today().year)  # TODO: Check for vulnerability

@app.route("/<lang>/download")
def download_page(lang):
    return render_template('tmpl/download.htm', locale=locale, lang=lang)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
