import json
import random
import tkinter as tk
import requests
import pandas as pd
import numpy as np
from statistics import mean


# вычисление кореляции Пирсона
def pearson_sim(u, v):
    # ищем общие элементы у пользователей u и v и ищем средние значения
    sum_u, sum_v = 0, 0
    intersection = []
    for i in range(len(u)):
        if u[i] != 0 and v[i] != 0:
            intersection.append(i)
            sum_u += u[i]
            sum_v += v[i]
    if len(intersection) == 0:
        return 0
    mu_u = sum_u / len(intersection)
    mu_v = sum_v / len(intersection)
    # расчет
    numerator, denominator_u, denominator_v = 0, 0, 0
    for i in intersection:
        numerator += (u[i] - mu_u) * (v[i] - mu_v)
        denominator_u += (u[i] - mu_u) ** 2
        denominator_v += (v[i] - mu_v) ** 2
    denominator = (np.sqrt(denominator_u) * np.sqrt(denominator_v))
    if denominator == 0:
        sim = 0
    else:
        sim = numerator / denominator
    return sim


# вычисление вектора схожести игрока с другими
def get_similarity(rating_table, user_index):
    users_number = len(rating_table)
    user_data = rating_table[user_index]
    similarity_arr = []
    for user in range(users_number):
        other_user_data = rating_table[user]
        sim = pearson_sim(user_data, other_user_data)
        similarity_arr.append(sim)
    similarity_arr[user_index] = 0
    return similarity_arr


# вычисление среднего значения оценок пользователя по известным значениям за исключением игры index
def mean_user_ratings(user_data, index):
    arr = []
    for i in range(len(user_data)):
        if user_data[i] > 0 and i != index:
            arr.append(user_data[i])
    return mean(arr)


# делаем прогноз для пользователя с индексом user_index по игре с индексом game_index
def get_prediction(rating_table, similarity, user_index, game_index):
    mu = mean_user_ratings(rating_table[user_index], game_index)
    numerator, denominator = 0, 0
    for other_user_index in range(len(rating_table)):
        if other_user_index != user_index and rating_table[other_user_index][game_index] != 0:
            m = mean_user_ratings(rating_table[other_user_index], game_index)
            numerator += (rating_table[other_user_index][game_index] - m) * similarity[other_user_index]
            denominator += np.absolute(similarity[other_user_index])
    if denominator == 0:
        denominator = 1
    rating = mu + numerator / denominator
    if rating > 5:
        return 5
    elif rating < 1:
        return 1
    else:
        return rating


def get_predicted_games(test_user, rating_table):

    users_number, games_number = np.shape(rating_table)
    predicted_games_index, predicted_games = [], []
    print('Прогнозирование для игрока ' + str(test_user))
    similarity = get_similarity(rating_table, test_user)
    for game_index in range(games_number):
        if rating_table[test_user][game_index] == 0:
            predicted_games_index.append(game_index)
            prediction = get_prediction(rating_table, similarity, test_user, game_index)
            predicted_games.append(prediction)
    return predicted_games_index, predicted_games


# получаем название игры по app_id
def get_app_name(game_id):
    link = 'http://steamspy.com/api.php?request=appdetails&appid=' + str(game_id)
    r = requests.get(link)
    r = r.json()
    return r['name']


# получаем список игр у игрока по user_id
def get_player_games(player_id):
    # ключ для доступа к SteamWebAPI
    key = '69ED7D3D039A25A61CC4B8EA95E85DE3'
    link = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v1' + '?key=' + key + '&steamid=' + player_id
    r = requests.get(link)
    try:
        r = r.json()
    except json.decoder.JSONDecodeError:
        print('json.decoder.JSONDecodeError caught')
        return 'None'
    # исключаем пустые ответы на запросы с закрытых аккаунтов
    if r['response'] == {}:
        print('Close profile')
        return 'None'
    return r['response']


def get_player_ratings(player_games, all_games, average_time_list):
    player_rating = [0 for i in range(len(all_games))]
    player_games = player_games['games']
    for game in player_games:
        if str(game['appid']) in all_games:
            ind = all_games.index(str(game['appid']))
            time = game['playtime_forever']
            average_time = average_time_list[ind]
            if time < 0.4*average_time:
                player_rating[ind] = 1
            elif time < 0.8*average_time:
                player_rating[ind] = 2
            elif time < 1.2*average_time:
                player_rating[ind] = 3
            elif time < 1.4*average_time:
                player_rating[ind] = 4
            else:
                player_rating[ind] = 5
    return player_rating


def get_recommendation():
    player_id = entry_1.get()
    if player_id:
        player_games = get_player_games(player_id)

        # считываем рейтинговую таблицу
        data = pd.read_csv('data_rating_table.csv')
        games_id = list(data.columns)
        del games_id[0]
        users_ids = list(data['Unnamed: 0'])
        del data['Unnamed: 0']
        data = data.values

        if player_games != 'None':
            label_2['text'] = 'Рекомендации для пользователя \n' + player_id + ':'
            if int(player_id) in users_ids:

                predicted_games_indexes, predicted_games_rating = get_predicted_games(users_ids.index(int(player_id)), data)
                print(len(predicted_games_rating))
                print(predicted_games_rating)
                recommended_games_indexes = []
                for j in range(len(predicted_games_indexes)):
                    if predicted_games_rating[j] >= 4.8:
                        recommended_games_indexes.append(predicted_games_indexes[j])
                print(len(recommended_games_indexes))
                print(recommended_games_indexes)
                random_list = []
                for i in range(7):
                    game_index = random.choice(recommended_games_indexes)
                    random_list.append(games_id[game_index])
                label_rec1['text'] = get_app_name(random_list[0])
                label_rec2['text'] = get_app_name(random_list[1])
                label_rec3['text'] = get_app_name(random_list[2])
                label_rec4['text'] = get_app_name(random_list[3])
                label_rec5['text'] = get_app_name(random_list[4])
                label_rec6['text'] = get_app_name(random_list[5])
                label_rec7['text'] = get_app_name(random_list[6])
                # считываем названия популярных игр
                with open('data_positive_rate.txt', 'r') as file_in:
                    positive_rate_games = json.load(file_in)
                random_list = []
                for i in range(3):
                    game = random.choice(positive_rate_games)
                    random_list.append(game)
                label_rec8['text'] = random_list[0]
                label_rec9['text'] = random_list[1]
                label_rec10['text'] = random_list[2]

            else:
                # 76561198121354598
                # 76561198047134912
                # считываем среднее время игр из текстового файла
                with open('data_games_average_playing_time_1.txt', 'r') as file_in:
                    games_average_playing_time = json.load(file_in)
                user_ratings = get_player_ratings(player_games, games_id, games_average_playing_time)

                n, m = data.shape
                table = [[0] * m for i in range(n + 1)]
                for i in range(n):
                    for j in range(m):
                        table[i][j] = data[i][j]
                for j in range(m):
                    table[n][j] = user_ratings[j]
                predicted_games_indexes, predicted_games_rating = get_predicted_games(n, table)
                print(len(predicted_games_rating))
                print(predicted_games_rating)
                recommended_games_indexes = []
                for j in range(len(predicted_games_indexes)):
                    if predicted_games_rating[j] >= 4.8:
                        recommended_games_indexes.append(predicted_games_indexes[j])
                print(len(recommended_games_indexes))
                print(recommended_games_indexes)
                random_list = []
                for i in range(7):
                    game_index = random.choice(recommended_games_indexes)
                    random_list.append(games_id[game_index])
                label_rec1['text'] = get_app_name(random_list[0])
                label_rec2['text'] = get_app_name(random_list[1])
                label_rec3['text'] = get_app_name(random_list[2])
                label_rec4['text'] = get_app_name(random_list[3])
                label_rec5['text'] = get_app_name(random_list[4])
                label_rec6['text'] = get_app_name(random_list[5])
                label_rec7['text'] = get_app_name(random_list[6])
                # считываем названия популярных игр
                with open('data_positive_rate.txt', 'r') as file_in:
                    positive_rate_games = json.load(file_in)
                random_list = []
                for i in range(3):
                    game = random.choice(positive_rate_games)
                    random_list.append(game)
                label_rec8['text'] = random_list[0]
                label_rec9['text'] = random_list[1]
                label_rec10['text'] = random_list[2]


        else:
            label_2['text'] = 'Такого id не существует \n или профиль закрыт'
    else:
        print('Empty text')






win = tk.Tk()
win.title("Рекомендательная система Steam")
win.geometry("380x350+100+100")
win.resizable(False, False)
photo = tk.PhotoImage(file='icon.png')
win.iconphoto(False, photo)
win.config(bg='#f0f5f5')

label_1 = tk.Label(win, text="Введите идентификатор пользователя:",
                   bg='#f0f5f5',
                   fg='#141f1f',
                   font=('Arial', 10))
label_1.grid(row=0, column=0, columnspan=3)

entry_1 = tk.Entry(win)
entry_1.grid(row=1, column=0)

btn_1 = tk.Button(win, text='Дать рекомендацию',
                  activebackground='#c2d6d6',
                  bg='#e0ebeb',
                  fg='#141f1f',
                  font=('Arial', 10),
                  command=get_recommendation)
btn_1.grid(row=1, column=3)

label_2 = tk.Label(win, bg='#f0f5f5',
                   fg='#141f1f',
                   font=('Arial', 10))
label_2.grid(row=2, column=0, columnspan=3)

label_rec1 = tk.Label(win, bg='#f0f5f5', fg='#141f1f', font=('Arial', 8))
label_rec2 = tk.Label(win, bg='#f0f5f5', fg='#141f1f', font=('Arial', 8))
label_rec3 = tk.Label(win, bg='#f0f5f5', fg='#141f1f', font=('Arial', 8))
label_rec4 = tk.Label(win, bg='#f0f5f5', fg='#141f1f', font=('Arial', 8))
label_rec5 = tk.Label(win, bg='#f0f5f5', fg='#141f1f', font=('Arial', 8))
label_rec6 = tk.Label(win, bg='#f0f5f5', fg='#141f1f', font=('Arial', 8))
label_rec7 = tk.Label(win, bg='#f0f5f5', fg='#141f1f', font=('Arial', 8))
label_rec8 = tk.Label(win, bg='#f0f5f5', fg='#141f1f', font=('Arial', 8))
label_rec9 = tk.Label(win, bg='#f0f5f5', fg='#141f1f', font=('Arial', 8))
label_rec10 = tk.Label(win, bg='#f0f5f5', fg='#141f1f', font=('Arial', 8))

label_rec1.grid(row=3, column=0, columnspan=3)
label_rec2.grid(row=4, column=0, columnspan=3)
label_rec3.grid(row=5, column=0, columnspan=3)
label_rec4.grid(row=6, column=0, columnspan=3)
label_rec5.grid(row=7, column=0, columnspan=3)
label_rec6.grid(row=8, column=0, columnspan=3)
label_rec7.grid(row=9, column=0, columnspan=3)
label_rec8.grid(row=10, column=0, columnspan=3)
label_rec9.grid(row=11, column=0, columnspan=3)
label_rec10.grid(row=12, column=0, columnspan=3)

win.mainloop()



