'''
Created on Jan 31, 2014

@author: aaron
'''
from datetime import date, datetime, timedelta
from dateutil import rrule, easter, relativedelta
from decorators import decorate_date_args
class TradingDays:
    """This class defines the days that the US stock exchange is open."""
    
    # Holidays with fixed [month, day] 
    month_day_constants = [[1, 1],
                           [7, 4],
                           [12, 25]]
    
    @decorate_date_args('start_date', 'end_date')
    def __init__(self, start_date = None, end_date=None):
        if start_date is None:
            start_date = datetime.today() - relativedelta.relativedelta(years=+2)
            
        if end_date is None:
            end_date = start_date + relativedelta.relativedelta(years=10)
            
        [d.replace(hour=0, minute=0, second=0, microsecond=0) for d in (start_date, end_date)]
            
        r = rrule.rrule(rrule.DAILY,
                        byweekday=[rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR],
                        dtstart = start_date)
        
        rs = rrule.rruleset()
        rs.rrule(r)     
        
        start_year = start_date.year
        stop_year = end_date.year
        
        # Need to exclude New Years, MLK day, Washington's Birthday, Good Friday, Memorial Day,
        # 4th of July, Labor Day, Thanksgiving, and Christmas
        
        for year in range(start_year, stop_year):
            [rs.exdate(datetime.combine(date(year, h[0], h[1]), datetime.min.time())) 
                for h in self.month_day_constants]
        
            # Exclude MLK day (3rd Monday Jan)
            first_day_of_month = date(year, 1, 1)
            day_of_week = first_day_of_month.weekday() # Monday = 0 ... Sunday = 6
            if (day_of_week == 0):
                delta_day = 14
            else:
                delta_day =  21 - day_of_week
            rs.exdate(datetime.combine(first_day_of_month + 
                                       timedelta(days=delta_day), datetime.min.time())) 
        
            # Exclude Washington's B-day (3rd Moday Feb)
            first_day_of_month = date(year, 2, 1)
            day_of_week = first_day_of_month.weekday() # Monday = 0 ... Sunday = 6
            if (day_of_week == 0):
                delta_day = 14
            else:
                delta_day =  21 - day_of_week
            rs.exdate(datetime.combine(first_day_of_month + 
                                       timedelta(days=delta_day), datetime.min.time())) 
        
            # Memorial Day (Last Monday of May)
            last_day_of_month = date(year, 5, 31)
            day_of_week = last_day_of_month.weekday()
            delta_day = -day_of_week
            rs.exdate(datetime.combine(first_day_of_month + 
                                       timedelta(days=delta_day), datetime.min.time()))        
        
            # Labor Day (1st Monday of Sept)
            first_day_of_month = date(year, 9, 1)
            day_of_week = first_day_of_month.weekday() # Monday = 0 ... Sunday = 6
            if (day_of_week == 0):
                delta_day = 0
            else:
                delta_day =  7 - day_of_week
            rs.exdate(datetime.combine(first_day_of_month + 
                                       timedelta(days=delta_day), datetime.min.time())) 
        
            # Thanksgiving (4th Thursday of Nov)
            first_day_of_month = date(year, 11, 1)
            day_of_week = first_day_of_month.weekday() # Thursday = 3
            if (day_of_week < 3):
                delta_day = 24 - day_of_week
            else:
                delta_day = 31 - day_of_week
            
            rs.exdate(datetime.combine(first_day_of_month + 
                                       timedelta(days=delta_day), datetime.min.time())) 
        
            # Good friday
            good_friday_day = easter.easter(year) - timedelta(days=-2)
            rs.exdate(datetime.combine(good_friday_day, datetime.min.time()))
        
        self.rule = rs
        
    def next_trading_day(self):
        return self.rule.after(datetime.today()).date()
    
    def last_trading_day(self):
        return self.rule.before(datetime.today(), True).date()
    
    @decorate_date_args('start_date', 'end_date')
    def get_trading_days(self, start_date=None, end_date=None):    
        return [h.date() for h in self.rule.between(start_date, end_date)]
    
    @decorate_date_args('in_date')
    def is_trading_day(self, in_date = date.today()):
        return in_date in self.rule
    
    def __getitem__(self,attr):
        return self.rule[attr]
    
    
if __name__ == '__main__':
    calandar = TradingDays(start_date="2015/01/01")
    #n = calandar.last_trading_day(4026)
      
    #b = calandar.get_trading_days(datetime(4026, 1, 1, 0, 0, 0), date(4026, 12, 10))
    i = calandar.is_trading_day(datetime(2015,3,2, 1, 3, 9))
    print "Is Trading Day: %s"%i
    
    

    
        
        
            
    