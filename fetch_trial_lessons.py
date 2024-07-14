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
        
        # Запрос для получения уроков
        lessons_url = f'https://{hostname}/v2api/1/lesson/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}
        
        page = 0
        per_page = 100 # Количество записей на странице
        lessons_data = []

        while True:
            lessons_params = {
                'filters': {
                    'lesson_type_id': 3,
                    'status': 'finished',
                },
                'page': page,
                'per-page': per_page
            }
            
            response = requests.post(lessons_url, headers=headers, json=lessons_params)

            if response.status_code == 200:
                lessons = response.json().get('items', [])
                if not lessons:
                    break
                
                lessons_data.extend(lesson for lesson in lessons if 'date' in lesson)
                
                if len(lessons) < per_page:
                    break

                page += 1
            else:
                print('Ошибка получения уроков:', response.text)
                break

        # Сохранение данных в CSV файл
        with open('trial_lessons.csv', 'w', newline='') as csvfile:
            fieldnames = ['Дата', 'Количество']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            start_date = datetime(2024, 6, 13)
            end_date = datetime.now() - timedelta(days=1)

            lessons_by_date = {start_date + timedelta(days=i): 0 for i in range((end_date - start_date).days + 1)}

            for lesson in lessons_data:
                date = datetime.strptime(lesson['date'], '%Y-%m-%d')
                lessons_by_date[date] += 1

            for date, count in sorted(lessons_by_date.items()):
                writer.writerow({'Дата': date.strftime('%Y-%m-%d'), 'Количество': count})
            
            writer.writerow({'Дата': '# Last updated', 'Количество': datetime.now().isoformat()})
        
        print('Список пробных уроков сохранен в trial_lessons.csv')
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_trial_lessons()
