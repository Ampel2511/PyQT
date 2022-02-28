import hashlib
import hmac
import sys, socket
import time
import logging
from threading import Thread

import log.client_log_config
import log.decorator_log_config
from db.commands import add_user, get_chat_id, get_user_id
from utils import Utils, logs

client_logger = logging.getLogger('client')


class Client(Utils):
    transport = None
    ip = None

    def client_authenticate(self, connection):
        message = connection.recv(32)
        hash = hmac.new(self.secret_key, message, hashlib.sha1)
        digest = hash.digest()
        connection.send(digest)

    @logs
    def client_registration(self, login, info, pswd):
        try:
            add_user(login, info, pswd)
            return True
        except:
            client_logger.error('Error client_registration')

    @logs
    def create_presence_message(self, account_name, msg_time=time.time()):
        client_logger.info('Создание сообщения для отправки на сервер...')
        message = {
            "action": "presence",
            "time": msg_time,
            "user": {
                "account_name": account_name
            }
        }

        return message

    @logs
    def write_message(self, login, contact_login, message_text):
        try:
            from_user_id = get_user_id(login)
            to_user_id = get_user_id(contact_login)
            chat_id = get_chat_id(from_user_id, to_user_id)
            message = {
                "action": "message",
                "chat_id": chat_id,
                "from_user_id": from_user_id,
                "to_user_id": to_user_id,
                "message_text": message_text,
            }
            client_logger.info('Отправка сообщения от клиенту...')
            self.send_message(self.transport, message)
            return self.get_message_from_server()
        except:
            client_logger.error('Error write_message')

    @logs
    def get_message_from_server(self):
        while True:
            try:
                client_logger.info('Получение ответа от сервера...')
                message = self.get_message(self.transport)
                return self.handle_message(message)
            except:
                client_logger.info('Error get_message_from_server')

    @logs
    def create_thread(self):
        t = Thread(target=self.get_message_from_server, args=(self,))
        t.daemon = True
        t.start()

    @logs
    def get_contacts(self, login):
        try:
            message = {
                "action": "get_contacts",
                "time": time.time(),
                "login": login
            }
            self.send_message(self.transport, message)
            return self.get_message_from_server()
        #     return [get_user_login(contact.client_id) for contact in get_contacts(get_user_id(login))]
        except:
            client_logger.error('Error get_contacts')

    @logs
    def add_new_contact(self, login, contact_login):
        try:
            message = {
                "action": "add_contact",
                "time": time.time(),
                "login": login,
                "contact_login": contact_login,
            }
            self.send_message(self.transport, message)
            return self.get_message_from_server()
        except:
            client_logger.error('Error add_new_contact')

    @logs
    def delete_contact(self, login):
        try:
            contact_login = input('Введите логин пользователя, которого хотите удалить из контактов: ')
            message = {
                "action": "del_contact",
                "time": time.time(),
                "login": login,
                "contact_login": contact_login,
            }
            self.send_message(self.transport, message)
        except:
            client_logger.error('Error delete_contact')

    @logs
    def get_all_users(self):
        try:
            message = {
                "action": "get_all_users"
            }
            self.send_message(self.transport, message)
        except:
            client_logger.error('Error get_all_users')

    @logs
    def start_chat(self, login, contact_login):
        try:
            message = {
                "action": "start_chat",
                'login': login,
                'contact_login': contact_login
            }
            self.send_message(self.transport, message)
            return self.get_message_from_server()
        except:
            client_logger.error('Error start_chat')

    @logs
    def get_history(self, login, contact_login):
        try:
            # return [[get_user_login(message.from_user_id), message.message_text] for message in
            #         get_users_messages(get_user_id(login), get_user_id(contact_login))]
            message = {
                "action": "get_history",
                'login': login,
                'contact_login': contact_login
            }
            self.send_message(self.transport, message)
            return self.get_message_from_server()
        except:
            client_logger.error('Error get_history')

    @logs
    def control_panel(self, socket):
        login = ''
        n = int(input(f"Выберите команду, введя нужный номер: \n"
                      f"1 - Зарегистрироваться \n"
                      f"2 - Авторизоваться \n"))
        if n == 1:
            login = self.client_registration()
        if n == 2:
            login = input("Введите свой логин: ")
        while True:
            i = int(input(f"Выберите команду, введя нужный номер: \n"
                          f"3 - Получить список своих контактов \n"
                          f"4 - Добавить пользователя в свой список контактов \n"
                          f"5 - Удалить пользователя из своего списка контактов \n"
                          f"6 - Просмотреть всех пользователей \n"
                          f"7 - Добавить еще одного пользователя \n"
                          f"8 - Создать новый чат с пользователем \n"
                          f"9 - Отправить сообщение пользователю \n"
                          f"10 - Посмотреть историю сообщения с пользователем \n"))
            if i == 3:
                self.get_contacts(socket, login)
            if i == 4:
                self.add_new_contact(socket, login)
            if i == 5:
                self.delete_contact(socket, login)
            if i == 6:
                self.get_all_users(socket)
            if i == 7:
                self.client_registration()
            if i == 8:
                self.start_chat(socket, login)
            if i == 9:
                self.write_message(socket, login)
            if i == 10:
                self.get_history(socket, login)

    @logs
    def client_main(self):
        try:
            client_logger.info('Получение адреса и порта из параметров командной строки...')
            server_address = sys.argv[1]
            server_port = int(sys.argv[2])
            if not 65535 >= server_port >= 1024:
                raise ValueError
        except IndexError:
            client_logger.info('Установки параметров соединения по умолчанию...')
            server_address = '127.0.0.1'
            server_port = 7777
        except ValueError:
            client_logger.error('Неверный порт. Порт должен быть указан в пределах от 1024 до 65535')
            sys.exit(1)
        client_logger.info('Создание сокета и установка соединения...')
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transport.connect((server_address, server_port))
        self.client_authenticate(self.transport)