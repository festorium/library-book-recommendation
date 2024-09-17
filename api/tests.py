import time
import requests
import pytest

# Define the base URL of your API
BASE_URL = 'http://localhost:8000'  # Adjust the URL as necessary

# Define the endpoint for recommendations
RECOMMENDATIONS_ENDPOINT = '/recommendations'

# Define the user ID for testing
USER_ID = 'test_user_id'  # Replace with a valid user ID for testing

# Define the JWT token for authentication
JWT_TOKEN = 'your_jwt_token_here'  # Replace with a valid JWT token

@pytest.mark.parametrize('user_id', [USER_ID])
def test_recommendations_response_time(user_id):
    # Set up the request headers including the Authorization header
    headers = {
        'Authorization': f'Bearer {JWT_TOKEN}',
        'Content-Type': 'application/json'
    }

    # Set up the request payload
    params = {
        'user_id': user_id
    }

    # Start timing
    start_time = time.time()
    
    # Make the request to the endpoint
    response = requests.get(BASE_URL + RECOMMENDATIONS_ENDPOINT, headers=headers, params=params)

    # End timing
    end_time = time.time()
    
    # Calculate response time
    response_time = end_time - start_time

    # Check if response time is within acceptable limits
    assert response.status_code == 200, "Response status code is not 200"
    assert response_time < 2, "Response time is too slow"

    # Optionally, check the content of the response
    response_data = response.json()
    assert response_data.get('ok') is True, "Response does not indicate success"
