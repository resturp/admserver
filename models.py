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
import md5


class Course():
    def __init__(self,course):
        self._coursename = course
        
    def backup(self):
        """Create backup of a course and store it on disk.
        Return the filename of the backup"""
        
        pass
    
    def backup_with_submissions(self):
        """Create backup of a course and store it on disk.
        Include user submissions and return the filename 
        of the backup."""
        pass
    
    def restore(self,filename):
        pass
    
class Assignment(object):

    def __init__(self,md5hash):
        self.md5hash = md5hash
        
    def get_scores(self):
        query = "Select assignment, tasknr, nickname, score, attemptcount, md5(email || ',' || assignment || ',' || tasknr) as usrhash from admsolutionattempts where md5(assignment) = %s ORDER by tasknr, score desc, attemptcount"        
        return Pgdb(self).get_records(query, (self.md5hash,))

    def get_title(self):
        query = "Select title from admassignment where md5(title) = %s"        
        return Pgdb(self).get_record(query, (self.md5hash,))[0]
    
    def store_total(self, tasknr, total):
        query = "Update admtask set totalscore = %s where md5(assignment) = %s and tasknr = %s"
        Pgdb(self).execute(query, (total, self.md5hash, tasknr))


class Admin(object):
    
    def __init__(self, handler):
        self.assignment = None
        self.users = None

    def get_users(self):
        if self.users == None:
            query = (""
            "Select "
            "   email, "
            "   nickname, "
            "   courses "
            "from "
            "   admuser "
            "order by email")
            self.users = Pgdb(self).get_records(query)
        return self.users

        
    def _get_header(self, data):
        head = "Python autograder submission \n" 
        head += "by: %s at: %s \n"
        head += "email: %s \n"
        head += "for task: %s of assignment: %s \n"
        head += "with score: %s \n"
        head += "\n"
        head += "Description:\n"
        head += "%s\n\n\n"
            
        head = head % (data[9], data[4], data[3], data[1], data[0], data[7], data[2],)
        return '# ' + head.replace('\n', '\n# ')[:-2] 

    
    def get_submission(self, md5hash):
        query = """select sa.assignment, sa.tasknr, description, email, submissionstamp, code, testsuite, score, attemptcount, nickname 
                   from admsolutionattempts as sa inner join admtask as t on 
                        t.assignment = sa.assignment and t.tasknr = sa.tasknr
                   where md5(sa.email || ',' || t.assignment || ',' || t.tasknr) = %s"""        
        data = Pgdb(self).get_record(query, (md5hash,))
        return data, self._get_header(data)

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
        
    def delete_task(self, assignment, tasknr):
        newassign = pgdb_ripsymbol + assignment
        query = "SELECT count(tasknr)+1 from admtask where assignment = %s"
        newtasknr = Pgdb(self).get_record(query, (newassign ,))[0]
        query = "UPDATE admtask set assignment = %s, tasknr = %s where assignment = %s and tasknr = %s"
        return Pgdb(self).execute(query,(newassign ,newtasknr,assignment,tasknr))

    def store_tests(self, title,task, description, tests, attempts, template):
        if not task.isdigit():
            query = "select count(assignment)+1 from admtask where assignment = %s"
            data = (title,)
            task = Pgdb(self).get_record(query,data)[0]            
            query = "INSERT into admtask (assignment, tasknr, description,testsuite, attempts, template) values (%s, %s, %s, %s, %s, %s)"
            data = (title, task, description, tests, attempts, template)
            return Pgdb(self).execute(query,data)
        else:
            query = "select count(assignment) from admtask where assignment = %s and tasknr = %s"
            data = (title, task)
            query = "UPDATE admtask set description = %s, testsuite = %s, attempts = %s, template = %s where assignment = %s and tasknr = %s"
            data = (description,tests, attempts, template, title, task)
            #print query
            #print data
            return Pgdb(self).execute(query,data)

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

    def store_assignment(self,title,deadline,description, course, isnew):
        if isnew :           
            query = "INSERT into admassignment (deadline, title, description, course) values (%s, %s, %s, %s)"
            data = (deadline, title, description, course)
            return Pgdb(self).execute(query,data)
        else:
            query = "UPDATE admassignment set description = %s, deadline = %s, course = %s where title = %s"
            data = (description,deadline, course, title)
            return Pgdb(self).execute(query,data)
        
    def delete_assignment(self, assignment):
        newassign = pgdb_ripsymbol + assignment
        query = "UPDATE admassignment set title = %s where title = %s"
        return Pgdb(self).execute(query,(newassign, assignment))
    
class User(object):
    
    def __init__(self, handler):
        self.email = tornado.escape.xhtml_escape(handler.current_user)
        query = "Select courses, nickname, password from admuser where email = %s"
        record = Pgdb(self).get_record(query, (self.email,))
        self.courses = ';' + record[0] + ';'
        self.nickname = record[1]
        self.password = record[2]
        
        wildcard = pgdb_ripsymbol + '%'

        query = "Select md5(title) as id, * from admassignment where title NOT SIMILAR TO %s and position(';' || course || ';' in %s) > 0 Order by course, deadline"        
        self.assginments = Pgdb(self).get_records(query, (wildcard, self.courses,))
        self.tasks = None
    

    def get_assignments(self):
        return self.assginments
    
    def get_email(self):
        return self.email
    
    def get_courses(self):
        return self.courses[1:-1]
    
    def get_nickname(self):
        return self.nickname
    
    def get_password(self):
        return self.password

    def set_courses(self,courses):
        self.courses = ';' + courses + ';'
    
    def set_nickname(self, nickname):
        self.nickname = nickname
    
    def set_password(self, password):
        self.password = password
    
    def store_profile(self):  
        query = "update admuser set courses = %s , nickname = %s where email = %s"
        data = (self.get_courses(), self.get_nickname(), self.email)
        return Pgdb(self).execute(query,data)

    def store_password(self):  
        query = "update admuser set password = md5(%s) where email = %s"
        data = (self.get_password(), self.email)
        return Pgdb(self).execute(query,data)
        
    
    def is_admin(self):
        return Pgdb(self).get_record("Select isadmin from admuser where email = %s",(self.email,))[0]
    

    def can_attempt(self, assignment, tasknr):
        query = "select  deadline > now() as current from admassignment where md5(title) = md5(%s)"
        data = (assignment,)
        if Pgdb(self).get_record(query, data)[0]:            
            query = "SELECT attempts, attemptcount from admsolutionattempts where email = %s and assignment = %s and tasknr = %s"
            data = (self.email, assignment, tasknr)
            result = Pgdb(self).get_record(query, data)
            if result is None:
                return True
            else:
                return (result[0] == 0) or (result[1] < result[0])
        else:
            return False
        
    def get_tasks(self, md5hash):
        if self.tasks == None:
            query = (""
            "Select distinct on (admtask.assignment || ',' || admtask.tasknr) "
            "   md5(admassignment.title) as id, "
            "   admtask.tasknr as tasknr,"
            "   admtask.description as description, "
            "   admtask.testsuite as testsuite, "
            "   admsolutionattempts.submissionstamp, "
            "   admsolutionattempts.code, "
            "   admsolutionattempts.results, "
            "   admsolutionattempts.attemptcount, "
            "   admtask.attempts, "
            "   admtask.totalscore, "
            "   admsolutionattempts.score, "
            "   admtask.template "
            "from "
            "   (admassignment inner join admtask on admassignment.title = admtask.assignment) left outer join admsolutionattempts "
            "   on (admassignment.title = admsolutionattempts.assignment AND admtask.tasknr = admsolutionattempts.tasknr and "
            "       admsolutionattempts.email = %s) "
            "where md5(admassignment.title) = %s"
            "order by admtask.assignment || ',' || admtask.tasknr, admsolutionattempts.submissionstamp desc ")
            self.tasks = Pgdb(self).get_records(query,(self.email,md5hash))           
        return self.tasks
    

    def store_solution(self, title, task, code, resultset, score):
        query = "Insert into admsolution (assignment, tasknr, email, submissionstamp,code, results, score) values (%s, %s, %s, now(), %s, %s, %s)"
        data = (title, task, self.email ,code, resultset, score)
        return Pgdb(self).execute(query,data)

        
