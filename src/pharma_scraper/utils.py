import logging
import os
import re

def setup_logger(name, log_file, level=logging.INFO):
    """Sets up a logger that writes to file and console."""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    handler_file = logging.FileHandler(log_file)
    handler_file.setFormatter(formatter)
    
    handler_console = logging.StreamHandler()
    handler_console.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler_file)
    logger.addHandler(handler_console)
    return logger

def sanitize_filename(doi):
    """Converts DOI to safe filename (e.g., 10.1016/j... -> 10.1016_j...)"""
    return doi.replace("/", "_") + ".pdf"