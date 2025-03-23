import json
import requests
import os
from pathlib import Path

# Swagger API endpoint (using Petstore as an example)
SWAGGER_URL = "https://petstore.swagger.io/v2/swagger.json"
FEATURE_FILE = "features/api_tests.feature"
STEPS_DIR = "features/steps"
STEPS_FILE = f"{STEPS_DIR}/api_steps.py"

def load_swagger_from_url(url):
    """Load Swagger spec from a URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def generate_feature_file(swagger_data):
    """Generate Gherkin feature file from Swagger data."""
    base_path = swagger_data.get('basePath', '')
    host = swagger_data.get('host', '')
    schemes = swagger_data.get('schemes', ['http'])
    base_url = f"{schemes[0]}://{host}{base_path}"

    feature_content = [
        f"Feature: {swagger_data['info']['title']} API\n",
        "  As an API consumer\n",
        "  I want to interact with the API\n",
        "  So that I can perform operations effectively\n\n"
    ]

    for path, methods in swagger_data['paths'].items():
        for method, details in methods.items():
            summary = details.get('summary', f'{method.upper()} {path}')
            scenario = f"  Scenario: {summary}\n"
            full_endpoint = f"{base_path}{path}"

            if method == 'get':
                scenario += (
                    f"    Given the API endpoint \"{full_endpoint}\" is available\n"
                    f"    When I send a GET request to \"{full_endpoint}\"\n"
                    f"    Then I receive a 200 status code\n"
                )
            elif method == 'post':
                params = details.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema', {}).get('properties', {})
                param_example = {k: "example" for k in params.keys()} or {"name": "example"}  # Default if no params
                scenario += (
                    f"    Given the API endpoint \"{full_endpoint}\" is available\n"
                    f"    When I send a POST request to \"{full_endpoint}\" with data\n"
                    f"      | {' | '.join(param_example.keys())} |\n"
                    f"      | {' | '.join(param_example.values())} |\n"
                    f"    Then I receive a 201 status code\n"
                )
            feature_content.append(scenario + "\n")

    # Write feature file
    os.makedirs("features", exist_ok=True)
    with open(FEATURE_FILE, 'w') as f:
        f.writelines(feature_content)
    print(f"Generated feature file: {FEATURE_FILE}")
    return base_url

def generate_step_definitions(base_url):
    """Generate step definitions for behave."""
    step_content = [
        "from behave import given, when, then\n",
        "import requests\n",
        "import json\n\n",
        f"BASE_URL = '{base_url}'  # Auto-generated from Swagger\n\n",
        "@given('the API endpoint \"{endpoint}\" is available')\n",
        "def step_api_available(context, endpoint):\n",
        "    context.endpoint = f'{BASE_URL}{endpoint}'\n",
        "    try:\n",
        "        requests.get(context.endpoint)\n",
        "    except requests.exceptions.RequestException:\n",
        "        pass  # Ignore availability check failure for simplicity\n\n",
        "@when('I send a GET request to \"{endpoint}\"')\n",
        "def step_send_get(context, endpoint):\n",
        "    context.response = requests.get(context.endpoint)\n\n",
        "@when('I send a POST request to \"{endpoint}\" with data')\n",
        "def step_send_post(context, endpoint):\n",
        "    data = {row.cells[0]: row.cells[1] for row in context.table}\n",
        "    context.response = requests.post(context.endpoint, json=data)\n\n",
        "@then('I receive a {status_code:d} status code')\n",
        "def step_check_status(context, status_code):\n",
        "    assert context.response.status_code == status_code, f'Expected {status_code}, got {context.response.status_code}'\n"
    ]

    # Write step definitions
    os.makedirs(STEPS_DIR, exist_ok=True)
    with open(STEPS_FILE, 'w') as f:
        f.writelines(step_content)
    print(f"Generated step definitions: {STEPS_FILE}")

def run_behave():
    """Execute the feature file with behave."""
    os.system("behave features")

def main():
    # Load Swagger from URL
    swagger_data = load_swagger_from_url(SWAGGER_URL)

    # Generate feature file and step definitions
    base_url = generate_feature_file(swagger_data)
    generate_step_definitions(base_url)

    # Run behave
    print("Running behave tests...")
    run_behave()

if __name__ == "__main__":
    main()