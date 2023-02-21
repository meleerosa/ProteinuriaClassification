import logging
import os
from datetime import datetime
from math import sqrt
from typing import Any, Dict

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler

from modules.config import Config
from modules.utils.decorator import TryDecorator
from modules.utils.file_handler import chk_and_make_dir

model_logger = logging.getLogger("model")

class Model:
    _input_data: pd.DataFrame
    _train_input: np.ndarray
    _train_target: np.ndarray
    _test_input: np.ndarray
    _test_target: np.ndarray
    _input_scaler: RobustScaler
    _target_scaler: RobustScaler 
    _model: xgb.XGBRegressor
    _config: dict
    _model_path: str
    
    @property
    def h_param(self):
        return self._h_param

    def __init__(self, preprocessed_data, h_param: Dict = None) -> None:
        self._config = Config.instance().config
        self._model_logger = logging.getLogger("Model")
        self._preprocessed_data = preprocessed_data
        if h_param is None:
            self._h_param = self._config["hyper_parameter"]
        else:
            self._h_param = h_param
        self._random_state = self._config['random_state']


    @TryDecorator(logger= model_logger)
    def _split_data(self) -> None:
        if self._preprocessed_data is None or self._preprocessed_data.empty:
            raise Exception("preprocessed data is Empty")
        
        train_set, test_set = train_test_split(
            self._preprocessed_data, test_size= 0.2, random_state= 42, shuffle= True, stratify= self._preprocessed_data['요단백']
        )

        #Under Sampling
        abnormal = train_set.loc[train_set['요단백'] == 1]
        normal = train_set.loc[train_set['요단백'] == 0][:len(abnormal)]
        train_set = pd.concat([normal, abnormal]).sample(frac=1, random_state=self._random_state['random_state'])

        self._train_input = train_set.drop(columns = ['요단백']).values
        self._train_target = train_set["요단백"].values
        self._test_input = test_set.drop(columns = ['요단백']).values
        self._test_target = test_set["요단백"].values



        model_logger.info("Model Data Count-------------------------------------")
        model_logger.info(
            "preprocessed dataset  : " + str(len(self._preprocessed_data))
        )
        model_logger.info("train dataset      : " + str(len(self._train_input)))
        model_logger.info("test dataset       : " + str(len(self._test_input)))
        model_logger.info("-----------------------------------------------------")

    def _build_model(self) -> None:
        self._model = xgb.XGBClassifier(
        n_estimators = 200,
        reg_alpha = 0,
        reg_lambda = 1,
        booster = 'gbtree',
        learning_rate = 0.03,
        gamma = 0.1,
        subsample = 0.4,
        colsample_bytree = 1,
        max_depth = 7
        )

    def _fit(self) -> None:
        self._model.fit(self._train_input, self._train_target)

    def evaluate_model(self) -> dict:
        actual = self._test_target
        predict = self._model.predict(self._test_input)
        actual_train = self._train_target.reshape(-1,1)
        predict_train = self._model.predict(self._train_input)

        eval_metric = {
            'Train Accuracy': accuracy_score(actual_train, predict_train),
            'Train F1 score': f1_score(actual_train, predict_train),
            'Accuracy': accuracy_score(actual, predict),
            'F1 score': f1_score(actual, predict),
        }

        return eval_metric


    def predict(self, input_data: Any) -> Any:
        pred = []
        for each_input in input_data:
            pred.append(self._model.predict(each_input))
        return pred

    def _load_model(self, model_path: str) -> None:
        if not os.path.exists(model_path):
            model_logger.error("Model does not exsist.")
        else:
            self._model = xgb.load_model(model_path)

    def _save_model(self, model_path: str) -> None:
        chk_and_make_dir(model_path)
        self._model.save(model_path)

    def save_model(self, model_path: str = None) -> None:
        current_dt = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._model_path = model_path
        if self._model_path is None:
            self._model_path = os.path.join(
                self._config["path"]["output"], current_dt, "model"
            )
        self._save_model(self._model_path)

    def load_model(self, model_dt: str) -> None:
        model_path = os.path.join(self._config["path"]["output"], model_dt, "model")
        self._load_model(model_path)

    def fit_and_evaluate(self) -> Dict:
        self._split_data()
        self._build_model()
        self._fit()
        return self.evaluate_model()

    def fit_and_predict_test(self) -> Any:
        self._split_data()
        self._build_model()
        self._fit()
        self.save_model()
        self.evaluate_model()
        return self.predict(self._test_input)

