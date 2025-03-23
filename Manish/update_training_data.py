import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.generative_ai_3 import GenerativeAI
from src.logger import setup_logger
from src.test_case_generator_2 import TestCaseGenerator

def update_training_data():
    logger = setup_logger()
    logger.info("Starting process to update training data...")

    # Initialize the TestCaseGenerator and GenerativeAI
    generator = TestCaseGenerator(r"D:\Manish\data\transactions.csv", r"D:\Manish\data\system_config.json")
    gen_ai = GenerativeAI(model_name="models/fine_tuned_gpt2", use_gpu=False)

    # Generate new test cases
    test_cases = generator.generate_test_cases()
    
    # Path to the training data file
    training_file = r"D:manish\data\training_data\banking_scenarios.txt"
    
    # Ensure the training data directory exists
    os.makedirs(os.path.dirname(training_file), exist_ok=True)
    
    # Read existing scenarios to avoid duplicates
    existing_scenarios = set()
    if os.path.exists(training_file):
        with open(training_file, "r") as f:
            existing_scenarios = set(line.strip() for line in f if line.strip())
    
    # Collect new scenarios
    new_scenarios = []
    
    # Process financial transactions
    for scenario in test_cases["financial_transactions"]:
        scenario_text = gen_ai.generate_test_scenario(
            transaction_type=scenario.get("type", "unknown"),  # Use dict.get() with default value
            source_currency=scenario.get("source_currency", "USD"),
            destination_currency=scenario.get("destination_currency", "USD"),
            amount=scenario.get("amount", 0),
            system_rules=generator.system_rules
        )
        training_text = gen_ai.convert_scenario_to_training_text(scenario_text)
        if training_text.strip() not in existing_scenarios:
            new_scenarios.append(training_text)
            existing_scenarios.add(training_text.strip())
            logger.info(f"Added financial transaction scenario to training data: {scenario_text[:50]}...")

    # Process fraud detection scenarios
    for scenario in test_cases["fraud_scenarios"]:
        scenario_text = gen_ai.generate_fraud_scenario(
            transaction=scenario,
            fraud_rules=generator.system_rules["fraud_detection"]
        )
        training_text = gen_ai.convert_scenario_to_training_text(scenario_text)
        if training_text.strip() not in existing_scenarios:
            new_scenarios.append(training_text)
            existing_scenarios.add(training_text.strip())
            logger.info(f"Added fraud detection scenario to training data: {scenario_text[:50]}...")

    # Process customer interaction scenarios
    for scenario in test_cases["customer_interactions"]:
        scenario_text = gen_ai.generate_customer_interaction_scenario(
            interaction_type=scenario.get("type", "unknown"),
            value=scenario.get("value", 0),
            system_rules=generator.system_rules
        )
        training_text = gen_ai.convert_scenario_to_training_text(scenario_text)
        if training_text.strip() not in existing_scenarios:
            new_scenarios.append(training_text)
            existing_scenarios.add(training_text.strip())
            logger.info(f"Added customer interaction scenario to training data: {scenario_text[:50]}...")

    # Append new scenarios to the file
    if new_scenarios:
        with open(training_file, "a") as f:
            for scenario in new_scenarios:
                f.write(scenario)
        logger.info(f"Added {len(new_scenarios)} new scenarios to {training_file}")
    else:
        logger.info("No new scenarios to add to training data.")

    logger.info(f"Training data updated successfully at {training_file}")

if __name__ == "__main__":
    update_training_data()