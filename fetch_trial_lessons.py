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
        
        lessons_params = {
            'filters': {
                'lesson_type_id': 3,
                'status': 'finished'
            }
        }
        
        response = requests.post(lessons_url, headers=headers, json=lessons_params)

        if response.status_code == 200:
            lessons = response.json().get('items', [])
            lessons_by_date = {}

            for lesson in lessons:
                date = lesson['date']
                if date not in lessons_by_date:
                    lessons_by_date[date] = 0
                lessons_by_date[date] += 1
            
            # Добавляем текущую дату и время к имени файла
            now = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'trial_lessons_{now}.csv'

            # Сохранение данных в CSV файл
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['Date', 'Trial Lessons Count']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for date, count in lessons_by_date.items():
                    writer.writerow({'Date': date, 'Trial Lessons Count': count})
            print(f'Список пробных уроков сохранен в {filename}')
        else:
            print('Ошибка получения уроков:', response.text)
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_trial_lessons()
