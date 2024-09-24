"""Anki related functions."""

from typing import Optional, List

import anki
import anki.collection
import anki.decks
import anki.models
import anki.notes
import anki.cards

import aqt
import aqt.qt

from .jpdb import JPDB_Note
from .setup import load_template


class KumaAnki:
    model_name: str = "Kuma Model"
    window = aqt.mw

    @staticmethod
    def collection() -> anki.collection.Collection:
        _collection = KumaAnki.window.col
        if _collection is None:
            raise Exception("Collection is not available.")
        return _collection

    @staticmethod
    def decks() -> anki.decks.DeckManager:
        _decks = KumaAnki.collection().decks
        if _decks is None:
            raise Exception("Decks are not available.")
        return _decks

    @staticmethod
    def models() -> anki.models.ModelManager:
        _models = KumaAnki.collection().models
        if _models is None:
            raise Exception("Models are not available.")
        return _models

    @staticmethod
    def create_note(note: JPDB_Note, deck_name: str) -> anki.notes.Note:
        model = KumaAnki.models().by_name(KumaAnki.model_name)
        if model is None:
            raise Exception("Model was not found: " + KumaAnki.model_name)

        deck = KumaAnki.decks().by_name(deck_name)
        if deck is None:
            raise Exception("Deck was not found: " + deck_name)

        ankiNote = anki.notes.Note(KumaAnki.collection(), model)
        ankiNote.note_type()["did"] = deck["id"]

        ankiNote["Expression"] = note.expression
        ankiNote["PartOfSpeech"] = note.part_of_speech
        ankiNote["Spelling"] = note.spelling
        ankiNote["Pitch"] = note.pitch
        ankiNote["Frequency"] = note.frequency
        ankiNote["Meanings"] = note.meanings
        ankiNote["Examples"] = note.examples
        ankiNote["ID"] = note.note_id

        return ankiNote

    @staticmethod
    def add_note(note: JPDB_Note, deck_name: str) -> None:
        KumaAnki.add_model()

        ankiNote = KumaAnki.create_note(note, deck_name)
        KumaAnki.collection().addNote(ankiNote)

    @staticmethod
    def find_notes(query: Optional[str] = None) -> List[int]:
        if query is None or query == "":
            return []
        return list(map(int, KumaAnki.collection().find_notes(query)))

    @staticmethod
    def add_model() -> None:
        if KumaAnki.model_name in [
            n.name for n in KumaAnki.models().all_names_and_ids()
        ]:
            return  # model already exists

        m = KumaAnki.models().new(KumaAnki.model_name)
        template = load_template()

        for field in template["inOrderFields"]:
            fm = KumaAnki.models().new_field(field)
            KumaAnki.models().add_field(m, fm)

        m["css"] = template["css"]

        for i, card in enumerate(template["cardTemplates"]):
            card_name = "Card " + str(i + 1)
            t = KumaAnki.models().new_template(card_name)
            t["qfmt"] = card["Front"]
            t["afmt"] = card["Back"]
            KumaAnki.models().add_template(m, t)

        KumaAnki.models().add(m)

    @staticmethod
    def find_cards(query: Optional[str] = None) -> Optional[int]:
        if query is None or query == "":
            return []
        return list(map(int, KumaAnki.collection().find_cards(query)))

    @staticmethod
    def get_cards_of_note(note_id: int) -> list[int]:
        """Returns the cards linked to a note."""
        return KumaAnki.find_cards("nid:" + str(note_id))


from operator import itemgetter


def reposition_on_frequency(deck_name: str) -> None:
    notes_id = KumaAnki.find_notes(f'"deck:{deck_name}"')
    notes = [KumaAnki.collection().get_note(i) for i in notes_id]

    name_freq = []
    for n in notes:
        frequency = n.fields[4]
        if frequency == "" or frequency is None:
            frequency = 200_000
        else:
            frequency = int(frequency)

        name_freq.append((n.id, frequency))

    name_freq.sort(key=itemgetter(1))

    cards_to_update = []
    for i, item in enumerate(name_freq):
        cards_id = KumaAnki.get_cards_of_note(item[0])
        for _id in cards_id:
            card = KumaAnki.collection().get_card(_id)
            if card.type > 0:
                continue
            card.due = i
            cards_to_update.append(card)
    KumaAnki.collection().update_cards(cards_to_update)
    # expression, frequency


def equal_note(
    note: anki.notes.Note, jpdb_note: JPDB_Note, *, check_spelling: bool = False
) -> bool:
    if note.fields[0] != jpdb_note.expression:
        return False
    if check_spelling and note.fields[2] != jpdb_note.spelling:
        return False
    return True


def is_in_deck(deck: str, note_id: str) -> bool:
    query = f'"deck:{deck}" ID:{note_id}'
    try:
        return len(KumaAnki.find_notes(query))
    except:
        print(query)
        return True  # won't create
