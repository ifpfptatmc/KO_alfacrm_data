import requests
import os

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
        
        # Запрос логов для получения значений entity
        logs_url = f'https://{hostname}/v2api/1/log/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}

        page = 0
        per_page = 100  # Количество записей на странице
        entities = set()

        while True:
            logs_params = {
                'page': page,
                'per-page': per_page
            }
            
            response = requests.post(logs_url, headers=headers, json=logs_params)

            if response.status_code == 200:
                logs = response.json().get('items', [])
                if not logs:
                    break

                for log in logs:
                    entities.add(log['entity'])
                
                if len(logs) < per_page:
                    break
                
                page += 1
            else:
                print('Ошибка получения логов:', response.text)
                break

        # Вывод всех уникальных значений entity
        print('Перечень всех значений entity:')
        for entity in entities:
            print(entity)
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_entities()
