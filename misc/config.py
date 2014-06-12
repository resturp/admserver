"""
.. module:: admserver/config
   :platform: Linix
   :synopsis: Module for ADMserver configuration settings.

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

pgdb_server = "localhost"
pgdb_database = "admserver"
pgdb_user = "<database username>"
pgdb_password = "<database password>"

#the rip symbol is used to concatanate before a foreign key of a record, to make it disappear
pgdb_ripsymbol = "#"

#the cookie_secret secret
cookie_secret = "ACOOKIESECRET"

#SSl certification settings
useSSL = True
sslCertPath = 'cert'
admRunPath = '.'