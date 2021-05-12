import json
import pandas as pd

pd.set_option('display.width', 600)
pd.set_option('display.max_columns', 15)

# считываем id неповторяющихся игр из текстового файла
with open('data_games_ids.txt', 'r') as file_in:
    games_ids_list = json.load(file_in)

# считываем среднее время игр из текстового файла
with open('data_games_average_playing_time.txt', 'r') as file_in:
    games_average_playing_time_list = json.load(file_in)

# считываем данные id игроков из текстового файла
with open('data_using_players_ids_1.txt', 'r') as file_in:
    players_ids_list = json.load(file_in)

# считываем списки игр пользователей из текстового файла
with open('data_players_games_1.txt', 'r') as file_in:
    players_games_list = json.load(file_in)

dic = {}
players_games_list_new = []
for games in players_games_list:
    for item in games:
        dic.update({item['appid']: item['playtime_forever']})
    players_games_list_new.append(dic)
    dic = {}

# удаляем игры, где не посчитано среднее время игры
del_indexes = []
del_ids = []
for i in range(len(games_average_playing_time_list)):
    if games_average_playing_time_list[i] == 0:
        del_indexes.append(i)
        del_ids.append(games_ids_list[i])
del_indexes.reverse()
for i in del_indexes:
    del games_ids_list[i]
    del games_average_playing_time_list[i]
for i in del_ids:
    for j in range(len(players_games_list_new)):
        if i in players_games_list_new[j].keys():
            players_games_list_new[j].pop(i)


n = len(players_ids_list)
m = len(games_ids_list)
table = [[0] * m for i in range(n)]

# высчитывание рейтингов
for i in range(len(players_ids_list)):
    for j in range(len(games_ids_list)):
        if games_ids_list[j] in players_games_list_new[i].keys():
            game_time = players_games_list_new[i].get(games_ids_list[j])
            average_time = games_average_playing_time_list[j]
            if game_time < 0.4*average_time:
                table[i][j] = 1
            elif game_time < 0.8*average_time:
                table[i][j] = 2
            elif game_time < 1.2*average_time:
                table[i][j] = 3
            elif game_time < 1.4*average_time:
                table[i][j] = 4
            else:
                table[i][j] = 5
        else:
            table[i][j] = 0

df_rating_table = pd.DataFrame(data=table, index=players_ids_list, columns=games_ids_list)
print(df_rating_table)

# записываем таблицу в файл
df_rating_table.to_csv('data_rating_table.csv')

# записываем id неповторяющихся игр из текстового файла
with open('data_games_ids_1.txt', 'w') as file_out:
    json.dump(games_ids_list, file_out)

# записываем среднее время игр из текстового файла
with open('data_games_average_playing_time_1.txt', 'w') as file_out:
    json.dump(games_average_playing_time_list, file_out)

# записываем списки игр пользователей из текстового файла
with open('data_players_games_2.txt', 'w') as file_out:
    json.dump(players_games_list_new, file_out)


