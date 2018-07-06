# -*- coding: utf-8 -*-
"""This module contains the array class of dtocean-maintenance
   for reading from dtocean-reliability and save the data in arrayDict

.. module:: array
   :platform: Windows

.. moduleauthor:: Bahram Panahandeh <bahram.panahandeh@iwes.fraunhofer.de>
                  Mathew Topper <dataonlygreater@gmail.com>
"""

import logging

import pandas as pd

from .static import poisson_process

# Set up logging
module_logger = logging.getLogger(__name__)


class Array(object):

    def __init__(self, startOperationDate,
                       simulationTimeDay,
                       rcompvalues,
                       rsubsysvalues,
                       eleclayout,
                       systype,
                       eventsTableKeys,
                       NoPoisson_eventsTableKeys,
                       printWP6):

        '''__init__ function: Saves the arguments in internal variabels.

        Args:
            startOperationDate (datetime): date of simulation start
            simulationTimeDay (float): simulation time in days
            rcompvalues (nested list): rcompvalues from RAM
            rsubsysvalues (nested list): rsubsysvalues from RAM
            eleclayout (str): electrical layout of array
            systype (str): system type of devices
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
            self.__rsubsysvalues (nested list): rsubsysvalues from RAM
            self.__rcompvalues (nested list): rcompvalues from RAM
            self.__simulationTime (float): simulation time in days
            self.__startOperationDate (datetime): Start of operation date
            self.__eleclayout (str): electrical layout of array
            self.__systype (str): system type of devices
            self.__eventsTableKeys (list of str): keys of event table dataframe
            self.__FM_ID_RA_ID (dictionary):
                Id of defined repair actions between logistics and maintenance
            self.__ramTableKeys (list of str): Keys of RAM table
            self.__ramTable (dataframe): RAM table

        '''

        # for print purposes
        self.__dtocean_maintenance_PRINT_FLAG = printWP6

        # Hours in one day
        self.__dayHours = 24.0

        # Days in one year
        self.__yearDays = 365.25

       # list rsubsysvalues from RAM (A4)
        self.__rsubsysvalues = rsubsysvalues

        # list rcompvalues from RAM
        self.__rcompvalues = rcompvalues

        # simulation time in day
        self.__simulationTimeDay = simulationTimeDay

        # Start of operation date
        self.__startOperationDate = startOperationDate

        # Electrical layout architecture. If None assume radial
        if eleclayout is None:
            self.__eleclayout = 'radial'
        else:
            self.__eleclayout = eleclayout

        # systype
        self.__systype = systype

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
        
        # Keys of RAM table
        self.__ramTableKeys  = ['deviceID',
                                'subSystem',
                                'failureRate',
                                'breakDown']
                
        # Original RAM table
        self.__ramTable = None
        
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

        # read the necessary information from RAM
        self.__readFromRAM()

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

        # Which component type is definedt
        for iCnt in range(0, component.shape[1]):

            column = component.columns.values[iCnt]
            componentID = component[column]['Component_ID']
            componentSubType = component[column]['Component_subtype']
            componentType = component[column]['Component_type']

            arrayDict[componentID] = {}
            arrayDict[componentID]['Breakdown'] = []
            arrayDict[componentID]['NrOfFM'] = \
                                component[componentID]['number_failure_modes']

            arrayDict[componentID]['CoBaMa_initOpEventsList'] = []
            arrayDict[componentID]['CoBaMa_FR List'] = []

            if 'device' in componentType:

                RamTableQueryDeviceID = componentType

                if (componentSubType == 'Mooring line' or
                    componentSubType == 'Foundation'):

                    RamTableQuerySubSystem = \
                                        'M&F sub-system mooring foundation'

                elif componentSubType == 'Dynamic cable':

                    RamTableQuerySubSystem = 'M&F sub-system dynamic cable'

                else:

                    RamTableQuerySubSystem = componentSubType

            elif 'subhub' in componentType:

                RamTableQueryDeviceID = componentType

            else:

                RamTableQueryDeviceID  = 'Array'
                RamTableQuerySubSystem = componentType[0:-3]

            if 'subhub' in componentType:

                dummyRamTable = self.__ramTable.loc[
                    (self.__ramTable['deviceID'] == RamTableQueryDeviceID)]

            else:

                dummyRamTable = self.__ramTable.loc[
                    (self.__ramTable['deviceID'] == \
                                                 RamTableQueryDeviceID) &
                    (self.__ramTable['subSystem'] == \
                                                 RamTableQuerySubSystem)]

            if len(dummyRamTable) > 0:

                dummyRamTable.reset_index(drop=True, inplace=True)

                failure = dummyRamTable.failureRate

                if 'subhub' in componentType:
                    arrayDict[componentID]['FR'] = failure[0] + failure[1]
                else:
                    arrayDict[componentID]['FR'] = failure[0]

                # M&F -> 50% Mooring and 50% foundation
                if (componentSubType == 'Mooring line' or
                    componentSubType == 'Foundation'):

                    arrayDict[componentID]['FR'] *= 0.5

            else:

                # failure rate will be read from component table
                arrayDict[componentID]['FR'] = component[componentID][
                                                            'failure_rate']

                if self.__dtocean_maintenance_PRINT_FLAG:

                    msgStr = ('WP6: The failure rate of {} can not be '
                              'read from dtocean-reliability. Therefore '
                              'the failure rate is read from component '
                              'table').format(componentID)
                    print msgStr

            arrayDict[componentID]['FR List'] = []

            device_systems = ['Hydrodynamic',
                              'Pto',
                              'Control',
                              'Support structure',
                              'Mooring line',
                              'Foundation',
                              'Dynamic cable',
                              'Array elec sub-system']
            
            if componentSubType in device_systems:

                deviceID = component[column]['Component_type']
                logic = deviceID in arrayDict.keys()

                # This is odd. Must be some repetition occuring which this
                # is meant to stop...

                if not logic:

                    loop = int(deviceID.rsplit('device')[1]) - 1
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
                                        annual_Energy_Production_perD[loop]
                    arrayDict[deviceID]['AnnualEnergyWP6'] = 0.0
                    arrayDict[deviceID]['DownTime'] = 0.0

            else:

                arrayDict[componentID]['UnCoMaCostLogistic']    = []
                arrayDict[componentID]['UnCoMaCostOM']          = []
                arrayDict[componentID]['CaBaMaCostLogistic']    = []
                arrayDict[componentID]['CaBaMaCostOM']          = []
                arrayDict[componentID]['CoBaMaCostLogistic']    = []
                arrayDict[componentID]['CoBaMaCostOM']          = []
                arrayDict[componentID]['UnCoMaNoWeatherWindow'] = False
                arrayDict[componentID]['CoBaMaNoWeatherWindow'] = False

            n_modes = component[componentID]['number_failure_modes']

            for iCnt1 in range(0, n_modes):

                arrayDict[componentID]['CoBaMa_initOpEventsList'].append([])
                arrayDict[componentID]['CoBaMa_FR List'].append(0)

                # Failure rate from RAM or database
                strDummy = componentID + '_' + str(iCnt1 + 1)

                if iCnt1 == 0:

                    # failure rate will be read from component table
                    if 'device' in componentType:

                        RamTableQueryDeviceID  = componentType

                        if (componentSubType == 'Mooring line' or
                            componentSubType == 'Foundation'):

                            RamTableQuerySubSystem = \
                                            'M&F sub-system mooring foundation'

                        elif componentSubType == 'Dynamic cable':

                            RamTableQuerySubSystem = \
                                            'M&F sub-system dynamic cable'

                        else:

                            RamTableQuerySubSystem = componentSubType


                    elif 'subhub' in componentType:

                        RamTableQueryDeviceID = componentType

                    else:

                        RamTableQueryDeviceID  = 'Array'
                        RamTableQuerySubSystem = componentType[0:-3]

                    if 'subhub' in componentType:

                        dummyRamTable = self.__ramTable.loc[
                            (self.__ramTable['deviceID'] == \
                                                     RamTableQueryDeviceID)]

                    else:
                        dummyRamTable = self.__ramTable.loc[
                            (self.__ramTable['deviceID'] == \
                                                     RamTableQueryDeviceID) &
                            (self.__ramTable['subSystem'] ==
                                                     RamTableQuerySubSystem)]

                    if len(dummyRamTable > 0):

                        dummyRamTable.reset_index(drop=True, inplace=True)
                        arrayDict[componentID]['Breakdown'].append(
                                                dummyRamTable.breakDown[0])

                        breakdown = arrayDict[componentID]['Breakdown']

                        if (len(breakdown[0]) > 0 and
                            'Array elec sub-system' in componentID):

                            dummyList = []

                            for iCnt2 in range(0, len(breakdown[0])):
                                dummyList.append(breakdown[0][iCnt2])

                            arrayDict[componentID]['Breakdown'] = dummyList

                    else:

                       if ('Substation' in componentID or
                           'Export Cable' in componentID):

                           arrayDict[componentID]['Breakdown'].append('All')

                       elif 'device' in componentType:

                           arrayDict[componentID]['Breakdown'].append(
                                                               componentType)

                       if self.__dtocean_maintenance_PRINT_FLAG == True:

                           msgStr = ('WP6: The impact of {} on devices can '
                                     'not be analysed from '
                                     'dtocean-reliability').format(componentID)
                           print msgStr

                    if 'subhub' in componentType:
                        arrayDict[componentID]['Breakdown'] = \
                                    arrayDict[componentID]['Breakdown'][0]


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

                if 0 < len(self.__Poisson):
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
            failureRate (float) : Failure rate of component

        '''

        rate_day = failureRate / self.__yearDays

        returnValue = poisson_process(self.__startOperationDate,
                                      self.__simulationTimeDay,
                                      rate_day)

        if type(returnValue) == list and 1 <= len(returnValue):
            self.__Poisson = returnValue
        else:
            self.__Poisson = []

    def __readFromRAM(self):

        '''readFromRAM function: Read the necessary information from RAM.

        '''

        ramDeviceIDList    = []
        ramSubSystemList   = []
        ramFailureRateList = []
        ramBreakDownList   = []

        # read the failure rates from self.__rsubsysvalues
        for iCnt in range(0, len(self.__rsubsysvalues)):

            system = self.__rsubsysvalues[iCnt]

            if (system[0] not in ["PAR", "SER"] and
                system[0][1] in ['Export Cable', 'Substation']and
                'array' in system[0][2]):

                ramFailureRateList.append(system[0][-1])
                ramSubSystemList.append(system[0][1])
                ramDeviceIDList.append('Array')
                ramBreakDownList.append('All')

                continue

            if (self.__eleclayout == 'radial' or
                self.__eleclayout == 'singlesidedstring' or
                self.__eleclayout == 'doublesidedstring'):

                if not 'device' in system[0][0][2]:

                    msgStr = "Device not detected in system hierarchy"
                    module_logger.debug(msgStr)

                    continue

                # Number of devices
                for iCnt1 in range(0, len(system)):

                    flagMFSubSystem = False
                    subsystem = system[iCnt1]

                    # Number of subsystems
                    for iCnt2 in range(0, len(subsystem)):

                        dummyStr = subsystem[iCnt2][1]

                        # E-Mail of Sam
                        # The first one is for the mooring/Foundation
                        # (mooring line/anchor)
                        if ('M&F sub-system' in dummyStr and
                            flagMFSubSystem == False):

                            dummyStr = dummyStr + ' mooring foundation'
                            flagMFSubSystem = True

                        #  The second one is for the the umbilical
                        # cable
                        elif ('M&F sub-system' in dummyStr and
                              flagMFSubSystem == True):

                            dummyStr = dummyStr + ' dynamic cable'

                        ramSubSystemList.append(dummyStr)
                        ramDeviceIDList.append(subsystem[iCnt2][2])

                        # In case of 'singlesidedstring' or
                        # 'doublesidedstring' failure rate is a list
                        dummyList = subsystem[iCnt2][4]

                        if (type(dummyList) == list and
                            subsystem[iCnt2][1] == 'Array elec sub-system'):
                            ramFailureRateList.append(subsystem[iCnt2][4][1])
                        else:
                            ramFailureRateList.append(subsystem[iCnt2][4])

                        # else part below
                        if 'Array elec sub-system' in subsystem[iCnt2][1]:

                            dummyList = []

                            if (self.__eleclayout == 'radial'):

                                for iCnt3 in range(0, iCnt1 + 1):
                                    dummyList.append(system[iCnt3][iCnt2][2])

                                ramBreakDownList.append(dummyList)

                            else:

                                ramBreakDownList.append('-')

                        else:

                            ramBreakDownList.append(subsystem[iCnt2][2])

            elif self.__eleclayout == 'multiplehubs':

                if not 'subhub' in system[1][0][0][2]:

                    msgStr = "Subhub not detected in system hierarchy"
                    module_logger.debug(msgStr)

                    continue

                for iCnt1 in range(0, len(system[1])):  # loop over subhubs

                    subhub = system[1][iCnt1]

                    if ('Substation' in subhub[0][1] or
                        'Elec sub-system' in subhub[0][1]):

                        ramFailureRateList.append(subhub[0][-1])
                        ramSubSystemList.append(subhub[0][1])
                        ramDeviceIDList.append(subhub[0][2])

                        # Which devices are conntected to the sub Hub
                        dummyList = []

                        # loop over subhubs
                        for ii1 in range(0, len(subhub)):

                            subhub2 = system[1][ii1]

                            if not 'device' in subhub2[0][0][2]: continue

                            # Number of devices
                            for ii2 in range(0, len(subhub2)):

                                device = subhub2[ii2][0][2]
                                dummyList.append(device)

                        ramBreakDownList.append(dummyList)

                    else:

                        # Number of devices
                        for iCnt2 in range(0, len(subhub)):

                            flagMFSubSystem = False
                            device = subhub[iCnt2]

                            # Number of subsystems
                            for iCnt3 in range(0, len(subhub[0])):

                                subsystem = device[iCnt3]

                                dummyStr = subsystem[1]

                                # E-Mail of Sam
                                #  the first one is for the mooring/Foundation
                                if ('M&F sub-system' in dummyStr and
                                    flagMFSubSystem == False):

                                    dummyStr = dummyStr + ' mooring foundation'
                                    flagMFSubSystem = True

                                # The second one is for the the umbilical
                                # cable
                                if ('M&F sub-system' in dummyStr and
                                    flagMFSubSystem == True):

                                    dummyStr = dummyStr + ' dynamic cable'

                                ramSubSystemList.append(dummyStr)
                                ramDeviceIDList.append(subsystem[2])
                                ramFailureRateList.append(subsystem[4])

                                # else part below
                                if 'Array elec sub-system' in dummyStr:

                                    dummyList = []

                                    for ii1 in range(0, iCnt2 + 1):
                                        dummyList.append(subhub[ii1][0][2])

                                    ramBreakDownList.append(dummyList)

                                else:

                                    ramBreakDownList.append(subsystem[2])

        # [1/hour] -> [1/year]
        for iCnt in range(0, len(ramFailureRateList)):

            yearhours = self.__dayHours * self.__yearDays
            ramFailureRateList[iCnt] = ramFailureRateList[iCnt] * yearhours

        ramData = {self.__ramTableKeys[0]: ramDeviceIDList,
                   self.__ramTableKeys[1]: ramSubSystemList,
                   self.__ramTableKeys[2]: ramFailureRateList,
                   self.__ramTableKeys[3]: ramBreakDownList}

        self.__ramTable = pd.DataFrame(ramData)
        
        # Patch double counting of umbilical cable
        dynamic_search = (self.__ramTable['subSystem'] ==
                                              "M&F sub-system dynamic cable")
        array_elec_search = (self.__ramTable['subSystem'] == 
                                                     "Array elec sub-system")
        
        if dynamic_search.any() and array_elec_search.any():
            
            umbilical_fr = self.__ramTable.loc[dynamic_search,
                                               "failureRate"].iloc[0]
            fix = self.__ramTable.loc[array_elec_search,
                                      "failureRate"] - umbilical_fr
            self.__ramTable.loc[array_elec_search, "failureRate"] = fix
        
        return
