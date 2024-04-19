"""Contains the features' interfaces."""

import json
import os
from pathlib import Path
from typing import Callable, Optional, List

import aqt
from aqt.utils import showInfo
import aqt.editor
from PyQt6.QtCore import Qt


from .anki import KumaAnki
from .jpdb import JPDB, JPDB_Note
from .jpdb import search_all_expressions_jpdb_url
from .jpdb import load_url
from .jpdb import get_all_entries_from_one_page


class Anki_SearchWidget(aqt.QWidget):
    def __init__(self, parent: aqt.QWidget, *, previous_query: Optional[str] = None):
        super().__init__(parent)

        self.query_lineEdit = aqt.QLineEdit(previous_query, self)
        self.query_results_list = aqt.QListWidget(self)
        self.search_button = aqt.QPushButton("Search Anki Collection", self)

        self.query_menu = aqt.QMenu(self)
        self.reposition_action = self.query_menu.addAction("Study Next")
        self.reposition_action.triggered.connect(self.on_reposition_action)
        self.query_results_list.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.query_results_list.customContextMenuRequested.connect(
            self.show_context_menu
        )

        self.select_deck_comboBox = aqt.QComboBox(self)

        self.main_layout = aqt.QHBoxLayout(self)
        self.search_layout = aqt.QFormLayout(self)
        self.edit_layout = aqt.QVBoxLayout(self)
        self.main_layout.addLayout(self.search_layout)
        self.main_layout.addLayout(self.edit_layout)
        self.layout_init()

        self.query_result_urls = []
        self.current_query_result = -1

        self.decks_list = KumaAnki.decks().all_names(force_default=False)
        self.current_deck = self.decks_list[0]
        self._can_generate = False

        self.notes_id = []

        self.widget_init()

        editor_widget = aqt.QWidget(self)
        self.editor = aqt.editor.Editor(KumaAnki.window, editor_widget, self)
        self.edit_layout.addWidget(editor_widget)

    def layout_init(self):
        self.search_layout.addRow("Query: ", self.query_lineEdit)
        self.search_layout.addRow("Select Deck: ", self.select_deck_comboBox)
        self.search_layout.addWidget(self.search_button)
        self.search_layout.addWidget(self.query_results_list)

    def widget_init(self):
        self.query_lineEdit.returnPressed.connect(self.on_search_pressed)

        self.select_deck_comboBox.addItems(self.decks_list)
        self.select_deck_comboBox.currentIndexChanged.connect(self.on_deck_selected)

        self.search_button.pressed.connect(self.on_search_pressed)

        self.query_results_list.currentItemChanged.connect(self.on_note_selected)

    def on_deck_selected(self):
        self.current_deck = self.select_deck_comboBox.currentText()

    def on_search_pressed(self):
        self.query_results_list.clear()

        query = self.query_lineEdit.text()
        if query == "":
            return
        query = f'"deck:{self.current_deck}" expression:' + query

        self.notes_id = KumaAnki.find_notes(query)
        notes_info = []
        for note_id in self.notes_id:
            note_name = KumaAnki.collection().get_note(note_id).fields[0]
            notes_info.append("Note " + note_name + " with id " + str(note_id))
        self.query_results_list.addItems(notes_info)

    def on_note_selected(self):
        note_id = self.notes_id[self.query_results_list.currentIndex().row()]
        self.editor.set_note(KumaAnki.collection().get_note(note_id))

    def show_context_menu(self, pos):
        item = self.query_results_list.itemAt(pos)
        if item is None:
            return
        self.query_menu.popup(self.query_results_list.mapToGlobal(pos))

    def on_reposition_action(self):
        note_id = self.notes_id[self.query_results_list.currentIndex().row()]
        cards_id = KumaAnki.get_cards_of_note(note_id)

        for card_id in cards_id:
            card = KumaAnki.collection().get_card(card_id)
            if card.type > 0:  # if not new
                continue

            card.due = 0
            KumaAnki.collection().update_card(card)


class JPDB_SearchWidget(aqt.QWidget):
    def __init__(self, parent: aqt.QWidget, *, previous_query: Optional[str] = None):
        super().__init__(parent)

        self.query_lineEdit = aqt.QLineEdit(previous_query, self)
        self.query_results_list = aqt.QListWidget(self)
        self.search_button = aqt.QPushButton("Search JPDB", self)

        self.deck_label = aqt.QLabel("Select a deck", self)
        self.select_deck_comboBox = aqt.QComboBox(self)
        self.generate_button = aqt.QPushButton("Generate Note", self)

        self._layout = aqt.QFormLayout(self)
        self.layout_init()

        self.query_result_urls = []
        self.current_query_result = -1

        self.decks_list = KumaAnki.decks().all_names(force_default=False)
        self.current_deck = self.decks_list[0]
        self._can_generate = False

        self.widget_init()

    def layout_init(self):
        self._layout.addRow("Query: ", self.query_lineEdit)
        self._layout.addRow("Results by\npertinence on JPDB: ", self.search_button)
        self._layout.addWidget(self.query_results_list)
        self._layout.addWidget(self.deck_label)
        self._layout.addWidget(self.select_deck_comboBox)
        self._layout.addWidget(self.generate_button)

        self.hide_generate()

    def widget_init(self):
        self.query_lineEdit.returnPressed.connect(self.search)
        self.search_button.pressed.connect(self.search)

        self.query_results_list.currentItemChanged.connect(
            self._on_query_results_changed
        )
        self.query_results_list.doubleClicked.connect(
            self._on_query_results_doubleClicked
        )

        self.select_deck_comboBox.addItems(self.decks_list)
        self.select_deck_comboBox.currentIndexChanged.connect(self._on_deck_selected)

        self.generate_button.pressed.connect(self.generate)

    def _on_query_results_changed(self) -> None:
        self.current_query_result = self.query_results_list.currentIndex()

    def _on_query_results_doubleClicked(self) -> None:
        url_index = self.query_results_list.currentIndex().row()
        url = self.query_result_urls[url_index]
        aqt.QDesktopServices.openUrl(aqt.QUrl(url))

    def _on_deck_selected(self) -> None:
        self.current_deck = self.select_deck_comboBox.currentText()

    def hide_generate(self) -> None:
        self.deck_label.hide()
        self.select_deck_comboBox.hide()
        self.generate_button.hide()

    def show_generate(self) -> None:
        self.deck_label.show()
        self.select_deck_comboBox.show()
        self.generate_button.show()

    def search(self) -> None:
        self.hide_generate()
        self._can_generate = False

        self.query_results_list.clear()

        query = self.query_lineEdit.text()
        if query == "":
            return

        query_results_entries = search_all_expressions_jpdb_url(query)
        self.query_result_urls = list(
            map(lambda x: JPDB.base_url + x, query_results_entries)
        )
        self.query_results_list.addItems(query_results_entries)

        self.show_generate()
        self._can_generate = True

    def generate(self) -> None:
        if not self._can_generate:
            showInfo("Cannot generate, please wait.")
            return

        url_index = self.query_results_list.currentIndex().row()
        jpdb_url = self.query_result_urls[url_index]
        jpdb_note = JPDB_Note.from_jpdb(jpdb_url)
        KumaAnki.add_note(jpdb_note, self.current_deck)

        showInfo("Note successfully generated.")


class VLSearchThread(aqt.QThread):
    finished = aqt.pyqtSignal(list)
    next_page = aqt.pyqtSignal(int)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        entries = self.get_all_entries_from_vocab_list(self.url)
        self.finished.emit(entries)

    def get_all_entries_from_vocab_list(self, vl_url):
        try:
            self.next_page.emit(int(vl_url.split("=")[-1]))
        except ValueError:
            self.next_page.emit(0)

        jpdb_soup = load_url(vl_url)
        entries = get_all_entries_from_one_page(jpdb_soup)
        entries = [JPDB.base_url + e.strip("#a") for e in entries]

        # last page
        if jpdb_soup.find(class_="pagination without-next"):
            return entries

        # first page
        without_prev = jpdb_soup.find(class_="pagination without-prev")
        if without_prev:
            next_root = without_prev.find_all("a", href=True)[-1]["href"][:-2]
            entries += self.get_all_entries_from_vocab_list(JPDB.base_url + next_root)
            return entries

        next_root = jpdb_soup.find(class_="pagination")
        next_root = next_root.find_all("a", href=True)[-1]["href"][:-2]
        entries += self.get_all_entries_from_vocab_list(JPDB.base_url + next_root)
        return entries


class VLGenerationThread(aqt.QThread):
    finished = aqt.pyqtSignal()
    generated = aqt.pyqtSignal(int)

    def __init__(self, current_deck: str, urls: List[str]):
        super().__init__()
        self.current_deck = current_deck
        self.urls = urls

    def run(self):
        # cannot be multithreaded due to JPDB constraints
        for i, url in enumerate(self.urls):
            self.generated.emit(i)

            expression = url.split("/")[-1]
            query = f'"deck:{self.current_deck}" Expression:{expression}'
            if len(KumaAnki.find_notes(query)) > 0:
                continue

            jpdb_note = JPDB_Note.from_jpdb(url)
            KumaAnki.add_note(jpdb_note, self.current_deck)
        self.finished.emit()


class JPDB_VocabListWidget(aqt.QWidget):
    def __init__(self, parent: aqt.QWidget, *, previous_query: Optional[str] = None):
        super().__init__(parent)

        self.query_lineEdit = aqt.QLineEdit(previous_query, self)
        self.query_results_list = aqt.QListWidget(self)
        self.search_button = aqt.QPushButton("Search vocab list on JPDB", self)
        self.query_results = []

        self.wait_label = aqt.QLabel(
            "Notes are being collecting, this can take a few minutes.", self
        )

        self.deck_label = aqt.QLabel("Select a deck", self)
        self.select_deck_comboBox = aqt.QComboBox(self)

        self.generate_button = aqt.QPushButton("Generate all notes", self)

        self.can_search = True
        self.can_generate = False
        self.decks_list = KumaAnki.decks().all_names(force_default=False)
        self.current_deck = self.decks_list[0]

        self.prog_bar = aqt.QProgressBar(self)
        self.prog_bar.hide()

        self._layout = aqt.QFormLayout(self)
        self.layout_init()
        self.widget_init()

        self.search_thread = aqt.QThread()
        self.generate_thread = aqt.QThread()

        self.last_query = ""

    def layout_init(self):
        self._layout.addRow("Query: ", self.query_lineEdit)
        self._layout.addRow("Get all notes: ", self.search_button)
        self._layout.addWidget(self.wait_label)
        self._layout.addWidget(self.query_results_list)
        self._layout.addWidget(self.deck_label)
        self._layout.addWidget(self.select_deck_comboBox)
        self._layout.addWidget(self.generate_button)
        self._layout.addWidget(self.prog_bar)

        self.wait_label.hide()

    def widget_init(self):
        self.query_lineEdit.returnPressed.connect(self.search)
        self.search_button.pressed.connect(self.search)

        self.query_results_list.doubleClicked.connect(
            self.on_query_results_doubleClicked
        )
        self.select_deck_comboBox.addItems(self.decks_list)
        self.select_deck_comboBox.currentIndexChanged.connect(self.on_deck_selected)

        self.generate_button.pressed.connect(self.generate_or_update)

    def search(self) -> None:
        if not self.can_search:
            return
        self.can_search = False
        self.can_generate = False

        self.query_results_list.clear()

        query = self.query_lineEdit.text()
        if JPDB.base_url not in query:
            self.can_search = True
            self.wait_label.hide()
            showInfo("Please enter a JPDB url.")
            return
        if "/vocabulary-list" not in query:
            self.can_search = True
            self.wait_label.hide()
            showInfo("Please enter a vocabulary list url.")
            return
        self.last_query = query

        entries = self.load_urls(query)
        if len(entries) > 0:
            self._on_search_finished(entries)
            return

        self.wait_label.show()

        self.search_worker = VLSearchThread(query)
        self.search_worker.next_page.connect(self._on_searching)
        self.search_worker.finished.connect(self._on_search_finished)
        self.search_worker.finished.connect(self.search_worker.quit)
        self.search_worker.start()

    def _on_searching(self, offset):
        self.wait_label.setText(str(offset) + " entries collected.")

    def _on_search_finished(self, entries):
        self.can_search = True
        self.can_generate = True
        self.wait_label.hide()

        self.query_results = entries
        self.query_results_list.addItems(entries)

        self.save_urls(self.last_query, self.query_results)

    def generate_or_update(self) -> None:
        if not self.can_generate:
            return
        self.can_search = False
        self.can_generate = False

        self.hide_deck_widget()
        self.prog_bar.show()
        self.prog_bar.setRange(0, len(self.query_results))
        self.prog_bar.setValue(0)

        self.generation_worker = VLGenerationThread(
            self.current_deck, self.query_results
        )
        self.generation_worker.generated.connect(self._on_generating)
        self.generation_worker.finished.connect(self._on_generation_finished)
        self.generation_worker.finished.connect(self.generation_worker.quit)
        self.generation_worker.start()

    def _on_generating(self, i):
        self.prog_bar.setValue(i)

    def _on_generation_finished(self):
        self.can_generate = True
        self.show_deck_widget()
        self.prog_bar.hide()
        showInfo("Generation Finished!")

    def on_query_results_doubleClicked(self) -> None:
        url_index = self.query_results_list.currentIndex().row()
        url = self.query_results[url_index]
        aqt.QDesktopServices.openUrl(aqt.QUrl(url))

    def on_deck_selected(self) -> None:
        self.current_deck = self.select_deck_comboBox.currentText()

    def hide_deck_widget(self):
        self.deck_label.hide()
        self.select_deck_comboBox.hide()

    def show_deck_widget(self):
        self.deck_label.show()
        self.select_deck_comboBox.show()

    def save_urls(self, vocab_list: str, urls: List[str]):
        path = Path(__file__).parent.joinpath("vocab_lists")
        os.makedirs(path, exist_ok=True)

        with path.joinpath(self._get_key(vocab_list)).open("w") as f:
            json.dump(urls, f)

    def load_urls(self, vocab_list: str) -> List[str]:
        path = Path(__file__).parent.joinpath("vocab_lists")
        path = path.joinpath(self._get_key(vocab_list))

        if not path.exists():
            return []

        with path.open("r") as f:
            urls = json.load(f)
        return urls

    def _get_key(self, vocab_list: str) -> str:
        return vocab_list.split("/")[-2]
