import os.path

from api import PetFriends
from settings import valid_email, valid_password
from settings import not_valid_email, not_valid_password

pf = PetFriends()


# Тест на получение ключа
def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    # Получение ключа с корректными данными
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result


# Тест № 1: Ввод не корректных данных
def test_get_api_key_for_not_valid_user(email=not_valid_email, password=not_valid_password):
    # При вводе некорректных данных не получаем ключ
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result


# Тест на проверку списка питомцев
def test_get_all_pets_with_valid_key(filter='my_pets'):
    # Производим проверку на получения сообщения формата Json о списке питомца
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


# Тест № 2: проверка списка питомцев не корректными данными.
def test_get_all_pets_no_valid_key(filter='mypets'):
    # Производим проверку с некорректным данными в поле фильтр для получения ошибки 403
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 403  # Ожидал при не корректных данных выдаст ошибку 403, поймал ошибку 500)
    assert result == 'html'


# Тест на добавления питомца
def test_post_add_new_pets(name='Fil', animal_type='dog', age='0', pet_photo='images/Cst1.jpg'):
    # При вводе корректных данных питомец добавляется
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name'] == name


# Тест № 3: Тест с вводом пустых строк
def test_post_add_new_pets_not_name(name='', animal_type='Собака', age='2', pet_photo='images/monkey.jpg'):
    # При вводе пустых данных ожидаем, статус кода 400
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400  # Баг, если вводить данные в swagger, то там не дает сделать, а здесь получаем код 200
    assert result['name'] == ''


# Тест на удаления питомца
def test_delete_pets():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Супер кот", "кот", "3", "Cat.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

        pet_id = my_pets['pets'][0]['id']
        status, _ = pf.delete_pet(auth_key, pet_id)

        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

        assert status == 200
        assert pet_id not in my_pets.values()


# Тест № 4 Удаление не существующего питомца
def test_delete_not_pet():
    # Проверяем на корректность ошибки, при вводе не существующего питомца
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    pet_id = '3432411'
    status, result = pf.delete_pet(auth_key, pet_id)
    assert status == 404
    assert pet_id is not result


# Тест на изменение информации питомца
def test_update_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    # При вводе корректны данных питомец добавляется
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("There is no my pets")


# Тест № 5: Проверка на ввод пустых данных
def test_update_pet_info_without_data(name='', animal_type='', age=2):
    # При вводе пустых данных ожидаем, что питомец не добавиться
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 400  # Баг получаем код 200, при пустых данных
        assert result['name'] is not None


# Тест № 6: Добавление питомца без фото
def test_create_pet_simple(name='Егорка', animal_type='Хоббит', age=108):
    # При добавлении всех параметров, питомец добавляется
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name


# Тест № 7: Добавление питомца без фото
def test_create_pet_simple_without_data(name='', animal_type='', age=0):
    # Ввод пустых данных для получения от системы код 400
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)
    assert status == 400
    assert result['name'] != name


# Тест № 8: на добавление фото к питомцу
def test_add_photo_pet(pet_photo='images/belka.jpeg'):
    # Добавление или изменение фотографии в существующего питомца
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    if len(my_pets['pets']) > 0:
        status, result = pf.post_change_pet_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)
        assert status == 200
        assert "pet_photo" in result
    else:
        raise Exception("There is no my Pets")


# Тест № 9: На добавления фото к не существующему питомцу
def test_add_photo_not_pet(pet_photo='images/belka.jpeg'):
    # При добавлении фото к не существующему питомцу ожидаем 400
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    pet_id = '123214341'
    status, result = pf.post_change_pet_photo(auth_key, pet_id, pet_photo)
    assert status == 400  # Баг поймал ошибку 500
    assert pet_id not in result


# Тест № 10: Добавление фото не разрешенного формата
def test_add_photo_pet_not_photo(pet_photo='images/VrY.gif'):
    # Проверяем фото другого формата на добавления к существующему питомцу. Ожидаем ошибку 400
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')
    if len(my_pets) > 0:
        status, result = pf.post_change_pet_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)
        assert status == 400  # Баг Ошибка 500, в swagger указано, что ошибка 400 отвечает за не корректный ввод данных
        assert pet_photo not in result
