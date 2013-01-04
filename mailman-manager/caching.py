# -*- coding: utf-8 -*-
from hashlib import sha1
import time
import pickle

def cache_disk(seconds = 30, cache_folder="/tmp"):  
    def doCache(f):  
        def inner_function(*args, **kwargs):  
  
            # calculate a cache key based on the decorated method signature  
            key = sha1(str(f.__module__) + str(f.__name__) + str(args) + str(kwargs)).hexdigest() + '.mailmanorm'  
            filepath = os.path.join(cache_folder, key)  
  
            # verify that the cached object exists and is less than $seconds old  
            if os.path.exists(filepath):  
                modified = os.path.getmtime(filepath)  
                age_seconds = time.time() - modified  
                if age_seconds < seconds:  
                    return pickle.load(open(filepath, "rb"))  
  
            # call the decorated function...  
            result = f(*args, **kwargs)  
  
            # ... and save the cached object for next time  
            pickle.dump(result, open(filepath, "wb"))  
  
            return result  
        return inner_function  
    return doCache
