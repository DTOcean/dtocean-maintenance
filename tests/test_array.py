# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 13:02:45 2018

@author: Mathew Topper
"""

import datetime as dt

from dtocean_maintenance.array import Array


def test_Array___calcPoissonEvents():
    
    start_date = dt.datetime(2016, 1, 1)
    simulation_time = 365
    failure_rate = 2
    
    test = Array(start_date,
                 simulation_time,
                 None,
                 None,
                 None,
                 None,
                 None,
                 None,
                 False)
    
    test._Array__calcPoissonEvents(failure_rate)
    
    assert len(test._Array__Poisson) > 0
    
    
def test_Array___calcPoissonEvents_empty():
    
    start_date = dt.datetime(2016, 1, 1)
    simulation_time = 1
    failure_rate = 2
    
    test = Array(start_date,
                 simulation_time,
                 None,
                 None,
                 None,
                 None,
                 None,
                 None,
                 False)
    
    test._Array__calcPoissonEvents(failure_rate)
    
    assert not test._Array__Poisson
