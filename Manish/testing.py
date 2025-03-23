import pandas as pd
import json
import os
from collections import defaultdict
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("D:/Manish/logs/testing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# File paths
BASE_DIR = r"D:\Manish"
TRANSACTIONS_FILE = os.path.join(BASE_DIR, "data", "transactions.csv")
CONFIG_FILE = os.path.join(BASE_DIR, "data", "system_config.json")

# Ensure the data and logs directories exist
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)

def load_transactions():
    """Load the transactions from the CSV file."""
    logger.info(f"Attempting to load transactions from {TRANSACTIONS_FILE}")
    try:
        df = pd.read_csv(TRANSACTIONS_FILE)
        logger.info(f"Loaded {len(df)} transactions from {TRANSACTIONS_FILE}")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {TRANSACTIONS_FILE}")
        raise
    except Exception as e:
        logger.error(f"Error loading transactions: {str(e)}")
        raise

def analyze_transactions(df):
    """Analyze the transaction data to derive configuration rules."""
    logger.info("Analyzing transactions to generate system configuration")
    config = {
        "transaction_limits": {},
        "fraud_detection": {},
        "customer_interaction": {}
    }

    # Step 1: Calculate transaction limits per transaction type and currency
    transaction_limits = defaultdict(lambda: defaultdict(list))
    for _, row in df.iterrows():
        if row["Expected Result"] == "Success":
            transaction_type = row["Transaction Type"]
            source_currency = row["Source Currency"]
            amount = row["Amount"]
            transaction_limits[transaction_type][source_currency].append(amount)

    for transaction_type, currencies in transaction_limits.items():
        config["transaction_limits"][transaction_type] = {}
        for currency, amounts in currencies.items():
            if amounts:
                max_amount = max(amounts)
                limit = round(max_amount * 1.2, -2)
                config["transaction_limits"][transaction_type][currency] = limit
            else:
                config["transaction_limits"][transaction_type][currency] = 1000

    # Step 2: Identify suspicious destinations
    suspicious_destinations = set()
    for _, row in df.iterrows():
        if row["Expected Result"] in ["Failure", "Hold"] and pd.notna(row["Destination Account"]):
            suspicious_destinations.add(row["Destination Account"])
    config["fraud_detection"]["suspicious_destinations"] = list(suspicious_destinations)

    # Step 3: Set fraud detection rules
    successful_amounts = df[df["Expected Result"] == "Success"]["Amount"]
    max_successful_amount = successful_amounts.max() if not successful_amounts.empty else 1000
    config["fraud_detection"]["max_amount_per_transaction"] = round(max_successful_amount * 1.5, -2)

    transactions_per_account = df.groupby("Source Account").size()
    max_transactions = transactions_per_account.max() if not transactions_per_account.empty else 5
    config["fraud_detection"]["max_transactions_per_day"] = int(max_transactions * 1.5)

    # Step 4: Set customer interaction rules
    config["customer_interaction"]["max_login_attempts"] = 3
    config["customer_interaction"]["session_timeout_minutes"] = 30

    logger.info("Completed analysis of transactions")
    return config

def write_config(config):
    """Write the configuration to system_config.json."""
    logger.info(f"Writing configuration to {CONFIG_FILE}")
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        logger.info(f"Successfully wrote configuration to {CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Error writing configuration: {str(e)}")
        raise

def main():
    try:
        # Load the transactions
        df = load_transactions()

        # Analyze the transactions to generate the config
        config = analyze_transactions(df)

        # Write the config to system_config.json
        write_config(config)
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()