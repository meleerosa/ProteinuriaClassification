import atexit
import os

from modules.config import Config
from modules.das_mlflow import DasMlflow
from modules.model import Model
from modules.postprocess import Postprocess
from modules.preprocess import Preprocess
from modules.utils.default_logger_config import DefaultLogger
from modules.utils.file_handler import chk_and_make_dir

if __name__ == "__main__":
    # config 설정
    config_path = os.path.join("config", "config.ini")
    config = Config.instance(config_path).config

    # logger 세팅
    default_logger = DefaultLogger()
    main_logger = default_logger.setDefaultLogger("main", config["log"]["path"])
    atexit.register(default_logger.rename_log_file)

    # output 디렉토리 세팅
    for path in config["path"]:
        chk_and_make_dir(config["path"][path])

    main_logger.info("Program Start")
    main_logger.info(config)
    preprocess = Preprocess()
    preprocessed_data = preprocess.run()
    model = Model(preprocessed_data)
    predicted_data = model.fit_and_evaluate()
    mlflow = DasMlflow("test2", model)
    predicted_data = mlflow.run()
    postprocess = Postprocess(predicted_data)
    result = postprocess.run()

    main_logger.info(f"result: {result}")