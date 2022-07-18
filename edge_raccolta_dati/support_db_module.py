import os
import sys
import sqlite3
import datetime

from sqlite3 import Error

from logger import logger


class SupportDb:

    def __init__(self, params_dict):
        if isinstance(params_dict, dict):
            self.params = params_dict
            self.db_path = os.getcwd() + '\\' + self.params['db_name']
        else:
            logger.exception('Database support module:\nErrore importazione parametri!\nEXIT!\n')
            sys.exit(1)
        self.create_table()
        self.last_entry = self.get_last_entry()

    def insert_datas(self, d=None, file_path=None, index=-1, key=None, is_send=0):
        if d is None and file_path is None and index == -1 and key is None and is_send == 0:
            return
        cmd = 'INSERT INTO ' + self.params['table_name'] + ' (' + \
              'key, file_path, idx, datas, is_sended, timestamp) VALUES (?,?,?,?,?,?);'

        values = (str(key) if key is not None else 'none',
                  str(file_path) if file_path is not None else 'none',
                  int(index),
                  str(d) if d is not None else 'none',
                  is_send,
                  str(datetime.datetime.now()),)
        try:
            connection, cursor = self.connect_to_db()
            cursor.execute(cmd, values)
            connection.commit()
            self.close_connection(connection, cursor)

            return
        except Exception as e:
            logger.exception(f'Support db module, error during datas insert; details:\n{e}')

    def connect_to_db(self):
        try:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()

            return connection, cursor

        except Exception as e:
            logger.exception(f'Support db module, connection error; details:\n{e}')

    def close_connection(self, connection, cursor):
        try:
            cursor.close()
            connection.close()
            del cursor,connection
        except Exception as e:
            logger.exception(f'Support db module, error during close connection; details:\n{e}')

        return

    def update_table(self, id_):
        cmd = 'UPDATE ' + self.params['table_name'] +\
              ' SET is_sended=1 WHERE id=?'
        try:
            connection, cursor = self.connect_to_db()
            cursor = connection.cursor()
            cursor.execute(cmd, (id_, ))
            connection.commit()
            self.close_connection(connection, cursor)

            return
        except Exception as e:
            logger.exception(f'Database support module exception:\n {e} \nIn function UPDATE_TABLE!')

    def create_table(self):
        cmd = 'CREATE TABLE IF NOT EXISTS ' + self.params['table_name'] + ' (' +\
              'id integer PRIMARY KEY, ' + \
              'key text NOT NULL, ' + \
              'file_path text NOT NULL, ' + \
              'idx integer NOT NULL, ' + \
              'datas text, ' + \
              'is_sended integer NOT NULL,' + \
              'timestamp text NOT NULL);'

        connection, cursor = self.connect_to_db()
        cursor.execute(cmd)
        connection.commit()
        self.close_connection(connection, cursor)

        return

    def get_last_entry(self):
        try:
            connection, cursor = self.connect_to_db()
            cursor.execute('SELECT * FROM ' +
                           self.params['table_name'] +
                           ' ORDER BY id DESC LIMIT 1')
            res = cursor.fetchone()
            self.close_connection(connection, cursor)

            return res

        except Error as e:
            logger.exception(f'Error during support db connection! Details:\n{e}')

    def get_entries_from_param(self, param, value):
        try:
            connection, cursor = self.connect_to_db()
            cursor.execute("SELECT * FROM {} WHERE {} = \"{}\" ORDER BY id"
                           .format(self.params['table_name'], param, value))
            res = cursor.fetchall()
            self.close_connection(connection, cursor)

            return res

        except Error as e:
            logger.exception(f'Error during support db connection! Details:\n{e}')

    def get_first_entry(self):
        try:
            connection, cursor = self.connect_to_db()
            cursor.execute('SELECT * FROM ' +
                           self.params['table_name'] +
                           ' ORDER BY id ASC LIMIT 1')
            res = cursor.fetchone()
            self.close_connection(connection, cursor)

            return res

        except Error as e:
            logger.exception(f'Error during support db connection! Details:\n{e}')

    def check_is_send(self, id_):
        cmd = "SELECT is_sended FROM {} WHERE rowid=?".format(self.params['table_name'])
        connection, cursor = self.connect_to_db()
        cursor.execute(cmd, (id_, ))
        res = cursor.fetchone()[0]
        self.close_connection(connection, cursor)

        if res:
            return True

        return False

    def check_db_lenght(self):
        cmd_last = 'SELECT * FROM ' +\
                    self.params['table_name'] +\
                    ' ORDER BY id DESC LIMIT 1'
        cmd_first = 'SELECT * FROM ' +\
                    self.params['table_name'] +\
                    ' ORDER BY id LIMIT 1'
        try:
            connection, cursor = self.connect_to_db()
            cursor.execute(cmd_last)
            last = cursor.fetchone()
            cursor.execute(cmd_first)
            first = cursor.fetchone()

            if first is None or last is None:
                return

            delta = last[0] - first[0]
            if delta >= self.params['max_lenght']:
                cmd = 'DELETE FROM ' + self.params['table_name'] +\
                      ' WHERE id=?'
                to_delete = []
                range_ = list(range(first[0], int(last[0]/2)))
                for i in range_:
                    if self.check_is_send(i):
                        to_delete.append((i,))
                if len(to_delete) > 0:
                    cursor.executemany(cmd, to_delete)
                    connection.commit()
            self.close_connection(connection, cursor)

            return

        except Error as e:
            logger.exception(f'Error during support db connection! Details:\n{e}')
        except Exception as e:
            logger.exception(f'Generc error in end routine! Details:\n{e}')

    def execute_command(self, cmd, commit=False, execute_many=False, params=None, retrn=False):
        try:
            connection, cursor = self.connect_to_db()
            if not retrn:
                if execute_many:
                    cursor.executemany(cmd, params)
                else:
                    cursor.execute(cmd)
                if commit:
                    connection.commit()
                self.close_connection(connection, cursor)
                return
            else:
                if execute_many:
                    cursor.executemany(cmd, params)
                    res = cursor.fetchall()
                else:
                    cursor.execute(cmd)
                    res = cursor.fetchall()
                if commit:
                    connection.commit()
                self.close_connection(connection, cursor)
                return res

        except Error as e:
            logger.exception(f'Database support module\nError during command execution!\nDetails:\n{e}')

    def read_db(self, N='*', order='DESC'):
        cmd = f'SELECT {N} FROM ' + self.params['table_name'] +\
              f' ORDER BY id {order}'

        try:
            connection, cursor = self.connect_to_db()
            cursor.execute(cmd)
            res = cursor.fetchall()
            self.close_connection(connection, cursor)

            return res

        except Exception as e:
            logger.exception(f'Database support module exception:\n{e}\nin function READ_DB')

    def check_entry(self, entry=None, d=None, file_path=None, index=-1, key=None, last=True):
        if last and entry is not None:
            if self.last_entry is None:
                return True
            if entry[1:5] != self.last_entry[1:5]:
                return True
            return False
        elif last and entry is None:
            if self.last_entry is None:
                return True
            values = (key if key is not None else 'none',
                      file_path if file_path is not None else 'none',
                      index,
                      str(d) if d is not None else 'none')
            if values != self.last_entry[1:5]:
                return True
            return False
        elif not last and entry is not None:
            values = (key if key is not None else 'none',
                      file_path if file_path is not None else 'none',
                      index,
                      str(d) if d is not None else 'none')
            if values != entry[1:5]:
                return True
            return False
        else:
            return False

    def end_routine(self, lock):
        if lock is None:
            self.last_entry = self.get_last_entry()
            self.check_db_lenght()
            return

        lock.acquire()
        self.last_entry = self.get_last_entry()
        self.check_db_lenght()
        lock.release()

        return
