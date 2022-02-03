import sys, socket
import time
import logging
from utils import Utils, logs
from client import ClientVerifier

client_logger = logging.getLogger('client')


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
    def write_message(self, socket):
        while True:
            try:
                message_text = input("Введите сообщение: ")
                message = {
                    "action": "message",
                    "message_text": message_text,
                }
                client_logger.info('Отправка сообщения от клиента...')
                self.send_message(socket, message)
            except:
                client_logger.error('Error')

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
        self.write_message(transport)


client = Client()


def main():
    client.client_main()


if __name__ == '__main__':
    main()
