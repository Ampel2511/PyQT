from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtWidgets, QtCore, QtGui, QtSql

import mess_templ
import sys
from client import client
from db.commands import *


class MyWindow(QtWidgets.QMainWindow):
    signal_msgArea = pyqtSignal(str)
    login = ''
    contact_login = ''

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = mess_templ.Ui_Messager()
        self.ui.setupUi(self)
        client.client_main()
        self.ui.registration.triggered.connect(self.registration)
        self.ui.authorization.triggered.connect(self.authorization)
        self.ui.add_contact.triggered.connect(self.add_contact)
        self.ui.contacts.itemDoubleClicked.connect(self.change_chat)
        self.ui.pushButton.clicked.connect(self.send_text)

    def registration(self):
        login, ok = self.ui.registration_form.getText(self, 'Регистрация', 'Введите логин:')
        if ok:
            info = f'info{login[-1]}'
            client.client_registration(login, info)

    def authorization(self):
        login, ok = self.ui.authorization_form.getText(self, 'Авторизация', 'Введите логин:')
        if ok:
            self.login = login
            self.get_contacts()

    def send_text(self):
        message_text = self.ui.messageArea.toPlainText()
        self.ui.messageArea.clear()
        client.write_message(self.login, self.contact_login, message_text)

    def get_contacts(self):
        chats = client.get_contacts(self.login)
        print(chats)
        self.ui.contacts.clear()
        self.ui.chatArea.clear()
        self.ui.contacts.addItems(chats)

    def change_chat(self, item):
        self.ui.chatArea.clear()
        self.contact_login = item.text()
        try:
            history = client.get_history(self.login, item.text())
            for message in history:
                self.ui.chatArea.append(f"{message[0]}: {message[1]}")
        except:
            client.start_chat(self.login, item.text())
            self.ui.chatArea.append(f"Вы начали чат с {item.text()} \n")

    def add_contact(self):
        contact_login, ok = self.ui.contact_name.getText(self, 'Добавить контакт', 'Введите логин:')
        if ok:
            client.add_new_contact(self.login, contact_login)

    def eventFilter(self, obj, event):
        if obj is self.ui.contacts.item and self.ui.contacts.item.hasFocus():
            print(event.type())
        return super().eventFilter(obj, event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
