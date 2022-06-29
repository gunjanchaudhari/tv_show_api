from ctypes import Union
import inspect
import os
import sqlite3
from sre_constants import SUCCESS
from pandas import DataFrame
from pandas.io import sql
from utils.enums import Status
from itertools import count

import pandas as pd


def debug_exception(error, suppress=False):
    print(os.environ.get("FLASK_ENV"), "this is flask env")
    if os.environ.get("FLASK_ENV") == "development":
        print(
            f"{type(error).__name__} at line {error.__traceback__.tb_lineno} of {inspect.stack()[1].filename }: {error}"
        )
    if not suppress:
        raise error


def write_in_sqlite(dataframe: DataFrame, database_file, table_name) -> Union[DataFrame, Status]:
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
            if(show.empty):
                show_table = sql.read_sql(
                    'select * from {};'.format(table_name), cnx)
                show_table = show_table.drop('id', axis=1)
                shows = pd.concat([show_table, dataframe], ignore_index=True)
                df = shows.astype(str)
                df.to_sql(name=table_name, con=cnx,
                          if_exists='replace', index_label='id', method='multi')
        except:
            df = dataframe.astype(str)
            df.to_sql(name=table_name, con=cnx,
                      if_exists='replace', index_label='id')

        return read_from_sqlite(database_file, table_name, dataframe['name'][0])
    except Exception as e:
        debug_exception(e, suppress=True)
        return Status.FAIL


def read_from_sqlite(database_file, table_name, name) -> Union[DataFrame, Status]:
    """
    :param database_file: where the database is stored
    :param table_name: the name of the table
    :param name: name to search in database
    :return: A Dataframe
    """
    try:
        cnx = sqlite3.connect(database_file)
        return sql.read_sql('select * from {} where name="{}";'.format(table_name, name), cnx)
    except Exception as e:
        debug_exception(e, suppress=True)
        return Status.FAIL


def read_show(database_file, table_name, id) -> Union[DataFrame, Status]:
    """
    :param database_file: where the database is stored
    :param table_name: the name of the table
    :param id: search a show with id
    """
    try:
        print("inside the read show")
        cnx = sqlite3.connect(database_file)
        print("after connection")
        show = sql.read_sql(
            'select * from {};'.format(table_name), cnx)
        print(show)
        return sql.read_sql('select * from {} where id="{}";'.format(table_name, id), cnx), show.shape[0]

    except Exception as e:
        debug_exception(e, suppress=True)
        return Status.FAIL


def delete_show(database_file, table_name, id) -> Status:
    """Delete a show with id"""

    try:
        cnx = sqlite3.connect(database_file)
        try:
            show = sql.read_sql(
                'select * from {} where id={};'.format(table_name, id), cnx)
            print(show, "showtiem biatch")
            if show.empty:
                print("Im heress")
                return Status.NOT_EXIST

            show = sql.read_sql('select * from {};'.format(table_name), cnx)
            print(show, "biatch Show")
            if show.shape[0] == 1:
                delstatmt = 'DELETE FROM tv_shows WHERE id=?'
                cursor = cnx.cursor()
                cursor.execute(delstatmt, (str(id,)))
                cnx.commit()
                return Status.SUCCESS
            shows = show.drop(id)
            shows = shows.drop('id', axis=1)
            shows = shows.reset_index()
            print(shows, "showss")
            df = shows.astype(str)
            df.to_sql(name=table_name, con=cnx,
                      if_exists='replace', index_label='id', method='multi')
            print(df, "final")
        except:
            return Status.INVALID
        return Status.SUCCESS
    except Exception as e:
        debug_exception(e, suppress=True)
        return Status.FAIL


def all_shows(database_file, table_name) -> Union[DataFrame, Status]:
    """Get a dataframe of all the shows"""
    try:
        cnx = sqlite3.connect(database_file)
        show = sql.read_sql(
            'select * from {};'.format(table_name), cnx)
        return show

    except Exception as e:
        debug_exception(e, suppress=True)
        return Status.FAIL


def write_sql(dataframe: DataFrame, database_file, table_name) -> Status:
    """Write the entire dataframe to database"""
    try:
        cnx = sqlite3.connect(database_file)
        df1 = dataframe.drop('id', axis=1)
        df = df1.astype(str)
        df.to_sql(name=table_name, con=cnx,
                  if_exists='replace', index_label='id', method='multi')
        return Status.SUCCESS

    except Exception as e:
        debug_exception(e, suppress=True)
        return Status.FAIL
