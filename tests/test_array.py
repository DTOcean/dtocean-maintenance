# -*- coding: utf-8 -*-

#    Copyright (C) 2017-2018 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime as dt

from dtocean_maintenance.array import Array


#def test_Array___calcPoissonEvents():
#    
#    start_date = dt.datetime(2016, 1, 1)
#    simulation_time = 365
#    failure_rate = 2
#    
#    test = Array(None,
#                 start_date,
#                 simulation_time,
#                 None,
#                 None,
#                 False)
#    
#    test._Array__calcPoissonEvents(failure_rate)
#    
#    assert len(test._Array__Poisson) > 0
#    
#    
#def test_Array___calcPoissonEvents_empty():
#    
#    start_date = dt.datetime(2016, 1, 1)
#    simulation_time = 1
#    failure_rate = 2
#    
#    test = Array(start_date,
#                 simulation_time,
#                 None,
#                 None,
#                 None,
#                 None,
#                 None,
#                 None,
#                 False)
#    
#    test._Array__calcPoissonEvents(failure_rate)
#    
#    assert not test._Array__Poisson
