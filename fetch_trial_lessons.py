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

        lessons_params = {
            'filters': {
            },
            'fields': ['date']
        }
        
        response = requests.post(lessons_url, headers=headers, json=lessons_params)

        if response.status_code == 200:
            lessons = response.json().get('items', [])
            
            # Подсчет количества уроков по датам
            date_counts = {}
            for lesson in lessons:
                lesson_date = lesson.get('date')
                if lesson_date:
                    date_counts[lesson_date] = date_counts.get(lesson_date, 0) + 1
            
            # Сохранение данных в CSV файл
            with open('trial_lessons.csv', 'w', newline='') as csvfile:
                fieldnames = ['Date', 'Number of Trial Lessons']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for lesson_date, count in date_counts.items():
                    writer.writerow({'Date': lesson_date, 'Number of Trial Lessons': count})
            print('Список пробных уроков сохранен в trial_lessons.csv')
        else:
            print('Ошибка получения данных о пробных уроках:', response.text)
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_trial_lessons()
