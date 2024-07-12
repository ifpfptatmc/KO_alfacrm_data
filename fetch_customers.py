import requests
import csv
import os

def fetch_customers():
    email = os.getenv('ALPHA_CRM_EMAIL')
    api_key = os.getenv('ALPHA_CRM_API_KEY')
    hostname = os.getenv('ALPHA_CRM_HOSTNAME')

    auth_url = f'https://{hostname}/v2api/auth/login'
    auth_data = {'email': email, 'api_key': api_key}

    try:
        auth_response = requests.post(auth_url, json=auth_data)
        auth_response.raise_for_status()
        token = auth_response.json().get('token')
        if not token:
            print('Ошибка: Токен не получен')
            return
        print(f'Токен: {token}')
    except requests.exceptions.RequestException as e:
        print(f'Ошибка авторизации: {e}')
        return

    customers_url = f'https://{hostname}/v2api/customer/index'
    params = {
        'filters': {'lead_status_id': 2},
        'page': 0
    }
    headers = {
        'X-ALFACRM-TOKEN': token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(customers_url, headers=headers, json=params)
        response.raise_for_status()
        customers = response.json().get('items', [])
        customer_ids = [customer['id'] for customer in customers]
        print(f'Список ID клиентов на стадии с ID 2: {customer_ids}')
    except requests.exceptions.RequestException as e:
        print(f'Ошибка получения списка клиентов: {e}')
        return

    file_path = 'customers_stage_2.csv'
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = ['customer_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for customer_id in customer_ids:
            writer.writerow({'customer_id': customer_id})

    print(f'CSV файл создан: {file_path}')

if __name__ == '__main__':
    fetch_customers()
