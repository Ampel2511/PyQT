import sys, socket
import time
import logging
import log.client_log_config
import log.decorator_log_config
from utils import Utils, logs, SocketError, TCPError
import threading
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
    def write_message(self, socket, semaphore_get, semaphore_send):
        while True:
            try:
                semaphore_send.acquire()
                message_text = input("Введите сообщение: ")
                message = {
                    "action": "message",
                    "message_text": message_text,
                }
                client_logger.info('Отправка сообщения от клиенту...')
                self.send_message(socket, message)
                semaphore_get.release()
            except:
                client_logger.error('Error')

    @logs
    def get_message_from_server(self, socket, semaphore_get, semaphore_send):
        while True:
            try:
                semaphore_get.acquire()
                client_logger.info('Получение сообщения от клиента...')
                message = self.get_message(socket)
                client_logger.info('Обработка сообщения от клиента...')
                print(self.handle_message(message))
                semaphore_send.release()
            except:
                client_logger.info('Error...')

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
        send = threading.Thread(target=self.write_message, args=(transport, self.semaphore_get, self.semaphore_send,))
        send.start()
        get = threading.Thread(target=self.get_message_from_server,
                               args=(transport, self.semaphore_get, self.semaphore_send,))
        get.start()


client = Client()


def main():
    client.client_main()


if __name__ == '__main__':
    main()
