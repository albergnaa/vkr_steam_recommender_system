import requests


# возвращает список друзей определенного игрока
def get_friend_list(key, user_id):
    link = 'http://api.steampowered.com/ISteamUser/GetFriendList/v1'
    r = requests.get(link + '?key=' + key + '&steamid=' + user_id)
    # исключаем пустые ответы на запросы с закрытых аккаунтов
    if len(r.json()) < 1:
        return ['None']
    else:
        friend_list = r.json()['friendslist']['friends']
        return [friend_list[i]['steamid'] for i in range(len(friend_list))]


# возвращает дополненный список id пользователей, не более 3000
def collect_steam_ids(key, ids_list, counter):
    del_indexes = []
    for i in range(len(ids_list)):
        res_list = get_friend_list(key, ids_list[i])
        for j in range(len(res_list)):
            # исключаем повторения в собранных данных
            if res_list[j] not in ids_list:
                # исключаем пустые ответы на запросы с закрытых аккаунтов
                if res_list[j] != 'None':
                    ids_list.append(res_list[j])
                    counter += 1
                else:
                    del_indexes.append(i)
            if counter > 3000:
                return counter, ids_list
    for i in del_indexes:
        del ids_list[i]
    return counter, ids_list


# ключ для доступа к SteamWebAPI
steam_web_api_key = '69ED7D3D039A25A61CC4B8EA95E85DE3'
# id первого игрока, с которого начинается сбор данных
starter_gamer_id = '76561198047134912'
users_ids = [starter_gamer_id]

# сбор данных
counter = 1
for ind in range(4):
    counter, users_ids = collect_steam_ids(steam_web_api_key, users_ids, counter)

# записываем id в текстовый файл
with open("data_players_ids.txt", "w") as file_out:
    print(*users_ids, file=file_out)
