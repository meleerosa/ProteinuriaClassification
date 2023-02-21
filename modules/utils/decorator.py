import logging
import os
import re
import sys
import time
import traceback
from functools import wraps


class RunningTimeDecorator:
    def __init__(self, logger=None, show_section: bool = True, show_pid: bool = True):
        self.__param = logger
        self.__show_section = show_section
        self.__show_pid = show_pid

    def __call__(self, func):
        def printLog(str_arg: str):
            if isinstance(self.__param, logging.Logger):
                logger = logging.getLogger(self.__param.name)
                logger.info(str_arg)
            else:
                print(str_arg)

        @wraps(func)
        def decorator(*args, **kwargs):
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
    def __init__(self, logger, exit=True):
        self.__param = logger
        self.__exit = exit

    def __call__(self, func):
        def printLog(str_arg: str):
            if isinstance(self.__param, logging.Logger):
                logger = logging.getLogger(self.__param.name)
                logger.error(str_arg)
            else:
                print(str_arg)

        @wraps(func)
        def decorator(*args, **kwargs):
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
