"""
logger.py

Central logging utility for the FusionToDescription exporter.
"""

import datetime
import traceback


class Logger:
    """
    Simple logger for the exporter.
    """

    LEVEL_INFO = "INFO"
    LEVEL_WARNING = "WARNING"
    LEVEL_ERROR = "ERROR"
    LEVEL_DEBUG = "DEBUG"

    enable_debug = True

    # =====================================================
    # Internal Logger
    # =====================================================

    @staticmethod
    def _log(level: str, message: str):

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        print(f"[{timestamp}] [{level}] {message}")

    # =====================================================
    # Public Methods
    # =====================================================

    @classmethod
    def info(cls, message: str):

        cls._log(cls.LEVEL_INFO, message)

    @classmethod
    def warning(cls, message: str):

        cls._log(cls.LEVEL_WARNING, message)

    @classmethod
    def error(cls, message: str):

        cls._log(cls.LEVEL_ERROR, message)

    @classmethod
    def debug(cls, message: str):

        if cls.enable_debug:
            cls._log(cls.LEVEL_DEBUG, message)

    # =====================================================
    # Exception Logging
    # =====================================================

    @classmethod
    def exception(cls, exception: Exception):

        cls.error(str(exception))
        cls.debug(traceback.format_exc())

    # =====================================================
    # Export Workflow Logging
    # =====================================================

    @classmethod
    def start(cls, operation: str):

        cls.info(f"Starting {operation}...")

    @classmethod
    def finish(cls, operation: str):

        cls.info(f"Finished {operation}.")

    @classmethod
    def separator(cls):

        print("-" * 60)