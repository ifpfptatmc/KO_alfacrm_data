import requests
import csv
import os
from datetime import datetime

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
        
        # Запрос логов для получения изменений статусов лидов
        logs_url = f'https://{hostname}/v2api/1/log/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}

        logs_params = {
            'filters': {
                'entity': 'lead',
                'date_time': {
                    '$gte': '2024-07-01',
                    '$lte': '2024-07-10'
                },
                'event': 'update',
                'fields_new.lead_status_id': {
                    '$exists': True
                }
            },
            'sort': 'date_time'
        }
        
        response = requests.post(logs_url, headers=headers, json=logs_params)

        if response.status_code == 200:
            logs = response.json().get('items', [])
            lead_status_changes = []

            for log in logs:
                lead_id = log.get('entity_id')
                fields_old = log.get('fields_old', [])
                fields_new = log.get('fields_new', [])

                old_status = next((field['lead_status_id'] for field in fields_old if isinstance(field, dict) and 'lead_status_id' in field), None)
                new_status = next((field['lead_status_id'] for field in fields_new if isinstance(field, dict) and 'lead_status_id' in field), None)
                change_date = log.get('date_time')

                if old_status is not None and new_status is not None:
                    lead_status_changes.append({
                        'Lead ID': lead_id,
                        'Old Status ID': old_status,
                        'New Status ID': new_status,
                        'Change Date': change_date
                    })
            
            # Сохранение данных в CSV файл
            with open('lead_status_changes.csv', 'w', newline='') as csvfile:
                fieldnames = ['Lead ID', 'Old Status ID', 'New Status ID', 'Change Date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for change in lead_status_changes:
                    writer.writerow(change)
            print('История изменений статусов лидов сохранена в lead_status_changes.csv')
        else:
            print('Ошибка получения логов:', response.text)
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_lead_status_changes()
