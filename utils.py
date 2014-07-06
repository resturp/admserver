from config import templateDir
import os

def readTemplate(fileName):       
    with open(os.path.join(templateDir,fileName)) as f:
        return f.read()

def couldBeHash(stringTest):
    if len(stringTest) == 32:
        for char in stringTest:
            if char not in "0123456789abcdef":
                return False
        return True
    return False
    