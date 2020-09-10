import logging
import logging.config
import os
import shutil
from pathlib import Path

SETTING_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent

FILENAME_LOGGER = os.path.join(SETTING_PATH, 'stdout', 'logger.log')
FILENAME_LOGGER_ERROR = os.path.join(
    SETTING_PATH,  'stdout', 'logger-errors.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            # - Error Line: %(line)s
            'format': '[%(asctime)s] [%(levelname)s] [%(bp)s] %(message)s',
        },
    },
    'handlers': {
        'extras_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'detailed',
            'mode': 'a',
            'filename': FILENAME_LOGGER
        },
        'errors': {
            'class': 'logging.FileHandler',
            'filename': FILENAME_LOGGER_ERROR,
            'mode': 'a',
            'level': 'ERROR',
            'formatter': 'detailed',
        },
    },
    'loggers': {
        'app': {
            'handlers': ['extras_handler']
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['errors']
    },
}
