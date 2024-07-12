import requests
import csv
import os
from datetime import datetime

def fetch_leads():
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
        
        # Запрос логов для получения лидов
        logs_url = f'https://{hostname}/v2api/1/log/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}

        logs_params = {
            'filters': {
                'entity': 'Lead',
                'fields_new': {
                    'lead_status_id': '8'  # ID стадии
                }
            }
        }
        
        response = requests.post(logs_url, headers=headers, json=logs_params)

        if response.status_code == 200:
            logs = response.json().get('items', [])
            lead_ids = [log['entity_id'] for log in logs]
            
            # Сохранение данных в CSV файл
            with open('leads_on_stage_8.csv', 'w', newline='') as csvfile:
                fieldnames = ['Lead ID']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for lead_id in lead_ids:
                    writer.writerow({'Lead ID': lead_id})
            print('Список ID лидов сохранен в leads_on_stage_8.csv')
        else:
            print('Ошибка получения логов:', response.text)
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_leads()
