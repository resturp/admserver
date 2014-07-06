""" TestCase with Methods that invoke the programmed exercise and 
    assert some state. All methods with leading _ underscores will 
    not be run autonomic during a test. Test methods are run in 
    random order so isolate them from each other."""

import unittest

class TestClass(unittest.TestCase):
    def setUp(self):
        self.total = 50
        self.score = 10

    def testExample(self):
        """Feedback for failing."""
        assert "something()" == "some value"
        #increase the score after the assertion is met
        self.score += 10
