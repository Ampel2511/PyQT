import binascii
import time
import hashlib
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5 import QtWidgets

import mess_templ
import sys

from client import Client


def login_required(func):
    def check_login(obj):
        if obj.login:
            result = func(obj)
            return result
        else:
            obj.registration()

    return check_login


class MyThread(QThread):
    def __init__(self, mainwindow, parent=None):
        super(MyThread, self).__init__(parent)
        self.mainwindow = mainwindow
        self.history = None
        self.count = 0

    def run(self):
        while True:
            if self.mainwindow.active:
                self.history = self.mainwindow.client.get_history(self.mainwindow.login, self.mainwindow.contact_login)
                while self.mainwindow.active:
                    for message in self.history:
                        if self.mainwindow.last_message < message[0]:
                            self.mainwindow.ui.chatArea.append(f"{message[1]}: {message[2]}")
                            self.mainwindow.last_message = message[0]
            else:
                self.quit()


class MyWindow(QtWidgets.QMainWindow):
    signal_msgArea = pyqtSignal(str)

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = mess_templ.Ui_Messager()
        self.ui.setupUi(self)

        self.login = None
        self.contact_login = None
        self.get_messages = None
        self.active = False
        self.last_message = None
        self.get_messages = MyThread(mainwindow=self)
        self.client = Client()
        self.client.client_main()

        self.ui.registration.triggered.connect(self.registration)
        self.ui.authorization.triggered.connect(self.authorization)
        self.ui.add_contact.triggered.connect(self.add_contact)
        self.ui.contacts.itemDoubleClicked.connect(self.change_chat)
        self.ui.pushButton.clicked.connect(self.send_text)

    def registration(self):
        login, ok = self.ui.registration_form.getText(self, 'Регистрация', 'Введите логин:')
        if ok:
            info = f'info{login[-1]}'
            psw = bytes(info, encoding='utf8')
            salt = bytes('hflsdjf', encoding='utf8')
            dk = hashlib.pbkdf2_hmac('sha256', psw, salt, 100000)
            my_hash = binascii.hexlify(dk)
            self.client.client_registration(login, info, my_hash)

    def authorization(self):
        login, ok = self.ui.authorization_form.getText(self, 'Авторизация', 'Введите логин:')
        if ok:
            self.login = login
            self.get_contacts()

    @login_required
    def send_text(self):
        if self.active:
            self.active = False
            time.sleep(0.5)
            message_text = self.ui.messageArea.toPlainText()
            self.ui.messageArea.clear()
            self.client.write_message(self.login, self.contact_login, message_text)
        self.active = True

    def get_contacts(self):
        chats = self.client.get_contacts(self.login)
        self.ui.contacts.clear()
        self.ui.chatArea.clear()
        self.ui.contacts.addItems(chats)

    def start_thread(self):
        try:
            self.active = True
            self.get_messages.start()
        except:
            return False

    def change_chat(self, item):
        self.active = False
        time.sleep(0.5)
        self.last_message = 0
        self.ui.chatArea.clear()
        self.contact_login = item.text()
        if len(self.client.get_history(self.login, self.contact_login)) > 0:
            self.start_thread()
        else:
            self.client.start_chat(self.login, item.text())
            self.ui.chatArea.append(f"Вы начали чат с {item.text()} \n")
            self.start_thread()

    @login_required
    def add_contact(self):
        self.active = False
        time.sleep(0.5)
        contact_login, ok = self.ui.contact_name.getText(self, 'Добавить контакт', 'Введите логин:')
        if ok:
            self.client.add_new_contact(self.login, contact_login)
            self.get_contacts()

    def eventFilter(self, obj, event):
        if obj is self.ui.contacts.item and self.ui.contacts.item.hasFocus():
            print(event.type())
        return super().eventFilter(obj, event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
