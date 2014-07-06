"""
.. module:: admserver/auth
   :platform: Linix
   :synopsis: Authentication handlers for login and logout.

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

import handlers
import models
import utils
import tornado.web
from pgdb import Pgdb
from config import useSSL

class LoginHandler(handlers.BaseHandler):
    def get(self):
        items = {}
        items["useSSL"] = useSSL
        self.render('html/login.html', title="ADM server", items=items)
        #loader = template.Loader('html')
        #self.write(loader.load('login.html').generate())

    def post(self):
        trash = "\t\n(!*(!&^!%$!%!#$%@$%!^!^%@GGFVGFVGFC786857576vfhgvgh"
        try:
            correctpw = Pgdb(self).get_record("Select password from admUser where email = %s", (self.get_argument("email",trash),))
            md5hash = Pgdb(self).get_record("select md5(%s) as md5hash", (self.get_argument("password",trash),))
            if correctpw[0] == md5hash[0]:
                self.set_secure_cookie("adm_user", self.get_argument("email"))
                self.redirect("/")
            else:
                if not utils.couldBeHash(self.get_argument("password",trash)):
                    if correctpw[0] == self.get_argument("password",trash):
                        self.set_secure_cookie("adm_user", self.get_argument("email"))
                        self.redirect("/password")
                    else:    
                        self.redirect("/login")
                else:
                    self.redirect("/login")
        except TypeError:
            self.redirect("/login")
  
        
class LogoutHandler(handlers.BaseHandler):
    def get(self):
        self.clear_cookie("adm_user")
        self.redirect("/login")
   
class AddUserHandler(handlers.BaseHandler):
    
    @tornado.web.authenticated
    def post(self):
        curuser = models.User(self)
        if curuser.is_admin():
            
            isactive = Pgdb(self).get_record("select count(email) from admuser where email = %s", (self.get_argument("email"),))
            if isactive[0] == 0:
                query = "Insert into admuser (email,password,isadmin,courses,nickname) values (%s,%s,%s,%s,%s)"
                data = (self.get_argument("email"), self.get_argument("password"), False ,self.get_argument("courses"), self.get_argument("nickname"),)
                #print data
                Pgdb(self).execute(query, data)
            else:
                print "user " + self.get_argument("email") + " already in database"
            self.redirect("/admin")
        