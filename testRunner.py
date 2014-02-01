"""
.. module:: admserver/testRunnen
   :platform: Linix
   :synopsis: Module to run tests on a submitted source.

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

import string
import random
import traceback 

def get_source_template():
    """ Return a string of the testrunner source template with placeholders.
     
    Replace the following placeholders with their target values:
    
    {% testclassname %}: prefer a random string
    
    {% source %}: The source code solution candidate
    
    {% tests %}: The provided testcases. Make sure to replace '\n' with '\n    ' to 
                 provide 1 extra indent. 

    :Parameters:
        none
    :Returns:
        a source template to run tests on a source.
             
    """

    return '''{% source %}
    
import time
import json
from multiprocessing import Process, Queue
from traceback import format_exc

def runTest{% testclassname %}(myTest, name, attr, myQ):
    """ try to run the test and return the testresult.
    returns by means of myQ: "<test>" + a json encoded string of:
    [testname, "succes|message|failed|exception", score, description]"""  
    try:
        ds = (attr.__doc__ or 'No suggestion')
        startScore = getattr(myTest, 'score', 0)
        getattr(myTest, name)()
        myScore = getattr(myTest, 'score', 0) - startScore
        
        if ds == (attr.__doc__ or 'No suggestion'):        
            myQ.put("<test>" + json.dumps([name, "succes", myScore, "You passed the test"]))
        else:
            myQ.put("<test>" + json.dumps([name, "message", myScore, "\\n" + (attr.__doc__ or 'No suggestion')]))
    except AssertionError:
        myQ.put("<test>" + json.dumps([name, "failed", 0, "\\n" + ds]))
    except Exception, e:
        myQ.put("<test>" + json.dumps([name, "exception", 0, "\\n" + ds + "\\n\\n" + format_exc()]))

class {% testclassname %}():
{% tests %}
    
def run{% testclassname %}():
    myTest = {% testclassname %}()
    results = []
    noresults = True
    try:
        myTest._setUp()
        total = getattr(myTest, 'total', 0)
        score = getattr(myTest, 'score', 0)
        yield ["<test>" + json.dumps(["setup","setup", score , "The test environment has been setup."]),total]
    except Exception:
        pass
    
    myScore = Queue()
    for name in dir(myTest):
        if not name[:1] == '_': 
            attr = getattr(myTest,name)
            if callable(attr):
                myQ = Queue()
                myProcess = Process(target=runTest{% testclassname %}, args=(myTest, name, attr, myQ))
                myProcess.start()
                myProcess.join()
                count = 0
                while myQ.empty() and count < 50:
                    time.sleep(0.05)
                    count += 1
                time.sleep(0.1)
                if myQ.empty():
                    myProcess.terminate() 
                    yield ["<test>" + json.dumps([name, "time", 0 , "It took more then 2.5 seconds to execute this test \\n" + (attr.__doc__ or 'No suggestion')]), 2500]
                    noresults = False
                else:                    
                    yield [myQ.get(False) , count * 50] 
                    noresults = False
                    
    if noresults:
        yield ["<test>" + json.dumps(["no test","testless",0,"There are no results. are there no tests?"]),0]

#    try:
#        toScore = myTest.score)
#        for data  
#        while not myScore.empty():
#            toScore += myScore.get()
            
#        yield "score: " + str((100 * eval (toScore)) / myTest.total) + "%"
#        myTest._tearDown()
#    except Exception:
#        pass   
'''


def test(source, tests):
    """ Test the source with the tests.
    
    Run this method with a python source and preferably isolated python testcases.
    Valid testcases are python methods that do not need not return anything but 
    assert some state after some operation. for instance, the following method could 
    be a testcase for a function min():
    ::
        def testMinPosInt():
            ''' min(x,y) with 2 positive ints should return the lower int''' 
            assert min(2,5) == 2
            
    Yet another testcase could be:
    ::
        def testMinNegPosInt():
            ''' min(x,y) with x < 0 and y >= 0 should return x''' 
            assert min(-2,5) == -2
         
    :Parameters:
      - `source` (str) - The proposed solution to be tested (valid python code)
      - `tests` (str) - The tests to run on the compiled source
 
    :Returns:
        A resultset of results for each testcase. A succesful test will return a 
        success notification. A failing test will return a failed notification plus
        the documentation supplied by the testcase. In both cases the running time 
        will be provided in () in miliseconds grain 50ms behind the notification.
        
        If the running time of 1 test becomes more then 2 seconds the test will be
        aborted and a notification "... took more than 2 seconds will be provided"
        also in this case the docstr of the test in provided as feedback.  
        
        If the test throws an exception, other then an assertion error, this 
        exception will be returned as is. 
 
    :Returns Type:
        string or list of strings 
 
    :Todo:
        Pass the time a method may take in the doc str of the test and stop the 
        execution of a test after this time returning a 'to slow' notification
        maybe by splitting the __doc """

    #create random name for the testsuite so we cannot outsmart the tests
    testclassname = ''.join(random.choice(string.ascii_uppercase) for x in range(12))
    #provide 1 extra indent to create a test class
    tests = "    " + tests.replace("\n","\n    ")
    newsource = get_source_template().replace("{% testclassname %}", testclassname)
    newsource = newsource.replace("{% source %}", source)
    newsource = newsource.replace("{% tests %}", tests)
    
    
    
    try: #add try  catch for incompilable code
        code_local = compile(newsource,'<string>','exec') 
        ns = {}
        exec code_local in ns    
        noreturn = True   
        for result in  ns['run' + testclassname]():
            yield result
            noreturn = False
        if noreturn:
            yield ["no results.",0]
    except SyntaxError as e:
        yield [traceback.format_exception_only(SyntaxError , e),0]
    except NameError as e:
        yield [traceback.format_exception_only(NameError , e),0]
