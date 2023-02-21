import os

import mlflow
from mlflow.tracking import MlflowClient

from modules.model import Model

MLFLOW_URI = os.getenv("DAS_MLFLOW_URI")


class DasMlflow:
    """DasMlflow class
        모델의 정보와 결과를 각 실험 별로 이름을 지정해 저장

    Attributes:
        self._model (type): mlflow를 통해 파라미터, 결과 등을 기록할 모델

    """

    def __init__(self, exp_name: str, model: Model) -> None:
        self._model = model
        mlflow.set_tracking_uri(MLFLOW_URI)

        client = MlflowClient()
        current_experiment = mlflow.get_experiment_by_name(exp_name)
        if current_experiment is None:
            self._experiment_id = client.create_experiment(exp_name)
        else:
            self._experiment_id = dict(current_experiment)["experiment_id"]

    def run(self):
        with mlflow.start_run(experiment_id=self._experiment_id) as run:
            mlflow.log_params(self._model.h_param)
            eval = self._model.fit_and_evaluate()
            mlflow.log_metrics(eval)
        mlflow.end_run()
        return eval
