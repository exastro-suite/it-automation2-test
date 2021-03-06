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

from common_libs.common import *  # noqa: F403
from flask import g
from libs.organization_common import check_auth_menu


def collect_menu_info(objdbca, menu):
    """
        メニュー情報の取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu: メニュー string
        RETRUN:
            info_data
    """
    # テーブル名
    t_common_menu = 'T_COMN_MENU'
    t_common_menu_table_link = 'T_COMN_MENU_TABLE_LINK'
    t_common_menu_column_link = 'T_COMN_MENU_COLUMN_LINK'
    t_common_column_class = 'T_COMN_COLUMN_CLASS'
    t_common_column_group = 'T_COMN_COLUMN_GROUP'
    t_common_menu_group = 'T_COMN_MENU_GROUP'
    
    # 変数定義
    lang = g.LANGUAGE
    
    # 『メニュー管理』テーブルから対象のデータを取得
    ret = objdbca.table_select(t_common_menu, 'WHERE MENU_NAME_REST = %s AND DISUSE_FLAG = %s', [menu, 0])
    if not ret:
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException("200-00001", log_msg_args, api_msg_args)  # noqa: F405
    
    menu_id = ret[0].get('MENU_ID')  # 対象メニューを特定するためのID
    menu_group_id = ret[0].get('MENU_GROUP_ID')  # 対象メニューグループを特定するためのID
    menu_name = ret[0].get('MENU_NAME_' + lang.upper())
    login_necessity = ret[0].get('LOGIN_NECESSITY')
    auto_filter_flg = ret[0].get('AUTOFILTER_FLG')
    initial_filter_flg = ret[0].get('INITIAL_FILTER_FLG')
    web_print_limit = ret[0].get('WEB_PRINT_LIMIT')
    web_print_confirm = ret[0].get('WEB_PRINT_CONFIRM')
    xls_print_limit = ret[0].get('XLS_PRINT_LIMIT')
    sort_key = ret[0].get('SORT_KEY')
    
    # メニューに対するロール権限をチェック（Falseなら権限エラー）
    role_check = check_auth_menu(menu_id)
    if not role_check:
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException("401-00001", log_msg_args, api_msg_args)  # noqa: F405
    
    # check_auth_menuの戻り値をprivilegeの値として使用([1: メンテナンス可, 2: 閲覧のみ] ロールが複数あり混在する場合は1が優先される)
    privilege = role_check
    
    # 『メニュー-テーブル紐付管理』テーブルから対象のデータを取得
    ret = objdbca.table_select(t_common_menu_table_link, 'WHERE MENU_ID = %s AND DISUSE_FLAG = %s', [menu_id, 0])
    if not ret:
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException("200-00002", log_msg_args, api_msg_args)  # noqa: F405
    
    menu_info = ret[0].get('MENU_INFO_' + lang.upper())
    sheet_type = ret[0].get('SHEET_TYPE')
    history_table_flag = ret[0].get('HISTORY_TABLE_FLAG')
    table_name = ret[0].get('TABLE_NAME')
    view_name = ret[0].get('VIEW_NAME')
    inherit = ret[0].get('INHERIT')
    vertical = ret[0].get('VERTICAL')
    row_insert_flag = ret[0].get('ROW_INSERT_FLAG')
    row_update_flag = ret[0].get('ROW_UPDATE_FLAG')
    row_disuse_flag = ret[0].get('ROW_DISUSE_FLAG')
    row_reuse_flag = ret[0].get('ROW_REUSE_FLAG')
    
    # 『メニューグループ管理』テーブルから対象のデータを取得
    ret = objdbca.table_select(t_common_menu_group, 'WHERE MENU_GROUP_ID = %s AND DISUSE_FLAG = %s', [menu_group_id, 0])
    if not ret:
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException("200-00003", log_msg_args, api_msg_args)  # noqa: F405
    
    menu_group_name = ret[0].get('MENU_GROUP_NAME_' + lang.upper())
    parent_menu_group_id = ret[0].get('PARENT_MENU_GROUP_ID')
    parent_menu_group_name = None
    if parent_menu_group_id:
        ret = objdbca.table_select(t_common_menu_group, 'WHERE MENU_GROUP_ID = %s AND DISUSE_FLAG = %s', [parent_menu_group_id, 0])
        if ret:
            parent_menu_group_name = ret[0].get('MENU_GROUP_NAME_' + lang.upper())
    
    menu_info_data = {
        'menu_info': menu_info,
        'menu_group_id': menu_group_id,
        'menu_group_name': menu_group_name,
        'parent_menu_group_id': parent_menu_group_id,
        'parent_menu_group_name': parent_menu_group_name,
        'menu_id': menu_id,
        'menu_name': menu_name,
        'sheet_type': sheet_type,
        'history_table_flag': history_table_flag,
        'table_name': table_name,
        'view_name': view_name,
        'inherit': inherit,
        'vertical': vertical,
        'row_insert_flag': row_insert_flag,
        'row_update_flag': row_update_flag,
        'row_disuse_flag': row_disuse_flag,
        'row_reuse_flag': row_reuse_flag,
        'login_necessity': login_necessity,
        'auto_filter_flg': auto_filter_flg,
        'initial_filter_flg': initial_filter_flg,
        'web_print_limit': web_print_limit,
        'web_print_confirm': web_print_confirm,
        'xls_print_limit': xls_print_limit,
        'sort_key': sort_key,
        'privilege': privilege
    }
    
    # 『カラムクラスマスタ』テーブルからcolumn_typeの一覧を取得
    ret = objdbca.table_select(t_common_column_class, 'WHERE DISUSE_FLAG = %s', [0])
    column_class_master = {}
    for recode in ret:
        column_class_master[recode.get('COLUMN_CLASS_ID')] = recode.get('COLUMN_CLASS_NAME')
    
    # 『カラムグループ管理』テーブルからカラムグループ一覧を取得
    ret = objdbca.table_select(t_common_column_group, 'WHERE DISUSE_FLAG = %s', [0])
    column_group_list = {}
    if ret:
        for recode in ret:
            add_data = {
                "column_group_id": recode.get('COL_GROUP_ID'),
                "column_group_name": recode.get('COL_GROUP_NAME_' + lang.upper()),
                "parent_column_group_id": recode.get('PA_COL_GROUP_ID')
            }
            column_group_list[recode.get('COL_GROUP_ID')] = add_data
    
    # 『メニュー-カラム紐付管理』テーブルから対象のデータを取得
    ret = objdbca.table_select(t_common_menu_column_link, 'WHERE MENU_ID = %s AND DISUSE_FLAG = %s ORDER BY COLUMN_DISP_SEQ ASC', [menu_id, 0])
    if not ret:
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException("200-00004", log_msg_args, api_msg_args)  # noqa: F405
    
    column_info_data = {}
    tmp_column_group = {}
    column_group_parent_of_child = {}  # カラムグループの親子関係があるとき、子の一番大きい親を結びつける
    for count, recode in enumerate(ret, 1):
        # json形式のレコードは改行を削除
        validate_option = recode.get('VALIDATE_OPTION')
        if type(validate_option) is str:
            validate_option = validate_option.replace('\n', '')
            
        before_validate_register = recode.get('BEFORE_VALIDATE_REGISTER')
        if type(before_validate_register) is str:
            before_validate_register = before_validate_register.replace('\n', '')
            
        after_validate_register = recode.get('AFTER_VALIDATE_REGISTER')
        if type(after_validate_register) is str:
            after_validate_register = after_validate_register.replace('\n', '')
        
        # カラムグループIDがあればカラムグループ名を取得
        column_group_id = recode.get('COL_GROUP_ID')
        column_group_name = ''
        if column_group_id:
            column_group_name = column_group_list.get(column_group_id).get('column_group_name')
        
        detail = {
            'column_id': recode.get('COLUMN_DEFINITION_ID'),
            'column_name': recode.get('COLUMN_NAME_' + lang.upper()),
            'column_name_rest': recode.get('COLUMN_NAME_REST'),
            'column_group_id': column_group_id,
            'column_group_name': column_group_name,
            'column_type': column_class_master[recode.get('COLUMN_CLASS')],
            'column_disp_seq': recode.get('COLUMN_DISP_SEQ'),
            'description': recode.get('DESCRIPTION_' + lang.upper()),
            'ref_table_name': recode.get('REF_TABLE_NAME'),
            'ref_pkey_name': recode.get('REF_PKEY_NAME'),
            'ref_col_name': recode.get('REF_COL_NAME'),
            'ref_sort_conditions': recode.get('REF_SORT_CONDITIONS'),
            'ref_multi_lang': recode.get('REF_MULTI_LANG'),
            'col_name': recode.get('COL_NAME'),
            'save_type': recode.get('SAVE_TYPE'),
            'auto_input': recode.get('AUTO_INPUT'),
            'input_item': recode.get('INPUT_ITEM'),
            'view_item': recode.get('VIEW_ITEM'),
            'unique_item': recode.get('UNIQUE_ITEM'),
            'required_item': recode.get('REQUIRED_ITEM'),
            'initial_value': recode.get('INITIAL_VALUE'),
            'validate_option': validate_option,
            'before_validate_register': before_validate_register,
            'after_validate_register': after_validate_register
        }
        col_num = 'c{}'.format(count)
        column_info_data[col_num] = detail
        
        # ####メモ：縦メニュー用の考慮がされていないため、最終的な修正が必要。
        # カラムグループ管理用配列に追加
        if column_group_id:
            if column_group_id not in tmp_column_group:
                tmp_column_group[column_group_id] = []
            
            tmp_column_group[column_group_id].append(col_num)
            
            # カラムグループの親をたどり格納
            end_flag = False
            target_column_group_id = column_group_id
            first_column_group_id = column_group_id
            loop_count = 0
            while not end_flag:
                for target in column_group_list.values():
                    if target.get('column_group_id') == target_column_group_id:
                        parent_column_group_id = target.get('parent_column_group_id')
                        if not parent_column_group_id:
                            end_flag = True
                            break
                        
                        if parent_column_group_id not in tmp_column_group:
                            tmp_column_group[parent_column_group_id] = []
                        
                        if target_column_group_id not in tmp_column_group[parent_column_group_id]:
                            tmp_column_group[parent_column_group_id].append(target_column_group_id)
                        
                        target_column_group_id = parent_column_group_id
                        column_group_parent_of_child[first_column_group_id] = parent_column_group_id
                
                # ループ数が100を超えたら無限ループの可能性が高いため強制終了
                loop_count += 1
                if loop_count > 100:
                    end_flag = True
    
    # カラムグループIDと対応のg番号配列を作成
    key_to_id = {}
    group_num = 1
    for group_id, value_list in tmp_column_group.items():
        key_to_id[group_id] = 'g' + str(group_num)
        group_num += 1
    
    # カラムグループ管理用配列について、カラムグループIDをg1,g2,g3...に変換し、idやnameを格納する。
    column_group_info_data = {}
    for group_id, value_list in tmp_column_group.items():
        add_data = {}
        columns = []
        for col in value_list:
            if col in key_to_id:
                columns.append(key_to_id[col])
            else:
                columns.append(col)
        
        add_data['columns'] = columns
        add_data['column_group_id'] = group_id
        add_data['column_group_name'] = column_group_list.get(group_id).get('column_group_name')
        parent_id = column_group_list.get(group_id).get('parent_column_group_id')
        add_data['parent_column_group_id'] = parent_id
        if parent_id:
            add_data['parent_column_group_name'] = column_group_list.get(parent_id).get('column_group_name')
        else:
            add_data['parent_column_group_name'] = None
        
        column_group_info_data[key_to_id[group_id]] = add_data
    
    # menu_info_dataに大元のカラムの並び順を追加
    # ####メモ：縦メニュー用の考慮がされていないため、最終的な修正が必要。
    columns = []
    for col_num, col_data in column_info_data.items():
        column_group_id = col_data['column_group_id']
        if not column_group_id:
            # カラムグループが無い場合はcol_num(c1, c2, c3...)を格納
            columns.append(col_num)
            continue
        
        if column_group_id in column_group_parent_of_child:
            # 大親のカラムグループIDをg番号(g1, g2, g3...)に変換した値を格納
            parent_column_group_id = column_group_parent_of_child.get(column_group_id)
            if key_to_id[parent_column_group_id] not in columns:
                columns.append(key_to_id[parent_column_group_id])
            continue
        else:
            # カラムグループIDをg番号(g1, g2, g3...)に変換した値を格納
            if key_to_id[column_group_id] not in columns:
                columns.append(key_to_id[column_group_id])
            continue
    
    menu_info_data['columns'] = columns
    
    info_data = {
        'menu_info': menu_info_data,
        'column_info': column_info_data,
        'column_group_info': column_group_info_data
    }
    
    return info_data


def collect_menu_column_list(objdbca, menu):
    """
        メニューのカラム一覧の取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu: メニュー string
        RETRUN:
            column_list
    """
    # 変数定義
    t_common_menu = 'T_COMN_MENU'
    t_common_menu_column_link = 'T_COMN_MENU_COLUMN_LINK'
    
    # 『メニュー管理』テーブルから対象のデータを取得
    ret = objdbca.table_select(t_common_menu, 'WHERE MENU_NAME_REST = %s AND DISUSE_FLAG = %s', [menu, 0])
    if not ret:
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException("200-00001", log_msg_args, api_msg_args)  # noqa: F405
    
    menu_id = ret[0].get('MENU_ID')  # 対象メニューを特定するためのID
    
    # メニューに対するロール権限をチェック（Falseなら権限エラー）
    role_check = check_auth_menu(menu_id)
    if not role_check:
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException("401-00001", log_msg_args, api_msg_args)  # noqa: F405
    
    # 『メニュー-カラム紐付管理』テーブルから対象のデータを取得
    ret = objdbca.table_select(t_common_menu_column_link, 'WHERE MENU_ID = %s ORDER BY COLUMN_DISP_SEQ ASC', [menu_id])
    if not ret:
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException("200-00004", log_msg_args, api_msg_args)  # noqa: F405
    
    column_list = []
    for recode in ret:
        column_list.append(recode.get('COLUMN_NAME_REST'))
    
    return column_list


def collect_pulldown_list(objdbca, menu):
    """
        IDカラム(IDColumn, LinkIDColumn, AppIDColumn)のプルダウン選択用一覧の取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu: メニュー string
        RETRUN:
            pulldown_list
    """
    # 変数定義
    t_common_menu = 'T_COMN_MENU'
    t_common_menu_column_link = 'T_COMN_MENU_COLUMN_LINK'
    t_common_column_class = 'T_COMN_COLUMN_CLASS'
    lang = g.LANGUAGE
    
    # 『カラムクラスマスタ』テーブルからcolumn_typeの一覧を取得
    ret = objdbca.table_select(t_common_column_class, 'WHERE DISUSE_FLAG = %s', [0])
    column_class_master = {}
    for recode in ret:
        column_class_master[recode.get('COLUMN_CLASS_ID')] = recode.get('COLUMN_CLASS_NAME')
    
    # 『メニュー管理』テーブルから対象のデータを取得
    ret = objdbca.table_select(t_common_menu, 'WHERE MENU_NAME_REST = %s AND DISUSE_FLAG = %s', [menu, 0])
    if not ret:
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException("200-00001", log_msg_args, api_msg_args)  # noqa: F405
    
    menu_id = ret[0].get('MENU_ID')  # 対象メニューを特定するためのID
    
    # メニューに対するロール権限をチェック（Falseなら権限エラー）
    role_check = check_auth_menu(menu_id)
    if not role_check:
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException("401-00001", log_msg_args, api_msg_args)  # noqa: F405
    
    # 『メニュー-カラム紐付管理』テーブルから対象のメニューのデータを取得
    ret = objdbca.table_select(t_common_menu_column_link, 'WHERE MENU_ID = %s AND DISUSE_FLAG = %s', [menu_id, 0])
    
    pulldown_list = {}
    # id_column_list = ["7", "11", "18"]  # id 7(IDColumn), id 11(LinkIDColumn), id 18(AppIDColumn)
    id_column_list = ["7", "11"]  # ####メモ：18(AppIDColumn)の場合は別の挙動になるはずなので、いったん除外。
    for recode in ret:
        column_class_id = str(recode.get('COLUMN_CLASS'))
        
        id_column_check = column_class_id in id_column_list
        if not id_column_check:
            continue
        
        column_name_rest = str(recode.get('COLUMN_NAME_REST'))
        ref_table_name = recode.get('REF_TABLE_NAME')
        ref_pkey_name = recode.get('REF_PKEY_NAME')
        ref_col_name = recode.get('REF_COL_NAME')
        if recode.get('REF_MULTI_LANG') == "1":
            ref_col_name = ref_col_name + "_" + lang.upper()
        
        # ####メモ：現状、ソートコンディションを考慮していない。
        # ref_sort_conditions = recode.get('REF_SORT_CONDITIONS')
        ret_2 = objdbca.table_select(ref_table_name, 'WHERE DISUSE_FLAG = %s', [0])
        column_pulldown_list = {}
        for recode_2 in ret_2:
            column_pulldown_list[recode_2.get(ref_pkey_name)] = recode_2.get(ref_col_name)
        
        pulldown_list[column_name_rest] = column_pulldown_list
    
    return pulldown_list


def collect_search_candidates(objdbca, menu, column):
    """
        IDカラム(IDColumn, LinkIDColumn, AppIDColumn)のプルダウン選択用一覧の取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu: メニュー string
            column: カラム string
        RETRUN:
            search_candidates
    """
    # 変数定義
    t_common_menu = 'T_COMN_MENU'
    t_common_menu_table_link = 'T_COMN_MENU_TABLE_LINK'
    t_common_menu_column_link = 'T_COMN_MENU_COLUMN_LINK'
    lang = g.LANGUAGE
        
    # 『メニュー管理』テーブルから対象のデータを取得
    ret = objdbca.table_select(t_common_menu, 'WHERE MENU_NAME_REST = %s AND DISUSE_FLAG = %s', [menu, 0])
    if not ret:
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException("200-00001", log_msg_args, api_msg_args)  # noqa: F405
    
    menu_id = ret[0].get('MENU_ID')  # 対象メニューを特定するためのID
    
    # メニューに対するロール権限をチェック（Falseなら権限エラー）
    role_check = check_auth_menu(menu_id)
    if not role_check:
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException("401-00001", log_msg_args, api_msg_args)  # noqa: F405

    # 『メニュー-カラム紐付管理』テーブルから対象の項目のデータを取得
    ret = objdbca.table_select(t_common_menu_column_link, 'WHERE MENU_ID = %s AND COLUMN_NAME_REST = %s AND DISUSE_FLAG = %s', [menu_id, column, 0])  # noqa: E501
    if not ret:
        log_msg_args = [menu, column]
        api_msg_args = [menu, column]
        raise AppException("200-00005", log_msg_args, api_msg_args)  # noqa: F405
    
    col_name = str(ret[0].get('COL_NAME'))
    column_class_id = str(ret[0].get('COLUMN_CLASS'))
    
    ref_table_name = ret[0].get('REF_TABLE_NAME')
    ref_pkey_name = ret[0].get('REF_PKEY_NAME')
    ref_multi_lang = ret[0].get('REF_MULTI_LANG')
    ref_col_name = ref_col_name = ret[0].get('REF_COL_NAME')
    if ref_multi_lang == "1":
        ref_col_name = ref_col_name + "_" + lang.upper()
    
    # 『メニュー-テーブル紐付管理』テーブルから対象のテーブル名を取得
    ret = objdbca.table_select(t_common_menu_table_link, 'WHERE MENU_ID = %s AND DISUSE_FLAG = %s', [menu_id, 0])
    if not ret:
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException("200-00002", log_msg_args, api_msg_args)  # noqa: F405
    
    table_name = ret[0].get('TABLE_NAME')
    
    # 対象のテーブルのカラム一覧を取得し、対象のカラムの有無を確認
    ret = objdbca.table_columns_get(table_name)
    if col_name not in ret[0]:
        log_msg_args = [menu, col_name]
        api_msg_args = [menu, col_name]
        raise AppException("200-00006", log_msg_args, api_msg_args)  # noqa: F405
    
    # 対象のテーブルからレコードを取得し、対象のカラムの値を一覧化
    ret = objdbca.table_select(table_name, 'WHERE DISUSE_FLAG = %s', [0])
    if not ret:
        # レコードが0件の場合は空をreturn
        return []
    
    search_candidates = []
    # id_column_list = ["7", "11", "18"]  # id 7(IDColumn), id 11(LinkIDColumn), id 18(AppIDColumn)
    id_column_list = ["7", "11"]  # ####メモ：18(AppIDColumn)の場合は別の挙動になるはずなので、いったん除外。
    id_column_check = column_class_id in id_column_list
    
    if id_column_check:
        # IDColumn系の場合は、参照元のレコードを取得し値を差し替える
        ret_2 = objdbca.table_select(ref_table_name, 'WHERE DISUSE_FLAG = %s', [0])
        ref_list = {}
        for recode_2 in ret_2:
            ref_list[recode_2.get(ref_pkey_name)] = recode_2.get(ref_col_name)
        
        for recode in ret:
            convert = ref_list[recode.get(col_name)]
            search_candidates.append(convert)
    else:
        for recode in ret:
            target = recode.get(col_name)
            search_candidates.append(target)
        
    # 重複を削除(元の並び順は維持)
    if search_candidates:
        search_candidates = list(dict.fromkeys(search_candidates))
    
    return search_candidates
