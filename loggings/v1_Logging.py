import logging

# Set up error logging to error.log
error_logger = logging.getLogger('error')
error_handler = logging.FileHandler('error.log')
error_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)

# Set up info logging to info.log
info_logger = logging.getLogger('info')
info_handler = logging.FileHandler('info.log')
info_handler.setLevel(logging.INFO)
info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
info_handler.setFormatter(info_formatter)
info_logger.addHandler(info_handler)

# Set up info logging to warning.log
warning_logger = logging.getLogger('warning')
warning_handler = logging.FileHandler('warning.log')
warning_handler.setLevel(logging.WARNING)
warning_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
warning_handler.setFormatter(warning_formatter)
warning_logger.addHandler(warning_handler)