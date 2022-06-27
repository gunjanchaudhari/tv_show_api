import inspect
import os
import sqlite3
from sre_constants import SUCCESS
from pandas import DataFrame
from pandas.io import sql
from utils.enums import Status
from itertools import count


def debug_exception(error, suppress=False):
    print(os.environ.get("FLASK_ENV"), "this is flask env")
    if os.environ.get("FLASK_ENV") == "development":
        print(
            f"{type(error).__name__} at line {error.__traceback__.tb_lineno} of {inspect.stack()[1].filename }: {error}"
        )
    if not suppress:
        raise error


def write_in_sqlite(dataframe, database_file, table_name):
    """
    :param dataframe: The dataframe which must be written into the database
    :param database_file: where the database is stored
    :param table_name: the name of the table
    """
    try:
        cnx = sqlite3.connect(database_file)
        try:
            show = sql.read_sql(
                'select * from {} where name="{}";'.format(table_name, dataframe['name'][0]), cnx)
            print(show, "first read")
            if(show.empty):
                show = sql.read_sql(
                    'select * from {};'.format(table_name), cnx)
                print(show, "this is showwww")
                dataframe['id'] = (show.shape[0]) + 1
                print(dataframe['id'])
                print("this show was empty")
                df = dataframe.astype(str)
                df.to_sql(name=table_name, con=cnx,
                          if_exists='append', index=False)

        except:
            print("show was empty")
            dataframe['id'] = 1
            df = dataframe.astype(str)
            df.to_sql(name=table_name, con=cnx,
                      if_exists='append', index=False)
        return read_from_sqlite(database_file, table_name, dataframe['name'][0])
    except Exception as e:
        debug_exception(e, suppress=True)
        return Status.FAIL


def read_from_sqlite(database_file, table_name, name):
    """
    :param database_file: where the database is stored
    :param table_name: the name of the table
    :return: A Dataframe
    """
    try:
        cnx = sqlite3.connect(database_file)
        return sql.read_sql('select * from {} where name="{}";'.format(table_name, name), cnx)
    except Exception as e:
        debug_exception(e, suppress=True)
        return Status.FAIL


def read_show(database_file, table_name, id):
    """
    :param database_file: where the database is stored
    :param table_name: the name of the table
    :return: A Dataframe
    """
    try:
        cnx = sqlite3.connect(database_file)
        show = sql.read_sql(
            'select * from {};'.format(table_name), cnx)

        return sql.read_sql('select * from {} where id="{}";'.format(table_name, id), cnx), show.shape[0]

    except Exception as e:
        debug_exception(e, suppress=True)
        return Status.FAIL


def delete_show(database_file, table_name, id):
    try:
        print(id)
        cnx = sqlite3.connect(database_file)
        show = sql.read_sql(
            'select * from {} where id="{}";'.format(table_name, id), cnx)
        print(show)
        if show.empty:
            return Status.NOT_EXIST
        delstatmt = 'DELETE FROM tv_shows WHERE id=?'
        cursor = cnx.cursor()
        cursor.execute(delstatmt, (id,))
        cnx.commit()
        return Status.SUCCESS
    except Exception as e:
        debug_exception(e, suppress=True)
        return Status.NOT_EXIST
