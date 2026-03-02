from os import path, listdir
from configparser import ConfigParser
import threading


_configs = {}
_loaded = False
_load_lock = threading.Lock()


def load_all_configs():
    new_configs = {}

    configs_dir = "configs"
    if not path.isdir(configs_dir):
        return new_configs

    for filename in sorted(listdir(configs_dir)):
        if not filename.endswith(".ini"):
            continue

        file_path = path.join(configs_dir, filename)
        cp = ConfigParser()
        with open(file_path, encoding="utf-8") as f:
            cp.read_file(f)

        for section in cp.sections():
            section_data = new_configs.setdefault(section, {})
            section_data.update(dict(cp[section]))

    return new_configs


def ensure_loaded():
    global _configs, _loaded
    with _load_lock:
        if _loaded:
            return
        _configs = load_all_configs()
        _loaded = True


def get_section(name):
    ensure_loaded()
    return dict(_configs.get(name, {}))


def get_all_sections():
    ensure_loaded()
    return {section: dict(values) for section, values in _configs.items()}
