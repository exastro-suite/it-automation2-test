# Copyright 2022 NEC Corporation#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
organization common function module
"""
from flask import request, g
import os
import base64

from common_libs.common.dbconnect import *  # noqa: F403
from common_libs.common.exception import AppException
from common_libs.common.logger import AppLog
from common_libs.common.message_class import MessageTemplate
from common_libs.api import set_api_timestamp, get_api_timestamp, app_exception_response, exception_response, check_request_body


def before_request_handler():
    """
    called before controller is excuted
    """
    try:
        set_api_timestamp()
        # create app log instance and message class instance
        g.applogger = AppLog()
        g.appmsg = MessageTemplate()

        check_request_body()

        # get organization_id
        organization_id = request.path.split("/")[2]
        g.ORGANIZATION_ID = organization_id
        # get workspace_id
        workspace_id = request.path.split("/")[4]
        g.WORKSPACE_ID = workspace_id

        # request-header check
        user_id = request.headers.get("User-Id")
        roles_org = request.headers.get("Roles")
        try:
            roles_decode = base64.b64decode(roles_org.encode()).decode("utf-8")
        except Exception:
            raise AppException("400-00001", ["Roles"], ["Roles"])
        roles = roles_decode.split("\n")
        if user_id is None or roles is None or type(roles) is not list:
            raise AppException("400-00001", ["User-Id or Roles"], ["User-Id or Roles"])

        g.USER_ID = user_id
        g.ROLES = roles

        debug_args = [request.method + ":" + request.url]
        g.applogger.info("[ts={}][api-start] url:{}".format(get_api_timestamp(), *debug_args))

        # set language
        language = request.headers.get("Language")
        if language:
            g.appmsg.set_lang(language)
            g.applogger.info("LANGUAGE({}) is set".format(language))
        else:
            language = os.environ.get("DEFAULT_LANGUAGE")
        g.LANGUAGE = language

        # initialize setting organization-db connect_info and connect check
        common_db = DBConnectCommon()  # noqa: F405
        g.applogger.debug("ITA_DB is connected")

        orgdb_connect_info = common_db.get_orgdb_connect_info(organization_id)
        common_db.db_disconnect()
        if orgdb_connect_info is False:
            raise AppException("999-00001", ["ORGANIZATION_ID=" + organization_id])

        g.db_connect_info = {}
        g.db_connect_info["ORGDB_HOST"] = orgdb_connect_info["DB_HOST"]
        g.db_connect_info["ORGDB_PORT"] = str(orgdb_connect_info["DB_PORT"])
        g.db_connect_info["ORGDB_USER"] = orgdb_connect_info["DB_USER"]
        g.db_connect_info["ORGDB_PASSWORD"] = orgdb_connect_info["DB_PASSWORD"]
        g.db_connect_info["ORGDB_ROOT_PASSWORD"] = orgdb_connect_info["DB_ROOT_PASSWORD"]
        g.db_connect_info["ORGDB_DATADBASE"] = orgdb_connect_info["DB_DATADBASE"]
        # gitlab connect info
        g.gitlab_connect_info = {}
        g.gitlab_connect_info["GITLAB_USER"] = orgdb_connect_info["GITLAB_USER"]
        g.gitlab_connect_info["GITLAB_TOKEN"] = orgdb_connect_info["GITLAB_TOKEN"]

        # initialize setting workspcae-db connect_info and connect check
        org_db = DBConnectOrg()  # noqa: F405
        g.applogger.debug("ORG_DB:{} can be connected".format(organization_id))

        wsdb_connect_info = org_db.get_wsdb_connect_info(workspace_id)
        org_db.db_disconnect()
        if wsdb_connect_info is False:
            raise AppException("999-00001", ["WORKSPACE_ID=" + workspace_id])

        g.db_connect_info["WSDB_HOST"] = wsdb_connect_info["DB_HOST"]
        g.db_connect_info["WSDB_PORT"] = str(wsdb_connect_info["DB_PORT"])
        g.db_connect_info["WSDB_USER"] = wsdb_connect_info["DB_USER"]
        g.db_connect_info["WSDB_PASSWORD"] = wsdb_connect_info["DB_PASSWORD"]
        g.db_connect_info["WSDB_DATADBASE"] = wsdb_connect_info["DB_DATADBASE"]

        ws_db = DBConnectWs(workspace_id)  # noqa: F405
        g.applogger.debug("WS_DB:{} can be connected".format(workspace_id))

        # set log-level for user setting
        g.applogger.set_user_setting(ws_db)
        ws_db.db_disconnect()
    except AppException as e:
        # catch - raise AppException("xxx-xxxxx", log_format, msg_format)
        return app_exception_response(e)
    except Exception as e:
        # catch - other all error
        return exception_response(e)


def check_auth_menu(menu_id, wsdb_istc=None):
    """
    check_auth_menu

    Arguments:
        menu_id: menu_id
        wsdb_istc: (class)DBConnectWs Instance
    Returns:
        (str) PRIVILEGE value
    """
    if not wsdb_istc:
        wsdb_istc = DBConnectWs(g.get('WORKSPACE_ID'))  # noqa: F405

    role_id_list = g.get('ROLES')
    prepared_list = list(map(lambda a: "%s", role_id_list))

    where = 'WHERE `MENU_ID`=%s AND `ROLE_ID` in ({}) AND `DISUSE_FLAG`=0'.format(",".join(prepared_list))
    data_list = wsdb_istc.table_select('T_COMN_ROLE_MENU_LINK', where, [menu_id, *role_id_list])

    res = False
    for data in data_list:
        privilege = data['PRIVILEGE']
        if privilege == '1':
            return privilege
        res = privilege

    return res
