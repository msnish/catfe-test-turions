from behave import given, when, then
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# Load system configuration
with open(r"D:\Manish\data\system_config.json", 'r') as f:
    config = json.load(f)

@given('a transaction of type "{transaction_type}" with amount {amount:d} in {source_currency} to {destination_currency}')
def step_given_transaction(context, transaction_type, amount, source_currency, destination_currency):
    context.transaction = {
        "type": transaction_type,
        "amount": amount,
        "source_currency": source_currency,
        "destination_currency": destination_currency
    }

@when('the transaction is processed')
def step_when_transaction_processed(context):
    transaction_type = context.transaction["type"]
    amount = context.transaction["amount"]
    source_currency = context.transaction["source_currency"]
    
    limit = config["transaction_limits"].get(transaction_type, {}).get(source_currency, float('inf'))
    context.result = "Success" if amount <= limit else "Failure"

@then('the result should be "{expected_result}"')
def step_then_result(context, expected_result):
    assert context.result == expected_result, f"Expected {expected_result}, but got {context.result}"

@given('a transaction to {destination_account} with amount {amount:d}')
def step_given_transaction_fraud(context, destination_account, amount):
    context.transaction = {
        "Destination Account": destination_account,
        "Amount": amount
    }

@when('the transaction is analyzed for fraud')
def step_when_analyzed_for_fraud(context):
    amount = context.transaction["Amount"]
    destination = context.transaction["Destination Account"]
    fraud_rules = config["fraud_detection"]
    
    risks = []
    if amount > fraud_rules["max_amount_per_transaction"]:
        risks.append("Amount exceeds max")
    if destination in fraud_rules["suspicious_destinations"]:
        risks.append("Suspicious destination")
    
    context.fraud_result = "Flag" if risks else "Pass"

@then('the fraud detection result should be "{fraud_result}"')
def step_then_fraud_result(context, fraud_result):
    assert context.fraud_result == fraud_result, f"Expected {fraud_result}, but got {context.fraud_result}"

@given('a customer with {login_attempts:d} login attempts')
def step_given_customer_login(context, login_attempts):
    context.customer = {"login_attempts": login_attempts}

@when('the login is processed')
def step_when_login_processed(context):
    max_attempts = config["customer_interaction"]["max_login_attempts"]
    context.login_result = "Success" if context.customer["login_attempts"] <= max_attempts else "Failure"

@then('the login result should be "{login_result}"')
def step_then_login_result(context, login_result):
    assert context.login_result == login_result, f"Expected {login_result}, but got {context.login_result}"