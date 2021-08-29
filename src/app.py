import os

import sentry_sdk
from flask import Flask
from flask import request
from sentry_sdk.integrations.flask import FlaskIntegration

from lib.dir import PROJECT_ABSOLUTE_PATH
from lib.rclone import Rclone

PORT = os.getenv("PORT")

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/api/v1/add_config", methods=['POST'])
def add_config():
    config = request.form.get("config")
    if os.path.exists(os.path.join(PROJECT_ABSOLUTE_PATH, "rclone.conf")):
        os.remove(os.path.join(PROJECT_ABSOLUTE_PATH, "rclone.conf"))
    with open(os.path.join(PROJECT_ABSOLUTE_PATH, "rclone.conf"), "a+") as fn:
        fn.write(config)
    return {
        "code": 200,
        "msg": "config file add succeed."
    }


@app.route("/api/v1/install_rclone", methods=['POST'])
def install_rclone():
    r = Rclone()
    tf = r.install_rclone()
    if tf:
        return {
            "code": 200,
            "msg": "rclone install succeed."
        }
    else:
        return {
            "code": 400
        }


@app.route("/api/v1/run_job", methods=['POST'])
def run_job():
    src = request.form.get("src")
    if not src:
        return {
            "code": 400,
            "msg": "Src not found."
        }
    dst = request.form.get("dst")
    if not dst:
        return {
            "code": 400,
            "msg": "dst not found."
        }

    r = Rclone()
    if not r.check_rclone_installed():
        tf = r.install_rclone()
        if tf:
            r.job_copy(src, dst)
            return {
                "code": 200,
                "msg": "Run job succeed."
            }
    else:
        r.job_copy(src, dst)
        return {
            "code": 200,
            "msg": "Run job succeed."
        }


@app.route("/api/v1/get_job", methods=['POST'])
def get_job():
    src = request.form.get("src")
    if not src:
        return {
            "code": 400,
            "msg": "Src not found."
        }
    dst = request.form.get("dst")
    if not dst:
        return {
            "code": 400,
            "msg": "dst not found."
        }
    s = {
        "code": 200,
    }
    r = Rclone()
    tf, infos_dict = r.get_job_info(src=src, dst=dst)
    # 任务存在
    if tf:
        s["infos"] = infos_dict
        return s
    else:
        return {
            "code": 400,
            "msg": "job not found."
        }


@app.route("/api/v1/get_job_log", methods=['POST'])
def get_job_log():
    src = request.form.get("src")
    if not src:
        return {
            "code": 400,
            "msg": "Src not found."
        }
    dst = request.form.get("dst")
    if not dst:
        return {
            "code": 400,
            "msg": "dst not found."
        }

    r = Rclone()
    tf, msg = r.get_job_logfile(src=src, dst=dst)
    if tf:
        return {
            "code": 200,
            "msg": msg
        }
    else:
        return {
            "code": 400,
            "msg": "file not found."
        }


@app.route("/api/v1/get_cmd_log")
def get_cmd_log():
    if os.path.exists("/root/rclone.log"):
        with open("/root/rclone.log", "a+") as fn:
            msg = fn.read()
        return {
            "code": 200,
            "msg": msg
        }
    else:
        return {
            "code": 400,
            "msg": "file not found."
        }


if __name__ == '__main__':
    if os.getenv("sentry_dsn"):
        print("sentry_dsn")
        sentry_sdk.init(
            dsn=os.getenv("sentry_dsn"),
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0
        )
    app.run("0.0.0.0", PORT)
