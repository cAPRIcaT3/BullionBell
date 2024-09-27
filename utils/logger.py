import logging

def setup_logging():
    # Create a custom logger
    logger = logging.getLogger('BullionBell')
    logger.setLevel(logging.DEBUG)  # Set the base level of logging

    # Create handlers with 'w' mode to overwrite the old file
    f_handler = logging.FileHandler('BullionBell.log', mode='w')  # Open the file in write mode
    f_handler.setLevel(logging.DEBUG)

    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(formatter)

    # Add handler to the logger
    logger.addHandler(f_handler)

    return logger