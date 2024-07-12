import requests
import csv
import os
from datetime import datetime

def fetch_entities():
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
        
        # Запрос логов для получения всех значений entity
        logs_url = f'https://{hostname}/v2api/log/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}

        logs_params = {
            'filters': {},
            'page': 0,
            'per_page': 100
        }
        
        entities = set()
        
        while True:
            response = requests.post(logs_url, headers=headers, json=logs_params)
            if response.status_code == 200:
                logs = response.json().get('items', [])
                if not logs:
                    break
                for log in logs:
                    entities.add(log['entity'])
                logs_params['page'] += 1
            else:
                print('Ошибка получения логов:', response.text)
                break
        
        # Сохранение данных в CSV файл
        with open('entities_list.csv', 'w', newline='') as csvfile:
            fieldnames = ['Entity']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for entity in entities:
                writer.writerow({'Entity': entity})
        print('Список значений entity сохранен в entities_list.csv')
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_entities()
