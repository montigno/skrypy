from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QPainter, QColor, QTextCursor

import jedi


class LineNumberArea(QWidget):

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(
            self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.lineNumberArea = LineNumberArea(self)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        # Nombre de lignes modifié
        self.blockCountChanged.connect(
            self.updateLineNumberAreaWidth
        )

        self.updateRequest.connect(
            self.updateLineNumberArea
        )

        self.updateLineNumberAreaWidth(0)

    def lineNumberAreaWidth(self):

        digits = len(str(max(1, self.blockCount())))

        return (8 + self.fontMetrics().horizontalAdvance("9") * digits)

    def updateLineNumberAreaWidth(self, newBlockCount):

        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):

        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(
                0,
                rect.y(),
                self.lineNumberArea.width(),
                rect.height()
            )

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def lineNumberAreaPaintEvent(self, event):

        painter = QPainter(self.lineNumberArea)

        painter.fillRect(
            event.rect(),
            QColor("#eeeeee")
        )

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()

        top = int(
            self.blockBoundingGeometry(block)
            .translated(self.contentOffset())
            .top()
        )

        bottom = (
            top +
            int(self.blockBoundingRect(block).height())
        )

        while (block.isValid() and top <= event.rect().bottom()):
            if (
                block.isVisible()
                and bottom >= event.rect().top()
            ):
                number = str(blockNumber + 1)
                painter.setPen(
                    QColor("#555555")
                )
                painter.drawText(
                    0,
                    top,
                    self.lineNumberArea.width() - 4,
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    number
                )

            block = block.next()

            top = bottom

            bottom = (top + int(self.blockBoundingRect(block).height()))

            blockNumber += 1

    def resizeEvent(self, event):

        super().resizeEvent(event)

        cr = self.contentsRect()

        self.lineNumberArea.setGeometry(
            QRect(
                cr.left(),
                cr.top(),
                self.lineNumberAreaWidth(),
                cr.height()
            )
        )


class CompletionPopup(QListWidget):

    def __init__(self, editor):
        super().__init__()

        self.editor = editor

        self.setWindowFlags(Qt.Popup)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

    def keyPressEvent(self, event):

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):

            self.editor.acceptCompletion()
            return

        if event.key() == Qt.Key_Tab:

            self.editor.acceptCompletion()
            return

        if event.key() == Qt.Key_Escape:

            self.hide()
            self.editor.setFocus()
            return

        if event.key() == Qt.Key_Down:

            row = self.currentRow()

            if row < self.count() - 1:
                self.setCurrentRow(row + 1)

            return

        if event.key() == Qt.Key_Up:

            row = self.currentRow()

            if row > 0:
                self.setCurrentRow(row - 1)

            return

        super().keyPressEvent(event)

   
class TextEditPy(CodeEditor):

    def __init__(self, editor, parent=None):

        super().__init__(parent)
        
        self.editor = editor

        self.completion_popup = CompletionPopup(self)

        self.completion_popup.itemClicked.connect(
            self.insertCompletionItem
        )

        self.completion_popup.hide()

    # ---------------------------------------------------------
    # KEYBOARD
    # ---------------------------------------------------------

    def keyPressEvent(self, event):

        # -----------------------------------------------------
        # Ctrl + Space
        # -----------------------------------------------------

        if (
            event.key() == Qt.Key_Space
            and event.modifiers() & Qt.ControlModifier
        ):

            self.showCompletion()

            event.accept()

            return

        # -----------------------------------------------------
        # TAB
        # -----------------------------------------------------

        if event.key() == Qt.Key_Tab:

            self.insertPlainText("    ")

            event.accept()

            return

        # -----------------------------------------------------
        # ESC
        # -----------------------------------------------------

        if event.key() == Qt.Key_Escape:

            if self.completion_popup.isVisible():

                self.completion_popup.hide()

                event.accept()

                return

        # -----------------------------------------------------
        # comportement normal
        # -----------------------------------------------------

        super().keyPressEvent(event)

        # -----------------------------------------------------
        # AUTO COMPLETION après "."
        # -----------------------------------------------------

        if event.text() == ".":

            self.showCompletion()

    # ---------------------------------------------------------
    # SHOW COMPLETION
    # ---------------------------------------------------------

    def showCompletion(self):

        cursor = self.textCursor()

        code = self.toPlainText()

        line = cursor.blockNumber() + 1

        column = cursor.positionInBlock()

        try:

            script = jedi.Script(
                code=code,
                path="skrypy_script.py"
            )

            completions = script.complete(
                line=line,
                column=column
            )

        except Exception as error:

            print(
                "Jedi completion error:",
                error
            )

            self.completion_popup.hide()

            return

        if not completions:

            self.completion_popup.hide()

            return

        popup = self.completion_popup

        popup.clear()

        for completion in completions:

            item = QListWidgetItem(
                completion.name
            )

            item.setData(
                Qt.UserRole,
                completion
            )

            popup.addItem(item)

        if popup.count() == 0:

            popup.hide()

            return

        popup.setCurrentRow(0)

        popup.setMinimumWidth(250)

        row_height = popup.sizeHintForRow(0)

        height = min(
            row_height * min(
                popup.count(),
                10
            ) + 4,
            250
        )

        popup.setFixedHeight(height)

        # -----------------------------------------------------
        # POSITION
        # -----------------------------------------------------

        rect = self.cursorRect()

        pos = self.mapToGlobal(
            rect.bottomLeft()
        )

        popup.move(pos)

        popup.show()

        # Très important :
        # le popup reçoit le clavier
        popup.setFocus()

    # ---------------------------------------------------------
    # ACCEPT COMPLETION
    # ---------------------------------------------------------

    def acceptCompletion(self):

        popup = self.completion_popup

        if not popup.isVisible():

            return

        item = popup.currentItem()

        if item is not None:

            self.insertCompletionItem(item)

        popup.hide()

        self.setFocus()

    # ---------------------------------------------------------
    # INSERT COMPLETION
    # ---------------------------------------------------------

    def insertCompletionItem(self, item):

        if item is None:

            return

        completion = item.text()

        if not completion:

            return

        cursor = self.textCursor()

        cursor.select(
            QTextCursor.WordUnderCursor
        )

        cursor.insertText(
            completion
        )

        self.setTextCursor(cursor)

        self.completion_popup.hide()

        self.setFocus()

    # ---------------------------------------------------------
    # MOUSE
    # ---------------------------------------------------------

    def mousePressEvent(self, event):
    
        self.completion_popup.hide()
    
        if self.editor:
            self.editor.clearSelection()
    
        super().mousePressEvent(event)