import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.logger import setup_logger

class SystemMonitor(FileSystemEventHandler):
    def __init__(self, config_file, test_case_generator, bdd_generator):
        self.logger = setup_logger()
        self.config_file = config_file
        self.test_case_generator = test_case_generator
        self.bdd_generator = bdd_generator

    def on_modified(self, event):
        if event.src_path.endswith("system_config.json"):
            self.logger.info("System configuration changed. Updating test cases and BDD features...")
            test_cases = self.test_case_generator.update_test_cases()
            self.bdd_generator.test_cases = test_cases
            self.bdd_generator.generate_all_features()

    def start_monitoring(self):
        observer = Observer()
        observer.schedule(self, path="data/", recursive=False)
        observer.start()
        self.logger.info("Started monitoring system configuration changes.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            self.logger.info("Stopped monitoring system configuration changes.")
        observer.join()