import random
import sqlalchemy as sq
from Constant import DNS
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()
engine = sq.create_engine(DNS)
Session = sessionmaker(bind=engine)


class Bot_guests(Base):
    """Класс (от Base) таблица Bot_guests
        колонки (id, guest_vk_id)

    """
    __tablename__ = "bot_guests"
    id = sq.Column(sq.Integer, primary_key=True)
    guest_vk_id = sq.Column(sq.Integer, nullable=False, unique=True)


class VK_users(Base):
    """Класс (от Base) таблица VK_users
        колонки (id, vk_id)

    """
    __tablename__ = "vk_users"
    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False)


class Guest_vk_users(Base):
    """Класс (от Base) таблица связи уникальных ключей
    Guest_vk_users
    колонки (id, guest_id, vk_user_id, like)

    """
    __tablename__ = "guest_vk_users"
    id = sq.Column(sq.Integer, primary_key=True)
    guest_id = sq.Column(
        sq.Integer, sq.ForeignKey("bot_guests.id"), nullable=False
    )
    vk_user_id = sq.Column(
        sq.Integer, sq.ForeignKey("vk_users.id"), nullable=False
    )
    like = sq.Column(sq.Boolean)
    # blacklist = sq.Column(sq.Boolean)

    bot_guests = relationship(Bot_guests, backref="guest_vk_users")
    vk_users = relationship(VK_users, backref="guest_vk_users")


def create_tables():
    """Функция создания таблиц

    :return: None
    """
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


class Metod:
    """Класс Metod, Описывает все методы работы
            гостя с базой данных

    """

    def add_quests(self, guest):
        """проверяет наличие гостя в базе
        если отсутствует то добавляет и возвращает False,
        если есть то возвращает True

        :param guest: guest_id (гость)
        :return: False/True
        """
        session = Session()
        goests = session.query(Bot_guests.guest_vk_id).all()
        list_goests = [list(el) for el in goests]
        if [guest] not in list_goests:
            add_gu = Bot_guests(guest_vk_id=guest)
            session.add(add_gu)
            session.commit()
            result = False
        else:
            result = True
        session.close()
        return result

    def get_qoest_id(self, qu_id):
        """Всаомогательная функция
        возвращает id ключ гостя

        :param qu_id: guest_id (гость)
        :return: guest_id.first()[0],  id ключ
        """
        session = Session()
        guest_id = (session.query(Bot_guests.id).
                    filter(Bot_guests.guest_vk_id == qu_id))
        session.close()
        return guest_id.first()[0]

    def add_users(self, qu_id, DATA_US):
        """Заполняет таблицу юзеров , закрепляя за гостем

        :param qu_id: id гостя
        :param DATA_US:  список юзеров
        :return: None
        """
        session = Session()
        for user in DATA_US:
            session.add(VK_users(vk_id=user))
            qoest_id = self.get_qoest_id(qu_id)
            vk_user_id = session.query(VK_users.id).\
                filter(VK_users.vk_id == user).first()[0]
            session.add(Guest_vk_users(
                guest_id=qoest_id, vk_user_id=vk_user_id
            ))
            session.commit()
        session.close()

    def get_user_random(self, qu_id):
        """Возвращает рандомно одного юзера из таблицы VK_users
        закрепленного за гостем

        :param qu_id: id гостя
        :return: r_users_vk , юзер
        """
        session = Session()
        guest_id = self.get_qoest_id(qu_id)
        users_id = (session.query(Guest_vk_users.vk_user_id).
                    filter(Guest_vk_users.guest_id == guest_id).all())
        random_user_id = random.choice(users_id)
        r_users_vk = session.query(VK_users.vk_id).\
            filter(VK_users.id == random_user_id[0]).first()[0]
        session.close()
        return r_users_vk

    def correct_like(self, qu_id, user):
        """ставит пометку в столбце like для юзера

        :param qu_id: id гостя
        :param user: id юзера
        :return: None
        """
        session = Session()
        result = (session.query(Guest_vk_users.id).
                  join(Bot_guests).join(VK_users))
        result = result.filter(
            Bot_guests.guest_vk_id == qu_id,
            VK_users.vk_id == user
        ).first()[0]
        correct = session.get(Guest_vk_users, result)
        correct.like = True
        session.commit()
        session.close()

    def get_users_likes(self, qu_id):
        """Возвращает список юзеров (избранное)
        с пометкой like закрепленных за гостем

        :param qu_id: id гостя
        :return: list_users, список
        """
        session = Session()
        list_users = []
        result = (session.query(VK_users.vk_id).
                  join(Guest_vk_users).join(Bot_guests))
        result = result.filter(
            Bot_guests.guest_vk_id == qu_id,
            Guest_vk_users.like == True
        ).all()
        for user in result:
            list_users += [user[0]]
        return list_users
        session.close()

    def delete_user(self, qu_id, user_id):
        session = Session()
        result = session.query(Guest_vk_users.vk_user_id) \
            .join(VK_users, VK_users.id == Guest_vk_users.vk_user_id) \
            .join(Bot_guests, Bot_guests.id == Guest_vk_users.guest_id) \
            .filter(VK_users.vk_id == user_id,
                    Bot_guests.guest_vk_id == qu_id).first()[0]
        session.query(Guest_vk_users) \
            .filter(Guest_vk_users.vk_user_id == result).delete()
        session.query(VK_users) \
            .filter(VK_users.id == result).delete()
        session.commit()
        session.close()

    def reset_base(self, qu_id):
        """Удаляет данные гостя и закрепленных за ним
        юзеров со всех таблиц

        :param qu_id:
        :return:
        """
        session = Session()
        result = session.query(Guest_vk_users.vk_user_id) \
            .join(Bot_guests, Bot_guests.id == Guest_vk_users.guest_id) \
            .join(VK_users, VK_users.id == Guest_vk_users.vk_user_id) \
            .filter(Bot_guests.guest_vk_id == qu_id).all()
        for user in result:
            session.query(Guest_vk_users) \
                .filter(Guest_vk_users.vk_user_id == user[0]).delete()
            session.query(VK_users) \
                .filter(VK_users.id == user[0]).delete()
        session.query(Bot_guests) \
            .filter(Bot_guests.guest_vk_id == qu_id).delete()
        session.commit()
        session.close()

    # def decor_session(some_function):  # декоратор открытий сессий
    #     def new_f(*args, **kwargs):
    #         session = Session()
    #         result = some_function(*args, **kwargs)
    #         session.close()
    #         return result
    #     return new_f()


if __name__ == '__main__':
    create_tables()
    bd = Metod()
    # bd.add_quests(555)
    # bd.get_qoest_id(7777)
    # # print(bd.add_quests(88))
    # users = [345345,4553,777,444,5555]
    # bd.add_users(555,users)
    # user_vk = 711878878
    # print(bd.get_user_random(user_vk))
    # bd.correct_like(555, 444)
    # bd.reset_base(7777)
    # bd.get_users_likes(7777)
    bd.reset_base(711878878)
    # @decor_session
