
import pandas as pd
from dateutil import parser
import datetime
import numpy as np

def deserialize_power_stats( power_series, deserialize=True, verbose=False ):
    '''This function will de-seralize the power stats stored in the related dataframe column.'''
    if deserialize:
        power_stats = eval(power_series)
    else:
        power_stats = power_series
    return power_stats

def get_power_plt_data( power_series, deserialize=True, zero=False, verbose=False ):
    '''Produce a time series from the power stats stashed in a dataframe column.'''
    dct = {}
    if deserialize:
        power_stats = deserialize_power_stats( power_series, verbose=verbose )
    else:
        power_stats = power_series
    start_time = parser.parse(power_stats["start_time"])
    end_time = parser.parse(power_stats["end_time"])
    for sensor in power_stats["per_sensor"].keys():
        xs = power_stats["per_sensor"][sensor][0]
        ys = power_stats["per_sensor"][sensor][1]
        dct[sensor] = [ [ start_time + datetime.timedelta(seconds=sec) for sec in xs ], ys ] 
        if zero and type(zero)==type(True):
            dct[sensor][0] = [ (tm - start_time).total_seconds() for tm in dct[sensor][0] ]
        elif zero:
            dct[sensor][0] = [ (tm - zero).total_seconds() for tm in dct[sensor][0] ]
    dct["start_time"] = start_time
    dct["end_time"] = end_time
    return dct


def interp_power_sum_min_max( power_series, zero=False, deserialize=True, sampling=(10000,10), verbose=False ):
    ''' Compute the total power from individual sensors.  Because of the sampling'''
    ''' nature of the power time series' we need to interpolate.'''
    dct = {}
    power_stats = deserialize_power_stats( power_series, deserialize=deserialize )
    start_time = parser.parse(power_stats["start_time"])
    end_time = parser.parse(power_stats["end_time"])

    # replace large samples if exceeded threshold
    for sensor in power_stats["per_sensor"].keys():
        num_samples = len(power_stats["per_sensor"][sensor][0])
        if num_samples>sampling[0]:
            if verbose:
                print("WARNING: Sampling sensor %s size=%d exceeded threshold %d" % \
                  (sensor, num_samples, sampling[0]))
            power_stats["per_sensor"][sensor] = [ \
                power_stats["per_sensor"][sensor][0][0:num_samples-1:sampling[1]],\
                power_stats["per_sensor"][sensor][1][0:num_samples-1:sampling[1]] ]
            if verbose:
                print("WARNING: Done sampling.", len(power_stats["per_sensor"][sensor][0]))
    
    # combine x axes into a "set" and sort as a list
    all_x = set()
    for sensor in power_stats["per_sensor"].keys():
        all_x = all_x.union( set( power_stats["per_sensor"][sensor][0] ) )
    all_x = list(all_x)
    all_x.sort()
   
    # iterate the x list and accumulate the sum via interpolation as needed
    power_sum = []
    for x in all_x:
        pw = 0
        for sensor in power_stats["per_sensor"].keys():
            if x in power_stats["per_sensor"][sensor][0]:
                idx = power_stats["per_sensor"][sensor][0].index(x)
                pw +=  power_stats["per_sensor"][sensor][1][idx]
            else:
                ipw = np.interp( x, power_stats["per_sensor"][sensor][0], power_stats["per_sensor"][sensor][1] )
                pw += ipw
        power_sum.append( pw )
    dct["sum"] = [ [ start_time + datetime.timedelta(seconds=sec) for sec in all_x ],  power_sum ]
    dct["start_time"] = start_time
    dct["end_time"] = end_time  
    max_power = max( dct["sum"][1] )
    idx_for_max = dct["sum"][1].index(max_power)
    x_for_max = dct["sum"][0][idx_for_max]
    dct["max"] = [ x_for_max, max_power ]
    return dct

