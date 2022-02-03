import json
import logging
import inspect
import threading

client_logger = logging.getLogger('client')
server_logger = logging.getLogger('server')
decorator_logger = logging.getLogger('decorator')


class SocketError(Exception):
    def __init__(self, text):
        self.text = text


class TCPError(Exception):
    def __init__(self, text):
        self.text = text



def logs(func):
    def save_logs(*args, **kwargs):
        result = func(*args, **kwargs)
        decorator_logger.info(f'Функция {func.__name__} была вызвана из функции {inspect.stack()[1][3]}')
        return result

    return save_logs


class Utils:
    semaphore_get = threading.Semaphore(0)
    semaphore_send = threading.Semaphore(1)

    @logs
    def send_message(self, opened_socket, message):
        json_message = json.dumps(message)
        response = json_message.encode("utf-8")
        opened_socket.send(response)

    @logs
    def get_message(self, opened_socket):
        response = opened_socket.recv(1024)
        if isinstance(response, bytes):
            json_response = response.decode("utf-8")
            response_dict = json.loads(json_response)
            if isinstance(response_dict, dict):
                return response_dict
            raise ValueError
        raise ValueError

    @logs
    def handle_message(self, message):
        if "response" in message:
            client_logger.info("Сообщение от сервера успешно получено!")
            if message["response"] == 200:
                return '200 : OK'
            client_logger.error('Ошибка при получении сообщения от сервера.')
            return f'400 : {message["error"]}'
        elif "action" in message:
            if message["action"] == "message":
                server_logger.info(f'Сообщение: {message["message_text"]} от клиента успешно получено!')
                return message["message_text"]
            elif message["action"] == "presence":
                server_logger.info(f'Сообщение "presence" от клиента успешно получено!')
                return {"response": 200}
        server_logger.error(f'Ошибка при получении сообщения от клиента')
        return {
            "response": 400,
            "error": 'Bad Request'
        }
