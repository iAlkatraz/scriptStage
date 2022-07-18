import os
import sys
import time
import yaml

from opc_ua_module_v4 import OpcUaModule_V4
from support_db_module import SupportDb
from logger import logger


class Retrieve:

    def __init__(self, conf_path):
        self.cfg = yaml.safe_load(open(conf_path))
        print(self.cfg)
        self.OPCUA = OpcUaModule_V4(conf_path)
        self.DB = SupportDb(self.cfg['support_db_params'])
        self.empty_d = {}

    def run(self):
        while 1:
            try:
                d = self.OPCUA.retrieve_data()
                if self.DB.last_entry is not None:
                    d_prev = yaml.safe_load(self.DB.last_entry[4])
                    if self.compare_datas(d, d_prev) and d != self.empty_d:
                        self.DB.insert_datas(d=d)
                else:
                    if d != self.empty_d:
                        self.DB.insert_datas(d=d)

                self.DB.last_entry = self.DB.get_last_entry()
                time.sleep(self.cfg['sleep'])

            except KeyboardInterrupt:
                sys.exit(1)
            except Exception as e:
                time.sleep(15)
                logger.exception(f'{e}')

    def compare_datas(self, d, d_prev):
        diff = 0
        for k,v in d.items():
            if d[k] != d_prev[k]:
                diff += 1
        if diff > 0:
            return True

        return False


conf_path = os.getcwd() + '\\conf.yml'
module = Retrieve(conf_path)
module.run()