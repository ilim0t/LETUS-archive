#! /usr/bin/env python3
import os
import re
from pathlib import Path
from typing import Dict, List
from urllib.parse import parse_qs, urlparse

import hydra
import requests
from bs4 import BeautifulSoup
from omegaconf import DictConfig

from utils import save_html


def obtain_login_cookie(cfg: DictConfig) -> Dict[str, str]:
    LOGIN_URL = "https://letus.ed.tus.ac.jp/login/index.php"
    # assert False, "For debug"

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


def fetch_course_list(cookies: Dict[str, str]) -> List[Dict[str, str]]:
    res = requests.get("https://letus.ed.tus.ac.jp", cookies=cookies)
    assert res.status_code == 200

    soup = BeautifulSoup(res.text, "html.parser")
    courses: List[Dict[str, str]] = [course.attrs for course in soup.select(
        "#inst21 > div.content > ul > li > div > a")]
    matched = [re.search(r'[\(（]([\dA-Z\+]+)[\)）]', course["title"]) for course in courses]
    is_classes = [match and all(len(num) == 7 for num in match[1].split("+")) for match in matched]

    classes = [course for course, is_class in zip(courses, is_classes) if is_class]
    return classes


def fetch_course_soups(course_list: List[Dict[str, str]], cookies: Dict[str, str]) -> Dict[str, BeautifulSoup]:
    course_soups: Dict[str, BeautifulSoup] = {}
    for course in course_list:
        course_name = course["title"]
        href = course["href"]

        querys = parse_qs(urlparse(href).query)
        assert "id" in querys
        course_id = querys["id"][0]

        # res = requests.get(f"https://letus.ed.tus.ac.jp/course/info.php?id={course_id}")
        # syllabus_soup = BeautifulSoup(res.text, "html.parser")

        res = requests.get(href, cookies=cookies)
        assert res.status_code == 200
        soup = BeautifulSoup(res.text, "html.parser")

        if __debug__:
            page_cache_dir = Path(hydra.utils.get_original_cwd()) / ".cache" / "pages"
            os.makedirs(page_cache_dir, exist_ok=True)
            save_html(res, page_cache_dir / f"{course_name}.html", "w")

        course_soups[course_name] = soup

    return course_soups
