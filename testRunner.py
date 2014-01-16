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
from multiprocessing import Process, Queue
from traceback import format_exc

def runTest{% testclassname %}(myTest, name, attr, myQ):
    try:    
        getattr(myTest, name)()
        myQ.put("test " + name + ": succes")
    except AssertionError:
        myQ.put("test " + name + ": failed, \\n    " + attr.__doc__.replace('\\n','\\n    '))
    except Exception, e:
        myQ.put("test " + name + ": raised exception, \\n    " + format_exc().replace('\\n','\\n    '))

class {% testclassname %}():
{% tests %}
    
def run{% testclassname %}():
    myTest = {% testclassname %}()
    results = []
    noresults = True
    for name in dir(myTest):
        if not name[:1] == '_': 
            attr = getattr(myTest,name)
            if callable(attr):
                myQ = Queue()
                myProcess = Process(target=runTest{% testclassname %}, args=(myTest, name, attr, myQ))
                myProcess.start()
                count = 0
                while myQ.empty() and count < 50:
                    time.sleep(0.05)
                    count += 1
                time.sleep(0.1)
                if myQ.empty():
                    myProcess.terminate()
                    
                    yield "test " + name + ": took more then 2 seconds to execute \\n" + attr.__doc__.replace('\\n','\\n    ')
                    noresults = False
                else:
                    yield myQ.get(False) #+ " (" + str(count * 50) + "ms)") 
                    noresults = False
    if noresults:
        yield "no results"
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
            yield "no results."
    except SyntaxError as e:
        yield traceback.format_exception_only(SyntaxError , e)
    except NameError as e:
        yield traceback.format_exception_only(NameError , e)
