from multiprocessing import cpu_count

import numpy as np
import pandas as pd
from pathos.multiprocessing import ProcessingPool as Pool


def parallelize_dataframe(func, df: pd.DataFrame) -> pd.DataFrame:
    """데이터프레임을 분할해서 cpu 병렬처리
    multi process

    Args:
        func ([type]): cpu 병렬처리에 사용할 함수
        df (pd.DataFrame): 분할할 데이터프레임

    Returns:
        pd.DataFrame: cpu 병렬처리된 데이터프레임
    """

    num_cores = cpu_count() - 1
    pool = Pool(num_cores)

    df_split = np.array_split(df, num_cores)

    len_df = len(df_split)
    if len_df < num_cores:
        num_cores = len_df

    df = pd.concat(pool.map(func, df_split))

    pool.close()
    pool.join()
    pool.clear()
    return df


def parallelize_dataframe_with_args(func, df: pd.DataFrame, *args) -> pd.DataFrame:
    """데이터프레임을 분할해서 cpu 병렬처리(func에 인자값이 필요한 경우)
    multi process

    Args:
        func ([type]): cpu 병렬처리에 사용할 함수
        df (pd.DataFrame): 분할할 데이터프레임
        args: func에 들어갈 인자값

    Returns:
        pd.DataFrame: cpu 병렬처리된 데이터프레임
    """

    num_cores = cpu_count() - 1
    pool = Pool(num_cores)

    df_split = np.array_split(df, num_cores)

    len_df = len(df_split)
    if len_df < num_cores:
        num_cores = len_df

    list_tuple_args = []
    list_args = list(args)

    for item in df_split:
        each_list_class = [item]
        each_list_class.append(list_args)
        list_tuple_args.append(tuple(each_list_class))
    df = pd.concat(pool.map(lambda x: func(*x), list_tuple_args))
    pool.close()
    pool.join()
    pool.clear()
    return df


def string_to_boolean(arg_str: str) -> bool or np.NaN:
    """str을 boolean으로 변환
        문자열이 "true", "1", "yes" 이면 True,
        문자열이 "false", "0", "no" 이면 False,
        그 외엔 np.NaN 리턴

    Args:
        arg_str (str): 변환할 문자열

    Returns:
        bool or np.NaN: 변환된 값
    """

    list_true = ["true", "1", "yes"]
    list_false = ["false", "0", "no"]

    if arg_str.lower() in list_true:
        return True
    if arg_str.lower() in list_false:
        return False
    return np.NaN


def list_chunk(lst: list, n_item: int) -> list:
    """리스트를 주어진 개수의 item 단위로 분할

    Args:
        lst (list): 분할할 리스트
        n_item (int): 분할할 각각의 item개수

    Returns:
        list: 분할된 리스트
    """
    return [lst[i : i + n_item] for i in range(0, len(lst), n_item)]


def unnesting(df: pd.DataFrame, explode_columns: list) -> pd.DataFrame:
    """컬럼 내부의 list를 explode하는 함수

    Args:
        df (pd.DataFrame): explode할 데이터프레임
        explode_columns (list): explode할 컬럼

    Returns:
        pd.DataFrame: explode된 데이터프레임
    """

    list_columns = df.columns
    idx = df.index.repeat(df[explode_columns[0]].str.len())
    df1 = pd.concat(
        [pd.DataFrame({x: np.concatenate(df[x].values)}) for x in explode_columns],
        axis=1,
    )
    df1.index = idx
    result = df1.join(df.drop(explode_columns, 1), how="left").reset_index(drop=True)
    result = result[list_columns]
    return result


def trim_df(df: pd.DataFrame) -> pd.DataFrame:
    """trim_df
    Dataframe의 모든 컬럼에 trim 적용

    Args:
        df (pd.DataFrame): trim을 적용할 dataframe

    Returns:
        pd.DataFrame: trim 적용된 dataframe
    """
    df_obj = df.select_dtypes(["object"])
    df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())
    return df


def is_number(value: str):
    try:
        judge = str(float(value))
        return False if (judge == "nan" or judge == "inf" or judge == "-inf") else True
    except ValueError:
        return False


def str_to_number(value: str):
    if is_number(value):
        try:
            return int(value)
        except ValueError:
            return float(value)
    return value
