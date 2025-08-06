from PyQt5.QtCore import Qt, QEvent, QPoint
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGraphicsView
from PyQt5.Qt import QLabel


class SubWindow(QDialog):
    def __init__(self, diagram_scene, editor, title):
        super(SubWindow, self).__init__()
        self.scalefactor = 1
        self.__prevMousePos = QPoint(0, 0)
        message = QLabel(title)
        message.setAlignment(Qt.AlignCenter)
        self.diagram_scene = diagram_scene
        self.diagram_view = QGraphicsView()
        self.diagram_view.setBackgroundBrush(QColor(30, 30, 30, 255))
        self.diagram_view.setMouseTracking(True)
        self.diagram_view.setRenderHints(QPainter.Antialiasing |
                                         QPainter.SmoothPixmapTransform)
        self.diagram_scene.setSceneRect(self.diagram_scene.itemsBoundingRect())
        self.diagram_view.centerOn(0, 0)
        self.diagram_view\
            .fitInView(self.diagram_scene.sceneRect(), Qt.KeepAspectRatio)
        self.diagram_view.viewport().installEventFilter(self)
        self.diagram_view.scale(0.4, 0.4)
        self.diagram_view.setScene(diagram_scene)
        # self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        layoutDiagram = QVBoxLayout()
        layoutDiagram.addWidget(message)
        layoutDiagram.addWidget(self.diagram_view)
        self.setLayout(layoutDiagram)
        self.showFullScreen()

    def eventFilter(self, source, event):
        if (source == self.diagram_view.viewport()):
            if (event.type() == QEvent.Wheel):
                return True
            if (event.type() == QEvent.MouseMove):
                self.mouseMouveDiagram(event)
        return False

    def wheelEvent(self, event):
        self.diagram_view.horizontalScrollBar().setEnabled(False)
        self.diagram_view.verticalScrollBar().setEnabled(False)
        adj = 0.1777
        if event.angleDelta().y() < 0:
            adj = -adj
        self.scalefactor += adj
        self.diagram_view.scale(1 + adj, 1 + adj)
        rectBounds = self.diagram_view.scene().itemsBoundingRect()
        self.diagram_view.scene().setSceneRect(rectBounds.x() - 200, rectBounds.y() - 200, rectBounds.width() + 400, rectBounds.height() + 400)

    def mouseDoubleClickEvent(self, event):
        try:
            pos = event.pos()
            itms = self.diagram_view.items(pos)
            if len(itms) != 0:
                SubWindow.mouseDoubleClickEvent(self, event)
            else:
                self.close()
        except Exception as err:
            pass

    def mousePressEvent(self, event):
        if event.button() == Qt.MidButton:
            self.__prevMousePos = event.pos()
        self.diagram_view.horizontalScrollBar().setEnabled(True)
        self.diagram_view.verticalScrollBar().setEnabled(True)

    def mouseMouveDiagram(self, event):
        if event.buttons() == Qt.MidButton:
            offset = self.__prevMousePos - event.pos()
            self.__prevMousePos = event.pos()
            self.diagram_view.horizontalScrollBar().setValue(self.diagram_view.horizontalScrollBar().value() + offset.x())
            self.diagram_view.verticalScrollBar().setValue(self.diagram_view.verticalScrollBar().value() + offset.y())
        else:
            super(SubWindow, self).mouseMoveEvent(event)

    def closeEvent(self, event):
        return QDialog.closeEvent(self, event)
