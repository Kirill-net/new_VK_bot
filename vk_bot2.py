import random
from random import randrange
from Constant import TOKEN_GR, TOKEN_USER
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from ap_vk_users import VK_Users
from base import Metod, create_tables

class VK_BOT:
    
    def write_msg(self, user_id, message):
        vk.method('messages.send',{'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })

    def new_message(self, event):
        message = event.text
        # '''id, first_name, last_name, (city-id), sex, bdate'''
        qoest_inf = ap.get_user_info(event.user_id)
        goest_in_bd = bd.add_quests(qoest_inf[0])
        if goest_in_bd == False:  # если гостя нет формируем базу юзеров
            vk_bot.write_msg(qoest_inf[0], (f'Привет, {qoest_inf[1]}!\
                    Формируется база подходящих для вас кандидатов....ждите'))
            # rev_sex = revers_sex(qoest_inf[4])
            # DATA_US = ap.data_users(qoest_inf[3], rev_sex, qoest_inf[5])
            DATA_US = ap.data_users(2, 1, 1996) # цифры заведены для теста
            bd.add_users(qoest_inf[0], DATA_US)
            return 'Готово. Набери "next" или "следующий" для начала просмотра'

        if message.upper() == 'NEXT' or message.upper() == 'СЛЕДУЮЩИЙ':
            vk_bot.write_msg(qoest_inf[0], 'Идет поиск, ждите')
            photos = 'NONE'
            while photos == 'NONE':  # проверяет наличие фото у кандидата
                us = bd.get_user_random(qoest_inf[0])  #получаем рандомно юзера гостя
                us_info = ap.get_user_info(us)  #получаем данные юзера
                photos = ap.photos_user(us_info[0])  # если вернет NONE, хорошо бы заодно удалить
            us_url = f'https://vk.com/id{us}'
            vk_bot.write_msg(
                qoest_inf[0], f'{us_info[1]} {us_info[2]}\n'
                f'{us_url}\n{photos[0]}\n{photos[1]}\n{photos[2]}\n\nДобавить в избранное?'
                )
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        responce = event.text
                        if responce.upper() == "ДА":
                            bd.correct_like(qoest_inf[0], us_info[0])
                            result = 'ДОБАВИЛИ\nНабери "next" или "следующий" для следующего просмотра'
                            break
                        else:
                            result = 'Набери "next" или "следующий" для следующего просмотра'
                            break
            return result


        elif message.upper() == 'HELP':
            return 'Доступны команды:\nHELP/next/следующий/избранное/СБРОС'


        # elif message.upper() == 'СБРОС':
        #     vk_bot.write_msg(qoest_inf[0], 'Сейчас произойдет сброс Базы Данных\n'
        #                                    'Если уверены, наберите "Да"')
        #     for event in longpoll.listen():
        #         if event.type == VkEventType.MESSAGE_NEW:
        #             if event.to_me:
        #                 responce = event.text
        #                 if responce.upper() == "ДА":
        #                     bd.reset_base(qoest_inf[0])
        #                     result = 'ВАША БAЗА СБРОШЕНА\n(для создания новой базы отправьте любое сообщение)'
        #                     break
        #                 else:
        #                     result = 'Набери "next" или "следующий" для следующего просмотра'
        #                     break
        #     return result

        elif message.upper() == 'ИЗБРАННОЕ':
            users_like = bd.get_users_likes(qoest_inf[0])
            if len(users_like) > 0:
                vk_bot.write_msg(qoest_inf[0], 'Список Имен:\n\n')
                for user in users_like:
                    us_info = ap.get_user_info(user)
                    vk_bot.write_msg(qoest_inf[0], f'{us_info[1]} {us_info[2]}')
                result = 'Готово'
            else:
                result = 'Список избранного пуст!'
            return result


        else:
            return 'Такой команды нет\nДля просмотра списка команд наберите "HELP"'





if __name__ == '__main__':

    vk = vk_api.VkApi(token=TOKEN_GR)
    longpoll = VkLongPoll(vk)
    ap = VK_Users(TOKEN_USER)
    bd = Metod()
    create_tables()
    print('start')
    
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                vk_bot = VK_BOT()
                vk_bot.write_msg(event.user_id, vk_bot.new_message(event))

