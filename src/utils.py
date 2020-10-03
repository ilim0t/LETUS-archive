#! /usr/bin/env python3
from pathlib import Path
from typing import Union

import requests


def save_html(response: requests.models.Response, file: Union[str, Path]) -> None:
    with open(file, "x") as f:
        f.write(response.text)
