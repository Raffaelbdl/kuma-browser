from copy import copy
from dataclasses import dataclass
import requests
from typing import Optional


import aqt
from aqt.utils import showInfo
import aqt.editor


from .anki import KumaAnki
from .jpdb import JPDB_Note, get_pitch_html, PITCH_DICTIONARY


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

        if response.status_code == 200:
            return self.notes(response.json()["vocabulary"])

        if response.status_code == 400:
            showInfo("Something went wrong. Please check the Deck Id")
            return []

        if response.status_code == 403:
            showInfo("Please check your API key")
            return []

        showInfo("Something unexpected went wrong.")
        return []

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


class VLAPIGenerationThread(aqt.QThread):
    finished = aqt.pyqtSignal()
    generated = aqt.pyqtSignal(int)

    def __init__(self, notes: list, current_deck: str):
        super().__init__()
        self.notes = notes
        self.current_deck = current_deck

    def run(self):
        for i, n in enumerate(self.notes):
            self.generated.emit(i)

            query = f'"deck:{self.current_deck}" Expression:{n.expression}'
            if len(KumaAnki.find_notes(query)) > 0:
                continue

            try:
                KumaAnki.add_note(n, self.current_deck)
            except:
                continue

        self.finished.emit()


import json
from pathlib import Path
from utils.pyqt6 import LineEditRadioButton


class JPDB_API_VocabListWidget(aqt.QWidget):
    def __init__(self, parent: aqt.QWidget, *, previous_query: Optional[str] = None):
        super().__init__(parent)

        self.path_to_config = Path(__file__).resolve().parent / "config" / "api.json"
        if not self.path_to_config.exists():
            config = {"token": ""}
        else:
            with self.path_to_config.open("r") as f:
                config = json.load(f)

        self.token_lineEdit = LineEditRadioButton(
            self, config["token"], False, "Check to save API key."
        )
        self.deckId_lineEdit = aqt.QLineEdit(self)

        self.deckId_lineEdit.setText("0")
        self.deckId_lineEdit.setValidator(aqt.QIntValidator())

        self.deck_label = aqt.QLabel("Select a deck", self)
        self.select_deck_comboBox = aqt.QComboBox(self)

        self.generate_button = aqt.QPushButton("Generate", self)

        self.prog_bar = aqt.QProgressBar(self)
        self.prog_bar.hide()

        self.can_generate = True
        self.decks_list = KumaAnki.decks().all_names(force_default=False)

        self._layout = aqt.QFormLayout(self)
        self.layout_init()
        self.widget_init()

    def layout_init(self):
        self._layout.addRow("Enter Token: ", self.token_lineEdit)
        self._layout.addRow("Enter Deck Id: ", self.deckId_lineEdit)
        self._layout.addWidget(self.deck_label)
        self._layout.addWidget(self.select_deck_comboBox)
        self._layout.addWidget(self.generate_button)
        self._layout.addWidget(self.prog_bar)

    def widget_init(self):
        self.select_deck_comboBox.addItems(self.decks_list)
        self.generate_button.pressed.connect(self.generate_or_update)

    def generate_or_update(self) -> None:
        if not self.can_generate:
            return
        self.can_generate = False

        token = self.token_lineEdit.text()

        if self.token_lineEdit.isChecked():
            with self.path_to_config.open("w") as f:
                json.dump({"token": self.token_lineEdit.text()}, f)

        deck_id = self.deckId_lineEdit.text()
        current_deck = self.select_deck_comboBox.currentText()
        api = JpdbAPI(token)

        notes = api.vocabulary_list(int(deck_id))
        if len(notes) == 0:
            self.can_generate = True
            self.prog_bar.hide()
            return

        notes = [
            to_jpdb_note(Note(**{k: v for (k, v) in zip(Note.__dataclass_fields__, n)}))
            for n in notes
        ]

        self.prog_bar.show()
        self.prog_bar.setRange(0, len(notes))
        self.prog_bar.setValue(0)

        self.generation_worker = VLAPIGenerationThread(notes, current_deck)
        self.generation_worker.generated.connect(self._on_generating)
        self.generation_worker.finished.connect(self._on_generation_finished)
        self.generation_worker.finished.connect(self.generation_worker.quit)
        self.generation_worker.start()

    def _on_generating(self, i):
        self.prog_bar.setValue(i)

    def _on_generation_finished(self):
        self.can_generate = True
        self.prog_bar.hide()
        showInfo("Generation Finished!")
