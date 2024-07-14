import requests
import csv
import os
from datetime import datetime, timedelta

def fetch_filtered_lessons():
    email = os.getenv('ALPHA_CRM_EMAIL')
    api_key = os.getenv('ALPHA_CRM_API_KEY')
    hostname = os.getenv('ALPHA_CRM_HOSTNAME')
    
    # Authorize
    auth_url = f'https://{hostname}/v2api/auth/login'
    auth_data = {'email': email, 'api_key': api_key}
    response = requests.post(auth_url, json=auth_data)
    
    if response.status_code == 200:
        token = response.json().get('token')
        
        # Set filters
        start_date = "2024-06-13"
        end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        filters = {
            "lesson_type_id": 3,
            "status": 3,
            "date_from": start_date,
            "date_to": end_date
        }

        lessons_url = f'https://{hostname}/v2api/1/lesson/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}
        page = 0
        per_page = 100
        all_lessons = []

        while True:
            lesson_params = {
                'filters': filters,
                'page': page,
                'per_page': per_page
            }

            response = requests.post(lessons_url, headers=headers, json=lesson_params)

            if response.status_code == 200:
                lessons = response.json().get('items', [])
                if not lessons:
                    break
                all_lessons.extend(lessons)
                page += 1
            else:
                print(f'Error fetching lessons: {response.text}')
                break
        
        # Count lessons per day
        lesson_count = {}
        for lesson in all_lessons:
            lesson_date = lesson.get('date')
            if lesson_date in lesson_count:
                lesson_count[lesson_date] += 1
            else:
                lesson_count[lesson_date] = 1

        # Fill in missing dates
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str not in lesson_count:
                lesson_count[date_str] = 0
            current_date += timedelta(days=1)

        # Save to CSV
        with open('trial_lessons.csv', 'w', newline='') as csvfile:
            fieldnames = ['date', 'lesson_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for date, count in sorted(lesson_count.items()):
                writer.writerow({'date': date, 'lesson_count': count})

        print('Lesson data saved to trial_lessons.csv')

    else:
        print(f'Error authenticating: {response.text}')

if __name__ == "__main__":
    fetch_filtered_lessons()
