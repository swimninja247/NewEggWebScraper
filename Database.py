""" This class is used to simplify the use of SQLite databases in the project.
    Author: Noah Czelusta
"""

import sqlite3


class Database:

    def __init__(self, name):
        self.db = sqlite3.connect(name)
        self.point = self.db.cursor()

    def add_row(self, table, data):
        """ Inserts a row data into table
        """
        bindings = '?'
        bindings += (len(data) - 1) * ',?'
        cmd = 'INSERT INTO {} VALUES({})'.format(table, bindings)
        self.point.execute(cmd, data)

    def update_col(self, table, data, condition={}, order='', limit=-1):
        """ Updates data in a table, defaults to all that meet condition
            \ndata = dictionary of column name and new values
            \ncondtion = dictionary of conditions
        """

        cmd = 'UPDATE {} '.format(table)

        cmd += 'SET '
        for pair in data.items():
            if isinstance(pair[1], str):
                cmd += '{} = \'{}\', '.format(pair[0], pair[1])
            else:
                cmd += '{} = {}, '.format(pair[0], pair[1])
        cmd = cmd[:len(cmd)-2]  # remove extra comma and space

        if condition:
            cmd += ' WHERE '
            for pair in condition.items():
                if isinstance(pair[1], str):
                    cmd += '{} = \'{}\', '.format(pair[0], pair[1])
                else:
                    cmd += '{} = {}, '.format(pair[0], pair[1])
            cmd = cmd[:len(cmd)-2]  # remove extra comma and space

        if limit != -1:
            cmd += ' ORDER BY {} '.format(order)
            cmd += 'LIMIT {}'.format(limit)

        self.point.execute(cmd)

    def fetch_data(self, table, columns, condition={}):
        """ Returns the data from the columns in the iterable, columns
        """
        cmd = 'SELECT '
        for col in columns:
            cmd += '{}, '.format(col)
        cmd = cmd[:len(cmd)-2]
        cmd += ' FROM {}'.format(table)
        if condition:
            cmd += ' WHERE '
            for pair in condition.items():
                if isinstance(pair[1], str):
                    cmd += '{} = \'{}\', '.format(pair[0], pair[1])
                else:
                    cmd += '{} = {}, '.format(pair[0], pair[1])
            cmd = cmd[:len(cmd)-2]  # remove extra comma and space

        self.point.execute(cmd)
        return self.point.fetchall()

    def delete(self, table, condition={}):
        """ Deletes rows from table where condition is met
        """
        cmd = 'DELETE FROM {}'.format(table)
        if condition:
            cmd += ' WHERE '
            for pair in condition.items():
                if isinstance(pair[1], str):
                    cmd += '{} = \'{}\', '.format(pair[0], pair[1])
                else:
                    cmd += '{} = {}, '.format(pair[0], pair[1])
            cmd = cmd[:len(cmd)-2]  # remove extra comma and space
        self.point.execute(cmd)

    def exit(self):
        self.db.commit()
        self.db.close()
