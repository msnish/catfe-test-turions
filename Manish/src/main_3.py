import argparse
import subprocess
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.test_case_generator_2 import TestCaseGenerator
from src.bdd_generator_2 import BDDGenerator
from src.system_monitor_2 import SystemMonitor
from src.logger import setup_logger
from src.app import app
from update_training_data import update_training_data

    
def run_file_based_mode():
    logger = setup_logger()
    logger.info("Starting Banking Test Generator in file-based mode...")
    
    # Initialize the test case generator
    generator = TestCaseGenerator(r"D:\Manish\data\transactions.csv", r"D:\Manish\data\system_config.json")
    
    # Generate initial test cases
    test_cases = generator.generate_test_cases()
    
    # Generate BDD feature files
    bdd_generator = BDDGenerator(test_cases)
    bdd_generator.generate_all_features()
    
    # Start monitoring for system changes
    monitor = SystemMonitor("data/system_config.json", generator, bdd_generator)
    monitor.start_monitoring()

def run_ui_mode():
    logger = setup_logger()
    logger.info("Starting Banking Test Generator in UI mode...")
    app.run(debug=True, host='0.0.0.0', port=5000)

def run_test_mode():
    logger = setup_logger()
    logger.info("Starting Banking Test Generator in test mode...")
    
    # Ensure the reports directory exists
    reports_dir = r"D:\Manish\data\reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Run behave and capture the output
    output_file = os.path.join(reports_dir, "behave_output.txt")
    logger.info("Running behave tests and saving output to %s", output_file)
    
    try:
        # Run behave with the features/generated/ directory
        result = subprocess.run(
            ["python", "-m", "behave", "features/generated/"],
            capture_output=True,
            text=True
        )
        
        # Combine stdout and stderr for the full output
        behave_output = result.stdout + result.stderr
        
        # Save the output to a file
        with open(output_file, "w") as f:
            f.write(behave_output)
        
        logger.info("Behave test output saved to %s", output_file)
        
        # Log a summary of the output
        logger.info("Behave test execution completed. Summary:\n%s", behave_output.splitlines()[-3:])
        
    except Exception as e:
        logger.error("Error running behave tests: %s", str(e))
        raise

def run_update_training_mode():
    logger = setup_logger()
    logger.info("Starting Banking Test Generator in update-training mode...")
    update_training_data()

def main():
    parser = argparse.ArgumentParser(description="Banking Test Scenario Generator")
    parser.add_argument('--mode', choices=['file', 'ui', 'test', 'update-training'], default='file',
                        help="Mode to run the application: 'file' for file-based generation, 'ui' for UI-based generation, 'test' to run behave tests, 'update-training' to update training data")
    args = parser.parse_args()

    if args.mode == 'file':
        run_file_based_mode()
    elif args.mode == 'ui':
        run_ui_mode()
    elif args.mode == 'test':
        run_test_mode()
    elif args.mode == 'update-training':
        run_update_training_mode()

if __name__ == "__main__":
    main()