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
        logs_url = f'https://{hostname}/v2api/log/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}

        # Конкретные даты
        start_date = '2024-07-01'
        end_date = '2024-07-10'

        logs_params = {
            'filters': {
                'entity': 'lead',
                'date_time': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
        }

        response = requests.post(logs_url, headers=headers, json=logs_params)

        if response.status_code == 200:
            logs = response.json().get('items', [])
            lead_changes = []

            for log in logs:
                fields_old = log.get('fields_old')
                fields_new = log.get('fields_new')
                
                if fields_old is not None and isinstance(fields_old, list):
                    old_status = next((field['lead_status_id'] for field in fields_old if isinstance(field, dict) and 'lead_status_id' in field), None)
                else:
                    old_status = None

                if fields_new is not None and isinstance(fields_new, list):
                    new_status = next((field['lead_status_id'] for field in fields_new if isinstance(field, dict) and 'lead_status_id' in field), None)
                else:
                    new_status = None

                if old_status or new_status:
                    lead_changes.append({
                        'Lead ID': log['entity_id'],
                        'Old Status ID': old_status,
                        'New Status ID': new_status,
                        'Change Date': log['date_time']
                    })
            
            # Сохранение данных в CSV файл
            with open('lead_status_changes.csv', 'w', newline='') as csvfile:
                fieldnames = ['Lead ID', 'Old Status ID', 'New Status ID', 'Change Date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for change in lead_changes:
                    writer.writerow(change)
            print('Изменения статусов лидов сохранены в lead_status_changes.csv')
        else:
            print('Ошибка получения логов:', response.text)
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_lead_status_changes()
