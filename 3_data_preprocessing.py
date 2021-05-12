import json


# считываем данные id игроков из текстового файла
with open('data_using_players_ids.txt', 'r') as file_in:
    users_ids_list = json.load(file_in)
# считываем данные игр игроков из текстового файла
with open('data_players_games.txt', 'r') as file_in:
    users_games_list = json.load(file_in)

print('Было записей до обработки: ' + str(len(users_games_list)))

users_games_list = [users_games_list[i]['response']['games'] for i in range(len(users_games_list))]

del_indexes = []
# удаляем игры, в которые не играли
for games_arr in users_games_list:
    for i in range(len(games_arr)):
        if games_arr[i]['playtime_forever'] == 0:
            del_indexes.append(i)
    del_indexes.reverse()
    for i in del_indexes:
        del games_arr[i]
    del_indexes = []


# ищем игроков с менее чем 5ю играми, оставляем в данных только список игр
del_indexes = []
for i in range(len(users_games_list)):
    if len(users_games_list[i]) < 5:
        del_indexes.append(i)

# удаляем игроков с менее чем 5ю играми
unnecessary_users = [users_ids_list[i] for i in del_indexes]
for value in unnecessary_users:
    users_ids_list.remove(value)
unnecessary_users_games = [users_games_list[i] for i in del_indexes]
for value in unnecessary_users_games:
    users_games_list.remove(value)

print('Осталось записей после обработки: ' + str(len(users_games_list)))

# записываем полученные данные в текстовые файлы
with open("data_using_players_ids_1.txt", 'w') as file_out:
    json.dump(users_ids_list, file_out)
with open("data_players_games_1.txt", 'w') as file_out:
    json.dump(users_games_list, file_out)

games_list = []
for item in users_games_list:
    for dic in item:
        games_list.append(dic['appid'])
game_set = list(set(games_list))

print('Неповторяющихся игр: ' + str(len(game_set)))

# запись id неповторяющихся игр
with open("data_games_ids.txt", 'w') as file_out:
    json.dump(game_set, file_out)





