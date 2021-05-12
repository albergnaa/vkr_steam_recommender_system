import requests
import json

# считываем данные id игроков из текстового файла
players_ids_list = []
with open('data_players_ids.txt', 'r') as f:
    for line in f:
        for word in line.split():
            players_ids_list.append(word)

print("Собрано всего id:" + str(len(players_ids_list)))

# ключ для доступа к SteamWebAPI
key = '69ED7D3D039A25A61CC4B8EA95E85DE3'

player_id_arr, player_games_arr = [], []
for player_id in players_ids_list:
    link = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v1' + '?key=' + key + '&steamid=' + player_id
    r = requests.get(link)
    r = r.json()
    # исключаем пустые ответы на запросы с закрытых аккаунтов
    if r['response'] != {}:
        player_id_arr.append(player_id)
        player_games_arr.append(r)

print('В результате обработки осталось id:' + str(len(player_id_arr)))
print('игры:' + str(len(player_games_arr)))

# записываем полученные данные в текстовые файлы
with open("data_using_players_ids.txt", 'w') as file_out:
    json.dump(player_id_arr, file_out)
with open("data_players_games.txt", 'w') as file_out:
    json.dump(player_games_arr, file_out)

