import requests
import json
import csv
import os
from datetime import datetime

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
        
        # Запрос уроков с фильтрацией
        lessons_url = f'https://{hostname}/v2api/1/lesson'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}
        
        payload = {
            "lesson_type_id": 3,
            "status": 3,
            "date_from": "13.06.2024",  # начальная дата
            "date_to": datetime.now().strftime("%d.%m.%Y")  # текущая дата
        }
        
        response = requests.post(lessons_url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            lessons = response.json().get('items', [])
            
            # Сохранение данных в CSV файл
            with open('filtered_lessons.csv', 'w', newline='') as csvfile:
                fieldnames = ['lesson_id', 'lesson_type_id', 'status', 'date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for lesson in lessons:
                    writer.writerow({
                        'lesson_id': lesson.get('id'),
                        'lesson_type_id': lesson.get('lesson_type_id'),
                        'status': lesson.get('status'),
                        'date': lesson.get('date')
                    })
            print('Список уроков сохранен в filtered_lessons.csv')
        else:
            print('Ошибка получения уроков:', response.text)
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_lessons()
