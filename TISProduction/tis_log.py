import logging

def init_tis_logger():
    f_formater=logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
    c_formater=logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    f_handler=logging.FileHandler('tis.log')
    f_handler.setLevel(logging.DEBUG)
    f_handler.setFormatter(f_formater)

    c_handler=logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)
    c_handler.setFormatter(c_formater)

    logger=logging.getLogger('tislogger')
    logger.addHandler(f_handler)
    logger.addHandler(c_handler)
    logger.setLevel(logging.DEBUG)

    return logger

def get_tis_logger():
    return logging.getLogger('tislogger')