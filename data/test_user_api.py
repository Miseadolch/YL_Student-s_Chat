from requests import delete, get, put, post

# корректный запрос для получения одного пользователя
print(get("http://127.0.0.1:5000/api/users/2").json())

# корректный запрос на удаление пользователя
print(delete("http://127.0.0.1:5000/api/users/3").json())

# корректный запрос на добавление пользователя
print(post("http://127.0.0.1:5000/api/users", json={'id': 3,
                                                    'email': 'mishashesgdtinin05@mail.ru',
                                                    'nickname': "Miseadolch23",
                                                    'surname': 'Щетинин',
                                                    'name': "Михаил Ярославович Щетинин",
                                                    'group': 'courses/539/groups/4631',
                                                    'hashed_password': 'Mamochka32'}).json())
# корректный запрос на редактирование пользователя
print(put("http://127.0.0.1:5000/api/users/3", json={'email': 'mishashetissafnin05@mail.ru',
                                                     'nickname': "NOTMIseadolch",
                                                     'surname': 'Щетинин',
                                                     'name': "Михаил Ярославович Щетинин",
                                                     'group': 'courses/539/groups/4631'}).json())

# некорректный запрос на получение пользователя; неверное id
print(get("http://127.0.0.1:5000/api/users/13").json())

# некорректный запрос на удаление пользователя; неверное id
print(delete("http://127.0.0.1:5000/api/users/13").json())

# некорректный запрос на добавления пользователя; id уже существует
print(post("http://127.0.0.1:5000/api/users", json={'id': 2,
                                                    'email': 'mishashetinin05@mail.ru',
                                                    'nickname': "Miseadolch",
                                                    'surname': 'Щетинин',
                                                    'name': "Михаил Ярославович Щетинин",
                                                    'group': 'courses/539/groups/4631',
                                                    'hashed_password': 'Mamochka32'}).json())

# некорректный запрос на добавления пользователя; неверное количество параметров
print(post("http://127.0.0.1:5000/api/users", json={'id': 6,
                                                    'name': "Михаил Ярославович Щетинин",
                                                    'group': 'courses/539/groups/4631',
                                                    'hashed_password': 'Mamochka32'}).json())

# некорректный запрос на редактирование пользователя; неверное id
print(put("http://127.0.0.1:5000/api/users/13", json={'email': 'mishashetinin05@mail.ru',
                                                      'nickname': "NOTMIseadolch",
                                                      'surname': 'Щетинин',
                                                      'name': "Михаил Ярославович Щетинин",
                                                      'group': 'courses/539/groups/4631'}).json())

# некорректный запрос на редактирование пользователя; неверное количество параметров
print(put("http://127.0.0.1:5000/api/users/3", json={'email': 'mishashetinin05@mail.ru',
                                                     'nickname': "NOTMIseadolch",
                                                     'group': 'courses/539/groups/4631'}).json())

# корректный запрос для получения всех пользователей
print(get("http://127.0.0.1:5000/api/users").json())
