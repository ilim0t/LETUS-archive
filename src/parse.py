#! /usr/bin/env python3
from typing import Dict, Tuple, Union, cast

from bs4 import BeautifulSoup, Tag


def soup_to_links(course_soups: Dict[str, BeautifulSoup]) -> Dict[Tuple[str, str, str], str]:
    links: Dict[Tuple[str, str, str], str] = {}

    for course_name, soup in course_soups.items():
        sections: Dict[str, Tag] = {
            section.attrs["aria-label"]: section for section in soup.find(class_="topics").children
        }
        section_link_tags: Dict[str, Tag] = {
            section_name: tag
            for section_name, section in sections.items()
            for tag in section.findChildren("a")
        }

        for section_name, tag in section_link_tags.items():
            # リンクに対応する文字列(名前, タイトル)の取得
            instancename = tag.find(class_="instancename")
            if instancename:  # 左にアイコンが表示されるようなLETUS特有のclass=activityを持ったelementの子であるリンク
                link_name: str = instancename.next
            else:  # 本文中のリンク
                previous = cast(Union[str, Tag], tag.previous)
                while not isinstance(previous, str):
                    previous = cast(Union[str, Tag], previous.previous)
                link_name = f'{previous}"{tag.text}"'

                second_next: Tag = tag.next_element.next_element
                link_name += second_next if isinstance(second_next, str) else second_next.text

            links[(course_name, section_name, link_name.strip())] = tag.attrs["href"]

    return links
