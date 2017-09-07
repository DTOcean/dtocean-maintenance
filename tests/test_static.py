# -*- coding: utf-8 -*-
"""
Created on Wed Sep 06 14:44:04 2017

@author: mtopper
"""

import pytest

import datetime as dt

import numpy as np
import pandas as pd

from dtocean_maintenance.static import (Availability,
                                        Energy,
                                        get_uptime_df,
                                        get_device_energy_df,
                                        get_opex_per_year,
                                        get_opex_lcoe,
                                        get_number_of_journeys)


@pytest.fixture(scope="module")
def events_tables_dict():
    
    cobama = {'ComponentID [-]': {0: np.nan},
              'ComponentSubType [-]': {0: np.nan},
              'ComponentType [-]': {0: np.nan},
              'FM_ID [-]': {0: np.nan},
              'RA_ID [-]': {0: np.nan},
              'costLogistic [Euro]': {0: np.nan},
              'costOM_Labor [Euro]': {0: np.nan},
              'costOM_Spare [Euro]': {0: np.nan},
              'currentAlarmDate [-]': {0: np.nan},
              'downtimeDeviceList [-]': {0: np.nan},
              'downtimeDuration [Hour]': {0: np.nan},
              'failureRate [1/year]': {0: np.nan},
              'indexFM [-]': {0: np.nan},
              'repairActionDate [-]': {0: np.nan},
              'repairActionRequestDate [-]': {0: np.nan}}
    
    cabama = {'ComponentID [-]': {0: np.nan},
              'ComponentSubType [-]': {0: np.nan},
              'ComponentType [-]': {0: np.nan},
              'FM_ID [-]': {0: np.nan},
              'RA_ID [-]': {0: np.nan},
              'costLogistic [Euro]': {0: np.nan},
              'costOM_Labor [Euro]': {0: np.nan},
              'costOM_Spare [Euro]': {0: np.nan},
              'downtimeDeviceList [-]': {0: np.nan},
              'downtimeDuration [Hour]': {0: np.nan},
              'indexFM [-]': {0: np.nan},
              'repairActionDate [-]': {0: np.nan},
              'repairActionRequestDate [-]': {0: np.nan}}
    
    ucoma = {'ComponentID [-]': {0: 'subhub003',
                                 1: 'subhub003',
                                 2: 'Pto001',
                                 3: 'Mooring line003',
                                 4: 'subhub003',
                                 5: 'Control002',
                                 6: 'Pto003',
                                 7: 'Dynamic cable001',
                                 8: 'Foundation002',
                                 9: 'subhub001',
                                 10: 'subhub003',
                                 11: 'Pto001',
                                 12: 'Control001',
                                 13: 'subhub003',
                                 14: 'Control002',
                                 15: 'Array elec sub-system003',
                                 16: 'subhub002',
                                 17: 'subhub002',
                                 18: 'subhub002',
                                 19: 'subhub002',
                                 20: 'Control001',
                                 21: 'Substation001',
                                 22: 'Control002',
                                 23: 'Pto001',
                                 24: 'subhub003',
                                 25: 'Pto002',
                                 26: 'subhub002',
                                 27: 'subhub003',
                                 28: 'subhub002',
                                 29: 'Control003',
                                 30: 'Control003',
                                 31: 'subhub003',
                                 32: 'Pto003',
                                 33: 'subhub002'},
             'ComponentSubType [-]': {0: 'subhub',
                                      1: 'subhub',
                                      2: 'Pto',
                                      3: 'Mooring line',
                                      4: 'subhub',
                                      5: 'Control',
                                      6: 'Pto',
                                      7: 'Dynamic cable',
                                      8: 'Foundation',
                                      9: 'subhub',
                                      10: 'subhub',
                                      11: 'Pto',
                                      12: 'Control',
                                      13: 'subhub',
                                      14: 'Control',
                                      15: 'Array elec sub-system',
                                      16: 'subhub',
                                      17: 'subhub',
                                      18: 'subhub',
                                      19: 'subhub',
                                      20: 'Control',
                                      21: 'Substation',
                                      22: 'Control',
                                      23: 'Pto',
                                      24: 'subhub',
                                      25: 'Pto',
                                      26: 'subhub',
                                      27: 'subhub',
                                      28: 'subhub',
                                      29: 'Control',
                                      30: 'Control',
                                      31: 'subhub',
                                      32: 'Pto',
                                      33: 'subhub'},
             'ComponentType [-]': {0: 'subhub003',
                                   1: 'subhub003',
                                   2: 'device001',
                                   3: 'device003',
                                   4: 'subhub003',
                                   5: 'device002',
                                   6: 'device003',
                                   7: 'device001',
                                   8: 'device002',
                                   9: 'subhub001',
                                   10: 'subhub003',
                                   11: 'device001',
                                   12: 'device001',
                                   13: 'subhub003',
                                   14: 'device002',
                                   15: 'device003',
                                   16: 'subhub002',
                                   17: 'subhub002',
                                   18: 'subhub002',
                                   19: 'subhub002',
                                   20: 'device001',
                                   21: 'Substation001',
                                   22: 'device002',
                                   23: 'device001',
                                   24: 'subhub003',
                                   25: 'device002',
                                   26: 'subhub002',
                                   27: 'subhub003',
                                   28: 'subhub002',
                                   29: 'device003',
                                   30: 'device003',
                                   31: 'subhub003',
                                   32: 'device003',
                                   33: 'subhub002'},
             'FM_ID [-]': {0: 'MoS4',
                           1: 'MoS4',
                           2: 'MoS1',
                           3: 'MoS5',
                           4: 'MoS4',
                           5: 'MoS1',
                           6: 'Insp1',
                           7: 'RtP6',
                           8: 'MoS4',
                           9: 'MoS4',
                           10: 'MoS4',
                           11: 'MoS1',
                           12: 'MoS1',
                           13: 'MoS4',
                           14: 'MoS1',
                           15: 'MoS7',
                           16: 'MoS4',
                           17: 'MoS4',
                           18: 'MoS4',
                           19: 'MoS4',
                           20: 'MoS1',
                           21: 'MoS2',
                           22: 'MoS1',
                           23: 'Insp1',
                           24: 'MoS4',
                           25: 'MoS1',
                           26: 'MoS4',
                           27: 'MoS4',
                           28: 'MoS4',
                           29: 'MoS1',
                           30: 'MoS1',
                           31: 'MoS4',
                           32: 'Insp1',
                           33: 'MoS4'},
             'RA_ID [-]': {0: 'LpM3',
                           1: 'LpM3',
                           2: 'LpM1',
                           3: 'LpM4',
                           4: 'LpM3',
                           5: 'LpM1',
                           6: 'LpM1',
                           7: 'LpM8',
                           8: 'LpM3',
                           9: 'LpM3',
                           10: 'LpM3',
                           11: 'LpM1',
                           12: 'LpM1',
                           13: 'LpM3',
                           14: 'LpM1',
                           15: 'LpM5',
                           16: 'LpM3',
                           17: 'LpM3',
                           18: 'LpM3',
                           19: 'LpM3',
                           20: 'LpM1',
                           21: 'LpM1',
                           22: 'LpM1',
                           23: 'LpM1',
                           24: 'LpM3',
                           25: 'LpM1',
                           26: 'LpM3',
                           27: 'LpM3',
                           28: 'LpM3',
                           29: 'LpM1',
                           30: 'LpM1',
                           31: 'LpM3',
                           32: 'LpM1',
                           33: 'LpM3'},
             'costLogistic [Euro]': {0: 164177,
                                     1: 144392L,
                                     2: 71133L,
                                     3: 266797L,
                                     4: 130003L,
                                     5: 41779L,
                                     6: 43261L,
                                     7: 989124L,
                                     8: 139330L,
                                     9: 128592L,
                                     10: 207344L,
                                     11: 46530L,
                                     12: 75095L,
                                     13: 112571L,
                                     14: 52716L,
                                     15: 1948872L,
                                     16: 236122L,
                                     17: 93015L,
                                     18: 171372L,
                                     19: 626407L,
                                     20: 73571L,
                                     21: 52621L,
                                     22: 68028L,
                                     23: 37024L,
                                     24: 79642L,
                                     25: 56654L,
                                     26: 146191L,
                                     27: 480462L,
                                     28: 300872L,
                                     29: 65352L,
                                     30: 5890038L,
                                     31: 144392L,
                                     32: 54971L,
                                     33: 480462L},
             'costOM_Labor [Euro]': {0: 63284,
                                     1: 63284L,
                                     2: 79418L,
                                     3: 135799L,
                                     4: 63284L,
                                     5: 26698L,
                                     6: 42089L,
                                     7: 72591L,
                                     8: 114159L,
                                     9: 121072L,
                                     10: 63284L,
                                     11: 41661L,
                                     12: 80912L,
                                     13: 69490L,
                                     14: 26698L,
                                     15: 128885L,
                                     16: 63284L,
                                     17: 69490L,
                                     18: 63284L,
                                     19: 159692L,
                                     20: 38426L,
                                     21: 74727L,
                                     22: 57829L,
                                     23: 37611L,
                                     24: 63284L,
                                     25: 32038L,
                                     26: 63284L,
                                     27: 159692L,
                                     28: 63284L,
                                     29: 34738L,
                                     30: 38449L,
                                     31: 63284L,
                                     32: 37636L,
                                     33: 159692L},
             'costOM_Spare [Euro]': {0: 94000,
                                     1: 94000L,
                                     2: 77000L,
                                     3: 125000L,
                                     4: 94000L,
                                     5: 5100L,
                                     6: 0L,
                                     7: 53000L,
                                     8: 3050L,
                                     9: 94000L,
                                     10: 94000L,
                                     11: 77000L,
                                     12: 5100L,
                                     13: 94000L,
                                     14: 5100L,
                                     15: 204000L,
                                     16: 94000L,
                                     17: 94000L,
                                     18: 94000L,
                                     19: 94000L,
                                     20: 5100L,
                                     21: 94000L,
                                     22: 5100L,
                                     23: 0L,
                                     24: 94000L,
                                     25: 77000L,
                                     26: 94000L,
                                     27: 94000L,
                                     28: 94000L,
                                     29: 5100L,
                                     30: 5100L,
                                     31: 94000L,
                                     32: 0L,
                                     33: 94000L},
             'downtimeDeviceList [-]': {0: [],
                                        1: [],
                                        2: ['device001'],
                                        3: ['device003'],
                                        4: [],
                                        5: ['device002'],
                                        6: ['device003'],
                                        7: ['device001'],
                                        8: ['device002'],
                                        9: [],
                                        10: [],
                                        11: ['device001'],
                                        12: ['device001'],
                                        13: [],
                                        14: ['device002'],
                                        15: ['device003',
                                             'device002',
                                             'device001'],
                                        16: [],
                                        17: [],
                                        18: [],
                                        19: [],
                                        20: ['device001'],
                                        21: ['device003',
                                             'device002',
                                             'device001'],
                                        22: ['device002'],
                                        23: ['device001'],
                                        24: [],
                                        25: ['device002'],
                                        26: [],
                                        27: [],
                                        28: [],
                                        29: ['device003'],
                                        30: ['device003'],
                                        31: [],
                                        32: ['device003'],
                                        33: []},
             'downtimeDuration [Hour]': {0: 384,
                                         1: 438L,
                                         2: 388L,
                                         3: 246L,
                                         4: 261L,
                                         5: 266L,
                                         6: 166L,
                                         7: 713L,
                                         8: 280L,
                                         9: 263L,
                                         10: 408L,
                                         11: 355L,
                                         12: 443L,
                                         13: 298L,
                                         14: 476L,
                                         15: 376L,
                                         16: 456L,
                                         17: 241L,
                                         18: 345L,
                                         19: 526L,
                                         20: 450L,
                                         21: 559L,
                                         22: 437L,
                                         23: 257L,
                                         24: 210L,
                                         25: 368L,
                                         26: 300L,
                                         27: 340L,
                                         28: 585L,
                                         29: 499L,
                                         30: 55167L,
                                         31: 39414L,
                                         32: 78434L,
                                         33: 156388L},
             'failureDate [-]': {0: '2016-02-18 00:00:00',
                                 1: '2016-02-22 00:00:00',
                                 2: '2016-03-03 00:00:00',
                                 3: '2016-03-09 00:00:00',
                                 4: '2016-04-09 00:00:00',
                                 5: '2016-04-15 00:00:00',
                                 6: '2016-04-21 00:00:00',
                                 7: '2016-04-23 00:00:00',
                                 8: '2016-05-11 00:00:00',
                                 9: '2016-06-03 00:00:00',
                                 10: '2016-06-18 00:00:00',
                                 11: '2016-06-28 00:00:00',
                                 12: '2016-07-24 00:00:00',
                                 13: '2016-08-01 00:00:00',
                                 14: '2016-08-20 00:00:00',
                                 15: '2016-09-01 00:00:00',
                                 16: '2016-09-07 00:00:00',
                                 17: '2016-09-23 00:00:00',
                                 18: '2016-10-06 00:00:00',
                                 19: '2016-11-09 00:00:00',
                                 20: '2017-01-02 00:00:00',
                                 21: '2017-02-11 00:00:00',
                                 22: '2017-03-26 00:00:00',
                                 23: '2017-04-02 00:00:00',
                                 24: '2017-04-19 00:00:00',
                                 25: '2017-04-23 00:00:00',
                                 26: '2017-07-14 00:00:00',
                                 27: '2017-07-23 00:00:00',
                                 28: '2017-08-16 00:00:00',
                                 29: '2017-08-22 00:00:00',
                                 30: '2017-09-10 00:00:00',
                                 31: '2017-09-12 00:00:00',
                                 32: '2017-09-28 00:00:00',
                                 33: '2017-10-03 00:00:00'},
             'failureRate [1/year]': {0: 2.8729583207999996,
                                      1: 2.8729583207999996,
                                      2: 0.45999935639999995,
                                      3: 0.15,
                                      4: 2.8729583207999996,
                                      5: 1.209997278,
                                      6: 0.45999935639999995,
                                      7: 0.03769379999999999,
                                      8: 0.1,
                                      9: 2.8729583207999996,
                                      10: 2.8729583207999996,
                                      11: 0.45999935639999995,
                                      12: 1.209997278,
                                      13: 2.8729583207999996,
                                      14: 1.209997278,
                                      15: 0.7944275160000001,
                                      16: 2.8729583207999996,
                                      17: 2.8729583207999996,
                                      18: 2.8729583207999996,
                                      19: 2.8729583207999996,
                                      20: 1.209997278,
                                      21: 2.0785308047999997,
                                      22: 1.209997278,
                                      23: 0.45999935639999995,
                                      24: 2.8729583207999996,
                                      25: 0.45999935639999995,
                                      26: 2.8729583207999996,
                                      27: 2.8729583207999996,
                                      28: 2.8729583207999996,
                                      29: 1.209997278,
                                      30: 1.209997278,
                                      31: 2.8729583207999996,
                                      32: 0.45999935639999995,
                                      33: 2.8729583207999996},
             'indexFM [-]': {0: 1,
                             1: 1L,
                             2: 1L,
                             3: 1L,
                             4: 1L,
                             5: 1L,
                             6: 2L,
                             7: 1L,
                             8: 1L,
                             9: 1L,
                             10: 1L,
                             11: 1L,
                             12: 1L,
                             13: 1L,
                             14: 1L,
                             15: 1L,
                             16: 1L,
                             17: 1L,
                             18: 1L,
                             19: 1L,
                             20: 1L,
                             21: 1L,
                             22: 1L,
                             23: 2L,
                             24: 1L,
                             25: 1L,
                             26: 1L,
                             27: 1L,
                             28: 1L,
                             29: 1L,
                             30: 1L,
                             31: 1L,
                             32: 2L,
                             33: 1L},
             'nrOfvessels [-]': {0: 1,
                                 1: 1L,
                                 2: 1L,
                                 3: 1L,
                                 4: 1L,
                                 5: 1L,
                                 6: 1L,
                                 7: 1L,
                                 8: 1L,
                                 9: 1L,
                                 10: 1L,
                                 11: 1L,
                                 12: 1L,
                                 13: 1L,
                                 14: 1L,
                                 15: 1L,
                                 16: 1L,
                                 17: 1L,
                                 18: 1L,
                                 19: 1L,
                                 20: 1L,
                                 21: 1L,
                                 22: 1L,
                                 23: 1L,
                                 24: 1L,
                                 25: 1L,
                                 26: 1L,
                                 27: 1L,
                                 28: 1L,
                                 29: 1L,
                                 30: 1L,
                                 31: 1L,
                                 32: 1L,
                                 33: 1L},
             'repairActionDate [-]': {0: '2016-02-25 09:00:00',
                                      1: '2016-03-04 00:00:00',
                                      2: '2016-03-13 15:00:00',
                                      3: '2016-03-13 15:00:00',
                                      4: '2016-04-13 15:00:00',
                                      5: '2016-04-19 09:00:00',
                                      6: '2016-04-25 00:00:00',
                                      7: '2016-04-27 09:00:00',
                                      8: '2016-05-15 03:00:00',
                                      9: '2016-06-08 09:00:00',
                                      10: '2016-06-23 09:00:00',
                                      11: '2016-07-05 09:00:00',
                                      12: '2016-08-02 09:00:00',
                                      13: '2016-08-08 09:00:00',
                                      14: '2016-08-30 00:00:00',
                                      15: '2016-09-07 15:00:00',
                                      16: '2016-09-12 09:00:00',
                                      17: '2016-09-29 09:00:00',
                                      18: '2016-10-11 06:00:00',
                                      19: '2016-11-17 00:00:00',
                                      20: '2017-01-07 00:00:00',
                                      21: '2017-02-25 09:00:00',
                                      22: '2017-04-03 18:00:00',
                                      23: '2017-04-07 18:00:00',
                                      24: '2017-04-25 00:00:00',
                                      25: '2017-04-27 09:00:00',
                                      26: '2017-07-19 03:00:00',
                                      27: '2017-07-27 21:00:00',
                                      28: '2017-08-22 06:00:00',
                                      29: '2017-08-30 00:00:00',
                                      30: '2017-09-18 21:00:00',
                                      31: '2022-03-05 00:00:00',
                                      32: '2026-08-30 00:00:00',
                                      33: '2035-07-27 21:00:00'},
             'repairActionRequestDate [-]': {0: '2016-02-18 12:00:00',
                                             1: '2016-02-24 10:00:00',
                                             2: '2016-03-07 04:00:00',
                                             3: '2016-03-09 04:00:00',
                                             4: '2016-04-09 12:00:00',
                                             5: '2016-04-15 03:00:00',
                                             6: '2016-04-21 00:00:00',
                                             7: '2016-04-23 04:00:00',
                                             8: '2016-05-11 03:00:00',
                                             9: '2016-06-03 12:00:00',
                                             10: '2016-06-18 12:00:00',
                                             11: '2016-06-28 03:00:00',
                                             12: '2016-07-24 03:00:00',
                                             13: '2016-08-01 12:00:00',
                                             14: '2016-08-20 03:00:00',
                                             15: '2016-09-02 12:00:00',
                                             16: '2016-09-07 12:00:00',
                                             17: '2016-09-23 12:00:00',
                                             18: '2016-10-06 12:00:00',
                                             19: '2016-11-09 12:00:00',
                                             20: '2017-01-02 03:00:00',
                                             21: '2017-02-11 12:00:00',
                                             22: '2017-03-26 03:00:00',
                                             23: '2017-04-02 00:00:00',
                                             24: '2017-04-19 12:00:00',
                                             25: '2017-04-23 03:00:00',
                                             26: '2017-07-14 12:00:00',
                                             27: '2017-07-23 12:00:00',
                                             28: '2017-08-16 12:00:00',
                                             29: '2017-08-22 03:00:00',
                                             30: '2017-09-10 03:00:00',
                                             31: '2022-02-24 11:00:00',
                                             32: '2026-08-18 18:00:00',
                                             33: '2035-07-23 21:00:00'},
             'seeTimeDuration [Hour]': {0: 42.189595564208744,
                                        1: 42.189595564208744,
                                        2: 88.24270278448401,
                                        3: 90.53272353224213,
                                        4: 42.189595564208744,
                                        5: 35.59814402385824,
                                        6: 46.766361766121065,
                                        7: 80.65745618610123,
                                        8: 76.10609338254085,
                                        9: 80.71472547888928,
                                        10: 42.189595564208744,
                                        11: 46.29075464509484,
                                        12: 107.8831210344214,
                                        13: 46.32698487672188,
                                        14: 35.59814402385824,
                                        15: 85.92353305603314,
                                        16: 42.189595564208744,
                                        17: 46.32698487672188,
                                        18: 42.189595564208744,
                                        19: 106.46184889433685,
                                        20: 51.23488593885915,
                                        21: 49.81810642060225,
                                        22: 77.10609338254085,
                                        23: 41.79075464509484,
                                        24: 42.189595564208744,
                                        25: 35.59814402385824,
                                        26: 42.189595564208744,
                                        27: 106.46184889433685,
                                        28: 42.189595564208744,
                                        29: 46.31810642060224,
                                        30: 51.266361766121065,
                                        31: 42.189595564208744,
                                        32: 41.81810642060224,
                                        33: 106.46184889433685},
             'typeOfvessels [-]': {0: 'CTV',
                                   1: 'CTV',
                                   2: 'Multicat',
                                   3: 'AHTS',
                                   4: 'CTV',
                                   5: 'CTV',
                                   6: 'CTV',
                                   7: 'CSV',
                                   8: 'Multicat',
                                   9: 'Multicat',
                                   10: 'CTV',
                                   11: 'CTV',
                                   12: 'Multicat',
                                   13: 'CTV',
                                   14: 'CTV',
                                   15: 'CLV',
                                   16: 'CTV',
                                   17: 'CTV',
                                   18: 'CTV',
                                   19: 'CSV',
                                   20: 'CTV',
                                   21: 'CTV',
                                   22: 'Multicat',
                                   23: 'CTV',
                                   24: 'CTV',
                                   25: 'CTV',
                                   26: 'CTV',
                                   27: 'CSV',
                                   28: 'CTV',
                                   29: 'CTV',
                                   30: 'CTV',
                                   31: 'CTV',
                                   32: 'CTV',
                                   33: 'CSV'},
             'waitingTimeDuration [Hour]': {0: 341.81040443579127,
                                            1: 395.81040443579127,
                                            2: 299.757297215516,
                                            3: 155.46727646775787,
                                            4: 218.81040443579127,
                                            5: 230.40185597614175,
                                            6: 119.23363823387893,
                                            7: 632.3425438138988,
                                            8: 203.89390661745915,
                                            9: 182.28527452111072,
                                            10: 365.81040443579127,
                                            11: 308.70924535490514,
                                            12: 335.1168789655786,
                                            13: 251.6730151232781,
                                            14: 440.40185597614175,
                                            15: 290.07646694396686,
                                            16: 413.81040443579127,
                                            17: 194.6730151232781,
                                            18: 302.81040443579127,
                                            19: 419.53815110566313,
                                            20: 398.7651140611408,
                                            21: 509.18189357939775,
                                            22: 359.89390661745915,
                                            23: 215.20924535490516,
                                            24: 167.81040443579127,
                                            25: 332.40185597614175,
                                            26: 257.81040443579127,
                                            27: 233.53815110566313,
                                            28: 542.8104044357913,
                                            29: 452.68189357939775,
                                            30: 55115.733638233876,
                                            31: 39371.81040443579,
                                            32: 78392.1818935794,
                                            33: 156281.53815110566}}
             
    events_tables_dict = {"CoBaMa_eventsTable": pd.DataFrame(cobama),
                          "CaBaMa_eventsTable": pd.DataFrame(cabama),
                          "UnCoMa_eventsTable": pd.DataFrame(ucoma)}
    
    return events_tables_dict


@pytest.fixture(scope="module")
def availability(events_tables_dict):
    
    commissioning_date = dt.datetime(2016, 1, 1)
    mission_time = 20
    device_ids = ['device003', 'device002', 'device001']
    
    uptime_df = get_uptime_df(commissioning_date,
                              mission_time,
                              device_ids,
                              events_tables_dict)
    
    availability = Availability(uptime_df)
    
    return availability


@pytest.fixture(scope="module")
def energy(events_tables_dict):
    
    commissioning_date = dt.datetime(2016, 1, 1)
    mission_time = 20
    device_ids = ['device003', 'device002', 'device001']
    mean_power_per_device = {'device003': 719178.075,
                             'device002': 678082.185,
                             'device001': 698630.13}
    
    uptime_df = get_uptime_df(commissioning_date,
                              mission_time,
                              device_ids,
                              events_tables_dict)
    
    dev_energy_df = get_device_energy_df(uptime_df,
                                         device_ids,
                                         mean_power_per_device)
    
    energy = Energy(dev_energy_df)
    
    return energy


def test_get_uptime_df(events_tables_dict):
    
    commissioning_date = dt.datetime(2016, 1, 1)
    mission_time = 20
    device_ids = ['device003', 'device002', 'device001']
    
    uptime_df = get_uptime_df(commissioning_date,
                              mission_time,
                              device_ids,
                              events_tables_dict)
    
    assert set(uptime_df.columns) == set(device_ids)
    assert (uptime_df.sum() < len(uptime_df)).all()
    
    
def test_get_device_energy_df(events_tables_dict):
    
    commissioning_year = 2016
    commissioning_date = dt.datetime(commissioning_year, 1, 1)
    mission_time = 20
    device_ids = ['device003', 'device002', 'device001']
    mean_power_per_device = {'device003': 719178.075,
                             'device002': 678082.185,
                             'device001': 698630.13}
    
    uptime_df = get_uptime_df(commissioning_date,
                              mission_time,
                              device_ids,
                              events_tables_dict)
    
    dev_energy_df = get_device_energy_df(uptime_df,
                                         device_ids,
                                         mean_power_per_device)
    
    expected_cols = ["Year", "Energy"] + device_ids
    dev_energys = dev_energy_df[device_ids]
    dev_energy_sum = dev_energys.sum(axis=1)
        
    assert set(expected_cols) == set(dev_energy_df.columns)
    assert np.isclose(dev_energy_sum, dev_energy_df["Energy"]).all()
    assert dev_energy_df["Year"].min() == commissioning_year
    assert dev_energy_df["Year"].max() == commissioning_year + mission_time
    
    
def test_get_opex_lcoe():
    
    cost_dict = {'Cost': {0: 0.0,
                          1: 9379513.0,
                          2: 223099.0,
                          3: 80678.0,
                          4: 0.0,
                          5: 0.0,
                          6: 259793.0,
                          7: 0.0,
                          8: 0.0,
                          9: 0.0,
                          10: 0.0,
                          11: 250800.0,
                          12: 0.0,
                          13: 0.0,
                          14: 0.0,
                          15: 0.0,
                          16: 0.0,
                          17: 0.0,
                          18: 0.0,
                          19: 0.0,
                          20: 0.0,
                          21: 0.0},
                 'Year': {x: x for x in xrange(22)}}
    
    ener_dict = {'Energy': {0: 0.0,
                            1: 15918766.9641,
                            2: 8529554.7092250008,
                            3: 2456054.7699600002,
                            4: 12059999.879400002,
                            5: 12093040.974960001,
                            6: 16366027.2336,
                            7: 18299999.817000002,
                            8: 18299999.817000002,
                            9: 18350136.802800003,
                            10: 18299999.817000002,
                            11: 18299999.817000002,
                            12: 18299999.817000002,
                            13: 18350136.802800003,
                            14: 18299999.817000002,
                            15: 18299999.817000002,
                            16: 18299999.817000002,
                            17: 18350136.802800003,
                            18: 18299999.817000002,
                            19: 18299999.817000002,
                            20: 18299999.817000002,
                            21: 2089.0410750000001},
                 'Year': {x: x for x in xrange(22)}}
    
    cost_df = pd.DataFrame(cost_dict)
    energy_df = pd.DataFrame(ener_dict)
    
    result = get_opex_lcoe(cost_df, energy_df, 0.05)
    
    assert 0 <= result < np.inf
    assert np.isclose(result, 0.0497459526411)


def test_get_opex_per_year(events_tables_dict):
    
    start_year = 2014
    commissioning_year = 2016
    start_date = dt.datetime(start_year, 1, 1)
    commissioning_date = dt.datetime(commissioning_year, 1, 1)
    mission_time = 20
    
    opex_per_year = get_opex_per_year(start_date,
                                      commissioning_date,
                                      mission_time,
                                      events_tables_dict)
        
    assert set(["Year", "Cost"]) == set(opex_per_year.columns)
    assert (opex_per_year["Cost"] >= 0.).all()
    assert opex_per_year["Year"].min() == 0
    assert opex_per_year["Year"].max() == (commissioning_year - start_year) \
                                                                + mission_time

def test_get_number_of_journeys(events_tables_dict):
    
    total_ops = get_number_of_journeys(events_tables_dict)
    
    assert total_ops == 34
    
    
def test_Availability_init(availability):
    
    assert availability._max_uptime
    

def test_Availability_get_max_uptime(events_tables_dict):
    
    commissioning_date = dt.datetime(2016, 1, 1)
    mission_time = 20
    device_ids = ['device003', 'device002', 'device001']
    
    uptime_df = get_uptime_df(commissioning_date,
                              mission_time,
                              device_ids,
                              events_tables_dict)
    
    test = Availability(uptime_df)
    max_uptime = test.get_max_uptime()
    
    assert max_uptime == len(uptime_df)
    

def test_Availability_get_array_uptime(availability):
    
    array_uptime = availability.get_array_uptime()
    
    assert 0. <= array_uptime <= availability._max_uptime


def test_Availability_get_array_downtime(availability):
    
    array_downtime = availability.get_array_downtime()
    
    assert 0. <= array_downtime <= availability._max_uptime
    

def test_Availability_get_array_availability(availability):
    
    array_availability = availability.get_array_availability()
    
    assert 0. <= array_availability <= 1.
    
    
def test_Availability_get_downtime_per_device(availability):
    
    device_ids = ['device003', 'device002', 'device001']
    downtime_per_device = availability.get_downtime_per_device(device_ids)
    downtimes = np.array(downtime_per_device.values())
    
    assert set(downtime_per_device.keys()) == set(device_ids)
    assert (downtimes <= availability._max_uptime).all()
    assert (downtimes >= 0.).all()


def test_Energy_get_device_energy_series(energy):
    
    device_ids = ['device003', 'device002', 'device001']
    device_energy_series = energy.get_device_energy_series()
    
    assert set(device_energy_series.index) == set(["Energy"] + device_ids)
    assert np.isclose(device_energy_series[device_ids].sum(),
                      device_energy_series["Energy"])


def test_Energy_get_energy_per_device(energy):
    
    device_ids = ['device003', 'device002', 'device001']
    energy_per_device = energy.get_energy_per_device(device_ids)
    energies = np.array(energy_per_device.values())
    
    assert set(energy_per_device.keys()) == set(device_ids)
    assert (energies >= 0.).all()
    

def test_Energy_get_project_energy_df(energy):
    
    start_year = 2014
    commissioning_year = 2016
    start_date = dt.datetime(start_year, 1, 1)
    commissioning_date = dt.datetime(commissioning_year, 1, 1)
    mission_time = 20
    
    device_energy_series = energy.get_device_energy_series()
    
    project_energy_df = energy.get_project_energy_df(start_date,
                                                     commissioning_date,
                                                     mission_time)    
    
    assert (project_energy_df["Energy"] >= 0.).all()
    assert np.isclose(project_energy_df["Energy"].sum(),
                      device_energy_series["Energy"])
    assert project_energy_df["Year"].min() == 0
    assert project_energy_df["Year"].max() == (commissioning_year - \
                                                    start_year) + mission_time
