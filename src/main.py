#! /usr/bin/env python3
from pathlib import Path
from typing import Dict

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
    else:
        cookies = login(cfg)

    with open(cache_cookie, "w") as f:
        yaml.dump(cookies, f, default_flow_style=False)

    print(cookies)  # For debug


def login(cfg: DictConfig) -> Dict[str, str]:
    raise Exception("For debug")
    res = requests.get("https://letus.ed.tus.ac.jp/login/index.php")
    assert res.status_code == 200

    soup = BeautifulSoup(res.text, "html.parser")
    token_element = soup.find("input", {"name": "logintoken", "type": "hidden"})

    assert token_element and "value" in token_element.attrs
    logintoken = token_element.attrs["value"]

    res = requests.post("https://letus.ed.tus.ac.jp/login/index.php", data={
        "username": cfg.user,
        "password": cfg["pass"],
        "rememberusername": 1,
        "anchor": "",
        "logintoken": logintoken
    }, allow_redirects=False)
    assert res.status_code == 303

    cookies = res.cookies.get_dict()
    assert all(key in cookies for key in ("MOODLEID1_2020", "MoodleSession2020"))
    return cookies


if __name__ == "__main__":
    main()
