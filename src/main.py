#! /usr/bin/env python3

import os
from pathlib import Path
from typing import Dict

import hydra
import yaml
from bs4 import BeautifulSoup
from omegaconf import DictConfig

from fetch import fetch_course_list, fetch_course_soups, obtain_login_cookie
from parse import soup_to_links
from utils import load_cache_cookie


@hydra.main(config_name="../config")
def main(cfg: DictConfig) -> None:
    cache_cookie = Path(hydra.utils.get_original_cwd()) / ".cache" / "cookies.yaml"

    # Get cookies
    assert cache_cookie.exists()
    if cache_cookie.exists():
        cookies = load_cache_cookie(cache_cookie)
    else:
        cookies = obtain_login_cookie(cfg)

    # Cache cookies
    with open(cache_cookie, "w") as f:
        os.makedirs(cache_cookie.parent, exist_ok=True)
        yaml.dump(cookies, f, default_flow_style=False)

    if __debug__:
        course_soups: Dict[str, BeautifulSoup] = {}
        page_cache_dir = Path(hydra.utils.get_original_cwd()) / ".cache" / "pages"
        for page in page_cache_dir.glob("*.html"):
            with open(page) as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                course_soups[page.name] = soup
    else:
        course_list = fetch_course_list(cookies)
        course_soups = fetch_course_soups(course_list, cookies)

    links = soup_to_links(course_soups)


if __name__ == "__main__":
    main()
