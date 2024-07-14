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
        
        # Установка дат
        start_date = datetime(2024, 6, 13)
        end_date = datetime.now() - timedelta(days=1)
        current_date = start_date
        
        results = []
        
        while current_date <= end_date:
            date_str = current_date.strftime('%d.%m.%Y')
            logs_url = f'https://{hostname}/v2api/1/lesson/index'
            headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}

            logs_params = {
                "filters": {
                    "lesson_type_id": 3,
                    "status": "finished",
                    "date_from": date_str,
                    "date_to": date_str
                }
            }
            
            response = requests.post(logs_url, headers=headers, json=logs_params)

            if response.status_code == 200:
                lessons = response.json().get('items', [])
                lesson_count = len(lessons)
                results.append({"date": date_str, "lesson_count": lesson_count})
            else:
                print('Ошибка получения уроков:', response.text)
                
            current_date += timedelta(days=1)
        
        # Сохранение данных в CSV файл
        with open('trial_lessons.csv', 'w', newline='') as csvfile:
            fieldnames = ['Date', 'Lesson Count', 'Last updated']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                result['Last updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow(result)
        
        print('Список уроков сохранен в trial_lessons.csv')
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_trial_lessons()
