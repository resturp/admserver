"""
.. module:: admserver/views
   :platform: Linux
   :synopsis: View class with attributes and methods for views.

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
import json

class submissionView(object):
    
    def getView(self, target, curuser, assignment):
        resultset = ''
        myScore = 0
        myTotal = 0
        
        
        for result, time in curuser.run_solution(target.get_argument("assignment","",True),target.get_argument("task","",True),target.get_argument("code", "", False)):
                
            data = json.loads( result.split("<test>")[1])
            if data[1] == "setup":
                myTotal = time
                assignment.store_total(target.get_argument("task","",True), myTotal)
                
            strResult = """<img height="24" width="24" src="/static/""" + data[1] + """.png" alt=""" + data[1] + """>"""
            strResult += " " + data[0]
            myScore += data[2]
            strResult += """ <a href='#' onclick="showDialog('""" + data[3].replace("\n","\\n").replace("'",'`').replace('"','`') + """');"> more info ...</a>"""
                
            strResult += "</BR>"
            resultset += strResult
            target.write(strResult)
            target.flush(False)

            
        if myTotal > 0:
            strResult =  """<img height="24" width="24" src="/static/score.png" alt="score"> Score:""" + str(myScore) + " out of " + str(myTotal) + " is " + str((myScore * 100) / myTotal) + "%"
            myTotal = (myScore * 100) / myTotal
        else:    
            strResult = """<img height="24" width="24" src="/static/score.png" alt="score"> Score:""" + str(myScore)
            myTotal = myScore
        resultset += strResult
        
        target.write(strResult)
        target.flush(False)
        
        return resultset, myTotal
        

