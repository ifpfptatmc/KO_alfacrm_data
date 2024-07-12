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
        
        # Запрос логов для получения изменений статусов лидов за последние 7 дней
        logs_url = f'https://{hostname}/v2api/1/log/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}

        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        logs_params = {
            'filters': {
                'entity': 'lead',
                'date_time': {
                    'from': start_date.strftime('%Y-%m-%d'),
                    'to': end_date.strftime('%Y-%m-%d')
                }
            },
            'fields_old': ['lead_status_id'],
            'fields_new': ['lead_status_id']
        }
        
        response = requests.post(logs_url, headers=headers, json=logs_params)

        if response.status_code == 200:
            logs = response.json().get('items', [])
            lead_status_changes = []
            
            for log in logs:
                old_status = next((field['lead_status_id'] for field in log['fields_old'] if 'lead_status_id' in field), None)
                new_status = next((field['lead_status_id'] for field in log['fields_new'] if 'lead_status_id' in field), None)
                if old_status is not None and new_status is not None:
                    lead_status_changes.append({
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
                for change in lead_status_changes:
                    writer.writerow(change)
            print('Данные изменений статусов лидов сохранены в lead_status_changes.csv')
        else:
            print('Ошибка получения логов:', response.text)
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_lead_status_changes()
