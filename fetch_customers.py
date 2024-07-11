import requests
import csv
import os

def fetch_data():
    email = os.getenv('ALPHA_CRM_EMAIL')
    api_key = os.getenv('ALPHA_CRM_API_KEY')
    hostname = os.getenv('ALPHA_CRM_HOSTNAME')

    # URL для авторизации
    auth_url = f'https://{hostname}/v2api/auth/login'
    auth_data = {'email': email, 'api_key': api_key}

    # Авторизация и получение токена
    response = requests.post(auth_url, json=auth_data)
    if response.status_code == 200:
        token = response.json().get('token')
        print('Токен:', token)

        # URL для получения списка клиентов
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

        # Получение клиентов
        response = requests.post(customers_url, headers=headers, json=params)
        if response.status_code == 200:
            customers = response.json().get('items', [])
            customer_ids = [customer['id'] for customer in customers]
            print('ID клиентов на стадии 2:', customer_ids)

            # Сохранение в CSV
            with open('customers_stage_2.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Customer ID'])
                for customer_id in customer_ids:
                    writer.writerow([customer_id])
        else:
            print('Ошибка получения списка клиентов:', response.text)
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_data()
