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
        
        # Запрос уроков
        lessons_url = f'https://{hostname}/v2api/1/lesson/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}

        # Задаем диапазон дат
        start_date = datetime(2024, 6, 13)
        end_date = datetime.now() - timedelta(days=1)

        # Инициализация данных
        date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        lesson_data = {date.strftime('%Y-%m-%d'): 0 for date in date_range}

        page = 0
        per_page = 100  # Количество записей на странице

        while True:
            lessons_params = {
                'filters': {
                    'lesson_type_id': 3,
                    'status': 'finished',
                    'date_from': start_date.strftime('%d.%m.%Y'),
                    'date_to': end_date.strftime('%d.%m.%Y')
                },
                'page': page,
                'per-page': per_page
            }
            
            response = requests.post(lessons_url, headers=headers, json=lessons_params)

            if response.status_code == 200:
                lessons = response.json().get('items', [])
                if not lessons:
                    break

                for lesson in lessons:
                    lesson_date = lesson['date']
                    if lesson_date in lesson_data:
                        lesson_data[lesson_date] += 1

                page += 1
                if len(lessons) < per_page:
                    break
            else:
                print('Ошибка получения уроков:', response.text)
                break

        # Сохранение данных в CSV файл
        with open('trial_lessons.csv', 'w', newline='') as csvfile:
            fieldnames = ['date', 'lesson_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for date, count in lesson_data.items():
                writer.writerow({'date': date, 'lesson_count': count})
            writer.writerow({'date': 'Last updated', 'lesson_count': datetime.now().isoformat()})
        print('Данные о пробных уроках сохранены в trial_lessons.csv')
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_trial_lessons()
