import requests
import json
import csv
import os
from datetime import datetime

def fetch_leads_with_stage_8():
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
        
        logs_url = f'https://{hostname}/v2api/1/log'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}
        
        payload = {
            "entity": "Customer",
            "event": 2,
            "fields_new": {
                "lead_status_id": 8
            }
        }
        
        response = requests.post(logs_url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            logs = response.json().get('items', [])
            
            # Сохранение данных в CSV файл
            with open('leads_stage_8.csv', 'w', newline='') as csvfile:
                fieldnames = ['lead_id', 'lead_source_id', 'date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for log in logs:
                    writer.writerow({
                        'lead_id': log.get('entity_id'),
                        'source': log.get('lead_source_id'),
                        'date': log.get('created_at')
                    })
                writer.writerow({'lead_id': 'Last updated', 'source': '', 'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

            print('Список лидов со стадией 8 сохранен в leads_stage_8.csv')
        else:
            print(f'Ошибка получения логов: {response.text}')
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_leads_with_stage_8()
