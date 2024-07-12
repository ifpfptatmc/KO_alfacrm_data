import requests
import csv
import os

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
        print('Авторизация успешна. Токен получен:', token)
        
        # Запрос на получение списка лидов, побывавших на стадии с ID 4
        leads_url = f'https://{hostname}/v2api/lead/index'
        params = {
            'filters': {
                'stage_id': 4  # ID стадии
            },
            'page': 0,  # Номер страницы (начинаем с 0)
            'limit': 100  # Максимальное количество записей на страницу
        }
        headers = {
            'X-ALFACRM-TOKEN': token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        lead_ids = []

        while True:
            response = requests.post(leads_url, headers=headers, json=params)
            if response.status_code == 200:
                leads = response.json().get('items', [])
                if not leads:
                    break

                for lead in leads:
                    lead_ids.append(lead['id'])

                params['page'] += 1
            else:
                print('Ошибка получения списка лидов:', response.text)
                break

        # Сохранение ID лидов в CSV файл
        with open('leads_stage_4.csv', 'w', newline='') as csvfile:
            fieldnames = ['lead_id']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for lead_id in lead_ids:
                writer.writerow({'lead_id': lead_id})

        print('Список ID лидов, побывавших на стадии с ID 4, успешно сохранён в leads_stage_4.csv')
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_leads()
