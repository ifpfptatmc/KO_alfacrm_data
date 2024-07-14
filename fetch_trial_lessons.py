import requests
import csv
import os
from datetime import datetime, timedelta

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
        
        # Установим даты
        start_date = datetime(2024, 6, 13)
        end_date = datetime.now() - timedelta(days=1)
        
        date_generated = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        
        # Подготовка CSV файла
        with open('trial_lessons.csv', 'w', newline='') as csvfile:
            fieldnames = ['date', 'lesson_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for date in date_generated:
                date_str = date.strftime('%Y-%m-%d')
                
                # Запрос уроков
                lessons_url = f'https://{hostname}/v2api/1/lesson/index'
                headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}
                lessons_params = {
                    'filters': {
                        'lesson_type_id': 3,
                        'status': 'finished',
                        'date_from': date_str,
                        'date_to': date_str
                    }
                }
                
                response = requests.post(lessons_url, headers=headers, json=lessons_params)
                
                if response.status_code == 200:
                    lessons = response.json().get('items', [])
                    lesson_count = len(lessons)
                else:
                    print('Ошибка получения уроков:', response.text)
                    lesson_count = 0
                
                writer.writerow({'date': date_str, 'lesson_count': lesson_count})
        
        print('Список уроков сохранен в trial_lessons.csv')
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_trial_lessons()
