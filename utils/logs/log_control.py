import logging
import colorlog
from logging import handlers
from common.setting import path_initializer

default_fmt = {
    "color_format": "%(log_color)s%(levelname)-9s%(asctime)s-%(name)s-%(filename)s[line:%(lineno)d]: %(message)s",
    "log_format": "%(levelname)-9s%(asctime)s-%(name)s-%(filename)s:[line:%(lineno)d]-[message]: %(message)s",
}

log_colors_config = {
    "DEBUG": "white",
    "INFO": "cyan",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}


class LogHandler(object):
    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.__log_file = path_initializer.log_all
        self.__error_file = path_initializer.log_err

        #! Initialize the log processor
        self.all_logger_handler = self.__init_logger_handler(self.__log_file)
        self.error_logger_handler = self.__init_logger_handler(self.__error_file)
        self.console_handle = self.__init_console_handle()

        #! Set the log format
        self.__set_log_formatter(self.all_logger_handler)
        self.__set_log_formatter(self.error_logger_handler)
        self.__set_color_formatter(self.console_handle, log_colors_config)

        #! Add a log handler to the logger
        self.__set_log_handler(self.all_logger_handler)
        self.__set_log_handler(self.error_logger_handler, level=logging.ERROR)
        self.__set_color_handle(self.console_handle)

    def __init_logger_handler(self, log_path):
        logger_handler = handlers.RotatingFileHandler(
            filename=log_path, maxBytes=1 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        return logger_handler

    def __init_console_handle(self):
        console_handle = colorlog.StreamHandler()
        return console_handle

    def __set_log_handler(self, logger_handler, level=logging.DEBUG):
        logger_handler.setLevel(level)
        self.logger.addHandler(logger_handler)

    def __set_color_handle(self, console_handle):
        console_handle.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handle)

    @staticmethod
    def __set_color_formatter(console_handle, color_config):
        formatter = colorlog.ColoredFormatter(
            default_fmt["color_format"], log_colors=color_config
        )
        console_handle.setFormatter(formatter)

    @staticmethod
    def __set_log_formatter(file_handler):
        formatter = logging.Formatter(default_fmt["log_format"])
        file_handler.setFormatter(formatter)


LOG = LogHandler().logger

