import random
import string
from config import *
import traceback
 


def get_source_template():
    with open(testRunTemplate) as f:
        return f.read()

def test(source, tests):
    """ Test the source with the tests.
    
    Run this method with a python source and a python testclass.
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
      - `tests` (str) - The testClas to run on the compiled source
 
    :Returns:
        A resultset of results for each testcase. A succesful test will return a 
        success notification. A failing test will return a failed notification plus
        the documentation supplied by the testcase. In both cases the running time 
        will be provided in () in miliseconds grain 50ms behind the notification.
        
        If the running time of 1 test becomes more then 2.5 seconds the test will be
        aborted and a notification "... took more than 2.5 seconds will be provided"
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

    newsource = get_source_template()
    if  'class TestClass(unittest.TestCase):' in tests: 
        newsource = newsource.replace('class TestClass(unittest.TestCase):\n# tests #\n    pass', tests)
    else:
        #provide 1 extra indent to create a test class
        tests = "    " + tests.replace("\n","\n    ")
        newsource = newsource.replace("# tests #\n    pass", tests)
        
    newsource = newsource.replace("# source #", source)
    
    
    try: #add try  catch for incompilable code
        code_local = compile(newsource,'<string>','exec') 
        
        ns = {'admRunPath': admRunPath}
        exec code_local in ns    
        noreturn = True   
        for result in  ns['run']():
            yield result
            noreturn = False
        if noreturn:
            yield ["no results.",0]
    except SyntaxError as e:
        yield [traceback.format_exception_only(SyntaxError , e),0]
    except NameError as e:
        yield [traceback.format_exception_only(NameError , e),0]
