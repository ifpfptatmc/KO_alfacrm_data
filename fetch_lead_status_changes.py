import requests
import csv
import os
from datetime import datetime, timedelta

def fetch_lead_status_changes():
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
        
        # Даты
        start_date = '2024-07-01'
        end_date = '2024-07-10'

        # Запрос логов для получения истории изменений статусов лидов
        logs_url = f'https://{hostname}/v2api/log/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}

        logs_params = {
            'filters': {
                'entity': 'customer',
                'date_from': start_date,
                'date_to': end_date,
                'fields_old': {'lead_status_id': {'$exists': True}},
                'fields_new': {'lead_status_id': {'$exists': True}}
            },
            'page': 0,
            'per-page': 100
        }
        
        lead_changes = []
        while True:
            response = requests.post(logs_url, headers=headers, json=logs_params)
            if response.status_code != 200:
                print('Ошибка получения логов:', response.text)
                break
            
            logs = response.json().get('items', [])
            if not logs:
                break

            for log in logs:
                fields_old = log.get('fields_old', [])
                fields_new = log.get('fields_new', [])
                old_status = next((field['lead_status_id'] for field in fields_old if 'lead_status_id' in field), None)
                new_status = next((field['lead_status_id'] for field in fields_new if 'lead_status_id' in field), None)
                if old_status and new_status:
                    lead_changes.append({
                        'Lead ID': log['entity_id'],
                        'Old Status ID': old_status,
                        'New Status ID': new_status,
                        'Change Date': log['date_time']
                    })

            logs_params['page'] += 1

        # Сохранение данных в CSV файл
        csv_file_path = 'lead_status_changes.csv'
        with open(csv_file_path, 'w', newline='') as csvfile:
            fieldnames = ['Lead ID', 'Old Status ID', 'New Status ID', 'Change Date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(lead_changes)

        # Проверка содержания файла
        if lead_changes:
            print(f'Список изменений статусов лидов сохранен в {csv_file_path}')
        else:
            print('Нет изменений статусов лидов за указанный период')
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_lead_status_changes()
