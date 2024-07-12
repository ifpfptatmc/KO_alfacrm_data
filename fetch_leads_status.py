import requests
import csv
import os

def fetch_leads_status():
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
        
        # Запрос на получение всех лидов и их статусов
        leads_url = f'https://{hostname}/v2api/lead/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}

        leads_params = {
            'filters': {},
            'page': 0,
            'per_page': 100
        }
        
        leads_data = []

        while True:
            response = requests.post(leads_url, headers=headers, json=leads_params)
            if response.status_code == 200:
                leads = response.json().get('items', [])
                if not leads:
                    break
                for lead in leads:
                    lead_id = lead.get('id')
                    status_id = lead.get('lead_status_id')
                    leads_data.append({'Lead ID': lead_id, 'Status ID': status_id})
                leads_params['page'] += 1
            else:
                print('Ошибка получения лидов:', response.text)
                break
        
        # Сохранение данных в CSV файл
        with open('leads_status.csv', 'w', newline='') as csvfile:
            fieldnames = ['Lead ID', 'Status ID']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for data in leads_data:
                writer.writerow(data)
        print('Список лидов и их статусов сохранен в leads_status.csv')
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_leads_status()
