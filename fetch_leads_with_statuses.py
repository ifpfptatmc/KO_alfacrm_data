import requests
import json
import csv
import os
from datetime import datetime

def fetch_leads_with_statuses():
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
        
        logs_url = f'https://{hostname}/v2api/1/log/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}
        
        data = {
            "entity": "Customer",
            "page": 0  # Начальная страница
        }
        
        all_logs = []

        while True:
            response = requests.post(logs_url, headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                logs = response.json().get('items', [])
                if not logs:
                    break
                all_logs.extend(logs)
                data['page'] += 1
            else:
                print(f'Ошибка получения логов: {response.text}')
                break
            
        # Сохранение данных в CSV файл
        with open('leads_statuses.csv', 'w', newline='') as csvfile:
            fieldnames = ['lead_id', 'status_id', 'lead_source_id', 'date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for log in all_logs:
                if 'fields_new' in log:
                    fields_new = log['fields_new']
                    if isinstance(fields_new, list):
                        for field in fields_new:
                            if isinstance(field, dict) and 'lead_status_id' in field:
                                writer.writerow({
                                    'lead_id': log.get('entity_id'),
                                    'status_id': field['lead_status_id'],
                                    'lead_source_id': log.get('lead_source_id'),
                                    'date': log.get('date_time')
                                })
                    elif isinstance(fields_new, dict) and 'lead_status_id' in fields_new:
                        writer.writerow({
                            'lead_id': log.get('entity_id'),
                            'status_id': fields_new['lead_status_id'],
                            'lead_source_id': fields_new['lead_source_id'],
                            'date': log.get('date_time')
                        })
            writer.writerow({'lead_id': 'Last updated', 'status_id': '', 'lead_source_id': '', 'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

        print('Список лидов и их статусов сохранен в leads_statuses.csv')
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_leads_with_statuses()
