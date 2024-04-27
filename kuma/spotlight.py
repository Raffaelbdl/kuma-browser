from copy import copy
from dataclasses import dataclass
import requests

from kuma.jpdb import JPDB_Note, get_pitch_html, PITCH_DICTIONARY


@dataclass
class Note:
    spelling: str
    reading: str
    frequency_rank: int
    meanings: str
    part_of_speech: str


class JpdbAPI:
    def __init__(self, api_key: str):
        self.token = api_key

    def vocabulary_list(self, deck_id: int):
        url = "https://jpdb.io/api/v1/deck/list-vocabulary"

        payload = {"id": deck_id, "fetch_occurences": False}
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        response = requests.post(url, json=payload, headers=headers)
        notes = self.notes(response.json()["vocabulary"])
        return notes

    def notes(self, note_ids) -> dict:
        url = "https://jpdb.io/api/v1/lookup-vocabulary"

        payload = {
            "list": note_ids,
            "fields": [
                "spelling",
                "reading",
                "frequency_rank",
                "meanings",
                "part_of_speech",
            ],
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

        response = requests.post(url, json=payload, headers=headers)
        notes_info = response.json()["vocabulary_info"]
        return notes_info


def beautify_partofspeech(pos, expression=None) -> str:
    partofspeech_eq = {
        "n": "Noun",
        "pn": "Pronoun",
        "prt": "Particle",
        "int": "Interjection",
        "conj": "Conjunction",
        "pref": "Prefix",
        "suf": "Suffix",
        "cop": "Copula",
        "ctr": "Counter",
        "adj-i": "Adjective (い)",
        "adj-no": "Adjective (の)",
        "adj-na": "Adjective (な)",
        "adj-ku": "Adjective (く)",
        "adj-nari": "Adjective (なり)",
        "adj-pn": "Pre-noun adjective",
        "adv": "Adverb",
        "exp": "Expression",
        "aux": "Auxiliary",
        "name": "Name",
        "name-surname": "",
        "name-place": "",
        "name-male": "",
        "name-fem": "",
        "name-given": "",
        "num": "Numeric",
        "aux-adj": "Aux. adjective",
        "aux-v": "Auxiliary Verb",
        "vs": "Verb (する)",
        "vi": "intransitive",
        "vt": "transitive",
        "va": "Verb archaic",
        "v1": "1-dan",
        "v1-s": "1-dan",
        "v2": "2-dan",
        "vk": "irregular",
        "vs-c": "Verb (す)",
        "v4": {
            "": "",
            "v4u": "4-dan, う",
            "v4u-s": "4-dan, う",
            "v4k": "4-dan, く",
            "v4k-s": "4-dan, く",
            "v4g": "4-dan, ぐ",
            "v4g-s": "4-dan, ぐ",
            "v4s": "4-dan, す",
            "v4s-s": "4-dan, す",
            "v4t": "4-dan, つ",
            "v4t-s": "4-dan, つ",
            "v4n": "4-dan, ぬ",
            "v4n-s": "4-dan, ぬ",
            "v4b": "4-dan, ぶ",
            "v4b-s": "4-dan, ぶ",
            "v4m": "4-dan, む",
            "v4m-s": "4-dan, む",
            "v4r": "4-dan, る",
            "v4r-s": "4-dan, る",
            "v4r-i": "irregular",
            "v4aru": "4-dan",
        },
        "v5": {
            "": "",
            "v5u": "5-dan, う",
            "v5u-s": "5-dan, う",
            "v5k": "5-dan, く",
            "v5k-s": "5-dan, く",
            "v5g": "5-dan, ぐ",
            "v5g-s": "5-dan, ぐ",
            "v5s": "5-dan, す",
            "v5s-s": "5-dan, す",
            "v5t": "5-dan, つ",
            "v5t-s": "5-dan, つ",
            "v5n": "5-dan, ぬ",
            "v5n-s": "5-dan, ぬ",
            "v5b": "5-dan, ぶ",
            "v5b-s": "5-dan, ぶ",
            "v5m": "5-dan, む",
            "v5m-s": "5-dan, む",
            "v5r": "5-dan, る",
            "v5r-s": "5-dan, る",
            "v5r-i": "irregular",
            "v5aru": "5-dan",
        },
    }

    result = ""
    t_or_i = ", "

    def add_pos(res, pos):
        if len(res) > 0:
            res += ", "
        res += pos
        return res

    _pos = copy(pos)
    while len(_pos) > 0:
        p = _pos.pop(0)

        if p in ["vi", "vt"]:
            t_or_i += partofspeech_eq[p]
            continue

        if p == "v4" or p == "v5":
            _p = _pos.pop(0)
            try:
                result = add_pos(result, f"Verb ({partofspeech_eq[p][_p]}{t_or_i})")
            except KeyError:
                print(
                    f"part of speech {_p} is not implemented, please fill an issue on GitHub."
                )
            continue

        if p == "v1" or p == "v2":
            add_pos(result, f"Verb ({partofspeech_eq[p]}{t_or_i})")
            continue

        if p == "vk":
            result = add_pos(result, f"Verb ({partofspeech_eq['vk']}{t_or_i})")
            continue

        try:
            result = add_pos(result, partofspeech_eq[p])
        except:
            print(
                f"part of speech {p} is not implemented, please fill an issue on GitHub."
            )
            continue

    return result


def beautify_meaning(meaning) -> str:
    result = ""
    for i, m in enumerate(meaning):
        result += f"{i+1}. {m}\n"
    return result


def to_jpdb_note(note: Note):
    pitch = get_pitch_html(note.spelling, note.reading, PITCH_DICTIONARY)
    if pitch is None:
        pitch = ""
    return JPDB_Note(
        expression=note.spelling,
        part_of_speech=beautify_partofspeech(note.part_of_speech, note.spelling),
        spelling=note.reading,
        pitch=pitch,
        frequency=str(note.frequency_rank),
        meanings=beautify_meaning(note.meanings),
        examples="",  # not provided by the API
    )


def dict_on_first(_list):
    return {l[0]: l[1:] for l in _list}
