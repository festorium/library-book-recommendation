import time
import requests
import pytest

BASE_URL = 'http://localhost:8000'

RECOMMENDATIONS_ENDPOINT = '/recommendations'

USER_ID = '' 

JWT_TOKEN = '' 

@pytest.mark.parametrize('user_id', [USER_ID])
def test_recommendations_response_time(user_id):
    
    headers = {
        'Authorization': f'Bearer {JWT_TOKEN}',
        'Content-Type': 'application/json'
    }

    params = {
        'user_id': user_id
    }

    start_time = time.time()
    
    response = requests.get(BASE_URL + RECOMMENDATIONS_ENDPOINT, headers=headers, params=params)

    end_time = time.time()
    
    response_time = end_time - start_time

    assert response.status_code == 200, "Response status code is not 200"
    assert response_time < 2, "Response time is too slow"

    response_data = response.json()
    assert response_data.get('ok') is True, "Response does not indicate success"
