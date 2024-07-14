import requests
import csv
import os

def fetch_lesson_statuses():
    email = os.getenv('ALPHA_CRM_EMAIL')
    api_key = os.getenv('ALPHA_CRM_API_KEY')
    hostname = os.getenv('ALPHA_CRM_HOSTNAME')
    account_id = os.getenv('ALPHA_CRM_ACCOUNT_ID')

    # Авторизация
    auth_url = f'https://{hostname}/v2api/auth/login'
    auth_data = {'email': email, 'api_key': api_key}
    response = requests.post(auth_url, json=auth_data)

    if response.status_code == 200:
        token = response.json().get('token')
        print('Токен:', token)
        
        # Запрос всех возможных статусов уроков
        lesson_status_url = f'https://{hostname}/v2api/{account_id}/lesson/statuses'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}
        
        response = requests.get(lesson_status_url, headers=headers)
        
        if response.status_code == 200:
            statuses = response.json()
            
            # Сохранение данных в CSV файл
            with open('lesson_statuses.csv', 'w', newline='') as csvfile:
                fieldnames = ['status_id', 'name']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for status in statuses:
                    writer.writerow({'status_id': status['id'], 'name': status['name']})
            print('Список статусов уроков сохранен в lesson_statuses.csv')
        else:
            print('Ошибка получения статусов уроков:', response.text)
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_lesson_statuses()
