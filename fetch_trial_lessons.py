import requests
import json
import csv
import os
from datetime import datetime, timedelta

def fetch_lessons():
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
        
        # Установка дат
        start_date = datetime(2024, 6, 13)
        end_date = datetime.now() - timedelta(days=1)
        current_date = start_date

        # Подготовка для сбора данных
        lesson_count = {}

        while current_date <= end_date:
            date_str = current_date.strftime('%d.%m.%Y')
            lessons_url = f'https://{hostname}/v2api/1/lesson'
            headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}
            
            payload = {
                "lesson_type_id": 3,
                "status": 3,
                "date_from": date_str,
                "date_to": date_str
            }
            
            response = requests.post(lessons_url, headers=headers, data=json.dumps(payload))

            if response.status_code == 200:
                lessons = response.json().get('items', [])
                lesson_count[date_str] = len(lessons)
            else:
                print(f'Ошибка получения уроков за {date_str}:', response.text)
                lesson_count[date_str] = 0

            current_date += timedelta(days=1)

        # Сохранение данных в CSV файл
        with open('trial_lessons.csv', 'w', newline='') as csvfile:
            fieldnames = ['date', 'lesson_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for date, count in sorted(lesson_count.items(), key=lambda x: datetime.strptime(x[0], '%d.%m.%Y')):
                writer.writerow({'date': date, 'lesson_count': count})
            writer.writerow({'date': 'Last updated', 'lesson_count': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

        print('Список уроков сохранен в trial_lessons.csv')
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_lessons()
