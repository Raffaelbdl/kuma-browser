from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Optional, List

import anki
import anki.collection
import anki.decks
import anki.models
import anki.notes
import aqt
import aqt.main

from bs4 import BeautifulSoup
import requests

from .pitch import get_pitch_html
from .setup import load_template

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

    @staticmethod
    def extract_part_of_speech(jpdb_soup: BeautifulSoup) -> str:
        part_of_speech = ""
        for speech in jpdb_soup.find(class_="part-of-speech").contents:
            part_of_speech += speech.text + "\n"
        return part_of_speech

    @staticmethod
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

    @staticmethod
    def extract_pitch(
        jpdb_soup: BeautifulSoup, expression: str, pitch_dictionary: dict
    ) -> str:
        reading = (
            jpdb_soup.find("meta", attrs={"name": "description"})
            .attrs["content"]
            .split(" ")[4][1:-1]
        )
        pitch_html = get_pitch_html(expression, reading, pitch_dictionary)
        return pitch_html if pitch_html else ""

    @staticmethod
    def extract_frequency(jpdb_soup: BeautifulSoup) -> int:
        frequency = jpdb_soup.find(class_="tag tooltip")
        return frequency.text.split(" ")[-1] if frequency else "100000"

    @staticmethod
    def extract_meanings(jpdb_soup: BeautifulSoup) -> str:
        meanings_list = jpdb_soup.find(class_="subsection-meanings").find_all(
            class_="description"
        )

        meanings = ""
        for m in meanings_list:
            meanings += m.text + "<br>"

        return meanings

    @staticmethod
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


@dataclass
class JPDB_Note:
    expression: str
    part_of_speech: str
    spelling: str
    pitch: str
    frequency: str
    meanings: str
    examples: str

    @classmethod
    def from_jpdb(cls, url: Url):
        jpdb_soup = load_url(url)

        expression = jpdb_soup.find("title").text.split(" ")[0]
        part_of_speech = JPDB.extract_part_of_speech(jpdb_soup)
        spelling = JPDB.extract_spelling(jpdb_soup)
        frequency = JPDB.extract_frequency(jpdb_soup)
        pitch = JPDB.extract_pitch(jpdb_soup, expression, PITCH_DICTIONARY)
        meanings = JPDB.extract_meanings(jpdb_soup)
        examples = JPDB.extract_examples(jpdb_soup)

        return JPDB_Note(
            expression=expression,
            part_of_speech=part_of_speech,
            spelling=spelling,
            pitch=pitch,
            frequency=frequency,
            meanings=meanings,
            examples=examples,
        )


def search_expression_jpdb_url(expression: str) -> Url:
    """Returns the JPDB url page of the corresponding expression."""

    search_url = JPDB.search_url(expression)
    jpdb_soup = load_url(search_url)

    # case with only one result
    if jpdb_soup.find(class_="results details"):
        links = jpdb_soup.find_all("link", href=True)
        for l in links:
            if "canonical" in l.attrs["rel"]:
                return l.attrs["href"].strip("#a")

    entry = (
        jpdb_soup.find(class_="results search")
        .find(class_="view-conjugations-link")
        .attrs["href"]
    )

    return JPDB.base_url + entry.strip("#a")


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


class JPDB_Anki:
    model_name: str = "Kuma Model"

    @staticmethod
    def window() -> aqt.main.AnkiQt:
        return aqt.mw

    @staticmethod
    def collection() -> anki.collection.Collection:
        _collection = JPDB_Anki.window().col
        if _collection is None:
            raise Exception("Collection is not available.")
        return _collection

    @staticmethod
    def decks() -> anki.decks.DeckManager:
        _decks = JPDB_Anki.collection().decks
        if _decks is None:
            raise Exception("Decks are not available.")
        return _decks

    @staticmethod
    def models() -> anki.models.ModelManager:
        _models = JPDB_Anki.collection().models
        if _models is None:
            raise Exception("Models are not available.")
        return _models

    @staticmethod
    def create_note(note: JPDB_Note, deck_name: str) -> anki.notes.Note:
        model = JPDB_Anki.models().by_name(JPDB_Anki.model_name)
        if model is None:
            raise Exception("Model was not found: " + JPDB_Anki.model_name)

        deck = JPDB_Anki.decks().by_name(deck_name)
        if deck is None:
            raise Exception("Deck was not found: " + deck_name)

        ankiNote = anki.notes.Note(JPDB_Anki.collection(), model)
        ankiNote.note_type()["did"] = deck["id"]

        ankiNote["Expression"] = note.expression
        ankiNote["PartOfSpeech"] = note.part_of_speech
        ankiNote["Spelling"] = note.spelling
        ankiNote["Pitch"] = note.pitch
        ankiNote["Frequency"] = note.frequency
        ankiNote["Meanings"] = note.meanings
        ankiNote["Examples"] = note.examples

        return ankiNote

    @staticmethod
    def add_note(note: JPDB_Note, deck_name: str) -> None:
        JPDB_Anki.add_model()

        ankiNote = JPDB_Anki.create_note(note, deck_name)
        JPDB_Anki.collection().addNote(ankiNote)

    @staticmethod
    def find_notes(query: Optional[str] = None) -> Optional[int]:
        if query is None or query == "":
            return []
        return list(map(int, JPDB_Anki.collection().find_notes(query)))

    @staticmethod
    def add_model() -> None:
        if JPDB_Anki.model_name in [
            n.name for n in JPDB_Anki.models().all_names_and_ids()
        ]:
            return  # model already exists

        m = JPDB_Anki.models().new(JPDB_Anki.model_name)
        template = load_template()

        for field in template["inOrderFields"]:
            fm = JPDB_Anki.models().new_field(field)
            JPDB_Anki.models().add_field(m, fm)

        m["css"] = template["css"]

        for i, card in enumerate(template["cardTemplates"]):
            card_name = "Card " + str(i + 1)
            t = JPDB_Anki.models().new_template(card_name)
            t["qfmt"] = card["Front"]
            t["afmt"] = card["Back"]
            JPDB_Anki.models().add_template(m, t)

        JPDB_Anki.models().add(m)

    @staticmethod
    def find_cards(query: Optional[str] = None) -> Optional[int]:
        if query is None or query == "":
            return []
        return list(map(int, JPDB_Anki.collection().find_cards(query)))

    @staticmethod
    def get_cards_of_note(note_id: int) -> list[int]:
        """Returns the cards linked to a note."""
        return JPDB_Anki.find_cards("nid:" + str(note_id))
