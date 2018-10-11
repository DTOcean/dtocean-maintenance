# -*- coding: utf-8 -*-
"""This module contains the implementation of the static functions and support
classes.

.. module:: static
   :platform: Windows

.. moduleauthor:: Bahram Panahandeh <bahram.panahandeh@iwes.fraunhofer.de>
                  Mathew Topper <dataonlygreater@gmail.com>
"""

import math
import bisect
import random
import datetime

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

from dtocean_economics.functions import get_present_values, get_lcoe


class Availability(object):
    
    def __init__(self, uptime_df):
        
        self._uptime_df = uptime_df
        self._max_uptime = self._calc_max_uptime(uptime_df)
        self._array_uptime = None
        self._array_downtime = None
        
        return

    def get_max_uptime(self):
            
        return self._max_uptime
    
    def get_array_uptime(self):
        
        if self._array_uptime is None:
            self._array_uptime = self._calc_array_uptime(self._uptime_df)

        return self._array_uptime 
    
    def get_array_downtime(self):
        
        if self._array_downtime is None:
        
            array_uptime = self.get_array_uptime()
            self._array_downtime = self._calc_array_downtime(self._max_uptime,
                                                             array_uptime)
        
        return self._array_downtime
    
    def get_array_availability(self):
        
        array_downtime = self.get_array_downtime()
        array_availability = 1 - float(array_downtime) / self._max_uptime
        
        return array_availability
    
    def get_downtime_per_device(self, device_ids):
            
        device_downtime_series = self._max_uptime - self._uptime_df.sum()
        device_downtime_dict = {device_id: device_downtime_series[device_id]
                                                for device_id in device_ids}
        
        return device_downtime_dict
    
    @classmethod
    def _calc_max_uptime(cls, uptime_df):
    
        max_uptime_hours = len(uptime_df)
        
        return max_uptime_hours
    
    @classmethod
    def _calc_array_uptime(cls, uptime_df):
    
        array_uptime_series = uptime_df.max(1)
        array_uptime_hours = array_uptime_series.sum()
        
        return array_uptime_hours
    
    @classmethod
    def _calc_array_downtime(cls, max_uptime, array_uptime):
            
        array_downtime_hours = max_uptime - array_uptime
        
        return array_downtime_hours


class Energy(object):
    
    def __init__(self, device_energy_df):
        
        self._device_energy_df = device_energy_df
        self._device_energy_series = None
        
        return

    def get_device_energy_series(self):
        
        if self._device_energy_series is None:
            self._device_energy_series = self._calc_device_energy_series(
                                                        self._device_energy_df)
        
        return self._device_energy_series
    
    def get_energy_per_device(self, device_ids):
        
        device_energy_series = self.get_device_energy_series()
        dev_energy_dict = {device_id: device_energy_series[device_id] for
                                                       device_id in device_ids}
        
        return dev_energy_dict
    
    def get_project_energy_df(self, start_date,
                                    commissioning_date,
                                    mission_time):
        
        start_year = start_date.year
        commisioning_year = commissioning_date.year
        end_year = commisioning_year + int(mission_time)
        
        years = range(start_year, end_year + 1)
        n_years = len(years)
        year_idxs = range(n_years)
        year_map = {year: idx for year, idx in zip(years, year_idxs)}
        
        array_energy_df = self._device_energy_df.loc[:, ["Year", "Energy"]]
        array_energy_df["Year"] = array_energy_df["Year"].replace(year_map)
        array_energy_df = array_energy_df.set_index("Year")
        
        base_energy_dict = {"Year": year_map.values(),
                            "Energy": [0] * len(year_map)}
        base_energy_df = pd.DataFrame(base_energy_dict)
        base_energy_df = base_energy_df.set_index("Year")
        
        base_energy_df.update(array_energy_df)
        base_energy_df = base_energy_df.reset_index()
                
        base_energy_df["Year"] = base_energy_df["Year"].astype(int)
        base_energy_df = base_energy_df.sort_values("Year")
        
        return base_energy_df

    @classmethod        
    def _calc_device_energy_series(cls, device_energy_df):
        
        dev_energy_year_df = device_energy_df.set_index("Year")
        dev_energy_series = dev_energy_year_df.sum()
        
        return dev_energy_series


def get_uptime_df(commissioning_date,
                  mission_time,
                  device_ids,
                  events_tables_dict):
    
    # Calculate device uptime per year
    end_date = commissioning_date + relativedelta(years=int(mission_time))
    start_date_hour = commissioning_date.replace(microsecond=0,
                                                 second=0,
                                                 minute=0)
    end_date_hour = end_date.replace(microsecond=0, second=0, minute=0)
    uptime_dates = pd.date_range(start_date_hour, end_date_hour, freq="H")
    
    uptime_dict = {"Date": uptime_dates}
    
    for device_id in device_ids:
        uptime_dict[device_id] = [1] * len(uptime_dates)
    
    for event_df in events_tables_dict.itervalues():
                    
        repair_df = event_df.loc[:, ["repairActionRequestDate [-]",
                                     "repairActionDate [-]",
                                     "downtimeDuration [Hour]",
                                     'downtimeDeviceList [-]']]
        repair_df["repairActionRequestDate [-]"] = pd.to_datetime(
                                repair_df["repairActionRequestDate [-]"])
        repair_df["repairActionDate [-]"] = pd.to_datetime(
                                repair_df["repairActionDate [-]"])
        
        for _, row in repair_df.iterrows():
            
            isnull = pd.isnull(row).all()
            
            if isnull: continue
                                        
            for device_id in row['downtimeDeviceList [-]']:
            
                downtime_start = row["repairActionDate [-]"]
                downtime = row["downtimeDuration [Hour]"]
                downtime_end = downtime_start + \
                                     datetime.timedelta(hours=downtime)
                                     
                # Avoid zero downtime events
                if downtime_start == downtime_end: continue
            
                downtime_start_hour = downtime_start.replace(microsecond=0,
                                                             second=0,
                                                             minute=0)
                downtime_end_hour = downtime_end.replace(microsecond=0,
                                                         second=0,
                                                         minute=0)
            
                downtime_start_idx = bisect.bisect_right(uptime_dates,
                                                         downtime_start_hour)
                downtime_end_idx = bisect.bisect_left(uptime_dates,
                                                      downtime_end_hour)
                
                n_zeros = downtime_end_idx - downtime_start_idx
                
                uptime_dict[device_id][
                        downtime_start_idx:downtime_end_idx] = [0] * n_zeros
                
    uptime_df = pd.DataFrame(uptime_dict)
    uptime_df = uptime_df.set_index("Date")
                
    return uptime_df


def get_device_energy_df(uptime_df, device_ids, mean_power_per_device):
    
    uptime_df = uptime_df.resample("A").sum()
    uptime_df.index = uptime_df.index.map(lambda x: x.year)
    
    # Energy calculation
    dev_energy_dict = {device_id: [] for device_id in device_ids}
    
    for year, row in uptime_df.iterrows():
        
        for device_id in device_ids:
    
            year_energy = row[device_id] * mean_power_per_device[device_id]
            dev_energy_dict[device_id].append(year_energy)
            
    dev_energy_dict["Year"] = list(uptime_df.index.values)
    dev_energy_df = pd.DataFrame(dev_energy_dict)
    dev_energy_df = dev_energy_df.set_index("Year")
                    
    dev_energy_df["Energy"] = dev_energy_df.sum(1)
    dev_energy_df = dev_energy_df.reset_index()
    
    return dev_energy_df


def get_opex_per_year(start_date,
                      commissioning_date,
                      mission_time,
                      events_tables_dict):
    
    start_year = start_date.year
    commisioning_year = commissioning_date.year
    end_year = commisioning_year + int(mission_time)
        
    years = range(start_year, end_year + 1)
    n_years = len(years)
    year_idxs = range(n_years)
    
    eco_dict = {"Year": year_idxs,
                "Cost": [0] * n_years}
            
    eco_df = pd.DataFrame(eco_dict)
    eco_df = eco_df.set_index("Year")
            
    for event_df in events_tables_dict.itervalues():
        
        if event_df.isnull().values.all(): continue
    
        event_df = event_df.dropna()
        event_df = event_df.set_index("repairActionDate [-]")
        event_df.index = pd.to_datetime(event_df.index)
        
        event_df = event_df[["ComponentType [-]",
                             "costLogistic [Euro]",
                             "costOM_Labor [Euro]",
                             "costOM_Spare [Euro]"]]

        # Prepare a dataframe for each component type
        grouped = event_df.groupby("ComponentType [-]")
        group_dict = {}
        
        for name, comp_df in grouped:
                
            comp_df = comp_df.drop("ComponentType [-]", 1)
            comp_df["Total Cost"] = \
                            comp_df[["costLogistic [Euro]",
                                     "costOM_Labor [Euro]",
                                     "costOM_Spare [Euro]"]].sum(axis=1)
            comp_df = comp_df.apply(pd.to_numeric)
            comp_df = comp_df.resample("A").sum()
            comp_df.index = comp_df.index.map(lambda x: x.year)
            comp_df = comp_df.dropna()
                            
            group_dict[name] = comp_df

        # Record energy and costs for each year
        year_costs = []
        
        for year in years:

            year_cost = 0.  
        
            for name, comp_df in group_dict.iteritems():
                
                if year not in comp_df.index: continue
                    
                year_series = comp_df.loc[year]
                year_cost += year_series["Total Cost"]
                                  
            year_costs.append(year_cost)
            
        year_dict = {"Year": year_idxs,
                     "Cost": year_costs}

        year_df = pd.DataFrame(year_dict)
        year_df = year_df.set_index("Year")
        
        eco_df = eco_df.add(year_df)
        
    opex_per_year = eco_df.reset_index()
    
    return opex_per_year


def get_opex_lcoe(opex_df, energy_df, discount_rate):
    
    opex_costs = opex_df["Cost"].values
    opex_years = opex_df["Year"].values
    
    present_opex = get_present_values(opex_costs,
                                      opex_years,
                                      discount_rate)
    discounted_opex = present_opex.sum()
    
    energy_costs = energy_df["Energy"].values
    energy_years = energy_df["Year"].values
    
    present_energy = get_present_values(energy_costs,
                                        energy_years,
                                        discount_rate)
    discounted_energy = present_energy.sum()
    
    lcoe = get_lcoe(discounted_opex, discounted_energy)
    
    return lcoe


def get_number_of_journeys(events_tables_dict):
    
    total_ops = 0
    
    if not events_tables_dict['CaBaMa_eventsTable'].isnull().values.all():
        
        total_ops += len(events_tables_dict['CaBaMa_eventsTable'])
        
    if not events_tables_dict['CoBaMa_eventsTable'].isnull().values.all():
        
        total_ops += len(events_tables_dict['CoBaMa_eventsTable'])

    if not events_tables_dict['UnCoMa_eventsTable'].isnull().values.all():
        
        total_ops += len(events_tables_dict['UnCoMa_eventsTable'])
        
    return total_ops


def poisson_process(startOperationDate, simulationTime, failureRate):

    '''poisson_process function: Estimation of random failure occurence of
    components

    Args:
        startOperationDate (timedate) : start date of operation
        simulationtime (float)        : simulation time [day]
        failureRate (float)           : failure rate [1/day]

    Returns:
        randomList [list] : random failure occurence of a component [1/day]

    '''

    # result of poisson process
    randomList = []

    # intermediate results
    timeStep = []

    # intermediate results
    timeStepAll = 0
    number      = 0

    # poison parameter
    loopNumber       = 2000
    lowerPercentile  = 40
    upperPercentile  = 70
    timeStepLoop     = []
    numberLoop       = []
    numberLoopFilt   = []
    timeStepLoopFilt = []

    dummyStartOperationDate = datetime.datetime(startOperationDate.year,
                                                startOperationDate.month,
                                                startOperationDate.day,
                                                startOperationDate.hour)

    endOperationDate = dummyStartOperationDate + \
                                datetime.timedelta(days=simulationTime)

    # poisson trial loop
    for lCnt in range(0, loopNumber):

        timeStepAll = 0
        timeStep = []
        number = 0
        # calculation loop
        while timeStepAll < simulationTime:

            # time dt
            dt = -math.log(1.0 - random.random()) / failureRate
            timeStepAll = timeStepAll + dt
            number = number + 1
            timeStep.append(dt)

        #delete last entries
        number = number - 1
        del timeStep[-1]

        #save loop results
        numberLoop.append(number)
        timeStepLoop.append(timeStep)

    upperPercentileValue = np.percentile(numberLoop, upperPercentile)
    lowerPercentileValue = np.percentile(numberLoop, lowerPercentile)

    for lCnt in range(0, loopNumber):

        if ((numberLoop[lCnt] >= lowerPercentileValue) &
            (numberLoop[lCnt] <= upperPercentileValue)):

            numberLoopFilt.append(numberLoop[lCnt])
            timeStepLoopFilt.append(timeStepLoop[lCnt])

    if len(numberLoopFilt) > 0:

        loopIndex = random.randint(0, len(numberLoopFilt) - 1)
        timeStep = timeStepLoopFilt[loopIndex]
        number = numberLoopFilt[loopIndex]

    else:

        timeStep = []
        number = 0

    TimeStamp = dummyStartOperationDate

    for iCnt in range(0, len(timeStep)):

        addTime = int(np.round(timeStep[iCnt]))
        TimeStamp = TimeStamp + datetime.timedelta(days=addTime)

        # take only the events less than endOperationDate

        #if TimeStamp <= endOperationDate and iCnt < maxNrOfEvents:
        if TimeStamp <= endOperationDate:
            randomList.append(TimeStamp)
        else:
            break

    return randomList
