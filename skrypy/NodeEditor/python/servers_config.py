import os
import yaml

from . import Config
from . import set_dph
from . import get_dph

from PyQt5.QtWidgets import QComboBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, \
    QLineEdit, QTextEdit, QPushButton, QDialogButtonBox, QCheckBox
from PyQt5.QtCore import Qt


class servers_window(QDialog):
    def __init__(self, config, clust, parent=None):
        super(servers_window, self).__init__(parent)
        self.config = config
        self.clust = clust
        self.server_yml = Config().getServersList()
        self.getServersInfo()

    def getServersInfo(self):

        self.server_param = []
        dicts = {}
        
        with open(self.server_yml, 'r', encoding='utf8') as stream:
            dicts = yaml.load(stream, yaml.FullLoader)
            if not self.clust:
                self.mainWindow(dicts)
            else:
                self.getClusterParam(dicts[self.clust])
                
    def getClusterParam(self, clust):
        try:
            tmpA = clust['fd_command']
            tmpB = clust['fk_command']
            tmppd = get_dph(tmpA, tmpB).get_ushn()
        except Exception as err:
            print('error to open cluster config:', err)
            tmppd = ''
        self.server_param = [clust['host_name'],
                             clust['skrypy_server_directory'],
                             clust['server_workspace_directory'],
                             str(clust['cpu_number']),
                             bool(clust['X11_forwarding']),
                             clust['pre_execution_command'],
                             tmppd]

    def mainWindow(self, list_config):

        self.list_config = list_config

        self.setWindowTitle('Clusters configuration')
        self.setWindowFlags(self.windowFlags() &
                            Qt.WindowCloseButtonHint)
        self.setMinimumWidth(600)

        vbox = QVBoxLayout(self)

        hbox1 = QHBoxLayout()
        label = QLabel("Cluster Name :")
        self.server_name = QComboBox()
        if bool(list_config):
            self.server_name.addItems(list_config.keys())
        self.server_name.setMinimumWidth(int(self.size().width() / 4))
        self.server_name.currentIndexChanged.connect(self.actionCombobox)
        hbox1.addWidget(label)
        hbox1.addWidget(self.server_name)

        hbox2 = QHBoxLayout()
        host_name = QLabel("Host name :")
        self.area_name = QLineEdit()
        hbox2.addWidget(host_name)
        hbox2.addWidget(self.area_name)

        hbox2a = QHBoxLayout()
        labwd = QLabel("Password :")
        self.wd_field = QLineEdit()
        self.wd_field.setEchoMode(QLineEdit.Password)
        hbox2a.addWidget(labwd)
        hbox2a.addWidget(self.wd_field)

        hbox3 = QHBoxLayout()
        skrypy_dir = QLabel("Skrypy directory on this cluster :")
        self.skry_dir = QLineEdit()
        hbox3.addWidget(skrypy_dir)
        hbox3.addWidget(self.skry_dir)

        hbox4 = QHBoxLayout()
        wrk_space = QLabel("Workspace directory on this cluster :")
        self.wrkspace_dir = QLineEdit()
        hbox4.addWidget(wrk_space)
        hbox4.addWidget(self.wrkspace_dir)

        hbox5 = QHBoxLayout()
        cpu_nbr = QLabel("Mx number of cpus to use :")
        self.cpu_to_use = QLineEdit()
        hbox5.addWidget(cpu_nbr)
        hbox5.addWidget(self.cpu_to_use)

        hbox6 = QHBoxLayout()
        self.use_x11_bool = QCheckBox("X11 forwarding")
        hbox6.addWidget(self.use_x11_bool)

        vbox7 = QVBoxLayout()
        pre_exec = QLabel("Pre-execution command :")
        self.exec_cmd = QTextEdit()
        vbox7.addWidget(pre_exec)
        vbox7.addWidget(self.exec_cmd)

        buttonGo = QPushButton('Go', self)
        buttonCancel = QPushButton('Cancel', self)
        self.buttonSave = QPushButton('Save', self)
        buttonSaveAs = QPushButton('Save As ...', self)
        self.buttonDelete = QPushButton('Delete from list', self)
        hbox8 = QHBoxLayout()
        hbox8.addWidget(buttonGo)
        hbox8.addWidget(buttonCancel)
        hbox8.addWidget(self.buttonSave)
        hbox8.addWidget(buttonSaveAs)
        hbox8.addWidget(self.buttonDelete)

        if self.config == 'config':
            buttonGo.setEnabled(False)

        buttonGo.clicked.connect(self.go)
        buttonCancel.clicked.connect(self.CANCEL)
        self.buttonSave.clicked.connect(self.save)
        buttonSaveAs.clicked.connect(self.saveas)
        self.buttonDelete.clicked.connect(lambda: self.deleteServer(self.server_name.currentText()))

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox2a)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        vbox.addLayout(hbox5)
        vbox.addLayout(hbox6)
        vbox.addLayout(vbox7)
        vbox.addLayout(hbox8)

        self.setLayout(vbox)

        self.actionCombobox()

    def actionCombobox(self):
        current_server = self.server_name.currentText()

        if self.server_name.currentText() == 'template':
            self.buttonDelete.setEnabled(False)
            self.buttonSave.setEnabled(False)
        else:
            self.buttonDelete.setEnabled(True)
            self.buttonSave.setEnabled(True)

        self.area_name.setText(self.list_config[current_server]['host_name'])
        self.skry_dir.setText(self.list_config[current_server]['skrypy_server_directory'])
        self.wrkspace_dir.setText(self.list_config[current_server]['server_workspace_directory'])
        self.cpu_to_use.setText(str(self.list_config[current_server]['cpu_number']))
        self.use_x11_bool.setChecked(bool(self.list_config[current_server]['X11_forwarding']))
        self.exec_cmd.setText(self.list_config[current_server]['pre_execution_command'])
        try:
            tmpA = self.list_config[current_server]['fd_command']
            tmpB = self.list_config[current_server]['fk_command']
            tmppd = get_dph(tmpA, tmpB).get_ushn()
        except Exception as err:
            print('error to open cluster config:', err)
            tmppd = ''
        self.wd_field.setText(tmppd)

    def go(self):
        self.server_param = [self.area_name.text(),
                             self.skry_dir.text(),
                             self.wrkspace_dir.text(),
                             self.cpu_to_use.text(),
                             self.use_x11_bool.isChecked(),
                             self.exec_cmd.toPlainText(),
                             self.wd_field.text()]
        self.close()

    def CANCEL(self):
        self.server_param = []
        self.close()

    def save(self):
        tmp = set_dph(self.wd_field.text())
        tmppd = tmp.get_shn()
        tmppk = tmp.get_fk()

        self.list_config[self.server_name.currentText()] = {'host_name': self.area_name.text(),
                                                            'skrypy_server_directory': self.skry_dir.text(),
                                                            'server_workspace_directory': self.wrkspace_dir.text(),
                                                            'cpu_number': self.cpu_to_use.text(),
                                                            'X11_forwarding': self.use_x11_bool.isChecked(),
                                                            'pre_execution_command': self.exec_cmd.toPlainText(),
                                                            'fd_command': tmppd, 'fk_command': tmppk}
        with open(self.server_yml, 'w', encoding='utf8') as stream:
            yaml.dump(self.list_config, stream, default_flow_style=False)

    class _NewServerName(QDialog):

        def __init__(self, list_server, parent=None):
            super(servers_window._NewServerName, self).__init__(parent)
            self.list_server = list_server
            layout = QVBoxLayout(self)
            hlay1 = QHBoxLayout()
            layout.addLayout(hlay1)
            hlay1.addWidget(QLabel('new name:'))
            self.name_line = QLineEdit()
            hlay1.addWidget(self.name_line)
            hlay2 = QHBoxLayout()
            layout.addLayout(hlay2)
            ok = QPushButton('OK')
            hlay2.addWidget(ok)
            cancel = QPushButton('Cancel')
            hlay2.addWidget(cancel)
            ok.clicked.connect(self.ok_clicked)
            cancel.clicked.connect(self.reject)
            self.info = QLabel()
            layout.addWidget(self.info)

        def ok_clicked(self):
            if self.name_line.text() not in self.list_server:
                self.accept()
            else:
                self.info.setText("<span style=\" \
                                  font-size:10pt; \
                                  color:#cc0000;\" > error : "
                                  + self.name_line.text()
                                  + " already exists ! </span>")
                return

    def saveas(self):
        dial = self._NewServerName(self.list_config.keys())
        # dial.name_line.setText(dial.name_line.text())
        res = dial.exec_()
        if res:
            tmp = set_dph(self.wd_field.text())
            tmppd = tmp.get_shn()
            tmppk = tmp.get_fk()
            self.list_config[dial.name_line.text()] = {'host_name': self.area_name.text(),
                                                       'skrypy_server_directory': self.skry_dir.text(),
                                                       'server_workspace_directory': self.wrkspace_dir.text(),
                                                       'cpu_number': self.cpu_to_use.text(),
                                                       'X11_forwarding': self.use_x11_bool.isChecked(),
                                                       'pre_execution_command': self.exec_cmd.toPlainText(),
                                                       'fd_command': tmppd, 'fk_command': tmppk}
            with open(self.server_yml, 'w', encoding='utf8') as stream:
                yaml.dump(self.list_config, stream, default_flow_style=False)

            self.server_name.addItem(dial.name_line.text())
            # self.server_name.update()
            index = self.server_name.findText(dial.name_line.text(), Qt.MatchFixedString)
            self.server_name.setCurrentIndex(index)

    class _ConfirmationDialog(QDialog):

        def __init__(self, cur_serv, parent=None):
            super().__init__(parent)

            self.setWindowTitle("Confirmation")

            QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

            self.buttonBox = QDialogButtonBox(QBtn)
            self.buttonBox.accepted.connect(self.accept)
            self.buttonBox.rejected.connect(self.reject)

            layout = QVBoxLayout()
            message = QLabel("delete {}?".format(cur_serv))
            layout.addWidget(message)
            layout.addWidget(self.buttonBox)
            self.setLayout(layout)

    def deleteServer(self, currentServer):
        dial = self._ConfirmationDialog(currentServer)
        res = dial.exec_()
        if res:
            del self.list_config[currentServer]
            with open(self.server_yml, 'w', encoding='utf8') as stream:
                yaml.dump(self.list_config, stream, default_flow_style=False)
            index = self.server_name.findText(currentServer, Qt.MatchFixedString)
            self.server_name.removeItem(index)

    def get_params(self):
        return self.server_param


class getInfoHn():
    def __init__(self, wdtoHn):
        super(getInfoHn, self).__init__(parent)
