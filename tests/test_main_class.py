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


# Тест на получения ключа № 2
def test_get_api_key_for_not_valid_user(email=not_valid_email, password=not_valid_password):
    # При вводе некорректных данных не получаем ключ
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert not 'key' in result


# Тест на проверку списка питомцев
def test_get_all_pets_with_valid_key(filter='my_pets'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


# Тест на добавления питомца
def test_post_add_new_pets(name='Fil', animal_type='dog', age='0', pet_photo='images/Cst1.jpg'):
    # При вводе корректных данных питомец добавляется
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name'] == name


def test_post_add_new_pets_not_name(name='', animal_type='Собака', age='2', pet_photo='images/monkey.jpg'):
    # При вводе пустых данных ожидаем, статус кода 400
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400


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


# Тест на изменения информации № 2
def test_update_pet_info_without_data(name='', animal_type='', age=2):
    # При вводе пустых данных ожидаем, что питомец не добавиться
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    if len(my_pets['pets']) != 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 400


# Тест на добавления питомца без фото
def test_create_pet_simple(name='Егорка', animal_type='Хоббит', age=108):
    # При добавлении всех параметров, питомец добавляется
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name


# Тест на добавления питомца без фото № 2
def test_create_pet_simple_without_data(name='', animal_type='', age=0):
    # Ввод пустых данных для получения от системы код 400
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)
    assert status == 400
    assert result['name'] != name


# Тест на добавление фото к питомцу
def test_add_photo_pet(pet_photo='images/hobbit.jpg'):
    # Добавление или изменение фотографии в существующего питомца
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    if len(my_pets['pets']) > 0:
        status, result = pf.add_photo_pet(auth_key, my_pets['pets'][0]['id'], pet_photo)
        assert status == 200
        assert "pet_photo" in result
    else:
        raise Exception("There is no my Pets")
