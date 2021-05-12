import requests
import json
import sys


def show_work_status(singleCount, totalCount, currentCount):
    currentCount += singleCount
    percentage = 1. * currentCount / totalCount * 100
    status = '>' * int(percentage / 2) + '-' * (50 - int(percentage / 2))
    if percentage % 3:
        sys.stdout.write('\rStatus:[{0}]{1:.2f}%'.format(status, percentage))
        sys.stdout.flush()
    if percentage >= 100: print('\n')


# считываем данные id неповторяющихся игр из текстового файла
with open('data_games_ids.txt', 'r') as file_in:
    games_ids_list = json.load(file_in)

# получаем данные о среднем времени игры
average_playing_time_list = []
total_count, current_count = len(games_ids_list), 0
for game_id in games_ids_list:
    link = 'http://steamspy.com/api.php?request=appdetails&appid=' + str(game_id)
    r = requests.get(link)
    r = r.json()
    average_playing_time_list.append(r['average_forever'])
    show_work_status(1, total_count, current_count)
    current_count += 1

print(average_playing_time_list)

# записываем полученные данные в текстовые файлы
with open("data_games_average_playing_time.txt", 'w') as file_out:
    json.dump(average_playing_time_list, file_out)
