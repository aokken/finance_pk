'''
Created on Apr 25, 2015

@author: aaron
'''
from datetime import date, datetime
from dateutil import parser
import types

class decorate_date_args(object):
    """Decorator class that converts arguments into datetime objects.
    Arguments can be strings that can be converted to datetime via dateutil.parser, date objects, or
    datetime objects (passed through)."""
    
    def __init__(self, *args):
        """Arguments can be integers indicating position arguments to be acted on (first argument = 1), or strings for key's
        of keyword arguments that need to be converted to datetime objects."""
        self.kwargs_keys = []
        self.position_args = []
        
        for a in args:
            if isinstance(a, basestring):
                self.kwargs_keys.append(a)
                
            elif isinstance(a, (int, long)):
                if (a < 1):
                    raise ValueError("Position argument must be 1 or greater")
                self.position_args.append(a-1)
                
            else:
                raise TypeError("decorate_date_args must be position index of positional arguments or keyword key")
        
    def __call__(self, f):
        from functools import wraps
        @wraps(f)
        def f_dates(*args, **kwargs):
            l = list(args)
            for i in self.position_args:
                if i > len(args):
                    raise Exception("No argument passed for position argument '{}'".format(i+1))
                
                l[i] = _process_date(args[i])
                
            for key in self.kwargs_keys:
                if key in kwargs:
                    kwargs[key] = _process_date(kwargs[key])
                    
            return f(*l, **kwargs)
                    
        return f_dates
    
    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return types.MethodType(self, instance)
            
def _process_date(d):
    if d is None:
        return
        #raise TypeError("Functions decorated with decorate_start_end_date must have start_date and end_date as keyword argument")
            
    if isinstance(d, basestring):
        d = parser.parse(d)       
    elif isinstance(d, date):
        d = datetime.combine(d, datetime.min.time())
    elif isinstance(d, datetime):
        pass
    else:
        raise TypeError("Must be a date or datetime object, or string that can be parsed by dateutil.parser")
    
    return d