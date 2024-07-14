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

        # Запрос уроков
        lessons_url = f'https://{hostname}/v2api/1/lesson/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}

        page = 0
        per_page = 100  # Количество записей на странице
        trial_lessons = []

        while True:
            lessons_params = {
                'filters': {
                    "lesson_type_id": "3",
                    "status": "finished"
                },
                'page': page,
                'per-page': per_page
            }

            response = requests.post(lessons_url, headers=headers, json=lessons_params)

            if response.status_code == 200:
                lessons = response.json().get('items', [])
                if not lessons:
                    break
                trial_lessons.extend(lessons)
                page += 1
            else:
                print('Ошибка получения уроков:', response.text)
                break

        # Подсчет количества уроков по датам
        lesson_counts = {}
        for lesson in trial_lessons:
            lesson_date = lesson['date']
            if lesson_date in lesson_counts:
                lesson_counts[lesson_date] += 1
            else:
                lesson_counts[lesson_date] = 1

        # Сохранение данных в CSV файл
        with open('trial_lessons.csv', 'w', newline='') as csvfile:
            fieldnames = ['Date', 'Trial Lessons Count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for date, count in lesson_counts.items():
                writer.writerow({'Date': date, 'Trial Lessons Count': count})

            # Добавление даты/времени обновления
            writer.writerow({})
            writer.writerow({'Date': '# Last updated:', 'Trial Lessons Count': datetime.now().isoformat()})

        print('Список проведенных пробных уроков сохранен в trial_lessons.csv')
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_trial_lessons()
