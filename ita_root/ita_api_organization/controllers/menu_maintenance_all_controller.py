#   Copyright 2022 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import connexion
import six

from common_libs.common import *  # noqa: F403
from libs import menu_maintenance_all
from flask import jsonify

import sys
sys.path.append('../../')
from common_libs.loadtable.load_table import loadTable


def maintenance_all(body, workspace_id, menu):  # noqa: E501
    """maintenance_all

    レコードを一括で登録/更新/廃止/復活する # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param workspace_id: ワークスペース名
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str

    :rtype: InlineResponse200
    """
    # if connexion.request.is_json:
    #    body = object.from_dict(connexion.request.get_json())  # noqa: E501
    # return 'do some magic!'

    try:
        # DB接続
        objdbca = DBConnectWs(workspace_id)  # noqa: F405

        parameters = []
        if connexion.request.is_json:
            body = connexion.request.get_json()
            parameters = body

        # ####メモ：langは取得方法検討中
        result_data = menu_maintenance_all.rest_maintenance_all(objdbca, menu, parameters, 'ja')
        print(["result_data",result_data])
        #### result_code,msg未対応
        result = {
            "result": "result_code", #result_data[0],
            "data": result_data, #result_data[1],
            "message": "msg" #result_data[2]
        }
        return jsonify(result), 200
    
    except Exception as result:
        # ####メモ：Exceptionクラス作成後、resultをそのままreturnしたい。
        print(result)
        result_dummy = {
            "result": "StatusCode",
            "message": "aaa bbb ccc"
        }, 500
        return result_dummy