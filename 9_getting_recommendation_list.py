import json
import random
import requests
import pandas as pd

# получаем название игры по appid
def get_app_name(id):
    link = 'http://steamspy.com/api.php?request=appdetails&appid=' + game_id
    r = requests.get(link)
    r = r.json()
    return r['name']

# считываем индексы рекомендуемых элементов
with open('data_predicted_indexes.txt', 'r') as file_in:
    predicted_indexes = json.load(file_in)

# считываем рейтинги рекомендуемых элементов
with open('data_predicted_ratings.txt', 'r') as file_in:
    predicted_ratings = json.load(file_in)

# считываем названия популярных игр
with open('data_positive_rate.txt', 'r') as file_in:
    positive_rate_games = json.load(file_in)

# рейтинговую таблицу
data = pd.read_csv('data_rating_table.csv')
games_id = list(data.columns)
del games_id[0]

# ищем игры с рейтингов = 5
recommended_indexes = []
user_id = list(data['Unnamed: 0'])[0]
for i in range(len(predicted_indexes)):
    if predicted_ratings[i] == 5:
        recommended_indexes.append(predicted_indexes[i])

recommended_game_id = []
for game in recommended_indexes:
    recommended_game_id.append(games_id[game])

# случайным образом выбираем 7 игр с предсказанным рейтингом 5
recommended_game_names = []
number_recommendation = 7
for i in range(number_recommendation):
    game_id = random.choice(recommended_game_id)
    game_name = get_app_name(game_id)
    while game_name in recommended_game_names:
        game_id = random.choice(recommended_game_id)
        game_name = get_app_name(game_id)
    recommended_game_names.append(game_name)

# случайным образом выбираем 3 игры из рейтинга игр с положительными отзывами
number_recommendation = 3
for i in range(number_recommendation):
    game_id = random.randint(0, len(positive_rate_games)-1)
    game_name = positive_rate_games[game_id]
    while game_name in recommended_game_names:
        game_id = random.randint(0, len(positive_rate_games) - 1)
        game_name = positive_rate_games[game_id]
    recommended_game_names.append(game_name)

# даем рекомендацию
print('Рекомендации для игрока ' + str(user_id))
for i in recommended_game_names:
    print(i)
