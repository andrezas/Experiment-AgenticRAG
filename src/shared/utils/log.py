import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

from termcolor import colored


class ColoredFormatter(logging.Formatter):
    _COLOR_PER_LEVEL: ClassVar[dict[str, str]] = {
        "DEBUG": colored("DEBUG", "cyan"),
        "INFO": colored("INFO", "green"),
        "WARNING": colored("WARNING", "yellow"),
        "ERROR": colored("ERROR", "red"),
        "CRITICAL": colored("CRITICAL", "white", "on_red", attrs=["bold"]),
    }

    def format(self, record: logging.LogRecord) -> str:
        asctime = self._format_time(record, self.datefmt)
        record.asctime = colored(asctime, "blue")
        record.levelname = self._COLOR_PER_LEVEL.get(record.levelname, record.levelname)
        record.module = colored(record.module, "magenta")

        return f"[{record.levelname}]: {record.asctime} - [{record.name}] - {record.getMessage()}"

    @staticmethod
    def _format_time(record: logging.LogRecord, datefmt: str | None = None) -> str:
        dt = datetime.fromtimestamp(record.created, tz=UTC)
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")


class Logger:
    _logger: logging.Logger | None = None
    _log_path: Path | None = None

    @classmethod
    def configure(cls, log_path: str | None = None) -> None:
        if cls._logger is not None:
            root = logging.getLogger()
            for handler in root.handlers[:]:
                root.removeHandler(handler)

            for handler in cls._logger.handlers[:]:
                cls._logger.removeHandler(handler)
            cls._logger = None

        if log_path:
            cls._log_path = Path(log_path)

        cls._initialize_logger()

    @classmethod
    def _initialize_logger(cls) -> None:
        if cls._logger is not None:
            return

        cls._logger = logging.getLogger("agent-rag")
        cls._logger.setLevel(logging.DEBUG)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        formatter = ColoredFormatter()

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)

        cls._logger.addHandler(console_handler)

        if not root_logger.handlers:
            root_logger.addHandler(console_handler)

        if cls._log_path is None:
            cls._logger.warning("Logger not configured with a file path. Skipping file logging.")
        else:
            today_date = datetime.now(tz=UTC).date().strftime("%Y-%m-%d")
            cls._log_path.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(cls._log_path / f"agent_rag_{today_date}.log")
            file_handler.setLevel(logging.DEBUG)

            plain_fmt = "[%(levelname)s]: %(asctime)s - [%(name)s] - %(message)s"
            file_formatter = logging.Formatter(plain_fmt, datefmt="%Y-%m-%d %H:%M:%S")
            file_handler.setFormatter(file_formatter)

            cls._logger.addHandler(file_handler)
            root_logger.addHandler(file_handler)

    @classmethod
    def get_logger(cls) -> logging.Logger:
        if cls._logger is None:
            cls._initialize_logger()
        return cls._logger

    @classmethod
    def info(cls, message: str) -> None:
        cls.get_logger().info(message)

    @classmethod
    def debug(cls, message: str) -> None:
        cls.get_logger().debug(message)

    @classmethod
    def warning(cls, message: str) -> None:
        cls.get_logger().warning(message)

    @classmethod
    def error(cls, message: str) -> None:
        cls.get_logger().error(message)

    @classmethod
    def critical(cls, message: str) -> None:
        cls.get_logger().critical(message)
