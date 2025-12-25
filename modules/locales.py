from os import path, listdir
from configparser import ConfigParser
import threading


translations = {}
locales_name = {}
locales_code = ()

_loaded = False
_load_lock = threading.Lock()


def load_all_locales():
    new_translations = {}
    locales_dir = "locales"

    locales_code_default = ("en", "ru", "es")
    locales_code_extra = []
    new_locales_code = ()

    for filename in listdir(locales_dir):
        if filename.endswith(".ini"):
            cp = ConfigParser()
            lang = path.splitext(filename)[0]
            with open(path.join(locales_dir, filename), encoding="utf-8") as f:
                cp.read_file(f)

            if lang not in locales_code_default:
                locales_code_extra.append(lang)

            new_translations[lang] = {
                section: dict(cp[section]) for section in cp.sections()
            }

    new_locales_code = locales_code_default + tuple(sorted(locales_code_extra))
    new_locales_name = {
        locale_code: new_translations[locale_code]["title"]["language"]
        for locale_code in new_locales_code
    }

    return new_translations, new_locales_name, new_locales_code


def ensure_loaded():
    global translations, locales_name, locales_code, _loaded
    with _load_lock:
        if _loaded:
            return
        translations, locales_name, locales_code = load_all_locales()
        _loaded = True
