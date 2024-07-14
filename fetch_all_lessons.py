import requests
import csv
import os
from datetime import datetime

def fetch_all_lessons():
    email = os.getenv('ALPHA_CRM_EMAIL')
    api_key = os.getenv('ALPHA_CRM_API_KEY')
    hostname = os.getenv('ALPHA_CRM_HOSTNAME')
    
    # Авторизация
    auth_url = f'https://{hostname}/v2api/auth/login'
    auth_data = {'email': email, 'api_key': api_key}
    response = requests.post(auth_url, json=auth_data)
    
    if response.status_code == 200:
        token = response.json().get('token')
        
        lessons_url = f'https://{hostname}/v2api/1/lesson/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}
        page = 0
        per_page = 100
        all_lessons = []

        while True:
            lesson_params = {
                'page': page,
                'per_page': per_page
            }

            response = requests.post(lessons_url, headers=headers, json=lesson_params)

            if response.status_code == 200:
                lessons = response.json().get('items', [])
                if not lessons:
                    break
                all_lessons.extend(lessons)
                page += 1
            else:
                print(f'Ошибка получения уроков: {response.text}')
                break
        
        # Подсчет уроков по дням
        lesson_count = {}
        for lesson in all_lessons:
            lesson_date = lesson.get('date')
            if lesson_date in lesson_count:
                lesson_count[lesson_date] += 1
            else:
                lesson_count[lesson_date] = 1

        # Сохранение в CSV
        with open('all_lessons.csv', 'w', newline='') as csvfile:
            fieldnames = ['date', 'lesson_count', 'last_updated']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for date, count in sorted(lesson_count.items()):
                writer.writerow({'date': date, 'lesson_count': count, 'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')})

        print('Данные уроков сохранены в all_lessons.csv')

    else:
        print(f'Ошибка авторизации: {response.text}')

if __name__ == "__main__":
    fetch_all_lessons()
