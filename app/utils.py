import json
import logging
import inspect

from db.commands import get_contacts, get_user_id, add_contact, delete_contact, add_user, get_all_users, get_user_login, \
    create_chat, save_message, get_users_messages

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
    def give_contacts(self, login):
        # print([get_user_login(contact.client_id) for contact in get_contacts(get_user_id(login))])
        return {
            "response": 202,
            "alert": [get_user_login(contact.user_id).login for contact in get_contacts(get_user_id(login).id)]
        }

    @logs
    def add_new_user(self, user):
        return add_user(user['login'], user['info'])

    @logs
    def get_all_users(self):
        return get_all_users()

    @logs
    def add_contact(self, login, contact_login):
        user_id = get_user_id(login)
        client_id = get_user_id(contact_login)
        return add_contact(user_id, client_id)

    @logs
    def start_chat(self, login, contact_login):
        user_id = get_user_id(login)
        contact_id = get_user_id(contact_login)
        return create_chat(user_id, contact_id)

    @logs
    def del_contact(self, login, contact_login):
        user_id = get_user_id(login)
        client_id = get_user_id(contact_login)
        delete_contact(user_id, client_id)

    @logs
    def save_messages(self, chat_id, from_user_id, to_user_id, message):
        save_message(chat_id, from_user_id, to_user_id, message)

    @logs
    def get_history(self, login, contact_login):
        user_id = get_user_id(login)
        contact_id = get_user_id(contact_login)
        print([message.message_text for message in get_users_messages(user_id, contact_id)])

    @logs
    def handle_message(self, message):
        if "response" in message:
            client_logger.info("Сообщение от сервера успешно получено!")
            if message["response"] == 200:
                return '200 : OK'
            client_logger.error('Ошибка при получении сообщения от сервера.')
            return f'400 : {message["error"]}'
        elif "action" in message:
            if message["action"] == "presence":
                server_logger.info(f'Сообщение "presence" от клиента успешно получено!')
                self.save_messages()
                return {"response": 200}
            elif message["action"] == "message":
                try:
                    self.save_messages(message["chat_id"], message["from_user_id"],
                                       message["to_user_id"], message["message_text"])
                    server_logger.info(f'Сообщение успешно получено!')
                    return message["message_text"]
                except:
                    server_logger.error(f'Ошибка при получении сообщения')
            elif message["action"] == "get_contacts":
                try:
                    return self.give_contacts(message['login'])
                except:
                    server_logger.error(f'Ошибка при получении контактов')
            elif message["action"] == "add_contact":
                try:
                    self.add_contact(message['login'], message['contact_login'])
                    return {"response": 200}
                except:
                    server_logger.error(f'Ошибка при добавлении контакта')
            elif message["action"] == "del_contact":
                try:
                    self.del_contact(message['login'], message['contact_login'])
                    return {"response": 200}
                except:
                    server_logger.error(f'Ошибка при удалении контакта')
            elif message["action"] == "client_registration":
                try:
                    self.add_new_user(message['user'])
                    return {"response": 200}
                except:
                    server_logger.error(f'Ошибка при регистрации клиента')
            elif message["action"] == "get_all_users":
                try:
                    self.get_all_users()
                    return {"response": 200}
                except:
                    server_logger.error(f'Ошибка при просмотре пользователей')
            elif message["action"] == "start_chat":
                try:
                    self.start_chat(message['login'], message['contact_login'])
                    return {"response": 200}
                except:
                    server_logger.error(f'Ошибка при создании чата')
            elif message["action"] == "get_history":
                try:
                    self.get_history(message['login'], message['contact_login'])
                    return {"response": 200}
                except:
                    server_logger.error(f'Ошибка при получении истории сообщений')
        return {
            "response": 400,
            "error": 'Bad Request'
        }
