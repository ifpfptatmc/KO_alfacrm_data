import requests
import csv
import os
from datetime import datetime

def fetch_trial_lessons():
    email = os.getenv('ALPHA_CRM_EMAIL')
    api_key = os.getenv('ALPHA_CRM_API_KEY')
    hostname = os.getenv('ALPHA_CRM_HOSTNAME')

    # Авторизация
    auth_url = f'https://{hostname}/v2api/auth/login'
    auth_data = {'email': email, 'api_key': api_key}
    response = requests.post(auth_url, json=auth_data)

    if response.status_code == 200:
        token = response.json().get('token')
        print('Токен:', token)
        
        # Запрос данных о пробных уроках
        lessons_url = f'https://{hostname}/v2api/1/lesson/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}

        filters = {
            'lesson_type_id': 3,
            'status': 'finished'
        }

        response = requests.post(lessons_url, headers=headers, json={'filters': filters})
        print('Код ответа запроса:', response.status_code)
        print('Ответ:', response.json())

        if response.status_code == 200:
            lessons = response.json().get('items', [])
            print('Найденные уроки:', lessons)
            lessons_by_date = {}

            for lesson in lessons:
                lesson_date = lesson['date']
                if lesson_date not in lessons_by_date:
                    lessons_by_date[lesson_date] = 0
                lessons_by_date[lesson_date] += 1

            # Сохранение данных в CSV файл
            with open('trial_lessons.csv', 'w', newline='') as csvfile:
                fieldnames = ['Date', 'Number of Trial Lessons']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for date, count in lessons_by_date.items():
                    writer.writerow({'Date': date, 'Number of Trial Lessons': count})
            print('Данные о пробных уроках сохранены в trial_lessons.csv')
        else:
            print('Ошибка получения уроков:', response.text)
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_trial_lessons()
