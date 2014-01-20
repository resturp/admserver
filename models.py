"""
.. module:: admserver/models
   :platform: Linux
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
import json
from pgdb import Pgdb
from config import *
import testRunner

class User(object):
    
    def __init__(self, handler):
        self.email = tornado.escape.xhtml_escape(handler.current_user)
        query = "Select courses from admuser where email = %s"
        print self.email
        self.courses = ';' + Pgdb(self).get_record(query, (self.email,))[0] + ';'
        wildcard = pgdb_ripsymbol + '%'

        query = "Select md5(title) as id, * from admassignment where title NOT SIMILAR TO %s and position(';' || course || ';' in %s) > 0 Order by course, deadline"        
        self.assginments = Pgdb(self).get_records(query, (wildcard, self.courses,))
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

    def can_attempt(self, assignment, tasknr):
        query = "SELECT attempts, attemptcount from admsolutionattempts where email = %s and assignment = %s and tasknr = %s"
        data = (self.email, assignment, tasknr)
        result = Pgdb(self).get_record(query, data)
        if result is None:
            return True
        else:
            return (result[0] == 0) or (result[1] < result[0])
            
        
    def get_tasks(self, md5hash):
        if self.tasks == None:
            query = (""
            "Select distinct on (admtask.assignment || ',' || admtask.tasknr) "
            "   md5(admassignment.title) as id, "
            "   admtask.tasknr as tasknr, admtask.description as description, "
            "   admtask.testsuite as testsuite, "
            "   admsolutionattempts.submissionstamp, "
            "   admsolutionattempts.code, "
            "   admsolutionattempts.results, "
            "   admsolutionattempts.attemptcount, "
            "   admtask.attempts, "
            "   admtask.totalscore, "
            "   admsolutionattempts.score "
            "from "
            "   (admassignment inner join admtask on admassignment.title = admtask.assignment) left outer join admsolutionattempts "
            "   on (admassignment.title = admsolutionattempts.assignment AND admtask.tasknr = admsolutionattempts.tasknr and "
            "       admsolutionattempts.email = %s) "
            "where md5(admassignment.title) = %s"
            "order by admtask.assignment || ',' || admtask.tasknr, admsolutionattempts.submissionstamp desc ")
            self.tasks = Pgdb(self).get_records(query,(self.email,md5hash))           
        return self.tasks
    
    def delete_task(self, assignment, tasknr):
        newassign = pgdb_ripsymbol + assignment
        query = "SELECT count(tasknr)+1 from admtask where assignment = %s"
        newtasknr = Pgdb(self).get_record(query, (newassign ,))[0]
        query = "UPDATE admtask set assignment = %s, tasknr = %s where assignment = %s and tasknr = %s"
        return Pgdb(self).execute(query,(newassign ,newtasknr,assignment,tasknr))
    
    def run_solution(self, title, task, code):
        query = "Select testsuite from admtask where assignment = %s and tasknr = %s"
        data = (title, task)
        tests = Pgdb(self).get_record(query, data)[0] 
              
        for result, time in testRunner.test(code, tests):
            if isinstance(result, str):
                yield [result + '\n', time]
            else:
                strResult = ''
                for boodschap in result: 
                    strResult += boodschap
                yield ["<test>" + json.dumps(["compile", "compile", 0, "Your submission cannot be compiled\n" + strResult]),0]

    def store_solution(self, title, task, code, resultset, score):
        query = "Insert into admsolution (assignment, tasknr, email, submissionstamp,code, results, score) values (%s, %s, %s, now(), %s, %s, %s)"
        data = (title, task, self.email ,code, resultset, score)
        return Pgdb(self).execute(query,data)

    def store_tests(self, title,task, description, tests, attempts):
        if not task.isdigit():
            query = "select count(assignment)+1 from admtask where assignment = %s"
            data = (title,)
            task = Pgdb(self).get_record(query,data)[0]            
            query = "INSERT into admtask (assignment, tasknr, description,testsuite, attempts) values (%s, %s, %s, %s, %s)"
            data = (title, task, description, tests, attempts)
            return Pgdb(self).execute(query,data)
        else:
            query = "select count(assignment) from admtask where assignment = %s and tasknr = %s"
            data = (title, task)
            query = "UPDATE admtask set description = %s, testsuite = %s, attempts = %s where assignment = %s and tasknr = %s"
            data = (description,tests, attempts, title, task)
            return Pgdb(self).execute(query,data)
        
    def store_assignment(self,title,deadline,description, course, isnew):
        if isnew :           
            query = "INSERT into admassignment (deadline, title, description, course) values (%s, %s, %s, %s)"
            data = (deadline, title, description, course)
            return Pgdb(self).execute(query,data)
        else:
            query = "UPDATE admassignment set description = %s, deadline = %s, course = %s where title = %s"
            data = (description,deadline, course, title)
            print query
            print data
            return Pgdb(self).execute(query,data)
        
    def delete_assignment(self, assignment):
        newassign = pgdb_ripsymbol + assignment
        query = "UPDATE admassignment set title = %s where title = %s"
        return Pgdb(self).execute(query,(newassign, assignment))
    