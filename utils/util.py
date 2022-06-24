import inspect
import os
import sqlite3
from pandas.io import sql


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

    cnx = sqlite3.connect(database_file)
    df = dataframe.astype(str)
    df.to_sql(name=table_name, con=cnx, if_exists='append', index=False)


def read_from_sqlite(database_file, table_name, name):
    """
    :param database_file: where the database is stored
    :param table_name: the name of the table
    :return: A Dataframe
    """
    cnx = sqlite3.connect(database_file)
    return sql.read_sql('select * from {} where name="{}";'.format(table_name, name), cnx)
