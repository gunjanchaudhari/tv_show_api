from sre_constants import SUCCESS
from hologram import dataclass
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
    """Import a show from the tvmaze API"""
    try:
        result = requests.get(
            'https://api.tvmaze.com/search/shows?q={}'.format(name))
        jsonResult = result.json()
        df = pd.DataFrame([jsonResult[0]['show']])
        df.rename(columns={'id': 'tvmaze_id'}, inplace=True)
        df['last-update'] = datetime.datetime.now()
        fd = util.write_in_sqlite(df, database_file, table_name)
        resp_dic = fd.loc[0]
        href = request.host_url + "tv_shows/" + str(resp_dic['id'])
        resp = {'id': (str(resp_dic['id'])), 'tv_maze_id': (resp_dic['tvmaze_id']), 'last-update': (resp_dic['last-update']),
                '_links': {'self': {'href': href}}}
        return resp
    except Exception as e:
        util.debug_exception(e, suppress=True)
        return Status.FAIL


def get_show(id: int) -> Union[dict, Status]:
    """Get show from the database with the id"""
    try:
        fd, count = util.read_show(database_file, table_name, str(id))
        resp_dic = fd.loc[0]
        href = request.host_url + "tv_shows/"
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
        resp_dics = {'tvmaze_id': resp_dic['tvmaze_id'], 'url': resp_dic['url'], 'name': resp_dic['name'],
                     'language': resp_dic['language'], 'type': resp_dic['type'], 'genres': resp_dic['genres'],
                     'status': resp_dic['status'], 'runtime': resp_dic['runtime'], 'premiered': resp_dic['premiered'],
                     'schedule': resp_dic['schedule'], 'rating': resp_dic['rating'], 'network': resp_dic['network'],
                     'weight': resp_dic['weight'], '_links': resp_dic['_links']}

        return resp_dics

    except Exception as e:
        util.debug_exception(e, suppress=True)
        return Status.FAIL


def del_show(id: int) -> Status:
    """Delete a show"""
    try:
        ans = util.delete_show(database_file, table_name, (id))
        return ans

    except Exception as e:
        util.debug_exception(e, suppress=True)
        return Status.FAIL


def change_fields(data: dict, id: int) -> Union[dict, Status]:
    """Patch database with the given entries"""
    try:
        read, length = util.read_show(database_file, table_name, str(id))
        show_read = read.to_dict()
        for item in show_read:
            show_read[item] = show_read[item][0]
        for item in data:
            show_read[item] = data[item]
        show = util.all_shows(database_file, table_name)
        x = show.index[show['name'] == read['name'][0]].tolist()[0]
        show.loc[x] = show_read
        df = util.write_sql(show, database_file, table_name)
        if df == Status.SUCCESS:
            read, length = util.read_show(database_file, table_name, str(id))
            return read
    except Exception as e:
        util.debug_exception(e, suppress=True)
        return Status.FAIL
