import logging
import os
import re
import sys
import time
import traceback
from functools import wraps


class RunningTimeDecorator:
    """RunningTimeDecorator class
        실행 시간을 로깅하는 데코레이터 클래스

    Attributes:
        __param (logging.Logger or None): logger의 parameter
        __show_pid (bool): 프로세스ID 로깅 여부
        __show_section (bool): 실행 section 로깅 여부
        logger (None): 로거 객체
    """

    def __init__(self, logger=None, show_section: bool = True, show_pid: bool = True):
        self.__param = logger
        self.__show_section = show_section
        self.__show_pid = show_pid

# 클래스 객체 호출 함수
    def __call__(self, func):
        """ decorator 를 반환하는 클래스 객체 호출 함수
            함수를 받아서 실행 시간과 실행 결과를 로깅
            log, pid, time 출력 및 저장
        Args:
            func ([type]): log를 기록할 함수
        Returns:
            decorator: 입력 함수에 decorated 처리
        """

        def printLog(str_arg: str):
            if isinstance(self.__param, logging.Logger):
                logger = logging.getLogger(self.__param.name)
                logger.info(str_arg)
            else:
                print(str_arg)

        @wraps(func)
        def decorator(*args, **kwargs): # 가변 개수 인자를 받는다
            """함수의 실행 시작 시간, 종료 시간 및 경과 시간을 로깅하는 데코레이터

            Args:
                args: 데코레이터를 적용할 함수의 위치 인자 (가변 개수)
                kwargs: 데커레이터를 적용할 함수의 키워드 인자 (가변 개수)

            Return:
                decorator: 함수 앞 뒤에 처리
            """
            str_current_pid = ""

            if self.__show_section:
                if self.__show_pid:
                    str_current_pid = "(PID:" + str(os.getpid()) + ")"
                str_start = "{0}{1} Started.".format(func.__name__, str_current_pid)
                printLog(str_start)

            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()

            if self.__show_section:
                if self.__show_pid:
                    str_current_pid = "(PID:" + str(os.getpid()) + ")"
                str_finish = "{0}{1} Finished.".format(func.__name__, str_current_pid)
                printLog(str_finish)
            str_log = "{0}{1} Elapsed Time : {2:.2f} seconds".format(
                func.__name__, str_current_pid, end_time - start_time
            )
            printLog(str_log)
            return result

        return decorator


class TryDecorator:
    """TryDecorator class

    Attributes:
        __param (logging.Logger or None): logger의 parameter
        __exit (bool): 예외 발생 시 여부

    """

    def __init__(self, logger, exit=True):
        self.__param = logger
        self.__exit = exit

    def __call__(self, func):
        """ log를 print하는 클래스 객체 호출 함수
            예외 처리 로깅을 추가하는 함수

        Args:
            func ([type]): log를 기록할 함수
        Returns:
            decorator: 입력 함수에 decorated 처리
        """

        def printLog(str_arg: str):
            if isinstance(self.__param, logging.Logger):
                logger = logging.getLogger(self.__param.name)
                logger.error(str_arg)
            else:
                print(str_arg)

        @wraps(func)
        def decorator(*args, **kwargs): # 가변 개수 인자를 받는다
            """함수에서 발생하는 예외를 로깅하고 선택적으로 프로그램을 종료하는 데코레이터

            Args:
                args: 데코레이터를 적용할 함수의 위치 인자 (가변 개수)
                kwargs: 데커레이터를 적용할 함수의 키워드 인자 (가변 개수)

            Returns:
                decorator: 함수 앞 뒤에 처리
            """
            try:
                result = func(*args, **kwargs)
                return result

            except Exception:
                formatted_lines = traceback.format_exc().splitlines()
                num = [
                    idx
                    for idx, i in enumerate(formatted_lines)
                    if re.search(" line ", i) is not None
                ][-1]

                printLog("=" * 100)
                for formatted_line in formatted_lines[num:]:
                    printLog(formatted_line)
                printLog("=" * 100)
                if self.__exit:
                    sys.exit(1)

        return decorator
