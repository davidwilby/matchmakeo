import logging

def setUpLogging(module_name = __name__):
    logger = logging.getLogger(module_name)
    FORMAT = "[%(filename)s . %(funcName)20s() ] %(message)s"
    logging.basicConfig(format=FORMAT)
    return logger
