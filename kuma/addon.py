"""Contains the main Widget class."""

from functools import partial

import aqt
import aqt.qt


from .anki import KumaAnki
from .widget import Anki_SearchWidget
from .widget import JPDB_SearchWidget
from .widget import JPDB_VocabListWidget
from .jpdb_api import JPDB_API_VocabListWidget
from .widget import RepositionWidget


class KumaBrowser_Main(aqt.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._layout = aqt.QFormLayout(self)

        # Tool Bar
        tool_bar = aqt.QToolBar("Kuma Browser Toolbar", self)
        self._layout.addWidget(tool_bar)

        self._actions = {}
        self.add_action(
            tool_bar,
            "Search",
            Anki_SearchWidget(self),
        )
        self.add_action(
            tool_bar,
            "JPDB",
            JPDB_SearchWidget(self),
        )
        self.add_action(
            tool_bar,
            "JPDB VocabList",
            JPDB_VocabListWidget(self),
        )
        self.add_action(
            tool_bar,
            "Reposition",
            RepositionWidget(self),
        )
        self.add_action(
            tool_bar,
            "JPDB API VocabList",
            JPDB_API_VocabListWidget(self),
        )

        self.show_hide(0)
        aqt.QShortcut(aqt.QKeySequence("Escape"), self, activated=self.on_Espace)

    def add_action(self, toolbar: aqt.QToolBar, name: str, widget: aqt.QWidget):
        _action = aqt.QAction(name)
        _action.triggered.connect(partial(self.show_hide, len(self._actions)))
        _action.setCheckable(True)
        toolbar.addAction(_action)
        self._layout.addWidget(widget)
        self._actions[name] = {"action": _action, "widget": widget}

    def show_hide(self, n):
        print(n)
        for i, v in enumerate(self._actions.values()):
            if i == n:
                v["widget"].show()
                v["action"].setChecked(True)
            else:
                v["widget"].hide()
                v["action"].setChecked(False)

    def on_Espace(self):
        self.close()


def open_interface():
    KumaAnki.window.KumaBrowser_Main = KumaBrowser_Main()
    KumaAnki.window.KumaBrowser_Main.show()
