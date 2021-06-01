import requests
import time
class Photo_downloader:
    def __init__(self, vk_token: str, yad_token: str):
        self.vk_token = vk_token
        self.yad_token = yad_token
    # Получаем Json файл с инф о фотографиях в профиле вк, по умолчанию 5 фото
    def user_profile_photo(self, vk_id, photo_count=5):
        URL = 'https://api.vk.com/method/photos.getAll'
        params = {'owner_id': vk_id,
                  'album_id': 'profile',
                  'access_token': self.vk_token,
                  'v': '5.131',
                  'extended': '1',
                  'rev': '0',
                  'count': photo_count}
        response = requests.get(URL, params=params)
        return response.json()
    #создаем словарь ключом которого будет кол-во лайков (или лайки + дата публикации), значением ссылка на загрузку фото
    def photo_dict(self,vk_id):
        response = self.user_profile_photo(vk_id)
        ph_dict = {}
        for elements in response['response']['items']:
            # находим ссылку на фото в макс разрешении
            for ph_size_type in elements['sizes']:
                if ph_size_type['type'] == 'z':
                    url = ph_size_type['url']
            #Проверяем наличие фото с таким именнем в словаре и наполняем словарь
            if elements['likes']['count'] in ph_dict.keys():
                struck = time.gmtime(elements['date'])
                ph_dict[str(elements['likes']['count']) + ' likes ' + time.strftime('%d.%m.%Y', struck)] = url
            else:
                ph_dict[elements['likes']['count']] = url
        print(f'Выбрано {len(ph_dict.keys())} фотографий для загрузки')
        return ph_dict
    #заголовки для запросов ЯндексДиска
    def get_yad_headers(self):
        return {'Contetn-Type': 'application/json',
                'Authorization': 'OAuth {}'.format(self.yad_token)}
    #Создаем новую папку на ЯндексДиске и возвращаем путь к папке
    def put_back_up_folder(self,vk_id):
        new_folder_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_yad_headers()
        params = {'path': vk_id}
        response = requests.put(url=new_folder_url, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code == 201:
           print ("Backup folder is created")
        return params['path']
    #Загружаем файлы на Яндекс Диск
    def upload(self, vk_id):
        photo_dict = self.photo_dict(vk_id)
        headers = self.get_yad_headers()
        path = self.put_back_up_folder(vk_id)
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        id = 0
        for elements in photo_dict.keys():
            id += 1
            params = {'path': str(path) + '/' + str(elements),
                      'url': photo_dict[elements]}
            response = requests.post(url=upload_url,headers=headers, params=params)
            response.raise_for_status()
            if response.status_code == 202:
                print(f'Profile photo №{id} is uploaded')
if __name__ == '__main__':
    # вводим токены. Сначала ВК, потом Яндекс диск
    Vk_ph_dwn = Photo_downloader ('','')
    # Воодим Id. По умолчанию photo_count=5
    test = Vk_ph_dwn.upload('')

