import json
import numpy as np
from statistics import mean
import pandas as pd


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


# вычисление косинусовой меры близости
def cosine_sim(u, v):
    # ищем общие элементы у пользователей u и v
    intersection = []
    for i in range(len(u)):
        if u[i] != 0 and v[i] != 0:
            intersection.append(i)
    # расчет
    numerator, denominator_u, denominator_v = 0, 0, 0
    for i in intersection:
        numerator += u[i] * v[i]
        denominator_u += u[i] ** 2
        denominator_v += v[i] ** 2
    if len(intersection) == 0:
        return 0
    denominator = (np.sqrt(denominator_u) * np.sqrt(denominator_v))
    if denominator == 0:
        sim = 0
    else:
        sim = numerator / denominator
    return sim


# вычисление вектора схожести игрока с другими
def get_similarity(rating_table, user_index, metric):
    users_number = len(rating_table)
    user_data = rating_table[user_index]
    similarity_arr = []
    for user in range(users_number):
        other_user_data = rating_table[user]
        if metric == 'cosine':
            sim = cosine_sim(user_data, other_user_data)
            similarity_arr.append(sim)
        else:
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


# квадратичная ошибка
def squared_error(actual, predicted):
    return (actual - predicted) ** 2


def get_predicted_games(test_user):
    data = pd.read_csv('data_rating_table.csv')
    del data['Unnamed: 0']
    data = data.values
    users_number, games_number = np.shape(data)

    predicted_games_index, predicted_games = [], []
    print('Прогнозирование для игрока ' + str(test_user))
    similarity = get_similarity(data, test_user, 'pearson')
    count = 0
    for game_index in range(games_number):
        if data[test_user][game_index] == 0:
            predicted_games_index.append(game_index)
            count += 1
            prediction = get_prediction(data, similarity, test_user, game_index)
            predicted_games.append(prediction)
            print(count, prediction)
    return predicted_games_index, predicted_games

# индекс игрока для рекомендаций
user_index = 0
# получаем список предсказанных значений
indexes, ratings = get_predicted_games(user_index)

# запись индексы рекомендуемых игр
with open("data_predicted_indexes.txt", 'w') as file_out:
    json.dump(indexes, file_out)

# запись рейтингов рекомендуемых игр
with open("data_predicted_ratings.txt", 'w') as file_out:
    json.dump(ratings, file_out)
