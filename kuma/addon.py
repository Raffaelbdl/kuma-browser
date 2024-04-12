"""Contains the main Widget class."""

from typing import Optional

import aqt
import aqt.qt

from PyQt6 import QtCore

from .anki import KumaAnki
from .widget import Anki_SearchWidget
from .widget import JPDB_SearchWidget


class KumaBrowser_Main(aqt.QWidget):
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

        aqt.QShortcut(aqt.QKeySequence("Escape"), self, activated=self.on_Espace)

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

    def on_Espace(self):
        self.close()


def open_interface():
    KumaAnki.window.KumaBrowser_Main = KumaBrowser_Main()
    KumaAnki.window.KumaBrowser_Main.show()
