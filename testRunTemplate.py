# source #
    
import time
import json
import unittest
from multiprocessing import Process, Queue
from traceback import format_exc
from config import admRunPath

def runTest(myTest, name, attr, myQ):
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

class TestClass(unittest.TestCase):
# tests #
    pass

def run():
    #global admRunPath
    #print vars()
    #if not 'admRunPath' in vars():
    #    admRunPath = '.'
    #else:
    #    print admRunPath
        
    myTest = TestClass('setUpClass')
    results = []
    noresults = True
    try:
        myTest._setUp()
        total = getattr(myTest, 'total', 0)
        score = getattr(myTest, 'score', 0)
        yield ["<test>" + json.dumps(["setup","setup", score , "The test environment has been setup."]),total]
    except Exception:
        try:
            myTest.setUp()
            total = getattr(myTest, 'total', 0)
            score = getattr(myTest, 'score', 0)
            yield ["<test>" + json.dumps(["setup","setup", score , "The test environment has been setup."]),total]
        except Exception:
            pass

    
    myScore = Queue()
    for name in dir(TestClass):
        if not (name[:1] == '_' or name in dir(unittest.TestCase)): 
            attr = getattr(myTest,name)
            if callable(attr):
                import os
                os.chdir(admRunPath)
                myQ = Queue()
                myProcess = Process(target=runTest, args=(myTest, name, attr, myQ))
                myProcess.start()
                
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
        yield ["<test>" + json.dumps(["no test","testless", 0,"There are no results. are there no tests?"]),0]

    try:
        myTest.tearDown()
        yield ["<test>" + json.dumps(["teardown","teardown", 0, "The test environment has been teared down."]),total]
    except Exception:
        pass

