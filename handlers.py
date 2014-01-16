"""
.. module:: handlers
   :platform: Linix
   :synopsis: Classes that handle server GET and POST requests.

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

import tornado.web
import models
import hashlib
import traceback


class BaseHandler(tornado.web.RequestHandler):
    """Extension on the Requesthandler to add cookie based authentication.

    This Class is intended for extension purposes only.
    """
    def get_current_user(self):
        """Return the email address of the current user from a secure cookie.
        :returns:  str.
        """
        return self.get_secure_cookie("adm_user")
    
            
class AssignmentHandler(BaseHandler):
    """Handle GET requests to /.
    """
    
    @tornado.web.authenticated
    def get(self):
        """Instantiate a current user instance of the User model and 
        render the html/assignment.html.
        
        :precondition: The user is authenticated
        :postcondition:  a rendered version of the html/assignment.html page.
        """
        curuser = models.User(self)
        items = {}
        items["name"] = curuser.get_email()
        items["assignments"] = curuser.get_assignments()
        items["isadmin"] = curuser.is_admin()
        self.render('html/assignment.html', title="ADM server", items=items)

    @tornado.web.authenticated    
    def post(self):
        """Instantiate a current user instance of the User model and 
        store the posted values as a user submission of a solution.
        
        :postcondition:  a redirection to the /assignment/<hash>#<task> page and an posted
                         silution stored in the database
        :done:  redirect to the assignment page at the specific task? 
        """
        print self.get_argument("code", "", False)
        curuser = models.User(self)
        resultset = ''
        for result in curuser.run_solution(self.get_argument("assignment","",True),self.get_argument("task","",True),self.get_argument("code", "", False)):
            resultset = resultset + result
            self.write(result)
            self.flush(False)
        
        e = curuser.store_solution(self.get_argument("assignment","",True),self.get_argument("task","",True),self.get_argument("code", "", False),resultset)
        if isinstance(e,Exception):
            self.write("Error storing solution\n" + e)
        self.flush(True)        
            
        ##I replaced the redirect with clientside code We only want to return 
        ##The returnvalues of the tests one by one
    
class EntryHandler(BaseHandler):
    """Handle GET requests to /assignment/<hash>.
    
    Where hash is a md5 hash of a valid assignment title
    """

    @tornado.web.authenticated
    def get(self, md5hash):
        """Instantiate a current user instance of the User model and 
        render the html/assignment.html.
        
        :precondition: The user is authenticated
        :postcondition:  a rendered version of the html/solution.html page.
        """        
        curuser = models.User(self)
        items = {}
        items["name"] = curuser.get_email()
        items["assignment"] = curuser.get_assignment(md5hash)
        items["tasks"] = curuser.get_tasks(md5hash) 
        items["isadmin"] = curuser.is_admin()               
        self.render('html/solution.html', title="ADM server", items=items)
        
        
class AdminHandler(BaseHandler):
    """Handle GET requests to /admin."""
    
    @tornado.web.authenticated
    def get(self):
        """Instantiate a current user instance of the User model and 
        render the html/admin.html page if this user is an administrator.
        
        :postcondition:  a redirection to the logout page if user is not admin.
        :postcondition:  a rendered version of the html/admin.html page if the user is admin.
        """
        curuser = models.User(self)
        if not curuser.is_admin():
            self.redirect("/logout")
        else:
            items = {}
            items["name"] = curuser.get_email()
            items["assignments"] = curuser.get_assignments()
            self.render('html/admin.html', title="ADM server", items=items)

    @tornado.web.authenticated        
    def post(self):
        """Instantiate a current user instance of the User model and 
        store the posted values for description and tests in the database
        if the user is admin.
         
        :postcondition:  a redirection to the logout page if user is not admin.
        :postcondition:  a redirection to the /admin page and an updated task 
                         in the database
        :todo:  redirect to the assignment page at the specific task? 
        """
        curuser = models.User(self)
        if not curuser.is_admin():
            self.redirect("/logout")
        else:
            e = curuser.store_assignment(self.get_argument("title","",True),self.get_argument("deadline","",True),self.get_argument("description", "", False), self.get_argument("isnew","",True).lower() == "true" )
            if isinstance(e,Exception):
                self.write("<pre>Error storing assignment\n" + str(e) + "</pre>")
                self.flush(True)
            else:
                self.redirect("/admin")

            
class AdminEntryHandler(BaseHandler):
    """Handle GET requests to /admin/<hash>.
    
    The hash should be a valid md5 hash of the title of a specific assignment
    This way we prevent trouble due to spaces and other characters in title names."""
    @tornado.web.authenticated
    def get(self, md5hash):
        """Instantiate a current user instance of the User model and 
        render the html/adminentry.html page if this user is an administrator.
        
        :postcondition:  a redirection to the logout page if user is not admin.
        :postcondition:  a rendered version of the html/adminentry.html page if the user is admin.
        """
        curuser = models.User(self)
        if not curuser.is_admin():
            self.redirect("/logout")
        else:
            items = {}
            items["name"] = curuser.get_email()
            items["assignment"] = curuser.get_assignment(md5hash)
            items["tasks"] = curuser.get_tasks(md5hash)        
            self.render('html/adminentry.html', title="ADM server", items=items)

    @tornado.web.authenticated        
    def post(self,md5Hash):
        """Instantiate a current user instance of the User model and 
        store the posted values for description and tests in the database.
        
        :postcondition:  a redirection to the logout page if user is not admin.
        :postcondition:  a redirection to the /admin page and an updated task 
                         in the database
        :done:  redirect to the assignment page at the specific task? 
        """
        curuser = models.User(self)
        if not curuser.is_admin():
            self.redirect("/logout")
        else:
            e = curuser.store_tests(self.get_argument("assignment","",True),self.get_argument("task","",True),self.get_argument("description", "", False), self.get_argument("tests", "", False))
            if isinstance(e,Exception):
                self.write("<pre>Error storing test\n" + e + "</pre>")
                self.flush(True)
            else:
                self.redirect("/admin/"  + md5Hash + "#task" + self.get_argument("task","",True))

class DeleteTaskHandler(BaseHandler):
    """Handle POST requests to /deletetask
    
    The post argument assignment should be a valid assignment title of a specific 
    assignment The task argument a valid task number."""
    @tornado.web.authenticated
    def post(self):
        """Instantiate a current user instance of the User model and 
        store the posted values for description and tests in the database
        if the user is admin.
         
        :postcondition:  a redirection to the logout page if user is not admin.
        :postcondition:  a redirection to the /assignment page and an deleted task 
                         in the database 
        """
        curuser = models.User(self)
        if not curuser.is_admin():
            self.redirect("/logout")
        else:
            e = curuser.delete_task(self.get_argument("assignment","",True),self.get_argument("task","",True))
            if isinstance(e,Exception):
                self.write("<pre>Error deleting task\n" + e + "</pre>")
                self.flush(True)
            else:
                m = hashlib.md5()
                m.update(self.get_argument("assignment","",True))
                self.redirect("/admin/" + m.hexdigest())

class DeleteAssignmentHandler(BaseHandler):
    """Handle POST requests to /deletetask
    
    The post argument assignment should be a valid assignment title of a specific 
    assignment The task argument a valid task number."""
    @tornado.web.authenticated
    def post(self):
        """Instantiate a current user instance of the User model and 
        store the posted values for description and tests in the database
        if the user is admin.
         
        :postcondition:  a redirection to the logout page if user is not admin.
        :postcondition:  a redirection to the /assignment page and an deleted task 
                         in the database 
        """
        curuser = models.User(self)
        if not curuser.is_admin():
            self.redirect("/logout")
        else:
            e = curuser.delete_assignment(self.get_argument("assignment","",True))
            if isinstance(e,Exception):
                self.write("<pre>Error deleting assignment\n" + e + "</pre>")
                self.flush(True)
            else:
                self.redirect("/admin")

