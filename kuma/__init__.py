from functools import partial
from typing import Optional

import aqt
from aqt.utils import showInfo, qconnect
import aqt.qt
import anki
import anki.notes
import anki.collection

from .jpdb import JPDB_Anki
from .interface import JPDB_SearchWidget, Anki_SearchWidget


class JPDB_Widget(aqt.QWidget):
    def __init__(self, parent: aqt.QWidget) -> None:
        super().__init__(parent)

        self._layout = aqt.QFormLayout(self)
        self.search_button = aqt.QPushButton("Search on JPDB")
        self._layout.addWidget(self.search_button)


class JPDB_Interface(aqt.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._layout = aqt.QFormLayout(self)

        # Tool Bar
        tool_bar = aqt.QToolBar("Kuma Browser Toolbar", self)

        self.search_action = aqt.QAction("Search", self)
        self.search_action.triggered.connect(self.on_search_triggered)
        self.search_action.setCheckable(True)
        self.search_action.setChecked(True)
        tool_bar.addAction(self.search_action)

        self.jpdb_action = aqt.QAction("JPDB", self)
        self.jpdb_action.triggered.connect(self.on_jpdb_triggered)
        self.jpdb_action.setCheckable(True)
        self.jpdb_action.setChecked(False)
        tool_bar.addAction(self.jpdb_action)

        self._layout.addWidget(tool_bar)

        # Anki Page
        self.anki_search_widget = Anki_SearchWidget(self)
        self.anki_search_widget.show()
        self._layout.addWidget(self.anki_search_widget)

        # JPDB Page
        self.jpdb_search_widget = JPDB_SearchWidget(self)
        self.jpdb_search_widget.hide()
        self._layout.addWidget(self.jpdb_search_widget)

    def on_search_triggered(self) -> None:
        self.jpdb_search_widget.hide()
        self.anki_search_widget.show()
        self.jpdb_action.setChecked(False)
        self.search_action.setChecked(True)

    def on_jpdb_triggered(self) -> None:
        self.anki_search_widget.hide()
        self.jpdb_search_widget.show()
        self.search_action.setChecked(False)
        self.jpdb_action.setChecked(True)

    def on_deck_selected(self, combobox: aqt.QComboBox):
        self.current_deck = combobox.currentText()

    def on_model_selected(self, combobox: aqt.QComboBox):
        self.current_model = combobox.currentText()

    def on_generate_clicked(self):
        query = self.line_edit.text()
        if query == "":
            return
        query = f"deck:{self.current_deck} " + query

        self.query_results.clear()

        notes = self.jpdb_anki.find_notes(query)
        notes_info = []
        for note_id in notes:
            note_name = self.jpdb_anki.collection.get_note(note_id).fields[0]
            notes_info.append("Note " + note_name + " with id " + str(note_id))
        self.query_results.addItems(notes_info)

        self.jpdb_widget.show()

        # check if expression is in deck
        # show all notes that coreespond to query

        # url = jpdb.search_expression_jpdb_url(query)
        # jpdb_note = JPDB_Note.from_jpdb(url)
        # self.jpdb_anki.add_note(jpdb_note, self.current_deck)

        # showInfo("You generated a note for " + query + " !")


def open_interface():
    JPDB_Anki.window().JPDB_interface = JPDB_Interface()
    JPDB_Anki.window().JPDB_interface.show()


action = aqt.qt.QAction("Kuma Browser", JPDB_Anki.window())

qconnect(action.triggered, open_interface)
JPDB_Anki.window().form.menuTools.addAction(action)
