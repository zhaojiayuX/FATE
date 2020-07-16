#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import uuid
import pymysql
import typing

from arch.api.base.utils.store_type import StoreEngine
from arch.api.data_table.table import Table
from arch.api.utils.profile_util import log_elapsed
from arch.api import WorkMode
from fate_flow.settings import WORK_MODE


# noinspection SpellCheckingInspection,PyProtectedMember,PyPep8Naming
class MysqlTable(Table):
    def __init__(self,
                 mode: typing.Union[int, WorkMode] = WORK_MODE,
                 persistent_engine: str = StoreEngine.MYSQL,
                 namespace: str = None,
                 name: str = None,
                 partition: int = 1,
                 address: dict = None,
                 **kwargs):
        self._name = name or str(uuid.uuid1())
        self._namespace = namespace or str(uuid.uuid1())
        self._partitions = partition
        self._strage_engine = persistent_engine
        self.address = address
        self._mode = mode
        '''
        database_config
        {
            'user': 'root',
            'passwd': 'fate_dev',
            'host': '127.0.0.1',
            'port': 3306,
            'charset': 'utf8'
        }
        '''
        try:
            self.con = pymysql.connect(host=self.address.get('host'),
                                       user=self.address.get('user'),
                                       passwd=self.address.get('passwd'),
                                       port=self.address.get('port'),
                                       db=namespace)
            self.cur = self.con.cursor()
        except:
            print("DataBase connect error,please check the db config.")

    def execute(self, sql, select=True):
        self.cur.execute(sql)
        if select:
            while True:
                result = self.cur.fetchone()
                if result:
                    yield result
                else:
                    break
        else:
            result = self.cur.fetchall()
            return result

    def get_name(self):
        return self._name

    def get_namespace(self):
        return self._namespace

    def get_partitions(self):
        return self._partitions

    def get_storage_engine(self):
        return self._strage_engine

    def get_address(self):
        return {'name': self._name, 'namespace': self._namespace}

    @log_elapsed
    def collect(self, min_chunk_size=0, use_serialize=True, **kwargs) -> list:
        sql = 'select * from {}'.format(self._name)
        data = self.execute(sql)
        return data

    def destroy(self):
        super().destroy()
        sql = 'drop table {}'.format(self._name)
        return self.execute(sql)

    @log_elapsed
    def count(self, **kwargs):
        sql = 'select count(*) from {}'.format(self._name)
        return self.execute(sql)

    def close(self):
        self.con.close()