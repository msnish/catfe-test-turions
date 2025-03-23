import logging
import os

def setup_logger():
    logger = logging.getLogger("FinancialTestGenerator")
    logger.setLevel(logging.INFO)
    
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    fh = logging.FileHandler("logs/test_generator.log")
    fh.setLevel(logging.INFO)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger