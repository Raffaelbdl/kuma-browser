"""JPDB related functions."""

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import List

from bs4 import BeautifulSoup
import requests

from .pitch import get_pitch_html

Url = str

PITCH_DICTIONARY = json.load(
    open(Path(__file__).parent.joinpath("pitch_dictionary.json"), "r")
)


def load_url(url: Url) -> BeautifulSoup:
    return BeautifulSoup(requests.get(url).content, "html.parser")


class JPDB:
    base_url = "https://jpdb.io"

    @staticmethod
    def search_url(query: str) -> Url:
        return "https://jpdb.io/search?q=" + query


def extract_part_of_speech(jpdb_soup: BeautifulSoup) -> str:
    part_of_speech = ""
    for speech in jpdb_soup.find(class_="part-of-speech").contents:
        part_of_speech += speech.text + "\n"
    return part_of_speech


def extract_spelling(jpdb_soup: BeautifulSoup) -> str:
    contents = jpdb_soup.find(class_="primary-spelling").find("ruby").contents

    spelling = ""
    for s in contents:
        s = str(s)
        if "<rt>" in s:
            in_s = s.strip("<rt>").strip("</rt>")
            if len(in_s) > 0:
                s = "[" + in_s + "]"
            else:
                s = ""
        spelling += s

    return spelling


def extract_pitch(jpdb_soup: BeautifulSoup, expression: str) -> str:
    reading = (
        jpdb_soup.find("meta", attrs={"name": "description"})
        .attrs["content"]
        .split(" ")[4][1:-1]
    )
    pitch_html = get_pitch_html(expression, reading, PITCH_DICTIONARY)
    return pitch_html if pitch_html else ""


def extract_frequency(jpdb_soup: BeautifulSoup) -> int:
    frequency = jpdb_soup.find(class_="tag tooltip")
    return frequency.text.split(" ")[-1] if frequency else "100000"


def extract_meanings(jpdb_soup: BeautifulSoup) -> str:
    meanings_list = jpdb_soup.find(class_="subsection-meanings").find_all(
        class_="description"
    )

    meanings = ""
    for m in meanings_list:
        meanings += m.text + "<br>"

    return meanings


def extract_examples(jpdb_soup: BeautifulSoup) -> str:
    examples_section = jpdb_soup.find(class_="subsection-examples")
    if not examples_section:
        return ""

    examples_list = examples_section.find_all(class_="used-in")
    jp = [e.find(class_="jp").text for e in examples_list]
    en = [e.find(class_="en").text for e in examples_list]
    examples_list = list(zip(jp, en))

    examples = ""
    for i, (ex_jp, ex_en) in enumerate(examples_list):
        examples += str(i) + ". " + ex_jp + "<br>" + ex_en + "<br>"

    return examples


def extract_id(url: Url) -> str:
    return url.split("/")[-2]


@dataclass
class JPDB_Note:
    expression: str
    part_of_speech: str
    spelling: str
    pitch: str
    frequency: str
    meanings: str
    examples: str
    note_id: str

    @classmethod
    def from_jpdb(cls, url: Url):
        jpdb_soup = load_url(url)

        expression = jpdb_soup.find("title").text.split(" ")[0]
        part_of_speech = extract_part_of_speech(jpdb_soup)
        spelling = extract_spelling(jpdb_soup)
        frequency = extract_frequency(jpdb_soup)
        pitch = extract_pitch(jpdb_soup, expression)
        meanings = extract_meanings(jpdb_soup)
        examples = extract_examples(jpdb_soup)
        note_id = extract_id(url)

        return JPDB_Note(
            expression=expression,
            part_of_speech=part_of_speech,
            spelling=spelling,
            pitch=pitch,
            frequency=frequency,
            meanings=meanings,
            examples=examples,
            note_id=note_id,
        )


def search_all_expressions_jpdb_url(query: str) -> List[Url]:
    search_url = JPDB.search_url(query)
    jpdb_soup = load_url(search_url)

    # if single entry
    if jpdb_soup.find(class_="results details"):
        links = jpdb_soup.find_all("link", href=True)
        for l in links:
            if "canonical" in l.attrs["rel"]:
                entry = l.attrs["href"].strip("#a").replace(JPDB.base_url, "")
                return [entry]

    entries = []
    for entry in jpdb_soup.find_all("div", {"id": re.compile("result-")}):
        entries.append(
            entry.find(class_="view-conjugations-link").attrs["href"].strip("#a")
        )

    return entries


def get_all_entries_from_one_page(jpdb_soup: BeautifulSoup) -> List[str]:
    entries = jpdb_soup.find_all(class_="vocabulary-spelling")
    return [s.find("a", href=True)["href"] for s in entries]
