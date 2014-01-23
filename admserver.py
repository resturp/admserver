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

import handlers
import auth
import socket
import tornado.ioloop
import tornado.httpserver
import os


settings = {
    "cookie_secret": "ADMSERVERRANDOMVALUEVALUE",
    "login_url": "/login",
    "xsrf_cookies": True,
}

application = tornado.web.Application([
    (r"/(favicon.ico)", tornado.web.StaticFileHandler, {"path": "static"}),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    (r"/login", auth.LoginHandler),
    (r"/logout", auth.LogoutHandler),
    (r"/profile", handlers.profileHandler),    
    (r"/", handlers.AssignmentHandler),
    (r"/assignment", handlers.AssignmentHandler),
    (r"/assignment/([^/]+)", handlers.EntryHandler),
    (r"/deleteassignment", handlers.DeleteAssignmentHandler),
    (r"/admin", handlers.AdminHandler),
    (r"/admin/([^/]+)", handlers.AdminEntryHandler),
    (r"/deletetask", handlers.DeleteTaskHandler),
    
    
], **settings )

http_server = tornado.httpserver.HTTPServer(application, ssl_options= {
    "certfile": os.path.join("cert", "self.crt"),
    "keyfile": os.path.join("cert", "self.key"),
})


if __name__ == "__main__":
    try:
        http_server.listen(443)
    except socket.error as e:
        http_server.listen(8080)
    
    tornado.ioloop.IOLoop.instance().start()
    