import requests
import csv
import os

def fetch_customers():
    email = os.getenv('ALPHA_CRM_EMAIL')
    api_key = os.getenv('ALPHA_CRM_API_KEY')
    hostname = os.getenv('ALPHA_CRM_HOSTNAME')

    # URL для авторизации
    auth_url = f'https://{hostname}/v2api/auth/login'
    auth_data = {
        'email': email,
        'api_key': api_key
    }

    # Выполнение запроса на авторизацию
    response = requests.post(auth_url, json=auth_data)
    if response.status_code == 200:
        token = response.json().get('token')
        print('Токен получен:', token)

        # URL для запроса списка клиентов
        customers_url = f'https://{hostname}/v2api/customer/index'
        params = {
            'filters': {
                'lead_status_id': 2  # ID стадии
            },
            'page': 0  # Номер страницы
        }

        headers = {
            'X-ALFACRM-TOKEN': token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.post(customers_url, headers=headers, json=params)
        if response.status_code == 200:
            customers = response.json().get('items', [])
            customer_ids = [customer['id'] for customer in customers]
            print('Список ID клиентов на стадии с ID 2:', customer_ids)

            # Сохранение данных в CSV
            file_path = 'customers_stage_2.csv'
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['customer_id']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for customer_id in customer_ids:
                    writer.writerow({'customer_id': customer_id})

            print(f"Данные успешно сохранены в {file_path}")
        else:
            print('Ошибка получения списка клиентов:', response.text)
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_customers()
