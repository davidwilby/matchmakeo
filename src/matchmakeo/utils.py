from logging import getLogger

def setUpLogging(module_name = __name__):
    return getLogger(module_name)
