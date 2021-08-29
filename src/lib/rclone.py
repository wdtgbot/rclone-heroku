import os
import shutil
import subprocess
import zipfile

import requests

from dir import PROJECT_ABSOLUTE_PATH
from log import Loggers
from md5 import get_md5_str


class Rclone:
    def __init__(self):
        self.rclone_path_of_zip = None
        self.rclone_bin_path = os.path.join(PROJECT_ABSOLUTE_PATH, "rclone", "bin", "rclone")
        self.rclone_logfile_dir = os.path.join(PROJECT_ABSOLUTE_PATH, "log", "tmp")

    def job_copy(self, src, dst):
        if not os.path.exists(self.rclone_logfile_dir):
            os.makedirs(self.rclone_logfile_dir)
            Loggers().get_logger("info").info(
                "创建rclone临时日志目录: {rclone_logfile_dir}".format(rclone_logfile_dir=self.rclone_logfile_dir))
        cmd = 'screen -dmS {screen_id} {rclone_bin} copy --use-json-log -vv --stats 10s --ignore-existing --log-file={log_file_path} {src} {dst}'.format(
            screen_id=get_md5_str(src + dst), rclone_bin=self.rclone_bin_path,
            log_file_path=os.path.join(self.rclone_logfile_dir, get_md5_str(src + dst) + ".log"), src=src, dst=dst)
        subprocess.Popen(cmd, shell=True)

    def get_job_info(self, src, dst) -> (bool, dict):
        """
        获取任务信息
        :param src:
        :param dst:
        :return: bool: 任务是否存在
        dict: {} for ts,tts,percentage,speed,eta,finish
        """
        logfile_name = get_md5_str(src + dst) + ".log"
        logfile_path = os.path.join(self.rclone_logfile_dir, logfile_name)
        if os.path.exists(logfile_path):
            infos = {
                'finish': 0
            }
            with open(logfile_path) as fn:
                for x in fn:
                    if 'go routines active' in x:
                        infos['ts'] = infos['tts']
                        infos['percentage'] = '100%'
                        infos['speed'] = '0/s'
                        infos['eta'] = '0s'
                        infos['finish'] = 1
                    if 'info' in x:
                        msgs = x.split(' ')
                        try:
                            infos['ts'] = msgs[5]
                            infos['tts'] = msgs[7] + msgs[8]
                            infos['percentage'] = msgs[9]
                            infos['speed'] = msgs[10] + msgs[11]
                            infos['eta'] = msgs[13].replace('\\nErrors:', '')
                        except:
                            pass
                return True, infos
        else:
            return False, None

    def check_rclone_installed(self) -> bool:
        """
        判断是否安装rclone
        :return: bool
        """
        if os.path.exists(self.rclone_bin_path):
            return True
        else:
            return False

    def install_rclone(self) -> bool:
        """
        安装rclone
        :return: bool
        """
        Loggers().get_logger("info").info("开始下载rclone")
        rclone_install_url = "https://downloads.rclone.org/rclone-current-linux-amd64.zip"
        i = 0
        while i < 3:
            try:
                response = requests.get(rclone_install_url, timeout=20)
                break
            except requests.exceptions.RequestException:
                Loggers().get_logger("info").info("重试{i} :下载rclone".format(i=i))
                i += 1
        if i == 3:
            Loggers().get_logger("error").info("rclone 下载超时")
            return False
        # install rclone
        rclone_zip_path = os.path.join(PROJECT_ABSOLUTE_PATH, "rclone.zip")
        if os.path.exists(rclone_zip_path):
            os.remove(rclone_zip_path)
        if i < 3:
            with open(rclone_zip_path, "wb") as fn:
                fn.write(response.content)
            Loggers().get_logger("info").info("rclone 下载完成")
        zip_file = zipfile.ZipFile(rclone_zip_path)
        zip_list = zip_file.namelist()
        print(zip_list)
        for f in zip_list:
            if str(f).endswith("rclone"):
                zip_file.extract(f, os.path.join(PROJECT_ABSOLUTE_PATH, "rclone"))
                Loggers().get_logger("info").info("rclone 解压完成")
                print("-- rclone 解压完成")
        zip_file.close()
        self.__find_rclone_from_path(os.path.join(PROJECT_ABSOLUTE_PATH, "rclone"))
        if self.rclone_path_of_zip:
            if not os.path.exists(os.path.join(PROJECT_ABSOLUTE_PATH, "rclone", "bin")):
                os.mkdir(os.path.join(PROJECT_ABSOLUTE_PATH, "rclone", "bin"))
            if os.path.exists(self.rclone_bin_path):
                os.remove(self.rclone_bin_path)
            shutil.move(self.rclone_path_of_zip, self.rclone_bin_path)
            subprocess.Popen("chmod +x {rclone_path}".format(
                rclone_path=self.rclone_bin_path), shell=True)

        # clear
        if os.path.exists(rclone_zip_path):
            os.remove(rclone_zip_path)
            Loggers().get_logger("info").info("清理临时文件: {path}".format(path=rclone_zip_path))

        rclone_extract_path = os.path.join(PROJECT_ABSOLUTE_PATH, "rclone")
        for dir in os.listdir(rclone_extract_path):
            print(dir)
            if dir != "bin":
                print("删除")
                os.removedirs(os.path.join(rclone_extract_path, dir))
                Loggers().get_logger("info").info("清理临时文件夹: {path}".format(path=os.path.join(rclone_extract_path, dir)))
        return True

    def __find_rclone_from_path(self, path):
        if path.endswith("bin"):
            return
        if os.path.isfile(path):
            self.rclone_path_of_zip = path

        if os.path.isdir(path):
            for x in os.listdir(path):
                self.__find_rclone_from_path(path=os.path.join(path, x))
