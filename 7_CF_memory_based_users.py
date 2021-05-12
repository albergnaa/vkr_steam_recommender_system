import random
import numpy as np
from statistics import mean
import pandas as pd

pd.set_option('display.width', 600)
pd.set_option('display.max_columns', 15)

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

# считываем таблицу рейтингов
data = pd.read_csv('data_rating_table.csv')
del data['Unnamed: 0']
data = data.values
print(data)
# [[4, 0, 5, 5, 3, 4], [4, 2, 1, 0, 2, 1], [3, 0, 2, 4, 1, 5], [4, 4, 0, 0, 2, 5], [2, 1, 3, 5, 4, 4]]
users_number, games_number = np.shape(data)
# число пользователей для тестовой выборки
test_number = 100
test_users = []
# выбираем пользователей для тестовой выборки случайным образом
for i in range(test_number):
    u = random.randint(0, users_number - 1)
    while u in test_users:
        u = random.randint(0, users_number - 1)
    test_users.append(u)

metrics = ['pearson', 'cosine']

for metric in metrics:
    print('Метрика: ' + metric)
    RMSE = 0
    for user_index in test_users:
        print('Прогнозирование для игрока ' + str(user_index))
        similarity = get_similarity(data, user_index, metric)
        se, count = 0, 0
        for game_index in range(games_number):
            if data[user_index][game_index] != 0:
                actual_rating = data[user_index][game_index]
                prediction_rating = get_prediction(data, similarity, user_index, game_index)
                se += squared_error(actual_rating, prediction_rating)
                count += 1
        RMSE += np.sqrt(se / count)
        print('RMSE для игрока: ' + str(np.sqrt(se / count)))
    print('Средняя RMSE с метрикой ' + str(metric) + ' ' + str(RMSE / len(test_users)))
