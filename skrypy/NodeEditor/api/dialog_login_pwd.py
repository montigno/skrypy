import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QFormLayout, QLabel, QLineEdit, QPushButton,
                             QMessageBox, QDialogButtonBox, QDesktopWidget)

class LoginPasswd(QMainWindow):
    def __init__(self, titl, parent=None):
        super(LoginPasswd, self).__init__(parent)
        self.start(titl)
        
    def start(self, titl):
       
        # Set the window properties (title and initial size)
        self.setWindowTitle(titl)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.setGeometry(100, 100, 400, 150)  # (x, y, width, height)
        self.move(qtRectangle.topLeft())

        # Create a central widget for the main window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a QFormLayout to arrange the widgets
        form_layout = QFormLayout()

        # Create QLabel and QLineEdit widgets for username
        username_label = QLabel("Username:")
        self.username_field = QLineEdit()

        # Create QLabel and QLineEdit widgets for password
        password_label = QLabel("Password:")
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._control)
        buttons.rejected.connect(self._reject)

        # Add widgets to the form layout
        form_layout.addRow(username_label, self.username_field)
        form_layout.addRow(password_label, self.password_field)
        form_layout.addWidget(buttons)

        # Set the layout for the central widget
        central_widget.setLayout(form_layout)
        
    def _control(self):
        print(self.username_field.text(), self.password_field.text())
        self.close()

    def _reject(self):
        print(None, None)
        self.close()

    
if __name__=="__main__":
    app = QApplication(sys.argv)
    myprogram = LoginPasswd(sys.argv[1])
    myprogram.show()
    sys.exit(app.exec_())
