from django.db import connection

from ira.model.output import Output
from ira.model.query import Query
from http import HTTPStatus


def execute_sql_query(query: Query) -> Output:
    with connection.cursor() as cursor:
        try:
            cursor.execute(query.value)
            if query.is_dql:
                return Output(HTTPStatus.OK,
                              query,
                              result=fetch_all(cursor))
            return Output(HTTPStatus.OK,
                          query,
                          message="Query has affected {number_of_rows} row(s)."
                          .format(query=query.value, number_of_rows=cursor.rowcount))
        except Exception as exception:
            return Output(HTTPStatus.BAD_REQUEST,
                          query,
                          message="Query faced logic issue; "
                                  "See exception message:{exception_message}"
                          .format(query=query.value, exception_message=exception))


# Got the idea on how to create a dictionary which allows duplicate key from here:
# https://stackoverflow.com/questions/29519858/adding-duplicate-keys-to-json-with-python
class DuplicateKeyDict(dict):
    def __init__(self, items):
        if items:
            self[None] = None
        self._items = items

    def items(self):
        return self._items


def fetch_all(cursor):
    column_names = [column[0] for column in cursor.description]
    result = []
    for row in cursor.fetchall():
        result.append(DuplicateKeyDict(list((zip(column_names, row)))))
    return result
