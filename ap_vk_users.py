import requests
from pprint import pprint
from Constant import TOKEN_USER


class VK_Users:
    def __init__(self, TOKEN_USER):
        self.URL_API = 'https://api.vk.com/method'
        self.TOKEN_USER = TOKEN_USER


    def revers_sex(self, sex):
        if sex == 1:
            rev_sex = 2
        elif sex == 2:
            rev_sex = 1
        else:
            rev_sex = 0
        return rev_sex


    def data_users(self, city, sex, year):
        age_from = 2019-year
        age_to = 2029-year
        params = {
            'access_token': self.TOKEN_USER,
            'sort': 0,
            'count': 500,
            'has_photo': 1,
            'v': 5.199,
            'fields': 'city,sex,counters',
            # 'birth_year': year,
            'age_from': age_from,
            'age_to': age_to,
            'city': city,  # идентификатор , не название
            'sex': sex
        }
        data_users = []
        response = requests.get(f'{self.URL_API}/users.search', params=params)
        data = response.json()['response']['items']
        for user in data:
            try:
                if user['sex'] == sex and user['city']['id'] == 2 :
                    data_users.append(user['id'])
            except:
                pass
        return data_users


    def get_user_info(self, user_vk):
        params = {
            'access_token': self.TOKEN_USER,
            'user_ids': user_vk,
            'fields': 'city,sex,bdate',
            'v': 5.199
            }
        response = requests.get(f'{self.URL_API}/users.get', params=params)
        user_info = response.json()['response'][0]
        user_info = [user_info['id'], user_info['first_name'], user_info['last_name'],
                     user_info['city']['id'], user_info['sex'], user_info['bdate'][5:]]
        return user_info


    def photos_user(self, user_vk): # возвращает 3 фото (макс лайки, учитывает совпадение) , если нет то возвращает NONE
        params = {
            'access_token': self.TOKEN_USER,
            'user_id': user_vk,
            'extended': 1,
            'v': 5.199
            }
        photos = []
        likes = []
        response = requests.get(f'{self.URL_API}/photos.getUserPhotos', params=params)
        try:
            user_photos = response.json()['response']['items']
            if len(user_photos) > 3:
                for photo in user_photos:            # создаем и сортируем лист лайков
                     likes.append(photo['likes']['count'])
                sort_likes = sorted(likes, reverse=True)[:3]
                for el in sort_likes:                # вытаскиваем фото по 3-м первым лайкам
                    for photo in user_photos:
                        if photo['likes']['count'] == el:
                            photos.append(photo['sizes'][-1]['url'])
                            user_photos.remove(photo)
                            break
                result = photos
            else:
                result = 'NONE'
        except:
            result = 'NONE'
        return result


if __name__ == '__main__':
    ap = VK_Users(TOKEN_USER)
    sex = 1
    city = 2
    year = 1986
    # data_qoest = ap.data_users(sex, city, year)
    # pprint(ap.data_users(2,1,1986))
    # user_vk = 809529828
    # print(ap.get_user_info(user_vk))
    # pprint(ap.data_users(2, 1, 1986))
    # user_vk = 711878878
    user_vk = 326325001
    pprint(ap.photos_user(user_vk))
