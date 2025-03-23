import pandas as pd
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.logger import setup_logger
from src.generative_ai_3 import GenerativeAI

class TestCaseGenerator:
    def __init__(self, transaction_file, config_file):
        self.logger = setup_logger()
        self.transactions = pd.read_csv(transaction_file)
        print(self.transactions)
        self.config_file = config_file
        self.config = self.load_config()
        self.system_rules = self.load_system_rules()
        self.gen_ai = GenerativeAI(model_name="distilgpt2", use_gpu=False)
        self.logger.info("TestCaseGenerator initialized.")

    def load_config(self):
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def load_system_rules(self):
        # Load system rules from JSON
        self.logger.info(f"Loading system rules from {self.config_file}...")
        with open(self.config_file, 'r') as f:
            return json.load(f)


    def generate_test_cases(self):
        test_cases = {
            "financial_transactions": [],
            "fraud_detection": [],
            "customer_interactions": []
        }
        
        # Financial transactions test cases
        for _, row in self.transactions.iterrows():
            transaction_type = row["Transaction Type"]
            source_currency = row["Source Currency"]
            destination_currency = row["Destination Currency"]
            amount = row["Amount"]
            transaction_id = row["Transaction ID"]
            
            system_rules = self.config["transaction_limits"]
            scenario = self.gen_ai.generate_test_scenario(
                transaction_type, source_currency, destination_currency, amount, system_rules
            )
            test_cases["financial_transactions"].append({
                "Transaction ID": transaction_id,
                "Scenario": scenario,
                "Expected Result": row["Expected Result"],
                "Amount": amount,
                "Transaction Type": transaction_type,
                "Source Currency": source_currency,
                "Destination Currency": destination_currency
            })
        
        # Fraud detection test cases
        for _, row in self.transactions.iterrows():
            fraud_rules = self.config["fraud_detection"]
            scenario = self.gen_ai.generate_fraud_scenario(row, fraud_rules)
            test_cases["fraud_detection"].append({
                "Transaction ID": row["Transaction ID"],
                "Scenario": scenario,
                "Amount": row["Amount"],
                "Destination Account": row["Destination Account"]
            })
        
        # Customer interaction test cases
        max_attempts = self.config["customer_interaction"]["max_login_attempts"]
        for login_attempts in [2, 4, 6]:  # Test various login attempts
            scenario = self.gen_ai.generate_customer_interaction_scenario("login_attempts", login_attempts, self.config["customer_interaction"])
            test_cases["customer_interactions"].append({
                "Interaction Type": "login_attempts",
                "Value": login_attempts,
                "Scenario": scenario
            })
        
        self.logger.info(f"Generated test cases: {len(test_cases['financial_transactions'])} financial, {len(test_cases['fraud_detection'])} fraud, {len(test_cases['customer_interactions'])} customer interaction.")
        return test_cases

    def update_test_cases(self):
        self.config = self.load_config()
        return self.generate_test_cases()