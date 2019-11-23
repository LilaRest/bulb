from django.conf import settings
import logging.handlers
import logging
import sys
import os

class LevelFilter(logging.Filter):
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno != self.level

def init_bulb_logger_singleton():

    global bulb_logger

    # Create the bulb logger.
    bulb_logger = logging.getLogger("bulb")
    bulb_logger.setLevel(logging.DEBUG)

    # Add ACVTIVITY level.
    logging.ACTIVITY = 60
    logging.__all__ += ["ACTIVITY"]
    logging.addLevelName(logging.ACTIVITY, "ACTIVITY")

    def activity(self, message, *args, **kws):
        if self.isEnabledFor(logging.ACTIVITY):
            self._log(logging.ACTIVITY, message, args, **kws)

    logging.Logger.activity = activity

    # Create formatter for stream_handler, all_rotating_file_handler, errors_rotating_file_handler.
    formatter = logging.Formatter("[BULB %(levelname)s] [%(asctime)s] from '%(pathname)s' at line %(lineno)s in %(funcName)s : \"%(message)s\"")

    # Create the stream handler.
    stream_handler = logging.StreamHandler(sys.stdout)
    if settings.DEBUG:
        stream_handler.setLevel(logging.DEBUG)

    else:
        stream_handler.setLevel(logging.INFO)

    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(LevelFilter(logging.ACTIVITY))
    bulb_logger.addHandler(stream_handler)

    # Create the all file handler.
    all_rotating_file_handler = logging.handlers.RotatingFileHandler(filename=os.path.join(settings.BASE_DIR, "bulb.all.log"),
                                                                     maxBytes=1000000, backupCount=0)
    all_rotating_file_handler.setLevel(logging.DEBUG)
    all_rotating_file_handler.setFormatter(formatter)
    bulb_logger.addHandler(all_rotating_file_handler)

    # Create the warnings, errors and criticals file handler.
    errors_rotating_file_handler = logging.handlers.RotatingFileHandler(filename=os.path.join(settings.BASE_DIR, "bulb.errors.log"),
                                                                       maxBytes=500000, backupCount=0)
    errors_rotating_file_handler.setLevel(logging.WARNING)
    errors_rotating_file_handler.setFormatter(formatter)
    errors_rotating_file_handler.addFilter(LevelFilter(logging.ACTIVITY))
    bulb_logger.addHandler(errors_rotating_file_handler)

    # Create formatter for activity_rotating_file_handler.
    activity_formatter = logging.Formatter("[BULB %(levelname)s] [%(asctime)s] : \"%(message)s\"")

    # Create the activity file handler.
    activity_rotating_file_handler = logging.handlers.RotatingFileHandler(filename=os.path.join(settings.BASE_DIR, "bulb.activity.log"),
                                                                          maxBytes=500000, backupCount=0)
    activity_rotating_file_handler.setLevel(logging.ACTIVITY)
    activity_rotating_file_handler.setFormatter(activity_formatter)
    bulb_logger.addHandler(activity_rotating_file_handler)

init_bulb_logger_singleton()
