import glob
import os
from typing import Dict

if os.name == "nt":
    import win32api
    import win32con


def file_is_hidden(dir: str, p: str) -> bool:
    """파일이 숨김파일인지 확인, 숨김 파일이면 True, 아니면 False 리턴

    Args:
        p (str): 파일 경로

    Returns:
        _type_: 숨김파일 여부
    """
    if os.name == "nt":
        attribute = win32api.GetFileAttributes(os.path.join(dir, p))
        return attribute & (
            win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM
        )
    else:
        return p.startswith(".")  # linux-osx


def get_file_list(
    directory_path: str,
    hidden_file: bool = False,
    files_only: bool = True,
    inc_subdir: bool = False,
) -> Dict:
    """파일이 숨김파일인지 확인, 숨김 파일이면 True, 아니면 False 리턴

    Args:
        directory_path (str): 디렉토리 경로
        hidden_file (bool): 숨김 파일 표시 여부
        files_only (bool): 파일만 표시 여부
        inc_subdir (bool): 하위 폴더 탐색 여부

    Returns:
        _type_: 파일과 각 파일의 경로
    """
    def is_file(file_path: str):
        if files_only:
            return os.path.isfile(file_path)
        else:
            return True

    names = []
    full_paths = []
    file_list = []
    if inc_subdir:
        for root, dirs, files in os.walk(directory_path):
            if len(files) < 1 and is_file(root):
                names.append(os.path.basename(root))
                full_paths.append(root)
            for file in files:

                full_path = os.path.join(root, file)
                if hidden_file:
                    if is_file(full_path):
                        names.append(file)
                        full_paths.append(full_path)
                else:
                    if is_file(full_path) and not file_is_hidden(root, file):
                        names.append(file)
                        full_paths.append(full_path)
    else:
        if hidden_file:
            file_list = [
                (os.path.join(directory_path, f), f)
                for f in os.listdir(directory_path)
                if is_file(os.path.join(directory_path, f))
            ]

        else:
            file_list = [
                (os.path.join(directory_path, f), f)
                for f in os.listdir(directory_path)
                if (
                    (not file_is_hidden(directory_path, f))
                    and (is_file(os.path.join(directory_path, f)))
                )
            ]
        full_paths = [f[0] for f in file_list]
        names = [f[1] for f in file_list]

    return {"fullpath": full_paths, "name": names}


def chk_and_make_dir(directory_path: str) -> None:
    """디렉토리 경로가 있는지 확인하고 없으면 경로를 생성하는 함수

    Args:
        directory_path (str): 디렉토리 경로

    Returns:
        None
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def get_last_path(dir: str, type: str = "dir", by: str = "name") -> str:
    """마지막으로 수정, 생성, 접근한 파일명과 경로를 반환하는 함수
        mtime: 파일 최종 수정일
        ctime: 파일 생성일
        atime: 파일 최근 접근일
        name: 파일 이름

    Args:
        dir (str): 디렉토리 경로
        type (str): 검색할 파일의 종류
        by (str): 검색 기준

    Returns:
        str: 
    """
    if type == "dir":
        dir_list_class = list(filter(os.path.isdir, glob.glob(dir + "/*")))
    elif type == "file":
        dir_list_class = list(filter(os.path.isfile, glob.glob(dir + "/*")))
    elif type == "all":
        dir_list_class = glob.glob(dir + "/*")
    else:
        dir_list_class = glob.glob(dir + "/*" + type)

    last_path = ""

    if len(dir_list_class) > 0:
        if by == "mtime":
            sort_by = os.path.getmtime
        elif by == "ctime":
            sort_by = os.path.getctime
        elif by == "atime":
            sort_by = os.path.getatime
        elif by == "name":
            return max(dir_list_class)

        last_path = max(dir_list_class, key=sort_by)
    return last_path
