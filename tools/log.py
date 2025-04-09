"""Log tool

This module is used for logging errors, exceptions an critical
"""

import logging
from typing import Dict


class Log:
    """
    Log class for Managing logs in Project
    """

    # Log Level Storage
    __level_category: Dict = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    def __init__(self, name, level: str = "info"):
        """
        Constructor for log class
        @param name: str
        @param level: str
        @filename: str
        :return: None
        """

        self.__format = logging.Formatter(
            "%(levelname)s: %(name)s: %(message)s: %(asctime)s", "%Y-%m-%d %H:%M:%S"
        )
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(self.__level_category.get(level.lower()))
        self.__stream_handler = logging.StreamHandler()
        self.__stream_handler.setFormatter(self.__format)
        self.__logger.addHandler(self.__stream_handler)

    def info(self, message):
        """
        info method logs info messages to log file
        @param message: str
        :return: None
        """
        self.__logger.info(message)

    def error(self, message):
        """
        Error method logs error messages to log file
        @param message: str
        :return: None
        """
        self.__logger.error(message)

    def critical(self, message):
        """
        Critical method logs critical messages to log file
        @param message: str
        :return: None
        """
        self.__logger.critical(message)

    def exception(self, message):
        """
        Exception method logs exception messages to log file
        @param message: str
        :return: None
        """
        self.__logger.exception(message)


    @classmethod
    def mail_log_handler(cls, msg,  recipient, subject, body):
        logging.basicConfig(
            filename="./logs/mail.log",
            force= True,
            format="%(levelname)s: %(name)s: %(message)s: %(asctime)s",
            datefmt="%d-%b-%y %H:%M:%S",
        )
        logging.error(f"{msg}\n recipient: {recipient}\n subject: {subject}\n body: {body}", exc_info=True)


