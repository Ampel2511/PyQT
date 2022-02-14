import sys, socket
import time
import logging
import log.client_log_config
import log.decorator_log_config
from db.commands import get_all_users, add_user, get_chat_id, get_user_id
from utils import Utils, logs, SocketError, TCPError
import dis

client_logger = logging.getLogger('client')


class ClientMeta(type):
    def __init__(self, clsname, base, clsdict):
        try:
            code_info = dis.code_info(clsdict.get('client_main'))
            if 'accept' and 'listen' in code_info:
                raise SocketError('accept и listen не должны быть в клиенте')
            if not 'AF_INET' and not 'SOCK_STREAM' in code_info:
                raise TCPError('TCP не используется')
            for k, v in clsdict.items():
                if type(v) == socket.socket:
                    raise AttributeError("В атрибутах не должно быть сокета")
        except SocketError as se:
            print(se)
        except TCPError as te:
            print(te)
        except AttributeError as ae:
            print(ae)
        except:
            pass


class ClientVerifier(metaclass=ClientMeta):
    pass


class Client(Utils, ClientVerifier):
    @logs
    def client_registration(self):
        try:
            login = input("Введите ваш Логин: ")
            info = input("Введите информацию о себе: ")
            add_user(login, info)
            return login
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
    def write_message(self, socket, login):
        try:
            contact_login = input('Введите логин пользователя, которому хотите отправить сообщение: ')
            message_text = input("Введите сообщение: ")
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
            self.send_message(socket, message)
        except:
            client_logger.error('Error write_message')

    @logs
    def get_message_from_server(self, socket):
        while True:
            try:
                client_logger.info('Получение сообщения от клиента...')
                message = self.get_message(socket)
                client_logger.info('Обработка сообщения от клиента...')
                print(self.handle_message(message))
            except:
                client_logger.info('Error get_message_from_server')

    @logs
    def get_contacts(self, socket, login):
        try:
            message = {
                "action": "get_contacts",
                "time": time.time(),
                "login": login
            }
            self.send_message(socket, message)
        except:
            client_logger.error('Error get_contacts')

    @logs
    def add_new_contact(self, socket, login):
        try:
            contact_login = input('Введите логин пользователя, которого хотите добавить в контакты: ')
            message = {
                "action": "add_contact",
                "time": time.time(),
                "login": login,
                "contact_login": contact_login,
            }
            self.send_message(socket, message)
        except:
            client_logger.error('Error add_new_contact')

    @logs
    def delete_contact(self, socket, login):
        try:
            contact_login = input('Введите логин пользователя, которого хотите удалить из контактов: ')
            message = {
                "action": "del_contact",
                "time": time.time(),
                "login": login,
                "contact_login": contact_login,
            }
            self.send_message(socket, message)
        except:
            client_logger.error('Error delete_contact')

    @logs
    def get_all_users(self, socket):
        try:
            message = {
                "action": "get_all_users"
            }
            self.send_message(socket, message)
        except:
            client_logger.error('Error get_all_users')

    @logs
    def start_chat(self, socket, login):
        try:
            contact_login = input('Введите логин пользователя с которым хотите начать чат: ')
            message = {
                "action": "start_chat",
                'login': login,
                'contact_login': contact_login
            }
            self.send_message(socket, message)
        except:
            client_logger.error('Error start_chat')

    @logs
    def get_history(self, socket, login):
        try:
            contact_login = input('Введите логин пользователя: ')
            message = {
                "action": "get_history",
                'login': login,
                'contact_login': contact_login
            }
            self.send_message(socket, message)
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
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        self.control_panel(transport)


client = Client()


def main():
    client.client_main()


if __name__ == '__main__':
    main()
