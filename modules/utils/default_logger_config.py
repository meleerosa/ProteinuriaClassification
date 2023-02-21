import logging
import os
from datetime import datetime

from modules.utils.file_handler import chk_and_make_dir
from modules.utils.logging_format import CustomFormatter


class DefaultLogger:
    """DefaultLogger class

    Attributes:

    """
    def __init__(self) -> None:
        pass

    def setDefaultLogger(
        self, logger_name: str, output_directory_path: str
    ) -> logging.Logger:
        """ 로거 설정함수
            어떤 로그를 어디에, 어떻게 기록할 지 설정

        Args:
            logger_name (str): 기록할 log의 이름
            output_directory_path (str): 출력값을 저장할 디렉토리 경로
        Returns:
            logging.getLogger(logger_name): 특정 이름의 로거 객체 반환
        """
        # 로거 설정
        log_file_name = os.path.join(
            output_directory_path,
            "log_current.log",
        )
        self._output_directory_path = output_directory_path
        chk_and_make_dir(output_directory_path)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(CustomFormatter())
        file_handler = logging.FileHandler(log_file_name)

        logging.basicConfig(
            level=logging.INFO,
            format="[%(levelname)s:%(name)s:%(asctime)s] %(message)s",
            datefmt="%Y/%m/%d %H:%M:%S",
            handlers=[stream_handler, file_handler],
        )

        return logging.getLogger(logger_name)

    def rename_log_file(self):
        """ 로그 이름 변경함수

        Args:
            None
        Returns:
            None
        """

        logging.shutdown()
        c_time = os.path.getctime(
            os.path.join(
                self._output_directory_path,
                "log_current.log",
            )
        )
        c_time = datetime.fromtimestamp(c_time).strftime("%Y%m%d_%H%M%S")
        os.rename(
            os.path.join(
                self._output_directory_path,
                "log_current.log",
            ),
            os.path.join(
                self._output_directory_path,
                f"log_{c_time}.log",
            ),
        )
