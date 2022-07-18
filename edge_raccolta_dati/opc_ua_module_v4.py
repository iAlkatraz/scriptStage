import re
import os
import sys
import yaml

from opcua import Client

from logger import logger


class OpcUaModule_V4:

    def __init__(self,conf_file_path):
        with open(conf_file_path) as f:
            self.configuration = yaml.safe_load(f)
        if not isinstance(self.configuration, dict):
            sys.exit('WRONG DICT!!')
        if not self.configuration['opcua_params']['static_plc']:
            #self.parse_path()
            sys.exit('WRONG!!')

        self.is_connected = False
        self.client = None

    def create_client(self):
        client = Client(self.configuration['machine_ip'], timeout=120)
        if self.configuration['opcua_params']['encrypt']:
            key_path = os.getcwd() + '\\key.pem'
            cert_path = os.getcwd() + '\\certificate.der'
            sec_str = self.configuration['opcua_params']['policy'] + ',' + self.configuration['opcua_params']['mode'] +\
                      ',' + cert_path + ',' + key_path
            client.set_security_string(sec_str)
        if self.configuration['opcua_params']['user_auth']:
            client.set_user(self.configuration['opcua_params']['user'])
            client.set_password(self.configuration['opcua_params']['passwd'])

        return client

    def retrieve_data(self):
        d = {}
        if not self.configuration['opcua_params']['persistent'] and self.client is None:
            try:
                client = self.create_client()
                client.connect()


                for n, node_id in self.configuration['var_list']['read'].items():
                    d[n] = client.get_node(node_id).get_value()

                client.disconnect()
                client.close_session()
                del client

            except Exception as e:
                try:
                    client.disconnect()
                    client.close_session()
                except OSError:
                    pass
                logger.error(f'OPC-UA MODULE v3 exception:\n{e}\n in function RETRIEVE_DATA!')

            return d

        elif self.configuration['opcua_params']['persistent'] and self.is_connected:
            try:
                for n, node_id in self.configuration['var_list']['read'].items():
                    d[n] = self.client.get_node(node_id).get_value()

            except Exception as e:
                self.is_connected = False
                try:
                    if not isinstance(self.client, Client):
                        self.client = self.create_client()
                    else:
                        self.client.disconnect()

                    self.client.connect()
                    self.is_connected = True

                    #logger.info(f"\n\nself.configuration['var_list']['read'].items: {self.configuration['var_list']['read'].items()}\n\n")

                    for n, node_id in self.configuration['var_list']['read'].items():
                        #logger.info(f"\nN: {n} - NODE_ID: {node_id}")
                        d[n] = self.client.get_node(node_id).get_value()

                except Exception as e:
                    self.is_connected = False
                    logger.error(f'OPC-UA MODULE v3 exception:\n{e}\n in function RETRIEVE_DATA!')
                    #raise Exception("Can't connect by OPCUA! The machine can be power-off!")

            return d

        elif self.configuration['opcua_params']['persistent'] and not self.is_connected:
            try:
                if not isinstance(self.client, Client):
                    self.client = self.create_client()

                self.client.connect()
                self.is_connected = True

                #logger.info(f"\n\nself.configuration['var_list']['read'].items: {self.configuration['var_list']['read'].items()}\n\n")

                for n, node_id in self.configuration['var_list']['read'].items():
                    #logger.info(f"\nN: {n} - NODE_ID: {node_id}")
                    d[n] = self.client.get_node(node_id).get_value()

            except Exception as e:
                self.is_connected = False
                logger.error(f'OPC-UA MODULE v3 exception:\n{e}\n in function RETRIEVE_DATA!')
                #raise Exception("Can't connect by OPCUA! The machine can be power-off!")

        return d

    def create_paths(self):
        for k,v in self.configuration['var_list']['read'].items():
            v = v.split('/')
            self.configuration['var_list']['read'][k] = v

        return

    @staticmethod
    def get_name(self, node):
        return node.get_display_name().Text

    @staticmethod
    def getIdentifier(self, node):
        s = str(node)
        if re.search('(ns\=)+', s):
            return s.replace('(', ' ').replace(')', '').split()[-1]
        else:
            ns = 'ns=' + str(node.get_browse_name()).replace(')', '').split('(')[1].split(':')[0]
            id_ = s.replace('(', ' ').replace(')', '').split()[-1]
            ns_id = ns + ';' + id_
            return ns_id
