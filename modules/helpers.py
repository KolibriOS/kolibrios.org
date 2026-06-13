from datetime import date
from re import compile as re_compile

from flask import redirect, render_template, request, url_for
from htmlmin import minify as minify_html

from modules import locales

_A_OPEN_WS = re_compile(r"(<a\b[^>]*>)\s+")
_A_CLOSE_WS = re_compile(r"\s+(</a>)")


def get_best_lang():
    return request.accept_languages.best_match(locales.locales_code) or "en"


def render_localized_template(lang, template_name):
    if lang not in locales.locales_code:
        return redirect(url_for("index", lang=get_best_lang()))

    html = render_template(template_name, year=date.today().year)
    html = _A_OPEN_WS.sub(r"\1", html)
    html = _A_CLOSE_WS.sub(r"\1", html)

    return minify_html(html, remove_empty_space=False)
