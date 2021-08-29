import logging.config
import os

from src.lib.dir import PROJECT_ABSOLUTE_PATH


class Loggers:
    def __init__(self):
        # set log files path
        self.log_path = os.path.join(PROJECT_ABSOLUTE_PATH, "log")
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

        # set log config path
        self.log_conf_path = os.path.join(PROJECT_ABSOLUTE_PATH, "settings", 'log.conf')
        if not os.path.exists(self.log_conf_path):
            self.settings_dir_path = os.path.join(PROJECT_ABSOLUTE_PATH, 'settings')
            if not os.path.exists(self.settings_dir_path):
                os.mkdir(self.settings_dir_path)
            self.generate_log_conf()

    def get_logger(self, name="__name__"):
        logging.config.fileConfig(self.log_conf_path)
        logger = logging.getLogger(name=name)
        return logger

    def generate_log_conf(self):
        conf_file_template = """[loggers]
keys=root,error,info
[logger_root]
level=DEBUG
qualname=root
handlers=debugs
[logger_error]
level=ERROR
qualname=error
handlers=errors
[logger_info]
level=INFO
qualname=info
handlers=infos
[handlers]
keys=infos,errors,debugs
[handler_infos]
class=FileHandler
level=INFO
formatter=form
args=('{log_path}/info.log','a')
[handler_errors]
class=FileHandler
level=DEBUG
formatter=form
args=('{log_path}/error.log','a')
[handler_debugs]
class=FileHandler
level=DEBUG
formatter=form
args=('{log_path}/debug.log','a')
[formatters]
keys=form
[formatter_form]
format=%(asctime)s %(filename)s %(levelname)s  %(message)s
datefmt=%Y-%m-%d %H:%M:%S""".format(log_path=self.log_path)
        if os.path.exists(self.log_conf_path):
            os.remove(self.log_conf_path)
        with open(self.log_conf_path, "a+") as fn:
            fn.write(conf_file_template)
