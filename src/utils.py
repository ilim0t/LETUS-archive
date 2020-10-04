#! /usr/bin/env python3
from pathlib import Path
from typing import Dict, Union, cast

import requests
import yaml


def load_cache_cookie(cache_cookie: Union[str, Path]) -> Dict[str, str]:
    with open(cache_cookie) as f:
        cookies = yaml.safe_load(f)
        if isinstance(cookies, dict) and \
                all(isinstance(key, str) for key in cookies.keys()) and \
                all(isinstance(value, str) for value in cookies.values()):
            pass
        else:
            raise Exception("キャッシュが不適切です。「.cache」ディレクトリを削除してからもう一度お試しください。")
        cookies = cast(Dict[str, str], cookies)
    return cookies


def save_html(response: requests.models.Response, file: Union[str, Path], mode: str = "x") -> None:
    with open(file, mode) as f:
        f.write(response.text)
