from datetime import date

from flask import redirect, render_template, request, url_for
from htmlmin import minify as minify_html

from modules import locales


def get_best_lang():
    return request.accept_languages.best_match(locales.locales_code) or "en"


def render_localized_template(lang, template_name):
    if lang not in locales.locales_code:
        return redirect(url_for("index", lang=get_best_lang()))

    return minify_html(
        render_template(
            template_name,
            year=date.today().year,
        ),
        remove_empty_space=True,
    )
