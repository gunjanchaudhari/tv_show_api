from sre_constants import SUCCESS
import requests
import pandas as pd
import datetime
import ast
from flask import request, jsonify
from typing import Union
from utils.config import database_file, table_name
from utils import util
from utils.enums import Status


def import_show(name: str) -> Union[dict, Status]:
    try:
        result = requests.get(
            'https://api.tvmaze.com/search/shows?q={}'.format(name))
        print(result, "this is result")
        jsonResult = result.json()
        # print(jsonResult)

        df = pd.DataFrame([jsonResult[0]['show']])
        print(df)
        df.rename(columns={'id': 'tvmaze_id'}, inplace=True)
        print(df)
        df['last-update'] = datetime.datetime.now()
        fd = util.write_in_sqlite(df, database_file, table_name)

        resp_dic = fd.loc[0]
        href = request.host_url + "tv_shows/" + str(resp_dic['id'])
        print(href)
        resp = {'id': (resp_dic['id']), 'tv_maze_id': (resp_dic['tvmaze_id']), 'last-update': (resp_dic['last-update']),
                '_links': {'self': {'href': href}}}
        print(resp)
        return resp
    except Exception as e:
        util.debug_exception(e, suppress=True)
        return Status.FAIL


def get_show(id: int) -> Union[dict, Status]:
    try:
        count, fd = util.read_show(database_file, table_name, str(id))
        resp_dic = fd.loc[0]
        # print(resp, "this shit")
        href = request.host_url + "tv_shows/"
        # resp_dic = ast.literal_eval(resp)
        if int(resp_dic['id']) == 1:
            resp_dic['_links'] = {'self': {'href': href+resp_dic['id']},
                                  'previous': {'href': href+str(count)},
                                  'next': {'href': href+str(int(resp_dic['id'])+1)}}
        if int(resp_dic['id']) == count:
            resp_dic['_links'] = {'self': {'href': href+resp_dic['id']},
                                  'previous': {'href': href+str(int(resp_dic['id'])-1)},
                                  'next': {'href': href+str(1)}}
        resp_dic['genres'] = ast.literal_eval(resp_dic['genres'])
        resp_dic['schedule'] = ast.literal_eval(resp_dic['schedule'])
        resp_dic['rating'] = ast.literal_eval(resp_dic['rating'])
        resp_dic['network'] = ast.literal_eval(resp_dic['network'])
        del resp_dic['webChannel']
        del resp_dic['dvdCountry']
        del resp_dic['externals']
        del resp_dic['image']
        resp_dics = {'id': resp_dic['id'], 'url': resp_dic['url'], 'name': resp_dic['name'],
                     'language': resp_dic['language'], 'type': resp_dic['type'], 'genres': resp_dic['genres'],
                     'status': resp_dic['status'], 'runtime': resp_dic['runtime'], 'premiered': resp_dic['premiered'],
                     'schedule': resp_dic['schedule'], 'rating': resp_dic['rating'], 'network': resp_dic['network'],
                     'weight': resp_dic['weight'], '_links': resp_dic['_links']}
        print(resp_dics)
        print(type(resp_dics))

        return resp_dics

    except Exception as e:
        util.debug_exception(e, suppress=True)
        return Status.FAIL


def del_show(id: int) -> Status:
    try:
        print("im here")
        ans = util.delete_show(database_file, table_name, str(id))
        return ans

    except Exception as e:
        util.debug_exception(e, suppress=True)
        return Status.FAIL
