"""
.. module:: admserver/admserver
   :platform: Linix
   :synopsis: Main module for initiating the adm server.

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

import socket
import tornado.ioloop
import tornado.httpserver
import os

try:
    from config import *
except ImportError:
    print "config file missing or corrupt:"
    print "copy and edit config file from 'misc' folder to the root folder."    
    quit()

import auth
import handlers

    
settings = {
    "cookie_secret": cookie_secret,
    "login_url": "/login",
    "xsrf_cookies": True,
}

application = tornado.web.Application([
    (r"/(favicon.ico)", tornado.web.StaticFileHandler, {"path": "static"}),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    (r"/login", auth.LoginHandler),
    (r"/logout", auth.LogoutHandler),
    (r"/profile", handlers.ProfileHandler),    
    (r"/password", handlers.PasswordHandler),    
    (r"/", handlers.AssignmentHandler),
    (r"/assignment", handlers.AssignmentHandler),
    (r"/assignment/([^/]+)", handlers.EntryHandler),
    (r"/deleteassignment", handlers.DeleteAssignmentHandler),
    (r"/admin", handlers.AdminHandler),
    (r"/admin/([^/]+)", handlers.AdminEntryHandler),
    (r"/download/([^/]+)", handlers.DownloadHandler),
    (r"/adduser", auth.AddUserHandler),    
    (r"/deletetask", handlers.DeleteTaskHandler),
    
    
], **settings )

if useSSL:
    http_server = tornado.httpserver.HTTPServer(application, ssl_options= {
        "certfile": os.path.join(sslCertPath , "self.crt"),
        "keyfile": os.path.join(sslCertPath, "self.key"),
    })
else:
    http_server = tornado.httpserver.HTTPServer(application)
    


if __name__ == "__main__":
    try:
        if useSSL:
            http_server.listen(443)
            print "ADM server started on port 443"
        else:
            http_server.listen(80)
            print "ADM server started on port 80"
    except socket.error as e:
        try:
            http_server.listen(8080)
            print "ADM server started on port 8080" 
        except socket.error:
            print "A server is running on port 8080"
            quit()
           
    tornado.ioloop.IOLoop.instance().start()
    