from db.db_server import session, Users, Contacts, History, Chats


def get_contacts(user_id):
    return session.query(Contacts).filter_by(user_id=user_id).all()


def add_user(login, info):
    try:
        old_user = get_user_id(login)
        if old_user:
            new_login = input(f'Пользователь с логином {login} уже существует, введите другой логин: ')
            add_user(new_login, info)
        print(f'добавление пользователя {login, info}')
        session.add(Users(login, info))
        session.commit()
        return True
    except:
        print('Возникла ошибка при добавлении нового пользователя')
        return False


def add_contact(user_id, client_id):
    try:
        session.add(Contacts(user_id, client_id))
        session.commit()
        return True
    except:
        print('Возникла ошибка при добавлении нового контакта')
        return False


def delete_contact(user_id, client_id):
    try:
        session.query(Contacts).filter_by(user_id=user_id, client_id=client_id).delete()
        session.commit()
        return True
    except:
        print('Возникла ошибка при удалении контакта')
        return False


def get_user_id(login):
    try:
        return session.query(Users).filter_by(login=login).first().id
    except:
        print(f'Пользователь с логином {login} не зарегистрирован')
        return False


def get_user_login(user_id):
    try:
        return session.query(Users).filter_by(id=user_id).first().login
    except:
        print(f'Пользователь с id {user_id} не зарегистрирован')
        return False


def get_all_users():
    try:
        print([[user.login, user.id] for user in session.query(Users).all()])
    except:
        return False


def create_chat(user_id, contact_id):
    try:
        session.add(Chats(user_id, contact_id))
        session.commit()
        return True
    except:
        print('Возникла ошибка при создании нового чата')
        return False


def get_chat_id(user_id, contact_id):
    return session.query(Chats) \
        .filter(Chats.from_user_id.in_([user_id, contact_id])) \
        .filter(Chats.to_user_id.in_([user_id, contact_id])) \
        .first().id


def get_users_messages(user_id, contact_id):
    return session.query(History).filter_by(chat_id=get_chat_id(user_id, contact_id)).all()


def save_message(chat_id, from_user_id, to_user_id, message_text):
    try:
        session.add(History(chat_id, from_user_id, to_user_id, message_text))
        session.commit()
        return True
    except:
        print('Возникла ошибка при сохранении сообщения')
        return False
