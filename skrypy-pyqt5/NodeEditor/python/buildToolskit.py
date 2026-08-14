from PyQt5.Qt import pyqtSignal, QFrame, QSizePolicy, Qt
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QGridLayout, QPushButton,
                             QWidget, QLabel, QVBoxLayout)


class BuildLibrary(QWidget):

    menu_choosen = pyqtSignal(str)

    def __init__(self, listModules, parent=None):
        super(BuildLibrary, self).__init__(parent)
        ncol = 3
        self.setMinimumWidth(120 + ncol * 40)
        self.setMaximumWidth(120 + ncol * 40)
        # self.setMaximumHeight(100)

        # row_number = int(len(listModules) / ncol) + (len(listModules) % ncol > 0)
        row_number = (len(listModules) + ncol - 1) // ncol
        # Create a QGridLayout instance
        glayout = QGridLayout()
        Separator = QFrame()
        Separator.setFrameShape(QFrame.HLine)
        Separator.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        # Separator.setLineWidth(1)
        # Separator.setFrameShadow(QFrame.Sunken)

        items = list(listModules.items())

        for index, (lab, ico) in enumerate(items):
            row = index // ncol
            col = index % ncol

            vbox = QVBoxLayout()

            label = QLabel(lab.replace('_', '\n'))
            label.setAlignment(Qt.AlignCenter)

            button = QPushButton()
            button.setObjectName(lab)
            button.setIcon(QIcon(ico))
            button.setIconSize(QSize(40, 40))
            button.setFixedSize(70, 70)
            button.clicked.connect(self.buttonClik)

            vbox.addWidget(button)
            vbox.addWidget(label)

            glayout.addLayout(vbox, row, col)
        self.setFixedHeight(row_number * 100)
        self.setLayout(glayout)

    def buttonClik(self):
        self.menu_choosen.emit(self.sender().objectName())
