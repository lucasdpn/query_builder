from sqlalchemy.sql import select
from sqlalchemy import Table, func, select

from model import operation_builder
from model import sql_operations as op

from utils.db import dal


"""
    This class provides common methods to manipulate queries. The query
itself, is defined in the class queries and the Factory class QueryBulder -see
model.query_builder- creates the operation accordingly the params['op']
variable.
"""


class IntermediateTable():
    def __init__(self, params, sub_operations):
        self._params = params
        self._sub_operations = sub_operations

        # get query
        obj = operation_builder.OperationBuilder().create(params['op'])
        self._operation = obj.get_statement(params, sub_operations)

        # create temp table to let the data accessible.
        self.create()
        with dal.engine.connect() as con:
            table = Table(self.save_at(), dal.metadata,
                          autoload=True, schema=dal.schema_output)
            self._columns = table.c
            self._number_of_rows = con.execute(
                    select([func.count()]).select_from(table)).scalar()
        #     stmt = select([table])
        #     self._data_table = con.execute(stmt).fetchall()

    def __str__(self):
        return (str(self._operation))

    def operation_name(self):
        return self._params['name']

    def save_at(self):
        return self.operation_name() + "_" + "table"

    def create(self):
        with dal.engine.connect() as con:
            con.execute("commit")
            con.execute(op.CreateTableAs(dal.schema_output,
                                         self.save_at(), self._operation))

    def access_data_table(self):
        return self._data_table

    def columns_name(self):
        return self._columns

    def delete(self):
        with dal.engine.connect() as con:
            con.execute("commit")
            con.execute(op.DropTable(dal.schema_output, self.save_at()))

    def number_of_rows(self):
        return self._number_of_rows