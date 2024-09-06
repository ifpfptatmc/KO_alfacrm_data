import requests
import json
import csv
import os
from datetime import datetime

def fetch_customers_with_status_and_source():
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
        
        customers_url = f'https://{hostname}/v2api/1/customer/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}
        
        data = {
            "page": 0,  # Начальная страница
            "is_study": 1,
            "removed": 1  # Включить архивных клиентов
        }
        
        all_customers = []

        while True:
            response = requests.post(customers_url, headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                customers = response.json().get('items', [])
                if not customers:
                    break
                all_customers.extend(customers)
                data['page'] += 1
            else:
                print(f'Ошибка получения данных клиентов: {response.text}')
                break
            
        # Сохранение данных в CSV файл
        with open('customers_statuses_sources.csv', 'w', newline='') as csvfile:
            fieldnames = ['customer_id', 'status_id', 'source_id', 'custom_first_sum', 'custom_first_tariff', 'datakontrakta']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for customer in all_customers:
                writer.writerow({
                    'customer_id': customer.get('id'),
                    'status_id': customer.get('lead_status_id'),
                    'source_id': customer.get('lead_source_id'),
                    'custom_first_sum': customer.get('custom_first_sum'),
                    'custom_first_tariff': customer.get('custom_first_tariff'),
                    'datakontrakta': customer.get('datakontrakta')
                })
            writer.writerow({'customer_id': 'Last updated', 'status_id': '', 'source_id': '', 'custom_first_sum': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'custom_first_tariff': '', 'datakontrakta': ''})

        print('Список клиентов с их текущими статусами, источниками и тарифами сохранен в customers_statuses_sources.csv')
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_customers_with_status_and_source()
