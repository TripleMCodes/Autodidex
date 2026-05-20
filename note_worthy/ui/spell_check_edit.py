from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QTextEdit
from spellchecker import SpellChecker


class SpellCheckTextEdit(QTextEdit):
    """
    A QTextEdit that underlines misspelled words in red.
    Owns its own SpellChecker instance — no external dependencies.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._spell = SpellChecker()
        self.textChanged.connect(self.highlight_misspelled_words)

    def highlight_misspelled_words(self):
        self.blockSignals(True)

        cursor = self.textCursor()
        text   = self.toPlainText()
        words  = text.split()
        misspelled = self._spell.unknown(words)

        # Clear previous underlines
        clear_fmt = QTextCharFormat()
        clear_fmt.setUnderlineStyle(QTextCharFormat.NoUnderline)
        cursor.beginEditBlock()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(clear_fmt)
        cursor.clearSelection()
        cursor.endEditBlock()

        # Apply red underline to each misspelled word
        err_fmt = QTextCharFormat()
        err_fmt.setUnderlineColor(QColor("red"))
        err_fmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)

        for word in misspelled:
            regex = QRegularExpression(r'\b{}\b'.format(word))
            it = regex.globalMatch(text)
            while it.hasNext():
                match = it.next()
                cursor.setPosition(match.capturedStart())
                cursor.setPosition(match.capturedEnd(), QTextCursor.KeepAnchor)
                cursor.mergeCharFormat(err_fmt)

        self.blockSignals(False)
