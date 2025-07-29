"""
detaillogger.py

DetailLogger: A logger for detailed tracebacks and caller info.

Author: Ryan LaPine
Date:   2025-07-28
Version:1.0
"""

import logging
import traceback
import inspect
from dataclasses import dataclass
from typing import Optional

#wrapped functions for direct calls
detaillogger = None

def log(message: str):
    global detaillogger
    if detaillogger is None:
        detaillogger = DetailLogger()
    caller = detaillogger._get_caller()
    detaillogger.log(message = message, caller=caller)

def log_exception(ex: BaseException, details: Optional[str] = None):
    global detaillogger
    if detaillogger is None:
        detaillogger = DetailLogger()
    caller = detaillogger._get_caller()
    detaillogger.log_exception(ex=ex, details=details, caller=caller)


class DetailLogger:
    """
    Logger that captures detailed messages, context, and exceptions with caller info.
    """

    ALLOWED_LEVELS = [
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
    ]
    DEFAULT_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DEFAULT_LOG_FILE = "detaillogger.log"

    def __init__(
        self,
        level: int = logging.DEBUG,
        fmt: str = DEFAULT_FORMAT,
        file_name: Optional[str] = None,
    ) -> None:
        """
        Initialize DetailLogger.

        Args:
            level:   Logging level (DEBUG, INFO, etc.).
            fmt:     Log message format string.
            file_name: Optional path to a file for log output.
        """
        # Base logger always set to DEBUG; handlers filter their own levels
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Validate level or default to DEBUG
        self.level = level if level in self.ALLOWED_LEVELS else logging.DEBUG

        # File handler (if requested)
        if file_name:
            fh = logging.FileHandler(file_name)
            fh.setLevel(self.level)
            fh.setFormatter(logging.Formatter(fmt))
            self.logger.addHandler(fh)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(self.level)
        ch.setFormatter(logging.Formatter(fmt))
        self.logger.addHandler(ch)

        # Select appropriate logging method
        self.log_function = {
            logging.DEBUG: self.logger.debug,
            logging.INFO: self.logger.info,
            logging.WARNING: self.logger.warning,
            logging.ERROR: self.logger.error,
            logging.CRITICAL: self.logger.critical,
        }.get(self.level, self.logger.debug)

    @dataclass
    class Caller:
        """
        Data class storing context of the caller.
        """
        full_path: str
        file_name: str
        function_name: str
        line_num: int

    def _get_caller(self) -> Caller:
        """
        Walk the stack to identify who called the logging method.

        Returns:
            Caller: context of the calling frame.
        """
        frame = inspect.currentframe()
        # f_back: _get_caller → log/log_exception → the real caller
        caller_frame = frame.f_back.f_back  # type: ignore
        info = inspect.getframeinfo(caller_frame)
        return self.Caller(
            full_path=info.filename,
            file_name=info.filename,
            function_name=info.function,
            line_num=info.lineno,
        )

    def log(self, message: str, caller: Caller = None) -> None:
        """
        Log a custom message along with caller info.

        Args:
            message: The detail message to record.
        """
        if caller is None:
            caller = self._get_caller()
        self.log_function(f"Details:  {message}")
        self.log_function(f"From:     {caller.file_name}")
        self.log_function(f"Function: {caller.function_name}()")
        self.log_function(f"Line:     {caller.line_num}\n")

    def log_exception(self, ex: BaseException, details: Optional[str] = None, caller: Caller = None) -> None:
        """
        Log an exception with traceback and caller context.

        Args:
            ex:      The exception instance.
            details: Extra information to include.
        """
        if caller is None:
            caller = self._get_caller()
        tb = traceback.extract_tb(ex.__traceback__)
        line = tb[-1].lineno if tb else None

        self.log_function(f"Exception type:    {type(ex).__name__}")
        self.log_function(f"Exception message: {ex}")
        if details:
            self.log_function(f"Details:           {details}")
        self.log_function(f"File:              {caller.file_name}")
        self.log_function(f"Function:          {caller.function_name}")
        self.log_function(f"Line:              {line}\n")


def main() -> None:
    """
    Simple CLI for testing DetailLogger.
    """
    log_to_file = input("Also log to file? (y/n):").strip().lower() == 'y'
    file_name = None
    if log_to_file:
        file_name = input("Enter filname:")
    detail_logger = DetailLogger(file_name=file_name)
    print()
    print("Options")
    print("1) Log details.")
    print("2) Log 'division by zero' exception.")
    print("3) Log custom exception.")
    print("q) Exit.")
    option = input("Enter an option:").strip()
    print()
    match option:
        case '1':
            msg = input("Enter message to log:")
            detail_logger.log(msg)
            # log(msg)
            print("Message logged.")

        case '2':
            msg = input("Enter additional message to log with exception:")
            print("Raising 'division by zero' exception.")
            try:
                x = 1/0
            except Exception as ex:
                detail_logger.log_exception(ex, details=msg)
                # log_exception(ex=ex, details=msg)
            print("Exception logged.")
        case '3':
            ex_name = input("Enter custom exception name:")
            try:
                raise Exception(ex_name)
            except Exception as ex:
                detail_logger.log_exception(ex)
                log_exception(ex=ex)
            print("Custom exception logged.")

if __name__ == "__main__":
    main()