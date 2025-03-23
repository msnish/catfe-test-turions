import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.test_case_generator import TestCaseGenerator
from src.bdd_generator import BDDGenerator
from src.system_monitor import SystemMonitor
from src.logger import setup_logger

def main():
    logger = setup_logger()
    logger.info("Starting Financial Test Generator...")
    
    # Initialize the test case generator
    generator = TestCaseGenerator(r"D:\Manish\data\transactions.csv", r"D:\Manish\data\system_config.json")
    
    # Generate initial test cases
    test_cases = generator.generate_test_cases()
    
    # Generate BDD feature files
    bdd_generator = BDDGenerator(test_cases)
    bdd_generator.generate_all_features()
    
    # Start monitoring for system changes
    monitor = SystemMonitor(r"D:\Manish\data\system_config.json", generator, bdd_generator)
    monitor.start_monitoring()

if __name__ == "__main__":
    main()