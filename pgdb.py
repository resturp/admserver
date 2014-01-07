"""
.. module:: admserver/pgdb
   :platform: Linix
   :synopsis: Pgdb class for connecting to pstgresql database.

.. moduleauthor:: Thomas Boose <thomas@boose.nl>

.. license:: Copyright 2014 Thomas Boose
   thomas at boose dot nl.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import psycopg2
from config import *


class Pgdb(object):
    """ Singleton class for handling all requests to the database.
    
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        """ overwrite the __new__ method to return the single instanse.
        
        only creat a new instance if cls._instance is not initionalized 
        yet."""
        if not cls._instance:
            cls._instance = super(Pgdb, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, params):
        """ Initialize the connection to the Postgresql and creat a cursor.
        
        :todo: then connection parameter should be separated in a config file"""
        self.conn = psycopg2.connect(database=pgdb_database, user=pgdb_user, password=pgdb_password, host=pgdb_server)
        self.cur = self.conn.cursor()
        
    def __del__(self):
        """ Destructor, close cursor and connection.""" 
        self.cur.close()
        self.conn.close()
        
    def execute(self,query,data):
        """ Execute any query that select. 
        
        This method can be used to run Insert, Update or delete query's
        
        :Parameters:
           - `query` - The SQL query statement to be executed. Do not concatenate user submitted 
                       content directly into the query string but use the data argument instead.
           - `data`  - A tuple ``a = (arg1, arg..., argn)`` containing all values to be pasted 
                       into the query. Psycopg make sure all values are passed in a secure and
                       valid manner.
        :Returns:
           Nothing.
        """
        self.cur.close()
        self.conn.close()
        self.conn = psycopg2.connect(database=pgdb_database, user=pgdb_user, password=pgdb_password, host=pgdb_server)
        self.cur = self.conn.cursor()
        self.cur.execute(query,data)
        self.conn.commit()
        
    def get_record(self, query, data=None):
        """ Pass a query to the database and return only the first record. 
        
        This method can be used to run a select query to get a single record 
        
        :Parameters:
           - `query` - The SQL select query statement. Do not concatenate user submitted 
                       content directly into the query string but use the data argument instead.
                       replace all user values with %s like so: 
                       ``select some, thing FROM atable WHERE some > %s AND some < %s``
           - `data`  - A tuple ``a = (arg1, arg..., argn)`` containing all values to be pasted 
                       into the query. Psycopg make sure all values are passed in a secure and
                       valid manner.
        :Returns:
           A tuple with all return values.
        """
        self.cur.execute(query, data)
        return self.cur.fetchone()

    def get_records(self, query, data=None):
        """ Pass a query to the database and return a list of tuples. 
        
        This method can be used to run a select query to get a list of records 
        
        :Parameters:
           - `query` - The SQL query statement to be executed. Do not concatenate user submitted 
                       content directly into the query string but use the data argument instead.
                       replace all user values with %s like so: 
                       ``select some, thing FROM atable WHERE some > %s AND some < %s``
           - `data`  - A tuple ``a = (arg1, arg..., argn)`` containing all values to be pasted 
                       into the query. Psycopg make sure all values are passed in a secure and
                       valid manner.
        :Returns:
           A list with all return tuples.
        """
        self.cur.execute(query, data)
        return self.cur.fetchall()
        