from flask import g
import os
"""
  Ansible共通モジュール
"""


def get_AnsibleDriverTmpPath():
    """
      Ansible用tmpバスを取得する。
      Arguments:
        なし
      Returns:
        Ansible用tmpバス
    """
    return getDataRelayStorageDir() + "/tmp/driver/ansible"

def getFileupLoadColumnPath(menuid, Column):
    """
      Ansible用tmpバスを取得する。
      Arguments:
        なし
      Returns:
        Ansible用tmpバス
    """
    return getDataRelayStorageDir() + "/uploadfiles/{}/{}".format(menuid,Column)


def getDataRelayStorageDir():
    return "{}{}/{}".format(os.environ["PYTHONPATH"], g.get('ORGANIZATION_ID'), g.get('WORKSPACE_ID'))
  

def getInputDataTempDir(EcecuteNo, DriverName):
    """
      Ansible Gitリポジトリ用 tmpバスを取得する。
      Arguments:
        EcecuteNo: 作業番号
        DriverName: オケストレータID  vg_tower_driver_name
      Returns:
        Ansible Gitリポジトリ用 tmpバス
    """
    ary = {}
    basePath = get_AnsibleDriverTmpPath()
    ary["BASE_DIR"] = basePath
    tgtPath = basePath + "/{}_{}".format(DriverName, EcecuteNo)
    ary["DIR_NAME"] = tgtPath
    return ary
