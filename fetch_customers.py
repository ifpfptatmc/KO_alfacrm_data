import requests
import csv
import os

# Данные для авторизации
email = os.getenv('ALPHA_CRM_EMAIL')
api_key = os.getenv('ALPHA_CRM_API_KEY')
hostname = os.getenv('ALPHA_CRM_HOSTNAME')

# URL для авторизации
auth_url = f'https://{hostname}/v2api/auth/login'

# Данные для запроса
auth_data = {
    'email': email,
    'api_key': api_key
}

# Выполнение запроса на авторизацию
response = requests.post(auth_url, json=auth_data)

if response.status_code == 200:
    token = response.json().get('token')
    print('Токен:', token)
    
    # URL для запроса списка клиентов
    customers_url = f'https://{hostname}/v2api/customer/index'

    # Параметры запроса
    params = {
        'filters': {
            'lead_status_id': 2  # ID стадии
        },
        'page': 0  # Номер страницы
    }

    # Заголовки запроса
    headers = {
        'X-ALFACRM-TOKEN': token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Выполнение запроса на получение списка клиентов
    response = requests.post(customers_url, headers=headers, json=params)

    if response.status_code == 200:
        customers = response.json().get('items', [])
        customer_ids = [customer['id'] for customer in customers]
        print('Список ID клиентов на стадии с ID 2:', customer_ids)
        
        # Запись данных в CSV файл
        with open('customers_stage_2.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Customer ID'])
            for customer_id in customer_ids:
                writer.writerow([customer_id])
        print("Данные успешно экспортированы в customers_stage_2.csv")
    else:
        print('Ошибка получения списка клиентов:', response.text)
else:
    print('Ошибка авторизации:', response.text)
