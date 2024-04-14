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
                    Формируется база подходящих тебе кандидатов....жди'))
            # rev_sex = revers_sex(qoest_inf[4])
            # DATA_US = ap.data_users(qoest_inf[3], rev_sex, qoest_inf[5])
            DATA_US = ap.data_users(2, 1, 1986) # цифры заведены для теста
            print((DATA_US))
            print (qoest_inf[0])
            bd.add_users(qoest_inf[0], DATA_US)
            return 'Готово. Набери "next" или "следующий" для начала просмотра'

        if message.upper() == 'NEXT' or message.upper() == 'СЛЕДУЮЩИЙ':
            vk_bot.write_msg(qoest_inf[0], 'Идет поиск, ждите')
            photos = 'NONE'
            while photos == 'NONE':  # проверяет наличие фото у кандидатов
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
                        print('ok')
                        request = event.text
                        if request.upper == "ДА":
                            print('добавляем')
                            result = 'Добавили!\n Набери "next" или "следующий" для следующего просмотра'
                            break
                        else:
                            result = 'Набери "next" или "следующий" для следующего просмотра'
                            break
            return result
        else:
            return 'НЕ понял команду'



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
                print('!!!!')
                vk_bot = VK_BOT()
                vk_bot.write_msg(event.user_id, vk_bot.new_message(event))

