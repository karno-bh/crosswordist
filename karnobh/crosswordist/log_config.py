"""
This module is a configuration of logger for the application.
Users of this module should run set_logger function after importing this module
"""
import logging.config as log_config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s '
                      '[%(levelname)8s] '
                      '[%(filename)s:%(lineno)s - %(funcName)s()] '
                      '%(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'karnobh.crosswordist': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
        # '__main__': {  # if __name__ == '__main__'
        #     'handlers': ['console'],
        #     'level': 'DEBUG',
        #     'propagate': False
        # },
    }
}


def set_logger():
    """
    Sets log configuration for the application.
    Should run in the main starting module of the application.
    :return: None
    """
    log_config.dictConfig(LOGGING_CONFIG)
