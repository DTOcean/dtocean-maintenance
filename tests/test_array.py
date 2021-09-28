# -*- coding: utf-8 -*-

#    Copyright (C) 2017-2021 Mathew Topper
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

# pylint: disable=redefined-outer-name,protected-access,no-member

import datetime as dt
from collections import Counter # Required for eval of text files

import numpy as np
import pytest

from dtocean_maintenance.array import Array
from dtocean_reliability.main import Network
from dtocean_reliability.parse import SubNetwork


@pytest.fixture(scope="module")
def eventsTableKeys():
    return ['failureRate [1/year]',
            'failureDate [-]',
            'repairActionRequestDate [-]',
            'repairActionDate [-]',
            'downtimeDuration [Hour]',
            'seeTimeDuration [Hour]',
            'waitingTimeDuration [Hour]',
            'downtimeDeviceList [-]',
            'ComponentType [-]',
            'ComponentSubType [-]',
            'ComponentID [-]',
            'FM_ID [-]',
            'RA_ID [-]',
            'indexFM [-]',
            'costLogistic [Euro]',
            'costOM_Labor [Euro]',
            'costOM_Spare [Euro]',
            'nameOfvessel [-]']


@pytest.fixture(scope="module")
def NoPoisson_eventsTableKeys():
    return ['repairActionEvents',
            'failureEvents',
            'belongsTo',
            'ComponentType',
            'ComponentSubType',
            'ComponentID',
            'FM_ID',
            'indexFM',
            'RA_ID',
            'failureRate',
            'Alarm']


@pytest.fixture(scope="module")
def database():
    
    return {'id1': {'item10': {'failratecrit': [4, 5, 6],
                               'failratenoncrit': [1, 2, 3]},
                    },
            'id2': {'item10': {'failratecrit': [4, 5, 6],
                               'failratenoncrit': [1, 2, 3]},
                    },
            'id3': {'item10': {'failratecrit': [4, 5, 6],
                               'failratenoncrit': [1, 2, 3]},
                    }}


@pytest.fixture
def electrical_network():
    
    dummyelechier = {'array': {'Export cable': [['id1']],
                               'Substation': ['id2'],
                               'layout': [['device001']]},
                     'device001': {'Elec sub-system': ['id3']}}
    dummyelecbom = {'array': {'Export cable': {'marker': [[0]],
                                               'quantity':
                                                       Counter({'id1': 1})},
                              'Substation': {'marker': [1],
                                             'quantity': Counter({'id2': 1})}},
                    'device001': {'marker': [2],
                                  'quantity': Counter({'id3': 1})}}
    
    return SubNetwork(dummyelechier, dummyelecbom)



def test_Array_init(eventsTableKeys,
                    NoPoisson_eventsTableKeys,
                    database,
                    electrical_network):
    
    ram_network = Network(database, electrical_network)
    ram_network.set_failure_rates(inplace=True)
    
    startOperationDate = dt.datetime(2016, 1, 1)
    simulationTimeDay = 365
    
    array = Array(ram_network,
                  startOperationDate,
                  simulationTimeDay,
                  eventsTableKeys,
                  NoPoisson_eventsTableKeys,
                  False)
    
    test = array._Array__ram_subsystem_metrics['Substation'].loc["array"]
    
    assert np.isclose(test["MTTF"], 1e6 / 5)
    assert test["Curtails"] == ['device001']


def test_Array___calcPoissonEvents(eventsTableKeys,
                                   NoPoisson_eventsTableKeys,
                                   database,
                                   electrical_network):
    
    ram_network = Network(database, electrical_network)
    ram_network.set_failure_rates(inplace=True)
    
    startOperationDate = dt.datetime(2016, 1, 1)
    simulationTimeDay = 365
    
    array = Array(ram_network,
                  startOperationDate,
                  simulationTimeDay,
                  eventsTableKeys,
                  NoPoisson_eventsTableKeys,
                  False)
    
    array._Array__calcPoissonEvents(10)
    
    assert len(array._Array__Poisson) > 0


def test_Array___calcPoissonEvents_empty(eventsTableKeys,
                                         NoPoisson_eventsTableKeys,
                                         database,
                                         electrical_network):
    
    ram_network = Network(database, electrical_network)
    ram_network.set_failure_rates(inplace=True)
    
    startOperationDate = dt.datetime(2016, 1, 1)
    simulationTimeDay = 1
    
    array = Array(ram_network,
                  startOperationDate,
                  simulationTimeDay,
                  eventsTableKeys,
                  NoPoisson_eventsTableKeys,
                  False)
    
    array._Array__calcPoissonEvents(2)
    
    assert not array._Array__Poisson
