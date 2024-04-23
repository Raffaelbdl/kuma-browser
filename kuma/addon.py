"""Contains the main Widget class."""

from typing import Optional

import aqt
from aqt.utils import showInfo
import aqt.qt

from PyQt6 import QtCore

from .anki import KumaAnki, reposition_on_frequency
from .widget import Anki_SearchWidget
from .widget import JPDB_SearchWidget
from .widget import JPDB_VocabListWidget
from .widget import RepositionWidget


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

        self.jpdb_vl_action = aqt.QAction("JPDB VocabList", self)
        self.jpdb_vl_action.triggered.connect(self.on_vl_jpdb_triggered)
        self.jpdb_vl_action.setCheckable(True)
        self.jpdb_vl_action.setChecked(False)
        tool_bar.addAction(self.jpdb_vl_action)

        self.reposition_action = aqt.QAction("Reposition", self)
        self.reposition_action.triggered.connect(self.on_reposition_triggered)
        self.reposition_action.setCheckable(True)
        self.reposition_action.setChecked(False)
        tool_bar.addAction(self.reposition_action)

        self._layout.addWidget(tool_bar)

        # Anki Page
        self.anki_search_widget = Anki_SearchWidget(self)
        self.anki_search_widget.show()
        self._layout.addWidget(self.anki_search_widget)

        # JPDB Page
        self.jpdb_search_widget = JPDB_SearchWidget(self)
        self.jpdb_search_widget.hide()
        self._layout.addWidget(self.jpdb_search_widget)

        # JPDB VL Page
        self.jpdb_vl_widget = JPDB_VocabListWidget(self)
        self.jpdb_vl_widget.hide()
        self._layout.addWidget(self.jpdb_vl_widget)

        self.reposition_widget = RepositionWidget(self)
        self.reposition_widget.hide()
        self._layout.addWidget(self.reposition_widget)

        aqt.QShortcut(aqt.QKeySequence("Escape"), self, activated=self.on_Espace)

    def on_search_triggered(self) -> None:
        self.jpdb_search_widget.hide()
        self.jpdb_vl_widget.hide()
        self.anki_search_widget.show()
        self.reposition_widget.hide()
        self.jpdb_action.setChecked(False)
        self.jpdb_vl_action.setChecked(False)
        self.search_action.setChecked(True)
        self.reposition_action.setChecked(False)

    def on_jpdb_triggered(self) -> None:
        self.anki_search_widget.hide()
        self.jpdb_vl_widget.hide()
        self.jpdb_search_widget.show()
        self.reposition_widget.hide()
        self.search_action.setChecked(False)
        self.jpdb_vl_action.setChecked(False)
        self.jpdb_action.setChecked(True)
        self.reposition_action.setChecked(False)

    def on_vl_jpdb_triggered(self) -> None:
        self.anki_search_widget.hide()
        self.jpdb_search_widget.hide()
        self.jpdb_vl_widget.show()
        self.reposition_widget.hide()
        self.search_action.setChecked(False)
        self.jpdb_action.setChecked(False)
        self.jpdb_vl_action.setChecked(True)
        self.reposition_action.setChecked(False)

    def on_reposition_triggered(self) -> None:
        self.anki_search_widget.hide()
        self.jpdb_search_widget.hide()
        self.jpdb_vl_widget.hide()
        self.reposition_widget.show()
        self.search_action.setChecked(False)
        self.jpdb_action.setChecked(False)
        self.jpdb_vl_action.setChecked(False)
        self.reposition_action.setChecked(True)

    def on_Espace(self):
        self.close()


def open_interface():
    KumaAnki.window.KumaBrowser_Main = KumaBrowser_Main()
    KumaAnki.window.KumaBrowser_Main.show()
