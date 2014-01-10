"""
.. module:: admserver/models
   :platform: Linix
   :synopsis: User class with attributes and methods for use cases.

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

import tornado
from pgdb import Pgdb
from config import *
import testRunner

class User(object):
    
    def __init__(self, handler):
        self.email = tornado.escape.xhtml_escape(handler.current_user)
        wildcard = pgdb_ripsymbol + '%'
        
        self.assginments = Pgdb(self).get_records("Select md5(title) as id, * from admassignment where title NOT SIMILAR TO %s", (wildcard,))
        self.assignment = None
        self.tasks = None
    
    def get_assignments(self):
        return self.assginments
    
    def get_email(self):
        return self.email
    
    def is_admin(self):
        return Pgdb(self).get_record("Select isadmin from admuser where email = %s",(self.email,))[0]
    
    def get_assignment(self, md5hash):
        if self.assignment == None:
            query = (""
            "Select "
            "   md5(title) as id, "
            "   admassignment.* "
            "from "
            "   admassignment "
            "where md5(title) = %s")
            self.assginment = Pgdb(self).get_record(query,(md5hash,))
        return self.assginment

    def get_tasks(self, md5hash):
        if self.tasks == None:
            query = (""
            "Select distinct on (admtask.assignment || admtask.tasknr) "
            "   md5(admassignment.title) as id, "
            "   admtask.tasknr as tasknr, admtask.description as description, "
            "   admtask.testsuite as testsuite, "
            "   admsolution.submissionstamp, "
            "   admsolution.code, "
            "   admsolution.results "
            "from "
            "   (admassignment inner join admtask on admassignment.title = admtask.assignment) left outer join admsolution "
            "   on (admassignment.title || admtask.tasknr = admsolution.task and "
            "       admsolution.email = %s) "
            "where md5(admassignment.title) = %s"
            "order by admtask.assignment || admtask.tasknr, admsolution.submissionstamp desc ")
            self.tasks = Pgdb(self).get_records(query,(self.email,md5hash))            
        return self.tasks
    
    def delete_task(self, assignment, tasknr):
        newassign = pgdb_ripsymbol + assignment
        query = "SELECT count(tasknr)+1 from admtask where assignment = %s"
        newtasknr = Pgdb(self).get_record(query, (newassign ,))[0]
        query = "UPDATE admtask set assignment = %s, tasknr = %s where assignment = %s and tasknr = %s"
        Pgdb(self).execute(query,(newassign ,newtasknr,assignment,tasknr))
    
    def run_solution(self, title, task, code):
        query = "Select testsuite from admtask where assignment = %s and tasknr = %s"
        data = (title, task)
        tests = Pgdb(self).get_record(query, data)[0] 
              
        for result in testRunner.test(code, tests):
            if isinstance(result, str):
                yield result + '\n'
            else:
                for boodschap in result: 
                    yield boodschap + '\n'

    def store_solution(self, title, task, code, resultset):
        query = "Insert into admsolution (task,email,submissionstamp,code, results) values (%s, %s, now(), %s, %s)"
        data = (title + task, self.email ,code, resultset)
        Pgdb(self).execute(query,data)

    def store_tests(self, title,task, description, tests):
        if not task.isdigit():
            query = "select count(assignment)+1 from admtask where assignment = %s"
            data = (title,)
            task = Pgdb(self).get_record(query,data)[0]            
            query = "INSERT into admtask (assignment, tasknr, description,testsuite) values (%s, %s, %s, %s)"
            data = (title, task, description,tests)
            Pgdb(self).execute(query,data)
        else:
            query = "select count(assignment) from admtask where assignment = %s and tasknr = %s"
            data = (title, task)
            query = "UPDATE admtask set description = %s, testsuite = %s where assignment = %s and tasknr = %s"
            data = (description,tests, title, task)
            Pgdb(self).execute(query,data)
        
    def store_assignment(self,title,deadline,description, isnew):
        if isnew :           
            query = "INSERT into admassignment (deadline, title, description) values (%s, %s, %s)"
            data = (deadline, title, description)
            Pgdb(self).execute(query,data)
        else:
            query = "UPDATE admassignment set description = %s, deadline = %s where title = %s"
            data = (description,deadline, title)
            Pgdb(self).execute(query,data)
        
    def delete_assignment(self, assignment):
        newassign = pgdb_ripsymbol + assignment
        query = "UPDATE admassignment set title = %s where title = %s"
        Pgdb(self).execute(query,(newassign, assignment))
    