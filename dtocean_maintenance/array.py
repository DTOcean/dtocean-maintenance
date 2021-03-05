# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Bahram Panahandeh
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

"""This module contains the array class of dtocean-maintenance
   for reading from dtocean-reliability and save the data in arrayDict

.. module:: array
    :platform: Windows

.. moduleauthor:: Bahram Panahandeh <bahram.panahandeh@iwes.fraunhofer.de>
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import logging

import pandas as pd

from .static import poisson_process

# Set up logging
module_logger = logging.getLogger(__name__)


class Array(object):

    def __init__(self, ram_network,
                       startOperationDate,
                       simulationTimeDay,
                       eventsTableKeys,
                       NoPoisson_eventsTableKeys,
                       printWP6):

        '''__init__ function: Saves the arguments in internal variabels.

        Args:
            ram_network (object): RAM Netwok object
            startOperationDate (datetime): date of simulation start
            simulationTimeDay (float): simulation time in days
            eventsTableKeys (list of str): keys of event table dataframe
            NoPoisson_eventsTableKeys (list of str):
                keys of NoPoisson event table dataframe
            printWP6 (bool):
                internal flag in order to print messages

        Attributes:
            self.__dtocean_maintenance_PRINT_FLAG (bool):
                internal flag in order to print messages
            self.__dayHours (float): hours in one day
            self.__yearDays (float): days in one year
            self.__ram_network (object): RAM Netwok object
            self.__simulationTimeDay (float): simulation time in days
            self.__startOperationDate (datetime): Start of operation date
            self.__eleclayout (str): electrical layout of array
            self.__systype (str): system type of devices
            self.__eventsTableKeys (list of str): keys of event table dataframe
            self.__FM_ID_RA_ID (dictionary):
                Id of defined repair actions between logistics and maintenance

        '''

        # for print purposes
        self.__dtocean_maintenance_PRINT_FLAG = printWP6

        # Hours in one day
        self.__dayHours = 24.0

        # Days in one year
        self.__yearDays = 365.25
        
        # simulation time in day
        self.__simulationTimeDay = simulationTimeDay

        # Start of operation date
        self.__startOperationDate = startOperationDate

        # keys of event table
        self.__eventsTableKeys = eventsTableKeys

        # keys of NoPoisson event table
        self.__NoPoisson_eventsTableKeys = NoPoisson_eventsTableKeys


        # Id of defined repair actions between WP5 and WP6
        self.__FM_ID_RA_ID = {}
        self.__FM_ID_RA_ID['Insp1'] = 'LpM1'
        self.__FM_ID_RA_ID['Insp2'] = 'LpM1'
        self.__FM_ID_RA_ID['MoS1']  = 'LpM1'
        self.__FM_ID_RA_ID['MoS2']  = 'LpM1'
        self.__FM_ID_RA_ID['Insp3'] = 'LpM2'
        self.__FM_ID_RA_ID['MoS3']  = 'LpM2'
        self.__FM_ID_RA_ID['Insp4'] = 'LpM3'
        self.__FM_ID_RA_ID['Insp5'] = 'LpM3'
        self.__FM_ID_RA_ID['MoS4']  = 'LpM3'
        self.__FM_ID_RA_ID['MoS5']  = 'LpM4'
        self.__FM_ID_RA_ID['MoS6']  = 'LpM4'
        self.__FM_ID_RA_ID['MoS7']  = 'LpM5'
        self.__FM_ID_RA_ID['MoS8']  = 'LpM5'
        self.__FM_ID_RA_ID['RtP1']  = 'LpM6'
        self.__FM_ID_RA_ID['RtP2']  = 'LpM6'
        self.__FM_ID_RA_ID['RtP3']  = 'LpM7'
        self.__FM_ID_RA_ID['RtP4']  = 'LpM7'
        self.__FM_ID_RA_ID['RtP5']  = 'LpM8'
        self.__FM_ID_RA_ID['RtP6']  = 'LpM8'
        
        # RAM Network object
        self.__ram_network = ram_network
        
        # Pre-populate RAM metrics per sub-system type
        self.__ram_subsystems = ['Export cable',
                                 'Substation',
                                 'Elec sub-system',
                                 'Station keeping',
                                 'Umbilical',
                                 'Support structure',
                                 'Hydrodynamic',
                                 'Pto',
                                 'Control']
        
        def get_metrics_df(x):
            metrics = ram_network.get_subsystem_metrics(x)
            if metrics is None: return None
            df = pd.DataFrame(metrics)
            df = df.set_index("System")
            return df
        
        self.__ram_subsystem_metrics = {x: get_metrics_df(x)
                                                for x in self.__ram_subsystems}
        
        return
    
    # Failure estimation module
    def executeFEM(self, arrayDict,
                         eventsTable,
                         eventsTableNoPoisson,
                         component,
                         failureMode,
                         repairAction,
                         inspection,
                         annual_Energy_Production_perD):

        '''executeFEM function: Generates tables for maintenance analysis.

        Args:
            arrayDict (dict):
                dictionary for the saving of model calculation
            eventsTable (dataframe):
                table which contains the failure events for different
                components
            eventsTableNoPoisson (dataframe):
                table which contains the failure events without poisson
                distribution
            component (dataframe):
                table which contains the information about components
            failureMode (dataframe):
                table which contains the information about failure modes
            repairAction (dataframe):
                table which contains the information about repair actions
            inspection (dataframe):
                table which contains the information about inspections
            annual_Energy_Production_perD (list of float):
                annual energy production of devices

        '''

        # EventsTable (DataFrame)
        failureRateList = []
        failureEventsList = []
        repairActionEventsList = []
        belongsToList = []
        componentTypeList = []
        componentSubTypeList = []
        componentIDList = []
        FM_IDList = []
        indexFMList = []
        RA_IDList = []

        failureEventsListNoPoisson = []
        repairActionEventsListNoPoisson = []
        belongsToListNoPoisson = []
        componentTypeListNoPoisson = []
        componentSubTypeListNoPoisson = []
        componentIDListNoPoisson = []
        FM_IDListNoPoisson = []
        indexFMListNoPoisson = []
        RA_IDListNoPoisson = []
        AlarmListNoPoisson = []
        failureRateListNoPoisson = []

        # Which component type is defined
        for iCnt in range(0, component.shape[1]):

            column = component.columns.values[iCnt]
            componentID = component[column]['Component_ID']
            componentSubType = component[column]['Component_subtype']
            componentType = component[column]['Component_type']

            arrayDict[componentID] = {}
            arrayDict[componentID]['NrOfFM'] = \
                                component[componentID]['number_failure_modes']

            arrayDict[componentID]['CoBaMa_initOpEventsList'] = []
            arrayDict[componentID]['CoBaMa_FR List'] = []
            
            # Get sub-system metrics (all systems)
            if componentSubType in ['Foundation', 'Moorings lines']:
                metrics = self.__ram_subsystem_metrics['Station keeping']
            else:
                metrics = self.__ram_subsystem_metrics[componentSubType]
            
            if metrics is None:
                
                err_str = ("System type '{}' is not available in the "
                           "RAM").format(componentSubType)
                raise RuntimeError(err_str)
            
            # Get metric for (unique) parent system
            system_metrics = metrics.loc[componentType]
            base_failure_rate = system_metrics["lambda"] * 8766
            
            if componentSubType in ['Foundation', 'Moorings lines']:
                
                link_idx = system_metrics["Link"]
                system = self.__ram_network[link_idx]
                
                systemP = system.get_probability_proportion(componentSubType)
                arrayDict[componentID]['FR'] = base_failure_rate * systemP
            
            else:
                
                arrayDict[componentID]['FR'] = base_failure_rate
            
            # Get breakdowns
            if componentType == "array":
                arrayDict[componentID]['Breakdown'] = ['All']
            else:
                arrayDict[componentID]['Breakdown'] = \
                                                system_metrics["Curtails"]
            
            arrayDict[componentID]['FR List'] = []
            
            device_systems = ['Elec sub-system',
                              'Hydrodynamic',
                              'Pto',
                              'Control',
                              'Support structure',
                              'Moorings lines',
                              'Foundation',
                              'Umbilical']
            
            if componentSubType in device_systems:

                deviceID = component[column]['Component_type']
                logic = deviceID in arrayDict.keys()

                # Initialise device keys only once
                if not logic:

                    dev_idx = int(deviceID.rsplit('device')[1]) - 1
                    arrayDict[deviceID] = {}

                    # for UnCoMa
                    arrayDict[deviceID]['UnCoMaOpEvents'] = []
                    arrayDict[deviceID]['UnCoMaOpEventsDuration'] = []
                    arrayDict[deviceID]['UnCoMaOpEventsCausedBy'] = []
                    arrayDict[deviceID]['UnCoMaOpEventsIndexFM'] = []
                    arrayDict[deviceID]['UnCoMaCostLogistic'] = []
                    arrayDict[deviceID]['UnCoMaCostOM'] = []
                    arrayDict[deviceID]['UnCoMaNoWeatherWindow'] = False

                    # for CaBaMa
                    arrayDict[deviceID]['CaBaMaOpEvents'] = []
                    arrayDict[deviceID]['CaBaMaOpEventsDuration'] = []
                    arrayDict[deviceID]['CaBaMaOpEventsCausedBy'] = []
                    arrayDict[deviceID]['CaBaMaOpEventsIndexFM'] = []
                    arrayDict[deviceID]['CaBaMaCostLogistic'] = []
                    arrayDict[deviceID]['CaBaMaCostOM'] = []

                    # for CoBaMa without derating
                    arrayDict[deviceID]['CoBaMaOpEvents'] = []
                    arrayDict[deviceID]['CoBaMaOpEventsDuration'] = []
                    arrayDict[deviceID]['CoBaMaOpEventsCausedBy'] = []
                    arrayDict[deviceID]['CoBaMaOpEventsIndexFM'] = []
                    arrayDict[deviceID]['CoBaMaCostLogistic'] = []
                    arrayDict[deviceID]['CoBaMaCostOM'] = []
                    arrayDict[deviceID]['CoBaMaNoWeatherWindow'] = False

                    # for CoBaMa with derating
                    arrayDict[deviceID]['CoBaMaDeratingOpEvents'] = []
                    arrayDict[deviceID]['CoBaMaDeratingOpEventsDuration'] = []
                    arrayDict[deviceID]['CoBaMaDeratingOpEventsCausedBy'] = []
                    arrayDict[deviceID]['CoBaMaDeratingOpEventsIndexFM'] = []
                    arrayDict[deviceID]['CoBaMaDeratingCostLogistic'] = []
                    arrayDict[deviceID]['CoBaMaDeratingCostOM'] = []

                    # general
                    arrayDict[deviceID]['AnnualEnergyWP2'] = \
                                        annual_Energy_Production_perD[dev_idx]
                    arrayDict[deviceID]['AnnualEnergyWP6'] = 0.0
                    arrayDict[deviceID]['DownTime'] = 0.0

            else:

                arrayDict[componentID]['UnCoMaCostLogistic']    = []
                arrayDict[componentID]['UnCoMaCostOM']          = []
                arrayDict[componentID]['UnCoMaNoWeatherWindow'] = False

                arrayDict[componentID]['CaBaMaCostLogistic']    = []
                arrayDict[componentID]['CaBaMaCostOM']          = []

                arrayDict[componentID]['CoBaMaCostLogistic']    = []
                arrayDict[componentID]['CoBaMaCostOM']          = []
                arrayDict[componentID]['CoBaMaNoWeatherWindow'] = False

            n_modes = component[componentID]['number_failure_modes']

            for iCnt1 in range(0, n_modes):

                arrayDict[componentID]['CoBaMa_initOpEventsList'].append([])
                arrayDict[componentID]['CoBaMa_FR List'].append(0)

                # Failure rate from RAM or database
                strDummy = componentID + '_' + str(iCnt1 + 1)

                failureRate = arrayDict[componentID]['FR'] * \
                                failureMode[strDummy]['mode_probability'] / \
                                                                        100.0
                arrayDict[componentID]['FR List'].append(failureRate)

                # for checking purposes
                failureEventsListNoPoisson.append(self.__startOperationDate)
                repairActionEventsListNoPoisson.append(
                                                    self.__startOperationDate)
                indexFMListNoPoisson.append(iCnt1 + 1)
                componentTypeListNoPoisson.append(componentType)
                componentSubTypeListNoPoisson.append(componentSubType)
                componentIDListNoPoisson.append(componentID)
                FM_IDListNoPoisson.append(failureMode[strDummy]['FM_ID'])
                RA_IDListNoPoisson.append(
                        self.__FM_ID_RA_ID[failureMode[strDummy]['FM_ID']])

                if componentSubType in device_systems:
                    belongsToListNoPoisson.append(deviceID)
                else:
                    belongsToListNoPoisson.append('Array')

                # failure rate from 1/year
                self.__calcPoissonEvents(failureRate)
                failureRateListNoPoisson.append(failureRate)

                if self.__Poisson:
                    AlarmListNoPoisson.append(self.__Poisson[0])
                else:
                    AlarmListNoPoisson.append(self.__startOperationDate)

                for dIndex in range(0,len(self.__Poisson)):

                    failureEventsList.append(self.__Poisson[dIndex])
                    repairActionEventsList.append(self.__Poisson[dIndex])

                    if componentSubType in device_systems:
                        belongsToList.append(deviceID)
                    else:
                        belongsToList.append('Array')

                    # [1/year]
                    failureRateList.append(failureRate)
                    indexFMList.append(iCnt1+1)
                    componentTypeList.append(componentType)
                    componentSubTypeList.append(componentSubType)
                    componentIDList.append(componentID)
                    FM_IDList.append(failureMode[strDummy]['FM_ID'])
                    RA_IDList.append(
                            self.__FM_ID_RA_ID[failureMode[strDummy]['FM_ID']])

#        self.__eventsTableKeys  = ['failureRate',
#                                   'repairActionEvents',
#                                   'failureEvents',
#                                   'belongsTo',
#                                   'ComponentType',
#                                   'ComponentSubType',
#                                   'ComponentID',
#                                   'FM_ID',
#                                   'indexFM',
#                                   'RA_ID']
        data = {self.__eventsTableKeys[0]: failureRateList,
                self.__eventsTableKeys[1]: repairActionEventsList,
                self.__eventsTableKeys[2]: failureEventsList,
                self.__eventsTableKeys[3]: belongsToList,
                self.__eventsTableKeys[4]: componentTypeList,
                self.__eventsTableKeys[5]: componentSubTypeList,
                self.__eventsTableKeys[6]: componentIDList,
                self.__eventsTableKeys[7]: FM_IDList,
                self.__eventsTableKeys[8]: indexFMList,
                self.__eventsTableKeys[9]: RA_IDList}

        eventsTable = pd.DataFrame(data)

        # sort of eventsTable
        eventsTable.sort_values(by=self.__eventsTableKeys[1], inplace=True)

        # start index with 0
        eventsTable.reset_index(drop=True, inplace=True)

#        self.__NoPoisson_eventsTableKeys = ['repairActionEvents',
#                                            'failureEvents',
#                                            'belongsTo',
#                                            'ComponentType',
#                                            'ComponentSubType',
#                                            'ComponentID',
#                                            'FM_ID',
#                                            'indexFM',
#                                            'RA_ID',
#                                            'Alarm',
#                                            'failureRate']
        data1 = {self.__NoPoisson_eventsTableKeys[0]:
                                            repairActionEventsListNoPoisson,
                 self.__NoPoisson_eventsTableKeys[1]:
                                            failureEventsListNoPoisson,
                 self.__NoPoisson_eventsTableKeys[2]: belongsToListNoPoisson,
                 self.__NoPoisson_eventsTableKeys[3]:
                                            componentTypeListNoPoisson,
                 self.__NoPoisson_eventsTableKeys[4]:
                                            componentSubTypeListNoPoisson,
                 self.__NoPoisson_eventsTableKeys[5]: componentIDListNoPoisson,
                 self.__NoPoisson_eventsTableKeys[6]: FM_IDListNoPoisson,
                 self.__NoPoisson_eventsTableKeys[7]: indexFMListNoPoisson,
                 self.__NoPoisson_eventsTableKeys[8]: RA_IDListNoPoisson,
                 self.__NoPoisson_eventsTableKeys[9]: failureRateListNoPoisson,
                 self.__NoPoisson_eventsTableKeys[10]: AlarmListNoPoisson
                }

        eventsTableNoPoisson = pd.DataFrame(data1)

        # sort of eventsTable
        eventsTableNoPoisson.sort_values(by=self.__eventsTableKeys[5],
                                         inplace=True)

        # start index with 0
        eventsTableNoPoisson.reset_index(drop=True, inplace=True)

        return arrayDict, eventsTable, eventsTableNoPoisson

    def __calcPoissonEvents(self, failureRate):

        '''calcPoissonEvents function: Calls the poisson process function

        Args:
            failureRate (float) : Failure rate of component (per year)

        '''

        rate_day = failureRate / self.__yearDays

        returnValue = poisson_process(self.__startOperationDate,
                                      self.__simulationTimeDay,
                                      rate_day)

        if isinstance(returnValue, list) and len(returnValue) >= 1:
            self.__Poisson = returnValue
        else:
            self.__Poisson = []
