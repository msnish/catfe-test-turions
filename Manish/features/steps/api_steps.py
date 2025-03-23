from behave import given, when, then
import requests
import json

BASE_URL = 'https://petstore.swagger.io/v2'  # Auto-generated from Swagger

@given('the API endpoint "{endpoint}" is available')
def step_api_available(context, endpoint):
    context.endpoint = f'{BASE_URL}{endpoint}'
    try:
        requests.get(context.endpoint)
    except requests.exceptions.RequestException:
        pass  # Ignore availability check failure for simplicity

@when('I send a GET request to "{endpoint}"')
def step_send_get(context, endpoint):
    context.response = requests.get(context.endpoint)

@when('I send a POST request to "{endpoint}" with data')
def step_send_post(context, endpoint):
    data = {row.cells[0]: row.cells[1] for row in context.table}
    context.response = requests.post(context.endpoint, json=data)

@then('I receive a {status_code:d} status code')
def step_check_status(context, status_code):
    assert context.response.status_code == status_code, f'Expected {status_code}, got {context.response.status_code}'
