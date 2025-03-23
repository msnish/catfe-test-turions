import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.logger import setup_logger


class BDDGenerator:
    def __init__(self, test_cases):
        self.logger = setup_logger()
        self.test_cases = test_cases
        self.features_dir = "features/generated"
        if not os.path.exists(self.features_dir):
            os.makedirs(self.features_dir)

    def generate_financial_transactions_feature(self):
        feature_content = (
            "@financial\n"
            "Feature: Financial Transactions\n"
            "  As a banking web app\n"
            "  I want to validate financial transactions\n"
            "  So that they comply with system rules\n\n"
            "  @transaction\n"
            "  Scenario Outline: Validate a financial transaction\n"
            "    Given a transaction of type \"<Transaction Type>\" with amount <Amount> in <Source Currency> to <Destination Currency>\n"
            "    When the transaction is processed\n"
            "    Then the result should be \"<Expected Result>\"\n\n"
            "    Examples:\n"
            "      | Transaction Type  | Amount | Source Currency | Destination Currency | Expected Result |\n"
        )
        
        for test_case in self.test_cases["financial_transactions"]:
            feature_content += (
                f"      | {test_case['Transaction Type']} | {test_case['Amount']} | "
                f"{test_case['Source Currency']} | {test_case['Destination Currency']} | {test_case['Expected Result']} |\n"
            )
        
        with open(f"{self.features_dir}/financial_transactions.feature", "w") as f:
            f.write(feature_content)
        self.logger.info("Generated financial_transactions.feature")

    def generate_fraud_detection_feature(self):
        feature_content = (
            "@fraud\n"
            "Feature: Fraud Detection\n"
            "  As a banking web app\n"
            "  I want to detect fraudulent transactions\n"
            "  So that I can prevent financial losses\n\n"
            "  @fraud_detection\n"
            "  Scenario Outline: Detect fraudulent transactions\n"
            "    Given a transaction to <Destination Account> with amount <Amount>\n"
            "    When the transaction is analyzed for fraud\n"
            "    Then the fraud detection result should be \"<Fraud Result>\"\n\n"
            "    Examples:\n"
            "      | Destination Account | Amount | Fraud Result |\n"
        )
        
        for test_case in self.test_cases["fraud_detection"]:
            scenario = test_case["Scenario"]
            fraud_result = "Flag" if "Risks: None" not in scenario else "Pass"
            feature_content += (
                f"      | {test_case['Destination Account']} | {test_case['Amount']} | {fraud_result} |\n"
            )
        
        with open(f"{self.features_dir}/fraud_detection.feature", "w") as f:
            f.write(feature_content)
        self.logger.info("Generated fraud_detection.feature")

    def generate_customer_interactions_feature(self):
        feature_content = (
            "@customer\n"
            "Feature: Customer Interactions\n"
            "  As a banking web app\n"
            "  I want to monitor customer interactions\n"
            "  So that I can ensure security and compliance\n\n"
            "  @login\n"
            "  Scenario Outline: Monitor customer login attempts\n"
            "    Given a customer with <Login Attempts> login attempts\n"
            "    When the login is processed\n"
            "    Then the login result should be \"<Login Result>\"\n\n"
            "    Examples:\n"
            "      | Login Attempts | Login Result |\n"
        )
        
        for test_case in self.test_cases["customer_interactions"]:
            scenario = test_case["Scenario"]
            login_result = "Success" if "Success" in scenario else "Failure"
            feature_content += (
                f"      | {test_case['Value']} | {login_result} |\n"
            )
        
        with open(f"{self.features_dir}/customer_interactions.feature", "w") as f:
            f.write(feature_content)
        self.logger.info("Generated customer_interactions.feature")

    def generate_all_features(self):
        self.generate_financial_transactions_feature()
        self.generate_fraud_detection_feature()
        self.generate_customer_interactions_feature()