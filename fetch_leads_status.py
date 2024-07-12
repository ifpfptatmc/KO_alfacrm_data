import requests
import csv
import os

def fetch_all_leads_status():
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
        
        # Запрос логов для получения статусов лидов
        logs_url = f'https://{hostname}/v2api/log/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}

        page = 0
        per_page = 100
        lead_statuses = []

        while True:
            logs_params = {
                'filters': {
                    'entity': 'customer',
                    'fields_new': {
                        'lead_status_id': {'$exists': True}
                    }
                },
                'page': page,
                'per-page': per_page
            }
            
            response = requests.post(logs_url, headers=headers, json=logs_params)

            if response.status_code == 200:
                logs = response.json().get('items', [])
                if not logs:
                    break
                for log in logs:
                    lead_id = log['entity_id']
                    status_id = log['fields_new'].get('lead_status_id')
                    if status_id:
                        lead_statuses.append({'Lead ID': lead_id, 'Status ID': status_id})
                
                page += 1
            else:
                print('Ошибка получения логов:', response.text)
                break

        # Сохранение данных в CSV файл
        with open('leads_status.csv', 'w', newline='') as csvfile:
            fieldnames = ['Lead ID', 'Status ID']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for lead_status in lead_statuses:
                writer.writerow(lead_status)

        print('Список статусов лидов сохранен в leads_status.csv')
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_all_leads_status()
