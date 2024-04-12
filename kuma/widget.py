"""Contains the features' interfaces."""

from typing import Optional

import aqt
from aqt.utils import showInfo
import aqt.editor
from PyQt6.QtCore import Qt


from .anki import KumaAnki
from .jpdb import JPDB, JPDB_Note
from .jpdb import search_all_expressions_jpdb_url


class Anki_SearchWidget(aqt.QWidget):
    def __init__(
        self, parent: aqt.QWidget, *, previous_query: Optional[str] = None
    ) -> None:
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

        self.decks_list = KumaAnki.decks().all_names()
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
    def __init__(
        self, parent: aqt.QWidget, *, previous_query: Optional[str] = None
    ) -> None:
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

        self.decks_list = KumaAnki.decks().all_names()
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
        self.query_lineEdit.returnPressed.connect(self._on_search_pressed)

        self.query_results_list.currentItemChanged.connect(
            lambda: self._on_query_results_changed()
        )
        self.query_results_list.doubleClicked.connect(
            lambda: self._on_query_results_doubleClicked()
        )

        self.search_button.pressed.connect(lambda: self._on_search_pressed())

        self.select_deck_comboBox.addItems(self.decks_list)
        self.select_deck_comboBox.currentIndexChanged.connect(
            lambda: self._on_deck_selected()
        )

        self.generate_button.pressed.connect(lambda: self._on_generate_pressed())

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

    def _on_search_pressed(self) -> None:
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

        # TODO add color for notes that already exist

        self.show_generate()
        self._can_generate = True

    def _on_generate_pressed(self) -> None:
        if not self._can_generate:
            showInfo("Cannot generate, please wait.")
            return

        url_index = self.query_results_list.currentIndex().row()
        jpdb_url = self.query_result_urls[url_index]
        jpdb_note = JPDB_Note.from_jpdb(jpdb_url)
        KumaAnki.add_note(jpdb_note, self.current_deck)

        showInfo("Note successfully generated.")
