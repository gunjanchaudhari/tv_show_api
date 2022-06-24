import requests
import pandas as pd
import datetime
import ast
from flask import request
from typing import Union
from utils.config import database_file, table_name
from utils import util
from utils.enums import Status


def import_show(name: str) -> Union[dict, Status]:
    try:
        result = requests.get(
            'https://api.tvmaze.com/search/shows?q={}'.format(name))
        print(result)
        jsonResult = result.json()
        df = pd.DataFrame([jsonResult[0]['show']])
        df['last-update'] = datetime.datetime.now()
        #write_in_sqlite(df, database_file, table_name)
        fd = util.read_from_sqlite(database_file, table_name, name)
        resp_dic = fd.loc[0]
        href = request.host_url + "tv_shows/import?name=" + name
        parsed_json = ast.literal_eval(resp_dic['_links'])
        del parsed_json['previousepisode']
        resp = {'id': (resp_dic['id']), 'last-update': (resp_dic['last-update']),
                '_links': {'self': {'href': href}}}
        return resp
    except Exception as e:
        util.debug_exception(e, suppress=True)
        return Status.FAIL
