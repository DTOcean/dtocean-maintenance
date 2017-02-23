# -*- coding: utf-8 -*-
"""This module contains the array class of dtocean-operations-and-maintenance
   for read from RAM and save the data in arrayDict

.. module:: arrayClass
   :platform: Windows
   :synopsis: array computational code for dtocean-operations-and-maintenance
   
.. moduleauthor:: Bahram Panahandeh <bahram.panahandeh@iwes.fraunhofer.de>
"""

# Set up logging
import logging
module_logger = logging.getLogger(__name__)
import pandas as pd

# Internal module import
from staticMethods import poissonProcess

#import random

class array(object):
           
    def __init__(self, startOperationDate, simulationTimeDay, rcompvalues, rsubsysvalues, eleclayout, systype, 
                 eventsTableKeys, NoPoisson_eventsTableKeys, printWP6, readFailureRateFromRAM):
        
        '''__init__ function: Saves the arguments in internal variabels.
                                                      
        Args:           
            startOperationDate (datetime)             : date of simulation start
            simulationTimeDay (float)                 : simulation time in days 
            rcompvalues (nested list)                 : rcompvalues from RAM 
            rsubsysvalues (nested list)               : rsubsysvalues from RAM 
            eleclayout (str)                          : electrical layout of array 
            systype (str)                             : system type of devices
            eventsTableKeys (list of str)             : keys of event table dataframe 
            NoPoisson_eventsTableKeys (list of str)   : keys of NoPoisson event table dataframe          
            printWP6 (bool)                           : internal flag in order to print the WP6-Messages (at the end of development can be removed or set to false)
            readFailureRateFromRAM (bool)             : internal flag in order to read from RAM (at the end of development can be removed or set to true)
        
        Attributes:          
            self.__dtocean_maintenance_PRINT_FLAG (bool)      : internal flag in order to print the WP6-Messages (at the end of development can be removed or set to false)                      
            self.__dayHours (float)                          : hours in one day 
            self.__yearDays (float)                          : days in one year       
            self.__rsubsysvalues (nested list)               : rsubsysvalues from RAM 
            self.__rcompvalues (nested list)                 : rcompvalues from RAM 
            self.__simulationTime (float)                    : simulation time in days     
            self.__startOperationDate (datetime)             : Start of operation date 
            self.__eleclayout (str)                          : electrical layout of array 
            self.__systype (str)                             : system type of devices
            self.__eventsTableKeys (list of str)             : keys of event table dataframe
            self.__FM_ID_RA_ID (dictionary)                  : Id of defined repair actions between WP5 and WP6 
            self.__ramTableKeys (list of str)                : Keys of RAM table
            self.__ramTable (dataframe)                      : RAM table 
            self.__readFailureRateFromRAM (bool)             : internal flag in order to read from RAM (at the end of development can be removed or set to true)
          
        Returns:
            no returns 
       
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

        # Electrical layout architecture
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
        self.__ramTableKeys  = ['deviceID', 'subSystem', 'failureRate', 'breakDown']
                
        # Original RAM table
        self.__ramTable = None
        
        # Flag read from RAM
        # True  -> Failure rate is read from RAM
        # False -> Failure rate is read from component table
        self.__readFailureRateFromRAM = readFailureRateFromRAM
        
                         
    # Failure estimation module
    def executeFEM(self, arrayDict,
                         eventsTable,
                         eventsTableNoPoisson,
                         component,
                         failureMode,
                         repairAction,
                         inspection,
                         annual_Energy_Production_perD):
                                 
        '''executeFEM function: Generates different tables for dtocean-operations-and-maintenance module.
                                                      
        Args:              
            arrayDict (dict)                              : dictionary for the saving of model calculation in dtocean-operations-and-maintenance module
            eventsTable (dataframe)                       : table which contains the failure events for different components 
            eventsTableNoPoisson (dataframe)              : table which contains the failure events without poisson distribution 
            component (dataframe)                         : table which contains the information about components
            failureMode (dataframe)                       : table which contains the information about failure modes
            repairAction (dataframe)                      : table which contains the information about repair actions
            inspection (dataframe)                        : table which contains the information about inspections
            annual_Energy_Production_perD (list of float) : annual energy production of devices
        
        Attributes:         
            no attributes                      

        Returns:
            no returns 
      
        '''
        
        # read the necessary information from RAM
        self.__readFromRAM() 
        
        # EventsTable (DataFrame)
        failureRateList        = []
        failureEventsList      = []
        repairActionEventsList = []
        belongsToList          = []  
        componentTypeList      = []
        componentSubTypeList   = []
        componentIDList        = []
        FM_IDList              = []
        indexFMList            = []
        RA_IDList              = []
        
        failureEventsListNoPoisson      = []
        repairActionEventsListNoPoisson = []
        belongsToListNoPoisson          = []  
        componentTypeListNoPoisson      = []
        componentSubTypeListNoPoisson   = []
        componentIDListNoPoisson        = []
        FM_IDListNoPoisson              = []
        indexFMListNoPoisson            = []
        RA_IDListNoPoisson              = []
        AlarmListNoPoisson              = []
        failureRateListNoPoisson        = []
                                             
        # Which component type is definedt        
        for iCnt in range(0,component.shape[1]):
                                                
            column           = component.columns.values[iCnt]                
            componentID      = component[column]['Component_ID']
            componentSubType = component[column]['Component_subtype']
            componentType    = component[column]['Component_type']

            arrayDict[componentID] = {}  
            arrayDict[componentID]['Breakdown'] = []             
            arrayDict[componentID]['NrOfFM']    = component[componentID]['number_failure_modes']
            
            arrayDict[componentID]['CoBaMa_initOpEventsList'] = [] 
            arrayDict[componentID]['CoBaMa_FR List'] = [] 
            
            # Read failure rate
            if self.__readFailureRateFromRAM == True:
                
                # failure rate will be read from component table
                if 'device' in componentType:
                    RamTableQueryDeviceID = componentType
                    RamTableQuerySubSystem = componentSubType
                    
                    if componentSubType == 'Mooring line' or componentSubType == 'Foundation': 
                        RamTableQuerySubSystem = 'M&F sub-system mooring foundation'
                        
                    if componentSubType == 'Dynamic cable': 
                        RamTableQuerySubSystem = 'M&F sub-system dynamic cable'  
                        
                elif 'subhub' in componentType:
                    RamTableQueryDeviceID = componentType

                else:
                    #RamTableQueryDeviceID  = 'device' + componentType[len(componentType)-3:len(componentType)]
                    RamTableQueryDeviceID  = 'Array'
                    RamTableQuerySubSystem = componentType[0:-3]                        
                                                                
                if 'subhub' in componentType:
                    dummyRamTable = self.__ramTable.loc[(self.__ramTable['deviceID'] == RamTableQueryDeviceID)]
                    
                else:
                    dummyRamTable = self.__ramTable.loc[(self.__ramTable['deviceID'] == RamTableQueryDeviceID) & (self.__ramTable['subSystem'] == RamTableQuerySubSystem)]
                                
                if len(0 < dummyRamTable):
                    dummyRamTable.reset_index(drop=True, inplace=True)
                    
                    if 'subhub' in componentType:
                        arrayDict[componentID]['FR'] = dummyRamTable.failureRate[0] + dummyRamTable.failureRate[1]
                    else:
                        arrayDict[componentID]['FR'] = dummyRamTable.failureRate[0]
                    
                    # M&F -> 50% Mooring and 50% foundation 
                    if componentSubType == 'Mooring line' or componentSubType == 'Foundation' or componentSubType == 'Dynamic cable': 
                        arrayDict[componentID]['FR'] = arrayDict[componentID]['FR'] * 0.5
 
                else:
                    # failure rate will be read from component table
                    arrayDict[componentID]['FR'] = component[componentID]['failure_rate'] 
                    if self.__dtocean_maintenance_PRINT_FLAG == True:
                        print 'WP6: The failure rate of ' + componentID + ' can not be read from dtocean-reliability. Therefore the failure rate is read from component table of dtocean-operations'
                                                                       
            else:
                # failure rate will be read from component table
                arrayDict[componentID]['FR'] = component[componentID]['failure_rate'] 
                       
            arrayDict[componentID]['FR List']   = []
                                 
            if 'Hydrodynamic' in componentID or 'Pto' in componentID or 'Control' in componentID or \
            'Support structure' in componentID or 'Mooring line' in componentID or \
            'Foundation' in componentID or 'Dynamic cable' in componentID or 'Array elec sub-system' in componentID:                
                                                
                deviceID = component[column]['Component_type']                
                logic = deviceID in arrayDict.keys()
                
                if not logic:
                    loop = int(deviceID.rsplit('device')[1])-1
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
                    arrayDict[deviceID]['CaBaMaNoWeatherWindow'] = False  

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
                    arrayDict[deviceID]['AnnualEnergyWP2'] = annual_Energy_Production_perD[loop]
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
                arrayDict[componentID]['CaBaMaNoWeatherWindow'] = False
                arrayDict[componentID]['CoBaMaNoWeatherWindow'] = False
                                             
            
            for iCnt1 in range(0,component[componentID]['number_failure_modes']):

                arrayDict[componentID]['CoBaMa_initOpEventsList'].append([]) 
                arrayDict[componentID]['CoBaMa_FR List'].append(0)
                    
                # Failure rate from RAM or database 
                strDummy = componentID + '_' + str(iCnt1+1)
                
                if iCnt1 == 0:
                    
                    # failure rate will be read from component table
                    if 'device' in componentType:
                        RamTableQueryDeviceID  = componentType
                        RamTableQuerySubSystem = componentSubType
                        
                        if componentSubType == 'Mooring line' or componentSubType == 'Foundation': 
                            RamTableQuerySubSystem = 'M&F sub-system mooring foundation'
                            
                        if componentSubType == 'Dynamic cable': 
                            RamTableQuerySubSystem = 'M&F sub-system dynamic cable'
                            
                    elif 'subhub' in componentType:
                            RamTableQueryDeviceID = componentType
                        
                    else:
                        #RamTableQueryDeviceID  = 'device' + componentType[len(componentType)-3:len(componentType)]
                        RamTableQueryDeviceID  = 'Array'
                        RamTableQuerySubSystem = componentType[0:-3]                        
                                                                    
                    if 'subhub' in componentType:
                        dummyRamTable = self.__ramTable.loc[(self.__ramTable['deviceID'] == RamTableQueryDeviceID)]
                        
                    else:
                        dummyRamTable = self.__ramTable.loc[(self.__ramTable['deviceID'] == RamTableQueryDeviceID) & (self.__ramTable['subSystem'] == RamTableQuerySubSystem)]
                                 
                    if len(0 < dummyRamTable):
                        dummyRamTable.reset_index(drop=True, inplace=True)
                        arrayDict[componentID]['Breakdown'].append(dummyRamTable.breakDown[0]) 
                        
                        if type(arrayDict[componentID]['Breakdown'][0]) == list and 0 < len(arrayDict[componentID]['Breakdown'][0]) and 'Array elec sub-system' in componentID:
                            dummyList = []
                            for iCnt2 in range(0,len(arrayDict[componentID]['Breakdown'][0])):
                                dummyList.append(arrayDict[componentID]['Breakdown'][0][iCnt2])
                            arrayDict[componentID]['Breakdown'] = dummyList
                                             
                    else:
                        
                       if 'Substation' in componentID or 'Export Cable' in componentID:
                           arrayDict[componentID]['Breakdown'].append('All')
                           
                       else:
                           if 'device' in componentType:
                               arrayDict[componentID]['Breakdown'].append(componentType)
    

                       if self.__dtocean_maintenance_PRINT_FLAG == True:                            
                           print 'WP6: The impact of ' + componentID + ' of devices can not be analysed from dtocean-reliability.'

                            
                    if 'subhub' in componentType:
                        arrayDict[componentID]['Breakdown'] = arrayDict[componentID]['Breakdown'][0] 
    
             
                failureRate = arrayDict[componentID]['FR']  * failureMode[strDummy]['mode_probability']/100.0     
                arrayDict[componentID]['FR List'].append(failureRate)
                                
                # for checking purposes
                failureEventsListNoPoisson.append(self.__startOperationDate)
                repairActionEventsListNoPoisson.append(self.__startOperationDate)                   
                indexFMListNoPoisson.append(iCnt1+1)                      
                componentTypeListNoPoisson.append(componentType)  
                componentSubTypeListNoPoisson.append(componentSubType)  
                componentIDListNoPoisson.append(componentID) 
                FM_IDListNoPoisson.append(failureMode[strDummy]['FM_ID'])
                RA_IDListNoPoisson.append(self.__FM_ID_RA_ID[failureMode[strDummy]['FM_ID']])
               
                if 'Hydrodynamic' in componentID or 'Pto' in componentID or 'Control' in componentID or \
                'Support structure' in componentID or 'Mooring line' in componentID or \
                'Foundation' in componentID or 'Dynamic cable' in componentID or 'Array elec sub-system' in componentID:                     
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
                                        
                    if 'Hydrodynamic' in componentID or 'Pto' in componentID or 'Control' in componentID or \
                    'Support structure' in componentID or 'Mooring line' in componentID or \
                    'Foundation' in componentID or 'Dynamic cable' in componentID or 'Array elec sub-system' in componentID: 
                           
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
                    RA_IDList.append(self.__FM_ID_RA_ID[failureMode[strDummy]['FM_ID']])
       
       # self.__eventsTableKeys  = ['failureRate', 'repairActionEvents', 'failureEvents', 'belongsTo', 'ComponentType', 'ComponentSubType', 'ComponentID', 'FM_ID', 'indexFM', 'RA_ID']
        data = {self.__eventsTableKeys[0]:failureRateList,
                self.__eventsTableKeys[1]:repairActionEventsList, 
                self.__eventsTableKeys[2]:failureEventsList, 
                self.__eventsTableKeys[3]:belongsToList, 
                self.__eventsTableKeys[4]:componentTypeList, 
                self.__eventsTableKeys[5]:componentSubTypeList,
                self.__eventsTableKeys[6]:componentIDList,
                self.__eventsTableKeys[7]:FM_IDList, 
                self.__eventsTableKeys[8]:indexFMList, 
                self.__eventsTableKeys[9]:RA_IDList}  
       
        eventsTable = pd.DataFrame(data)       

        # sort of eventsTable
        eventsTable.sort(columns=self.__eventsTableKeys[1], inplace=True)      
        
        # start index with 0
        eventsTable.reset_index(drop=True, inplace=True)
        
                
        # ['repairActionEvents', 'failureEvents', 'belongsTo', 'ComponentType', 'ComponentSubType', 'ComponentID', 'FM_ID', 'indexFM', 'RA_ID', 'Alarm', 'failureRate']
        data1 = {self.__NoPoisson_eventsTableKeys[0]:repairActionEventsListNoPoisson, 
                 self.__NoPoisson_eventsTableKeys[1]:failureEventsListNoPoisson, 
                 self.__NoPoisson_eventsTableKeys[2]:belongsToListNoPoisson, 
                 self.__NoPoisson_eventsTableKeys[3]:componentTypeListNoPoisson, 
                 self.__NoPoisson_eventsTableKeys[4]:componentSubTypeListNoPoisson,
                 self.__NoPoisson_eventsTableKeys[5]:componentIDListNoPoisson,
                 self.__NoPoisson_eventsTableKeys[6]:FM_IDListNoPoisson, 
                 self.__NoPoisson_eventsTableKeys[7]:indexFMListNoPoisson, 
                 self.__NoPoisson_eventsTableKeys[8]:RA_IDListNoPoisson,
                 self.__NoPoisson_eventsTableKeys[9]:failureRateListNoPoisson,
                 self.__NoPoisson_eventsTableKeys[10]:AlarmListNoPoisson
                }  
       
        eventsTableNoPoisson = pd.DataFrame(data1)       

        # sort of eventsTable
        eventsTableNoPoisson.sort(columns=self.__eventsTableKeys[5], inplace=True)      
        
        # start index with 0
        eventsTableNoPoisson.reset_index(drop=True, inplace=True)
        
        return arrayDict, eventsTable, eventsTableNoPoisson 

    def __calcPoissonEvents(self, failureRate):
             
        '''calcPoissonEvents function: Calls the poisson process function
                                                      
        Args:              
            failureRate (float) : Failure rate of component 
        
        Attributes:         
            no attributes                      

        Returns:
            no returns 
      
        '''        
        returnValue = poissonProcess(self.__startOperationDate, self.__simulationTimeDay, failureRate/self.__yearDays)
        
        if type(returnValue) == list and 1 <= len(returnValue):
            self.__Poisson = returnValue            
            
        else:
            self.__Poisson = []
   
    def __readFromRAM(self):
        
        '''readFromRAM function: Read the necessary information from RAM.
                                                      
        Args:              
            no arguments 
        
        Attributes:         
            no attributes                      

        Returns:
            no returns 
      
        '''                
        
        ramDeviceIDList    = []
        ramSubSystemList   = []
        ramFailureRateList = []
        ramBreakDownList   = []
    
        # read the failure rates from self.__rsubsysvalues
        for iCnt in range(0,len(self.__rsubsysvalues)):
                        
            if ('Substation' in self.__rsubsysvalues[iCnt][0][1] or 'Export Cable' in self.__rsubsysvalues[iCnt][0][1]) and \
            'array' in self.__rsubsysvalues[iCnt][0][2]:
                ramFailureRateList.append(self.__rsubsysvalues[iCnt][0][-1])                
                ramSubSystemList.append(self.__rsubsysvalues[iCnt][0][1])
                ramDeviceIDList.append('Array')                                               
                ramBreakDownList.append('All')
                                
            else:
                
                if  self.__eleclayout == 'radial' or self.__eleclayout == 'singlesidedstring' or self.__eleclayout == 'doublesidedstring':  

                    if 'device' in self.__rsubsysvalues[iCnt][0][0][2]:
                                              
                        for iCnt1 in range(0,len(self.__rsubsysvalues[iCnt])):  # Number of devices   
                            flagMFSubSystem = False                 
                            for iCnt2 in range(0,len(self.__rsubsysvalues[iCnt][iCnt1])): # Number of subsystems
                                
                                dummyStr = self.__rsubsysvalues[iCnt][iCnt1][iCnt2][1]
                                
                                # E-Mail of Sam
                                #  the first one is for the mooring/Foundation (mooring line/anchor)  
                                if 'M&F sub-system' in dummyStr and flagMFSubSystem == False:
                                    dummyStr = dummyStr + ' mooring foundation'
                                
                                #  The second one is for the the umbilical cable 
                                if 'M&F sub-system' in dummyStr and flagMFSubSystem == True:
                                    dummyStr = dummyStr + ' dynamic cable'
                                    
                                if 'M&F sub-system' in dummyStr and flagMFSubSystem == False:                            
                                    flagMFSubSystem = True                            
                             
                                ramSubSystemList.append(dummyStr)
                                ramDeviceIDList.append(self.__rsubsysvalues[iCnt][iCnt1][iCnt2][2])                          
                                 
                                # In case of 'singlesidedstring' or 'doublesidedstring' failure rate is a list
                                dummyList = self.__rsubsysvalues[iCnt][iCnt1][iCnt2][4]
                                if type(dummyList) == list and self.__rsubsysvalues[iCnt][iCnt1][iCnt2][1] == 'Array elec sub-system': 
                                    ramFailureRateList.append(self.__rsubsysvalues[iCnt][iCnt1][iCnt2][4][1])
                                else: 
                                    ramFailureRateList.append(self.__rsubsysvalues[iCnt][iCnt1][iCnt2][4])
                                
                                # else part below
                                #ramBreakDownList.append(self.__rsubsysvalues[iCnt][iCnt1][iCnt2][2])                                
                                if 'Array elec sub-system' in self.__rsubsysvalues[iCnt][iCnt1][iCnt2][1]:
                                    # radial, singlesidedstring, doublesidedstring, multiplehubs
                                    dummyList = []
                                    if self.__eleclayout == 'radial' or self.__eleclayout == 'multiplehubs':
                                        for iCnt3 in range(0,iCnt1+1):  
                                            dummyList.append(self.__rsubsysvalues[iCnt][iCnt3][iCnt2][2])
                                        ramBreakDownList.append(dummyList)                                                                  
                                                                                                       
                                    if self.__eleclayout == 'singlesidedstring' or self.__eleclayout == 'doublesidedstring':
                                        #ramBreakDownList.append(self.__rsubsysvalues[iCnt][iCnt1][iCnt2][2])
                                        ramBreakDownList.append('-') 
                                
                                else:
                                    ramBreakDownList.append(self.__rsubsysvalues[iCnt][iCnt1][iCnt2][2]) 
                                                    
                if  self.__eleclayout == 'multiplehubs':
                    
                    if 'subhub' in self.__rsubsysvalues[iCnt][1][0][0][2]:
                        
                        for iCnt1 in range(0,len(self.__rsubsysvalues[iCnt][1])):  # loop over subhubs
                                       
                            if ('Substation' in self.__rsubsysvalues[iCnt][1][iCnt1][0][1] or 'Elec sub-system' in self.__rsubsysvalues[iCnt][1][iCnt1][0][1]):
                                ramFailureRateList.append(self.__rsubsysvalues[iCnt][1][iCnt1][0][-1])                
                                ramSubSystemList.append(self.__rsubsysvalues[iCnt][1][iCnt1][0][1])
                                ramDeviceIDList.append(self.__rsubsysvalues[iCnt][1][iCnt1][0][2])
                                
                                # Which devices are conntected to the sub Hub
                                dummyList = []                                
                                for ii1 in range(0,len(self.__rsubsysvalues[iCnt][1])):  # loop over subhubs 
                                    
                                    if 'device' in self.__rsubsysvalues[iCnt][1][ii1][0][0][2]:                                
                                        for ii2 in range(0,len(self.__rsubsysvalues[iCnt][1][ii1])):  # Number of devices                                                                                         
                                            dummyList.append(self.__rsubsysvalues[iCnt][1][ii1][ii2][0][2]) 
                            
                                ramBreakDownList.append(dummyList) 
                                                                      
                            else:                                    
                                for iCnt2 in range(0,len(self.__rsubsysvalues[iCnt][1][iCnt1])):  # Number of devices 
                                     
                                    flagMFSubSystem = False  
                                    
                                    for iCnt3 in range(0,len(self.__rsubsysvalues[iCnt][1][iCnt1][0])):  # Number of subsystems
                                            
                                        dummyStr = self.__rsubsysvalues[iCnt][1][iCnt1][iCnt2][iCnt3][1]
                                        
                                        # E-Mail of Sam
                                        #  the first one is for the mooring/Foundation  
                                        if 'M&F sub-system' in dummyStr and flagMFSubSystem == False:
                                            dummyStr = dummyStr + ' mooring foundation'
                                        
                                        #  The second one is for the the umbilical cable 
                                        if 'M&F sub-system' in dummyStr and flagMFSubSystem == True:
                                            dummyStr = dummyStr + ' dynamic cable'
                                            
                                        if 'M&F sub-system' in dummyStr and flagMFSubSystem == False:                            
                                            flagMFSubSystem = True                            
                                     
                                        ramSubSystemList.append(dummyStr)
                                        ramDeviceIDList.append(self.__rsubsysvalues[iCnt][1][iCnt1][iCnt2][iCnt3][2])                                        
                                        ramFailureRateList.append(self.__rsubsysvalues[iCnt][1][iCnt1][iCnt2][iCnt3][4])
                                        
                                        
                                        # else part below                                        
                                        #ramBreakDownList.append(self.__rsubsysvalues[iCnt][1][iCnt1][iCnt2][iCnt3][2])
                                        if 'Array elec sub-system' in dummyStr:                                            
                                            dummyList = []                                            
                                            for ii1 in range(0,iCnt2+1):  
                                                dummyList.append(self.__rsubsysvalues[iCnt][1][iCnt1][ii1][0][2])
                                            ramBreakDownList.append(dummyList)                                                                                                                                                                                
                                        
                                        else:
                                            ramBreakDownList.append(self.__rsubsysvalues[iCnt][1][iCnt1][iCnt2][iCnt3][2])                                          
                                                                                                            
        
        # [1/hour] -> [1/year]
        for iCnt in range(0,len(ramFailureRateList)):
            ramFailureRateList[iCnt] = ramFailureRateList[iCnt]* self.__dayHours*self.__yearDays
            
            
        ramData = {self.__ramTableKeys[0]:ramDeviceIDList, 
                   self.__ramTableKeys[1]:ramSubSystemList, 
                   self.__ramTableKeys[2]:ramFailureRateList, 
                   self.__ramTableKeys[3]:ramBreakDownList} 
                
        self.__ramTable = pd.DataFrame(ramData)  
       
        return