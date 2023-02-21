import numpy as np


class Postprocess:
    _predicted_value: np.ndarray

    def __init__(self, predicted_value):
        self._predicted_value = predicted_value

    def post_process(self) -> None:
        self._post_processed_data = self._predicted_value
        pass

    def run(self):
        self.post_process()
        return self._post_processed_data
