# Positive rate-based recommendation model

import json
import pandas as pd
import requests


# получаем через запрос данные по топ100 играм со SteamSpy
r = requests.get('http://steamspy.com/api.php?request=top100forever')
dic_steam_spy = r.json()


dict_game_stats = {'appid': {}, 'name': {}, 'positive': {}, 'negative': {}}
for game_id, game_stats in dic_steam_spy.items():
    if game_stats != {} and game_stats is not None:
        dict_game_stats['appid'].update({game_id: game_stats.get("appid", {})})
        dict_game_stats['name'].update({game_id: game_stats.get('name', {})})
        dict_game_stats['positive'].update({game_id: game_stats.get('positive', {})})
        dict_game_stats['negative'].update({game_id: game_stats.get('negative', {})})

appid = list(dict_game_stats.get('appid').values())
name = list(dict_game_stats.get('name').values())
pos = list(dict_game_stats.get('positive').values())
neg = list(dict_game_stats.get('negative').values())

rating_list = pd.DataFrame(
    {'Game_id': appid,
     'Game_name': name,
     'Positive': pos,
     'Negative': neg})

# считаем относительное число положительных отзывов и сортируем по убыванию
rating_list['Positive_Rate'] = rating_list["Positive"] / (
        rating_list["Positive"] + rating_list["Negative"])
rating_list.sort_values("Positive_Rate", axis=0, ascending=False,
                        inplace=True, na_position='first')
rating_list = rating_list.reset_index(drop=True)

games_names = list(rating_list.get('Game_name'))[:50]

# записываем данные в файл
with open('data_positive_rate.txt', 'w') as file_out:
    json.dump(games_names, file_out)

