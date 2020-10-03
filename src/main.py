#! /usr/bin/env python3
from pathlib import Path
from typing import Dict, cast

import hydra
import requests
import yaml
from bs4 import BeautifulSoup
from omegaconf import DictConfig

from utils import save_html


@hydra.main(config_name="../config")
def main(cfg: DictConfig) -> None:
    original_cwd = Path(hydra.utils.get_original_cwd())
    cache_dir = original_cwd / ".cache"
    cache_dir.mkdir(exist_ok=True)
    cache_cookie = cache_dir / "cookies.yaml"

    # Get cookies
    if cache_cookie.exists():
        with open(cache_cookie) as f:
            cookies = yaml.safe_load(f)
            if isinstance(cookies, dict) and all(isinstance(key, str) for key in cookies.keys()) or all(isinstance(value, str) for value in cookies.values()):
                raise Exception("キャッシュが不適切です。「.cache」ディレクトリを削除してからもう一度お試しください。")
            cookies = cast(Dict[str, str], cookies)
    else:
        cookies = login(cfg)

    # Cache cookies
    with open(cache_cookie, "w") as f:
        yaml.dump(cookies, f, default_flow_style=False)

    print(cookies)  # For debug


def login(cfg: DictConfig) -> Dict[str, str]:
    LOGIN_URL = "https://letus.ed.tus.ac.jp/login/index.php"
    assert False, "For debug"

    res = requests.get(LOGIN_URL)
    assert res.status_code == 200

    soup = BeautifulSoup(res.text, "html.parser")
    token_element = soup.find("input", {"name": "logintoken", "type": "hidden"})

    assert token_element and "value" in token_element.attrs
    logintoken = token_element.attrs["value"]

    content = {
        "username": cfg.user,
        "password": cfg["pass"],
        "rememberusername": 1,
        "anchor": "",
        "logintoken": logintoken
    }
    res = requests.post(LOGIN_URL, data=content, allow_redirects=False)
    assert res.status_code == 303

    cookies = res.cookies.get_dict()
    assert all(key in cookies for key in ("MOODLEID1_2020", "MoodleSession2020"))
    return cookies


if __name__ == "__main__":
    main()
