import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "craft"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "base_url": "https://craftintertech.co.th/api/v1",
    "access_token": "",
    "refresh_token": "",
}


def _ensure_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    _ensure_dir()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            stored = json.load(f)
        config = {**DEFAULT_CONFIG, **stored}
        return config
    return dict(DEFAULT_CONFIG)


def save_config(config):
    _ensure_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    os.chmod(CONFIG_FILE, 0o600)


def get_token():
    config = load_config()
    return config.get("access_token", "")


def save_tokens(access_token, refresh_token=None):
    config = load_config()
    config["access_token"] = access_token
    if refresh_token:
        config["refresh_token"] = refresh_token
    save_config(config)


def clear_tokens():
    config = load_config()
    config["access_token"] = ""
    config["refresh_token"] = ""
    save_config(config)


def get_base_url():
    return load_config().get("base_url", DEFAULT_CONFIG["base_url"])
