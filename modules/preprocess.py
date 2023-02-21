import logging
import os
import pickle
from typing import Any, Tuple

import numpy as np
import pandas as pd

from modules.config import Config
from modules.utils.decorator import TryDecorator

preprocess_logger = logging.getLogger("Preprocess")

class Preprocess:

    _raw_data : pd.DataFrame
    _preprocessed_data: pd.DataFrame
    _train_input: np.ndarray
    _train_target: np.ndarray
    _test_input: np.ndarray
    _test_target: np.ndarray

    @property
    def raw_data(self):
        return self._raw_data

    @raw_data.setter
    def raw_data(self, value):
        self._raw_data = value

    def __init__(self) -> None:
        self._config = Config.instance().config

    def load_data(self):
        self._raw_data = pd.read_csv(
            os.path.join(self._config["path"]['data'], 'data.csv')
        , encoding= 'utf-8')
        pass

    def drop_anomalies(self):
        # 특별한 이상치 처리(전체 dataset에 적용)

        if '청력(우)' in self._raw_data.columns:
            idx = self._raw_data[self._raw_data['청력(우)'] == 3].index
            self._raw_data.drop(index = idx, inplace= True)

        if '청력(좌)' in self._raw_data.columns:
            idx = self._raw_data[self._raw_data['청력(좌)'] == 3].index
            self._raw_data.drop(index = idx, inplace= True)

        if ('시력(우)' in self._raw_data.columns):
            self._raw_data.loc[(self._raw_data['시력(우)'] == 9.9),'시력(우)'] = 0
        
        if '시력(좌)' in self._raw_data.columns:
            self._raw_data.loc[(self._raw_data['시력(좌)'] == 9.9),'시력(좌)'] = 0

        if '허리둘레' in self._raw_data.columns:
            idx = self._raw_data[(self._raw_data['허리둘레'] == 999.0) | (self._raw_data['허리둘레'] == 680.0)].index
            self._raw_data.drop(index = idx, inplace= True)
            
        self._raw_data = self._raw_data.reset_index(drop = True)

    def preprocess(self) -> None:
        self._raw_data = self._raw_data[[
            '연령대 코드(5세단위)', '신장(5Cm단위)',
            '허리둘레', '시력(우)', '식전혈당(공복혈당)', 
            'HDL 콜레스테롤', 'LDL 콜레스테롤',
            '혈색소', '(혈청지오티)AST', '(혈청지오티)ALT', 
            '감마 지티피', '흡연상태',
            '음주여부', '치석'
            ]]
        self._raw_data.dropna(inplace = True)
        self.drop_anomalies()
        self._preprocessed_data = self._raw_data
        preprocess_logger.info("Model Data Count-------------------------------------")
        preprocess_logger.info("raw dataset        : " + str(len(self._raw_data)))
        preprocess_logger.info(
            "preprocessed dataset  : " + str(len(self._preprocessed_data))
        )
        preprocess_logger.info("-----------------------------------------------------")
        pass

    def run(self) -> Any:
        self.load_data()
        self.preprocess()
        return self._preprocessed_data