import aqt
from aqt.utils import qconnect
import aqt.qt

from .addon import open_interface
from .anki import KumaAnki


action = aqt.qt.QAction("Kuma Browser", KumaAnki.window)

qconnect(action.triggered, open_interface)
KumaAnki.window.form.menuTools.addAction(action)
