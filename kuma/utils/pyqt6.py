from typing import Optional

import aqt


class LineEditRadioButton(aqt.QWidget):
    def __init__(
        self,
        parent: aqt.QWidget,
        content: Optional[str] = None,
        save: bool = False,
        tooltip: Optional[str] = None,
    ) -> None:
        super().__init__(parent)

        self.token_lineEdit = aqt.QLineEdit(content, self)
        self.token_radio = aqt.QRadioButton(self)
        self.token_radio.setChecked(save)
        self.token_radio.setToolTip(tooltip)

        self.setLayout(aqt.QHBoxLayout(self))
        self.layout().addWidget(self.token_lineEdit)
        self.layout().addWidget(self.token_radio)

    def text(self):
        return self.token_lineEdit.text()

    def isChecked(self):
        return self.token_radio.isChecked()
