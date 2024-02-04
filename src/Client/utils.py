import functools
import sys
import os
import time

def redirect_print_to_log():
    log = ""
    def outer(func):
        @functools.wraps
        def inner(*args, **kwargs):
            stdout = sys.stdout
            stderr = sys.stderr

            flag = "a"

            if os.path.exists(log):
                flag = "w+"

            with open(log, flag) as f:
                sys.stdout = f
                sys.stderr = f

                func(*args, **kwargs)

            sys.stdout = stdout
            sys.stderr = stderr
        return inner
    return outer