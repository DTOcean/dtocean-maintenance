# -*- coding: utf-8 -*-
"""This module contains the main class of dtocean-operations-and-maintenance
   for the calculation of LCOE

.. module:: LCOE_Calculator
   :platform: Windows
   :synopsis: LCOE calculation computational code for dtocean-operations-and-maintenance
   
.. moduleauthor:: Bahram Panahandeh <bahram.panahandeh@iwes.fraunhofer.de>
"""

               
 
# Set up logging
import logging
module_logger = logging.getLogger(__name__)

# Internal module import
from arrayClass import array
import math

import datetime
from datetime import timedelta

# Internal module import
from staticMethods import poissonProcess

# Internal module import for WP5
import sys
sys.path.append('..')
import string

import copy
import timeit

from dtocean_logistics.phases.om import logPhase_om_init
from dtocean_logistics.phases.om.select_logPhase import logPhase_select
from dtocean_logistics.feasibility.feasability_om import feas_om
from dtocean_logistics.selection.select_ve import select_e, select_v
from dtocean_logistics.selection.match import compatibility_ve
#from dtocean_logistics.performance.optim_sol import opt_sol
#from dtocean_logistics.performance.schedule.schedule_om import sched_om
#from dtocean_logistics.performance.economic.eco import cost
from dtocean_logistics.load.safe_factors import safety_factors
#from output_processing import out_process
from dtocean_logistics.phases import select_port_OM
from dtocean_logistics.phases.operations import logOp_init
from LOGISTICS_main import om_logistics_main

from dtocean_reliability.main import Variables, Main

# External module import
import numpy as np
import pandas as pd

class LCOE_Calculator(object):
    
    '''Cost calculation class of dtocean-operations-and-maintenance.
    
    Args:
      inputOMPtr (class)            : Pointer of class inputOM
    
    Attributes:
      self.__outputsOfWP6 (dict)                : Dictionary which contains the outputs of WP6 
      self.__wp6_outputsForLogistic (dict)   : Dictionary which contains the outputs of WP6 for WP5 
      Farm_OM (dict): This parameter records the O&M general information for the farm as whole
             keys:
                wage_specialist_day (float) [Euro/h]:    Wage for specialists crew at daytime e.g. diver
                wage_specialist_night (float) [Euro/h]:  Wage for specialists crew at night time e.g. diver
                wage_technician_day (float) [Euro/h]:    Wage for technicians at daytime
                wage_technician_night (float) [Euro/h]:  Wage for technicians at night time
                duration_shift (int) [h]:                Duration of a shift
                number_shifts_per_day (int) [-]:         Number of shifts per day
                workdays_summer (int) [-]:               Working Days per Week during summer
                workdays_winter (int) [-]:               Working Days per Week during winter
                number_crews_per_shift (int) [-]:        Number of crews per shift
                number_crews_available (int) [-]:        Number of available crews
                corrective_maintenance (bool) [-]:       User input if one wants to consider corrective maintenance
                condition_based_maintenance (bool) [-]:  User input if one wants to consider condition based maintenance
                calendar_based_maintenance (bool) [-]:   User input if one wants to consider calendar based maintenance
                number_components (int) [-]:             Number of components which should be considered in O&M.
                energy_selling_price (float) [Euro/kWh]: Energy selling price
                                            
	    Component (Pandas DataFrame): This table stores information related to the components. A component is any physical object required during the operation of the farm.
                                        Please note that each defined component will be a column in Pandas DataFrame table “Component”
             keys:
                failure_rate (float) [1/year]:                         Failure rate of the component
                number_failure_modes (int) [-]:                        Number of failure modes for this component
                start_date_calendar_based_maintenance (datetime) [-]:  Start date of calendar-based maintenance for each year
                end_date_calendar_based_maintenance	 (datetime)	[-]:    End date of calendar-based maintenance for each year
                interval_calendar_based_maintenance	int (year) [-]:    Interval of calendar-based maintenance
                start_date_condition_based_maintenance (datetime) [-]: Start date of condition-based maintenance for each year
                end_date_condition_based_maintenance (datetime) [-]:   End date of condition-based maintenance
                soh_function	(float) [-]:                              This parameter belongs to condition based strategy and is not yet fully defined.
                soh_threshold (float) [-]:	                         This parameter belongs to condition based strategy and is not yet fully defined
                is_floating	(bool) [-]:                               Component is floating and can be towed to port
                
	    Failure_Mode (Pandas DataFrame): This table stores information related to the failure modes of components
                                           Please note that each defined failure mode will be a column in Pandas DataFrame table “Failure_Mode”
             keys:
                Component (int) [-]:              This parameter is only an additional parameter for mapping between “Failure_Mode” table and “Component” table
                mode_probability (float) [%]:     Probability of occurrence of each failure modes
                spare_mass (float) [kg]:          Mass of the spare parts
                spare_height	 (float)	[m]:      Height of the spare parts
                spare_width	int (float) [m]:     Width of the spare parts
                spare_length (float) [m]:         Length of the spare parts
                cost_spare (float) [Euro]:        Cost of the spare parts
                cost_spare_transit	(float) [Euro]: Cost of the transport of the spare parts
                cost_spare_loading	(float) [Euro]: Cost of the loading of the spare parts
                lead_time_spare	(bool) [days]:  Lead time for the spare parts

	    Repair_Action (Pandas DataFrame): This table stores information related to the repair actions required for each failure modes
                                            Please note that each defined repair action will be a column in Pandas DataFrame table “Repair_Action”:
             keys:                    
                failure_mode_id (int) [-]:           This parameter is only an additional parameter for mapping between “Failure_Mode” table and “Repair_Action” table
                duration_maintenance (float) [h]:    Duration of time required on site for maintenance
                duration_accessibility (float) [h]:  Duration of time required on site to access the component or sub-systems to be repaired or replaced
                interruptable (bool) [-]:            Is the failure mode type interruptable or not
                delay_crew (float) [h]:              duration of time before the crew is ready
                delay_organisation (float) [h]:      duration of time before anything else is ready
                delay_spare	(float) [h]:            duration of time before the spare parts are ready
                number_technicians (int) [-]:        Number of technicians required to do the O&M
                number_specialists (int) [-]:        Number of specialists required to do the O&M
                wave_height_max_acc (float) [m]:     wave height max for operational limit conditions during the accessibility
                wave_periode_max_acc (float) [s]:    wave period max for operational limit conditions during the accessibility
                wind_speed_max_acc (float) [m/s]:	  wind speed max for operational limit conditions during the accessibility
                current_speed_max_acc (float) [m/s]: current speed max for operational limit conditions during the accessibility
                wave_height_max_om (float) [m]:      wave height max for operational limit conditions during the maintenance action
                wave_periode_max_om (float) [s]:     wave period max for operational limit conditions during the maintenance action
                wind_speed_max_om	 (float) [m/s]:    wind speed max for operational limit conditions during the maintenance action
                current_speed_max_om (float) [m/s]:  current speed max for operational limit conditions during the maintenance action
                requires_lifiting	 (bool) [-]:       Is lifting required?
                requires_divers (bool) [-]:          Are divers required?
                requires_towing (bool) [-]:          Is towing required?

	    Inspection (Pandas DataFrame): This table stores information related to the inspections required for each failure modes
                                            Please note that each defined inspection will be a column in Pandas DataFrame table “Repair_Action”:
             keys:                    
                failure_mode_id (int) [-]:           This parameter is only an additional parameter for mapping between “Failure_Mode” table and “Inspection” table
                duration_inspection (float) [h]:     Duration of time required on site for inspection
                duration_accessibility (float) [h]:  Duration of time required on site to access the component or sub-systems to be repaired or replaced
                delay_crew (float) [h]:              duration of time before the crew is ready
                delay_organisation (float) [h]:      duration of time before anything else is ready             
                number_technicians (int) [-]:        Number of technicians required to do the O&M
                number_specialists (int) [-]:        Number of specialists required to do the O&M
                wave_height_max_acc (float) [m]:     Wave height max for operational limit conditions during the accessibility
                wave_periode_max_acc (float) [s]:    Wave period max for operational limit conditions during the accessibility
                wind_speed_max_acc (float) [m/s]:	  Wind speed max for operational limit conditions during the accessibility
                current_speed_max_acc (float) [m/s]: Current speed max for operational limit conditions during the accessibility
                wave_height_max_om (float) [m]:      Wave height max for operational limit conditions during the maintenance action
                wave_periode_max_om (float) [s]:     Wave period max for operational limit conditions during the maintenance action
                wind_speed_max_om	 (float) [m/s]:    Wind speed max for operational limit conditions during the maintenance action
                current_speed_max_om (float) [m/s]:  Current speed max for operational limit conditions during the maintenance action
                requires_lifiting	 (bool) [-]:       Is lifting required?
                requires_divers (bool) [-]:          Are divers required?
                         
                
	    RAM_Param (dict): This parameter records the information for talking to RAM module
             keys:
                severitylevel (str) [-]:             Level of severity
                calcscenario (str) [-]:              scenario for the calculation
                systype (str) [-]:                   Type of system
                eleclayout (str) [-]:                Electrical layout architecture
                
	    Logistic_Param (dict): This parameter records the information for talking to logistic module
             keys:
                elementType (list(str)) [-]:                        Element type list includes all array sub-component: device; mooring line; foundation; static power cable; umbilical; collection point
                elementSubtype (list(str)) [-]:                     Element sub-type is only required when the element type is device. It corresponds to one of the four sub-systems of the device, 
                                                                    i.e: hydrodynamic; pto; control; support structure
                elementID (list(str)) [-]:                          ID number of the element unedr consideration should match with those defined in WP1, WP2, WP3 & WP4 
                waterDepth (dict (dict (float))) [m]:               Water depth of the element: Diving operations are limited to 30 meters water depth. Zero shoudl be indicated for surface/topside element inerventions 
                utm (dict (dict (list (float float int)))) [m m -]: UTM grid coordinate position of the element that require na O&M intervention
                                                         
 	    Simu_Param (dict): This parameter records the general information concerning the simulation
             keys:
                startOperationDate (datetime) [-]:                  Date of simulation start
                missionTime (float) [year]:                         Simulation time
                power_prod_perD_perS (numpy.ndarray) [W]:           Mean power production per device per state. The dimension of the array is Nbodies x Nstate (WP2)
                annual_Energy_Production_perD (numpy.ndarray) [Wh]: Annual energy production of each device on the array. The dimension of the array is Nbodies x 1 (WP2)
                power_prod_perD (numpy.ndarray) [W]:                Mean power production per device. The dimension of the array is Nbodies x 1 (WP2)
                array_layout (dict) [-]:                            The dictionary has a variable number of keys, equal to the number of devices in the array. The keys are built in the following way: 
                                                                    'DeviceID', where the ID is the identification number of the device. Each key is associated with a tuple, where the x and y coordinates are given  (WP2)
                nbodies (float) [-]:                                Mean power production per device. The dimension of the array is Nbodies x 1 (WP2)
                
	    Control_Param (dict): This parameter records the O&M module control from GUI (to be extended in future)
             keys:
                whichOptim (list) [bool]:                           Which O&M should be optimised [Unplanned corrective maintenance, Condition based maintenance, Calendar based maintenance]           
          
      self.__om_logistic (dict)                         : Output of WP5
      self.__inputsFromCore (list)                      : Dummy for the communication with core                  
      self.__inputOMPTR (class)                         : Instance pointer of inputOM     
      self.__arrayDict (dict)                           : Dictionary for saving of the array parameters
      self.__arrayPTR (class)                           : This variable will be used for saving of array instance.
      self.__ramPTR (class)                             : This variable will be used for saving of WP4_RAM instance.    
      self.__rsubsysvalues (list)                       : list rsubsysvalues from RAM 
      self.__eleclayout (string)                        : Electrical layout architecture     
      self.__startOperationDate (datetime)              : Start of operation date 
      self.__powerOfDevices (list)                      : Power of devices [W]       
      self.__annual_Energy_Production_perD (list)       : Annual energy production per device 
      self.__NrOfDevices (int)                          : Number of devices 
      self.__NrOfTurnOutDevices (int)                   : Number of turn out devices     
      self.__operationTimeYear (float)                  : Opration time in years
      self.__operationTimeDay (float)                   : Operation time in days 
      self.__endOperationDate (datetime)                : End of array operation 
      self.__nrOfMainComponents (int)                   : Number of main components to be considered in O&M [-]
      self.__nrOfFmOfEachComponent (int)                : Number of failure modes of each defined main components [-]
      self.__UnCoMa_eventsTable (panda dataframe)       : Table of failure events [-]
      self.__UnCoMa_outputEventsTable (panda dataframe) : Table of failure events for output [-]
      self.__eventsTableNoPoisson (panda dataframe)     : Table of failure events [-]      
    '''   
     
    def __init__(self, inputOMPTR):
        
        '''__init__ function: Saves the arguments in internal variabels.
                                                      
        Args:           
            inputOMPTR (class) : pointer of inputOM class
        
        Attributes:                            
            self.__inputOMPTR (class) : pointer of inputOM class            
            self.__Farm_OM (dict): This parameter records the O&M general information for the farm as whole
            keys:
                calendar_based_maintenance (bool) [-]   : User input if one wants to consider calendar based maintenance
                condition_based_maintenance (bool) [-]  : User input if one wants to consider condition based maintenance                             
                corrective_maintenance (bool) [-]       : User input if one wants to consider corrective maintenance
                duration_shift (int) [h]                : Duration of a shift
                helideck (str or bool -> logistic) [-]  : If there is helideck available or not?    
                number_crews_available (int) [-]        : Number of available crews
                number_crews_per_shift (int) [-]        : Number of crews per shift
                number_shifts_per_day (int) [-]         : Number of shifts per day                           
                wage_specialist_day (float) [Euro/h]    : Wage for specialists crew at daytime e.g. diver
                wage_specialist_night (float) [Euro/h]  : Wage for specialists crew at night time e.g. diver
                wage_technician_day (float) [Euro/h]    : Wage for technicians at daytime
                wage_technician_night (float) [Euro/h]  : Wage for technicians at night time                
                workdays_summer (int) [-]               : Working Days per Week during summer
                workdays_winter (int) [-]               : Working Days per Week during winter
                energy_selling_price (float) [Euro/kWh] : Energy selling price
                                
            self.__Component (Pandas DataFrame): This table stores information related to the components. A component is any physical object required during the operation of the farm.
            Please note that each defined component will be a column in Pandas DataFrame table “Component”
                keys:
                    component_id (str) [-]                                : Id of components   
                    component_type (str) [-]                              : Type of components
                    component_subtype: (str) [-]                          : sub type of components  
                    failure_rate (float) [1/year]                         : Failure rate of the components
                    number_failure_modes (int) [-]                        : Number of failure modes for this component
                    start_date_calendar_based_maintenance (datetime) [-]  : Start date of calendar-based maintenance for each year
                    end_date_calendar_based_maintenance	 (datetime)	[-]  : End date of calendar-based maintenance for each year
                    interval_calendar_based_maintenance	int (year) [-]   : Interval of calendar-based maintenance
                    start_date_condition_based_maintenance (datetime) [-] : Start date of condition-based maintenance for each year
                    end_date_condition_based_maintenance (datetime) [-]   : End date of condition-based maintenance
                    soh_threshold (float) [-]                             : This parameter belongs to condition based strategy
                    is_floating	(bool) [-]                              : Component is floating and can be towed to port
                    
            self.__Failure_Mode (Pandas DataFrame): This table stores information related to the failure modes of components
            Please note that each defined failure mode will be a column in Pandas DataFrame table “Failure_Mode”
                keys:
                    component_id (str) [-]             : Id of component
                    fm_id (str) [-]                    : Id of failure mode 
                    mode_probability (float) [%]       : Probability of occurrence of each failure modes
                    spare_mass (float) [kg]            : Mass of the spare parts
                    spare_height	 (float)	[m]      : Height of the spare parts
                    spare_width	int (float) [m]      : Width of the spare parts
                    spare_length (float) [m]           : Length of the spare parts
                    cost_spare (float) [Euro]          : Cost of the spare parts
                    cost_spare_transit	(float) [Euro] : Cost of the transport of the spare parts
                    cost_spare_loading	(float) [Euro] : Cost of the loading of the spare parts
                    lead_time_spare	(bool) [days]  : Lead time for the spare parts
            
            self.__Repair_Action (Pandas DataFrame): This table stores information related to the repair actions required for each failure modes
            Please note that each defined repair action will be a column in Pandas DataFrame table “Repair_Action”:
                keys:
                    component_id (str) [-]              : Id of component
                    fm_id (str) [-]                     : Id of failure mode                 
                    duration_maintenance (float) [h]    : Duration of time required on site for maintenance
                    duration_accessibility (float) [h]  : Duration of time required on site to access the component or sub-systems to be repaired or replaced
                    interruptable (bool) [-]            : Is the failure mode type interruptable or not                              
                    delay_crew (float) [h]              : duration of time before the crew is ready
                    delay_organisation (float) [h]      : duration of time before anything else is ready
                    delay_spare	(float) [h]           : duration of time before the spare parts are ready
                    number_technicians (int) [-]        : Number of technicians required to do the O&M
                    number_specialists (int) [-]        : Number of specialists required to do the O&M
                    wave_height_max_acc (float) [m]     : wave height max for operational limit conditions during the accessibility
                    wave_periode_max_acc (float) [s]    : wave period max for operational limit conditions during the accessibility
                    wind_speed_max_acc (float) [m/s]    : wind speed max for operational limit conditions during the accessibility
                    current_speed_max_acc (float) [m/s] : current speed max for operational limit conditions during the accessibility                
                    wave_height_max_om (float) [m]      : wave height max for operational limit conditions during the maintenance action
                    wave_periode_max_om (float) [s]     : wave period max for operational limit conditions during the maintenance action
                    wind_speed_max_om	 (float) [m/s]  : wind speed max for operational limit conditions during the maintenance action
                    current_speed_max_om (float) [m/s]  : current speed max for operational limit conditions during the maintenance action               
                    requires_lifiting	 (bool) [-]     : Is lifting required?
                    requires_divers (bool) [-]          : Are divers required?
                    requires_towing (bool) [-]          : Is towing required?
                            
            self.__Inspection (Pandas DataFrame): This table stores information related to the inspections required for each failure modes
            Please note that each defined inspection will be a column in Pandas DataFrame table “Repair_Action”:
                keys:                    
                    component_id (str) [-]              : Id of component
                    fm_id (str) [-]                     : Id of failure mode        
                    duration_inspection (float) [h]     : Duration of time required on site for inspection
                    duration_accessibility (float) [h]  : Duration of time required on site to access the component or sub-systems to be repaired or replaced
                    delay_crew (float) [h]              : duration of time before the crew is ready
                    delay_organisation (float) [h]      : duration of time before anything else is ready             
                    number_technicians (int) [-]        : Number of technicians required to do the O&M
                    number_specialists (int) [-]        : Number of specialists required to do the O&M
                    wave_height_max_acc (float) [m]     : Wave height max for operational limit conditions during the accessibility
                    wave_periode_max_acc (float) [s]    : Wave period max for operational limit conditions during the accessibility
                    wind_speed_max_acc (float) [m/s]    : Wind speed max for operational limit conditions during the accessibility
                    current_speed_max_acc (float) [m/s] : Current speed max for operational limit conditions during the accessibility
                    wave_height_max_om (float) [m]      : Wave height max for operational limit conditions during the maintenance action
                    wave_periode_max_om (float) [s]     : Wave period max for operational limit conditions during the maintenance action
                    wind_speed_max_om	 (float) [m/s]  : Wind speed max for operational limit conditions during the maintenance action
                    current_speed_max_om (float) [m/s]  : Current speed max for operational limit conditions during the maintenance action
                    requires_lifiting	 (bool) [-]     : Is lifting required?
                    requires_divers (bool) [-]          : Are divers required?
                         
                
            self.__RAM_Param (dict): This parameter records the information for talking to RAM module
                keys:          
                    calcscenario (str) [-]  : scenario for the calculation
                    eleclayout (str) [-]    : Electrical layout architecture
                    pointer (class) [-]     : pointer of dtocean-reliability class
                    severitylevel (str) [-] : Level of severity                
                    systype (str) [-]       : Type of system
                
            self.__Logistic_Param (dict): This parameter records the information for talking to logistic module
                keys:
                    cable_route (DataFrame)         : logistic parameter
                    collection_point (DataFrame)    : logistic parameter
                    connerctors (DataFrame)         : logistic parameter
                    device (DataFrame)              : logistic parameter
                    dynamic_cable (DataFrame)       : logistic parameter
                    equipments (dict)               : logistic parameter
                    external_protection (DataFrame) : logistic parameter
                    foundation (DataFrame)          : logistic parameter
                    landfall (DataFrame)            : logistic parameter
                    laying_rates (DataFrame)        : logistic parameter
                    layout (DataFrame)              : logistic parameter
                    lease_area (list)               : logistic parameter
                    line (DataFrame)                : logistic parameter
                    metocean (DataFrame)            : logistic parameter
                    other_rates (DataFrame)         : logistic parameter
                    penet_rates (DataFrame)         : logistic parameter
                    ports (DataFrame)               : logistic parameter
                    schedule_OLC (DataFrame)        : logistic parameter
                    site (DataFrame)                : logistic parameter
                    static_cable (DataFrame)        : logistic parameter
                    sub_device (DataFrame)          : logistic parameter
                    topology (DataFrame)            : logistic parameter
                    vessels (dict)                  : logistic parameter
                    
            self.__Simu_Param (dict): This parameter records the general information concerning the simulation
                keys:          
                    Nbodies (int) [-]                                  : Number of devices 
                    annual_Energy_Production_perD (numpy.ndarray) [Wh] : Annual energy production of each device on the array. The dimension of the array is Nbodies x 1 (WP2)
                    arrayInfoLogistic (DataFrame) [-]                  : Information about component_id, depth, x_coord, y_coord, zone, bathymetry, soil type
                    missionTime (float) [year]                         : Simulation time             
                    power_prod_perD (numpy.ndarray) [W]                : Mean power production per device. The dimension of the array is Nbodies x 1 (WP2) 
                    startOperationDate (datetime) [-]                  : Date of simulation start
                    
                    
            self.__Control_Param (dict): This parameter records the O&M module control from GUI (to be extended in future)
                keys:          
                    whichOptim (list) [bool]           : Which O&M should be optimised [Unplanned corrective maintenance, Condition based maintenance, Calendar based maintenance]
                    checkNoSolution (bool) [-]         : see below
                    checkNoSolutionWP6Files (bool) [-] : see below             
                    integrateSelectPort (bool) [-]     : see below)                 
              
                    ###############################################################################
                    ###############################################################################
                    ###############################################################################
                    # Some of the function developed by logistic takes some times for running. 
                    # With the following flags is possible to control the call of such functions.
                    
                    # Control_Param['integrateSelectPort'] is True  -> call OM_PortSelection
                    # Control_Param['integrateSelectPort'] is False -> do not call OM_PortSelection, set constant values for port parameters
                    Control_Param['integrateSelectPort'] = False 
                    
                    # Control_Param['checkNoSolution'] is True  -> check the feasibility of logistic solution before the simulation 
                    # Control_Param['checkNoSolution'] is False -> do not check the feasibility of logistic solution before the simulation
                    Control_Param['checkNoSolution'] = False 
                                                                      
                    # dtocean_operations print flag               
                    # Control_Param['dtocean_operations_PRINT_FLAG'] is True  -> print is allowed inside of dtocean_operations
                    # Control_Param['dtocean_operations_PRINT_FLAG'] is False -> print is not allowed inside of dtocean_operations
                    Control_Param['dtocean_operations_PRINT_FLAG'] = True 
                    
                    # dtocean-logistics print flag               
                    # Control_Param['dtocean-logistics_PRINT_FLAG'] is True  -> print is allowed inside of dtocean-logistics
                    # Control_Param['dtocean-logistics_PRINT_FLAG'] is False -> print is not allowed inside of dtocean-logistics
                    Control_Param['dtocean-logistics_PRINT_FLAG'] = True 
                    
                    # dtocean_operations test flag               
                    # Control_Param['dtocean_operations_TEST_FLAG'] is True  -> print the results in excel files
                    # Control_Param['dtocean_operations_TEST_FLAG'] is False -> do not print the results in excel files
                    Control_Param['dtocean_operations_TEST_FLAG'] = True                   
                                                            
                    ###############################################################################
                    ###############################################################################
                    ############################################################################### 
             
                           
            self.__strFormat1 (str) [-]                               : converting between datetime and string  
            self.__strFormat2 (str) [-]                               : converting between datetime and string
            self.__dayHours (float) [-]                               : Hours in one day
            self.__yearDays (float) [-]                               : Days in one year     
            self.__delayEventsAfterCaBaMaHour (float) [hour]          : Delay repair action after CaBaMa 
            self.__energy_selling_price (float) [Euro/kWh]               : Energy selling price             
            arrayDict (dict) [-]                                      : dictionary for the saving of model calculation in dtocean-operations-and-maintenance module
            startOperationDate (datetime) [-]                         : date of simulation start
            self.__powerOfDevices (list of float) [W]                 : power of devices
            self.__annual_Energy_Production_perD (list of float) [Wh] : Annual energy production per device                         
            self.__NrOfDevices (int) [-]                              : Number of devices
            self.__NrOfTurnOutDevices (int) [-]                       : Number of turn out devices          
            self.__operationTimeYear (float) [year]                   : Operation time in years (mission time)
            self.__operationTimeDay (float) [day]                     : Operation time in days
            self.__endOperationDate (datetime) [day]                  : end date of array operation
            self.__UnCoMa_eventsTableKeys (list of str) [-]           : keys of eventsTable (UnCoMa)
            self.__UnCoMa_outputEventsTableKeys (list of str) [-]     : keys of outputEventsTable (UnCoMa)          
            self.__NoPoisson_eventsTableKeys (list of str) [-]        : Keys of eventsTableNoPoisson
            self.__UnCoMa_eventsTable (DataFrame) [-]                 : eventsTable (UnCoMa)
            self.__UnCoMa_outputEventsTable (DataFrame) [-]           : eventsTable for output (UnCoMa)
            self.__eventsTableNoPoisson (DataFrame) [-]               : eventsTable (NoPoisson)
            self.__summerTime (bool) [-]                              : summer time
            self.__winterTime (bool) [-]                              : winter time
            self.__totalWeekEndWorkingHour (float) [hour]             : total weekend working hour
            self.__totalNotWeekEndWorkingHour (float) [hour]          : total not weekend working hour
            self.__totalDayWorkingHour (float) [hour]                 : total day working hour
            self.__totalNightWorkingHour (float) [hour]               : total night working hour
            self.__startDayWorkingHour (float) [-]                    : start hour of working
            self.__totalActionDelayHour (float) [hour]                : total repair action delay
            self.__actActionDelayHour (float) [hour]                  : actual action delay
            self.__outputsOfWP6 (dict) [-]                            : output of WP6
            self.__om_logistic (dict) [-]                             : output of logistic 
            self.__OUTPUT_dict_logistic (dict) [-]                    : output of logistic 
            self.__logPhase_om (class) [-]                            : logistic parameter
            self.__vessels (dict) [-]                                 : logistic parameter
            self.__equipments (dict) [-]                              : logistic parameter 
            self.__ports (DataFrame) [-]                              : logistic parameter
            self.__portDistIndex (dict) [-]                           : logistic parameter
            self.__phase_order (DataFrame) [-]                        : logistic parameter
            self.__site (DataFrame) [-]                               : logistic parameter
            self.__metocean (DataFrame) [-]                           : logistic parameter
            self.__device (DataFrame) [-]                             : logistic parameter
            self.__sub_device (DataFrame) [-]                         : logistic parameter
            self.__landfall (DataFrame) [-]                           : logistic parameter
            self.__entry_point (DataFrame) [-]                        : logistic parameter
            self.__layout (DataFrame) [-]                             : logistic parameter
            self.__connerctors (DataFrame) [-]                        : logistic parameter
            self.__dynamic_cable (DataFrame) [-]                      : logistic parameter
            self.__static_cable (DataFrame) [-]                       : logistic parameter
            self.__cable_route (DataFrame) [-]                        : logistic parameter
            self.__connerctors (DataFrame) [-]                        : logistic parameter
            self.__external_protection (DataFrame) [-]                : logistic parameter
            self.__topology (DataFrame) [-]                           : logistic parameter
            self.__schedule_OLC (DataFrame) [-]                       : logistic parameter
            self.__other_rates (DataFrame) [-]                        : logistic parameter  
            self.__logisticKeys (DataFrame) [-]                       : keys of dataframe for logistic functions                       
            self.__wp6_outputsForLogistic (DataFrame) [-]             : input for logistic module
            self.__ramPTR (class) [-]                                 : pointer of RAM
            self.__eleclayout (str) [-]                               : Electrical layout architecture
            self.__systype (str) [-]                                  : Type of system 
            self.__elechierdict (str) [-]                             : RAM parameter 
            self.__elecbomeg (str) [-]                                : RAM parameter  
            self.__moorhiereg (str) [-]                               : RAM parameter  
            self.__moorbomeg (str) [-]                                : RAM parameter  
            self.__userhiereg (str) [-]                               : RAM parameter 
            self.__userbomeg (str) [-]                                : RAM parameter  
            self.__db (str) [-]                                       : RAM parameter 
            self.__rsubsysvalues (nested list) [-]                    : rsubsysvalues from RAM 
            self.__rcompvalues (nested list) [-]                      : rcompvalues from RAM 
            self.__arrayPTR (class) [-]                               : pointer of arrayClass  
            self.__totalSeaTimeHour (float) [hour]                    : Total sea time 
            self.__totalSeaTimeHour (float) [hour]                    : Total sea time 
            self.__departOpDate (datetime) [-]                        : date of depart 
            self.__endOpDate (datetime) [-]                           : date of end of operation 
            self.__repairActionDate (datetime) [-]                    : date of repair action 
            self.__errorFlag (bool) [-]                               : error flag 
            self.__errorTable (DataFrame) [-]                         : error table 
            self.__CaBaMa_nrOfMaxActions (int) [-]                    : maximum number of parallel actions in calendar based maintenance
            self.__CaBaMa_eventsTableKeys (list of str) [-]           : keys of table CaBaMa_eventsTableKeys
            self.__CaBaMa_eventsTable (DataFrame) [-]                 : table CaBaMa_eventsTable 
            self.__CaBaMa_outputEventsTableKeys (list of str) [-]     : keys of table CaBaMa_eventsTableKeys
            self.__CaBaMa_outputEventsTable (DataFrame) [-]           : table CaBaMa_eventsTable                        
            self.__CoBaMa_nrOfMaxActions (int) [-]                    : maximum number of parallel actions in condition based maintenance
            self.__CoBaMa_eventsTableKeys (list of str) [-]           : keys of table CoBaMa_eventsTableKeys
            self.__CoBaMa_outputEventsTableKeys (list of str) [-]     : keys of table CaBaMa_eventsTableKeys
            self.__CoBaMa_outputEventsTable (DataFrame) [-]           : table CoBaMa_eventsTable
            self.__CoBaMa_eventsTable (DataFrame) [-]                 : table CoBaMa_eventsTable 
            self.__actIdxOfUnCoMa (int) [-]                           : actual index of UnCoMa_eventsTable
            self.__flagCalcUnCoMa (bool) [-]                          : flag of UnCoMa_eventsTable
            self.__PrepTimeCalcUnCoMa (float) [hour]                  : preparation time    
            self.__actIdxOfCaBaMa (int) [-]                           : actual index of CaBaMa_eventsTable
            self.__flagCalcCaBaMa (bool) [-]                          : flag of CaBaMa_eventsTable
            self.__PrepTimeCalcCaBaMa (float) [hour]                  : preparation time 
            self.__failureRateFactorCoBaMa (float) [%]                : factor for the correction of failure rate in case of condition based maintenance in %            
            self.__actIdxOfCoBaMa (int) [-]                           : actual index of CoBaMa_eventsTable
            self.__flagCalcCoBaMa (bool) [-]                          : flag of CoBaMa_eventsTable
            self.__PrepTimeCalcCoBaMa (float) [hour]                  : preparation time
            self.__powerDeratingCoBaMa (float) [%]                    : power derating in case of condition based maintenance after the detction of soh_threshold  
            self.__timeExtensionDeratingCoBaMaHour (float) [hours]    : time extension in case of condition based maintenance after the detction of soh_threshold  
            self.__checkNoSolution (bool) [-]                         : see below
            self.__integrateSelectPort (bool) [-]                     : see below 
            self.__dtocean_operations_PRINT_FLAG (bool) [-]           : see below
            self.__dtocean-logistics_PRINT_FLAG (bool) [-]            : see below              
          
            ###############################################################################
            ###############################################################################
            ###############################################################################
            # Some of the function developed by logistic takes some times for running. 
            # With the following flags is possible to control the call of such functions.
            
            # self.__integrateSelectPort is True  -> call OM_PortSelection
            # self.__integrateSelectPort is False -> do not call OM_PortSelection, set constant values for port parameters
            self.__integrateSelectPort 
            
            # self.__checkNoSolution is True  -> check the feasibility of logistic solution before the simulation 
            # self.__checkNoSolution is False -> do not check the feasibility of logistic solution before the simulation
            self.__checkNoSolution
             
            # dtocean_operations print flag               
            # self.__dtocean_operations_PRINT_FLAG is True  -> print is allowed inside of dtocean_operations
            # self.__dtocean_operations_PRINT_FLAG is False -> print is not allowed inside of dtocean_operations
            self.__dtocean_operations_PRINT_FLAG
            
            # dtocean-logistics print flag               
            # self.__dtocean-logistics_PRINT_FLAG is True  -> print is allowed inside of dtocean-logistics
            # self.__dtocean-logistics_PRINT_FLAG is False -> print is not allowed inside of dtocean-logistics
            self.__dtocean-logistics_PRINT_FLAG
            
            # dtocean_operations test flag               
            # self.__dtocean_operations_TEST_FLAG is True  -> print the results in excel files
            # self.__dtocean_operations_TEST_FLAG is False -> do not print the results in excel files
            self.__dtocean_operations_TEST_FLAG
            
            # Flag read from RAM
            # self.__readFailureRateFromRAM is True  -> Failure rate is read from RAM
            # self.__readFailureRateFromRAM is False -> Failure rate is read from component table (IWES)
            self.__readFailureRateFromRAM
                        
            # Flag ignore weather window
            # self.__ignoreWeatherWindow is True  -> The case "NoWeatherWindowFound" will be ignored in dtocean-operations 
            # self.__ignoreWeatherWindow is False -> The case "NoWeatherWindowFound" wont be ignored in dtocean-operations. In this case the coresponding device/devices will be switched off.
            self.__ignoreWeatherWindow            
                
           ###############################################################################
            ###############################################################################
            ############################################################################### 

             
        Returns:
            no returns 
       
        '''    

        #######################################################################

        # start: Read from inputOM                
        # Save the instance pointer of inputOM
        self.__inputOMPTR = inputOMPTR
        
        # Read the inputs from core         
        self.__Farm_OM          = self.__inputOMPTR.get_Farm_OM()
        self.__Component        = self.__inputOMPTR.get_Component()
        self.__Failure_Mode     = self.__inputOMPTR.get_Failure_Mode()
        self.__Repair_Action    = self.__inputOMPTR.get_Repair_Action()
        self.__Inspection       = self.__inputOMPTR.get_Inspection()
        self.__RAM_Param        = self.__inputOMPTR.get_RAM_Param()
        self.__Logistic_Param   = self.__inputOMPTR.get_Logistic_Param()
        self.__Simu_Param       = self.__inputOMPTR.get_Simu_Param()
        self.__Control_Param    = self.__inputOMPTR.get_Control_Param() 
              
        self.__changeOfLabels()         
        # end: Read from inputOM                
        #######################################################################
        
        #######################################################################
        # start: Declaration of constants for mainCalc 
        
        # For converting between datetime and string     
        self.__strFormat1 = "%d:%m:%Y %H:%M:%S" 
        self.__strFormat2 = "%Y-%m-%d %H:%M:%S" 
        
        # Hours in one day  
        self.__dayHours = 24.0 
        
        # Days in one year     
        self.__yearDays = 365.25 
        
        # Delete repair action after CaBaMa [hour]     
        self.__delayEventsAfterCaBaMaHour = 6*30*24 
                
        # end: Declaration of constants for mainCalc                 
        #######################################################################  

        #######################################################################
        # start: Declaration of general variables for mainCalc

        # Energy selling price [Euro/kWh]
        self.__energy_selling_price = self.__Farm_OM['energy_selling_price']
        
        # Instance pointer of arrayClass
        # Dictionary for saving the parameters
        self.__arrayDict = {}
        
        # Which O&M should be calculated?
        # [unplaned corrective maintenance, condition based maintenance, calandar based maintenance]  
        self.__whichOptim = self.__Control_Param['whichOptim']
        
        # Start of operation date
        self.__startOperationDate = self.__Simu_Param['startOperationDate']
        
        # Power of devices [W]
        self.__powerOfDevices = self.__Simu_Param['power_prod_perD'] 
        
        # Annual_Energy_Production_perD [Wh]
        self.__annual_Energy_Production_perD = self.__Simu_Param['annual_Energy_Production_perD']
        
        # Nr of devices []
        self.__NrOfDevices = self.__Simu_Param['Nbodies'] 
        
        # Nr of turn out devices []
        self.__NrOfTurnOutDevices = 0 
         
        # Operation time in years (mission time)
        self.__operationTimeYear = float(self.__Simu_Param['missionTime'])
        
        # Operation time in days
        self.__operationTimeDay = self.__Simu_Param['missionTime']*self.__yearDays
        
        # End of array operation
        self.__endOperationDate = self.__startOperationDate + timedelta(days = self.__operationTimeDay)   
                                                       
        # Keys of eventsTable
        self.__UnCoMa_eventsTableKeys        = ['failureRate', 'repairActionEvents', 'failureEvents', 'belongsTo', 'ComponentType',
                                                'ComponentSubType', 'ComponentID', 'FM_ID', 'indexFM', 'RA_ID']
      
        # eventsTable
        self.__UnCoMa_eventsTable       = None
        
        # event table for output
        self.__UnCoMa_outputEventsTableKeys  = ['failureRate [1/year]', 'failureDate [-]', 'repairActionRequestDate [-]', 'repairActionDate [-]',
                                                'downtimeDuration [Hour]', 'seeTimeDuration [Hour]', 'waitingTimeDuration [Hour]',
                                                'downtimeDeviceList [-]', 'ComponentType [-]', 'ComponentSubType [-]', 'ComponentID [-]',
                                                'FM_ID [-]', 'RA_ID [-]', 'indexFM [-]', 'costLogistic [Euro]', 'costOM_Labor [Euro]', 'costOM_Spare [Euro]',
                                                'typeOfvessels [-]', 'nrOfvessels [-]']
                                                
                                                      
        self.__UnCoMa_outputEventsTable      = pd.DataFrame(index=[0],columns=self.__UnCoMa_outputEventsTableKeys)
        
        # init
#        valuesForOutput = ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-',                                                      
#                           '-', '-', '-', '-', '-', '-', '-', '-' ] 
#                                                           
#        self.__UnCoMa_outputEventsTable.ix[0] = valuesForOutput                                                                
                                   
        # Keys of eventsTableNoPoisson
        self.__NoPoisson_eventsTableKeys  = ['repairActionEvents', 'failureEvents', 'belongsTo', 'ComponentType',
                                             'ComponentSubType', 'ComponentID', 'FM_ID', 'indexFM', 'RA_ID', 'failureRate', 'Alarm']
                        
        # eventsTableNoPoisson
        self.__eventsTableNoPoisson = None
                
        # summer time
        self.__summerTime = None
        
        # winter time
        self.__winterTime = None
        
        # total weekend working hour
        self.__totalWeekEndWorkingHour = None
        
        # total not weekend working hour
        self.__totalNotWeekEndWorkingHour = None
        
        # total day working hour
        self.__totalDayWorkingHour = None
        
        # total night working hour
        self.__totalNightWorkingHour = None
        
        # startDayWorkingHour
        self.__startDayWorkingHour = 6
        
        # total action delay 
        self.__totalActionDelayHour = 0
        
        # actual action delay 
        self.__actActionDelayHour = 0
         
        # end: Declaration of general variables for mainCalc                 
        #######################################################################          


            
        #######################################################################
        # start: Declaration of outputs of WP6   
        self.__outputsOfWP6 = {}  
        self.__outputsOfWP6['env_assess [-]'] = {}
        self.__outputsOfWP6['env_assess [-]']['UnCoMa_eventsTable'] = {} 
        self.__outputsOfWP6['env_assess [-]']['CaBaMa_eventsTable'] = {} 
        self.__outputsOfWP6['env_assess [-]']['CoBaMa_eventsTable'] = {} 
               
        self.__UnCoMa_dictEnvAssess = {}
        self.__CaBaMa_dictEnvAssess = {}
        self.__CoBaMa_dictEnvAssess = {}
                
        # for maintenance plans in WP6 
        self.__outputsOfWP6['eventTables [-]'] = {}
        
        # LCOE of array (float) [Euro/KWh] 
        self.__outputsOfWP6['lcoeOfArray [Euro/KWh]'] = 0
        
        # Annual energy of each devices (list of float) [Wh] 
        self.__outputsOfWP6['annualEnergyOfDevices [Wh]'] = []
        
        # Annual down time of each devices (list of float) [h] 
        self.__outputsOfWP6['annualDownTimeOfDevices [h]'] = []
        
        # Annual energy of array (float) [Wh] 
        self.__outputsOfWP6['annualEnergyOfArray [Wh]'] = 0 
        
                
        # CAPEX of array in case of condition based maintenance strategy (float) [Euro] 
        self.__outputsOfWP6['CapexOfArray [Euro]'] = 0 
                
        # determine the CAPEX of the array
        if self.__Farm_OM['condition_based_maintenance'] == True: 
               
            for iCnt in range(0,self.__Failure_Mode.shape[1]):
                                        
                column = self.__Failure_Mode.columns.values[iCnt]                
                if math.isnan(self.__Failure_Mode[column]['CAPEX_condition_based_maintenance']) == False and 0 < self.__Failure_Mode[column]['CAPEX_condition_based_maintenance']:                
                    self.__outputsOfWP6['CapexOfArray [Euro]'] = self.__outputsOfWP6['CapexOfArray [Euro]'] + self.__Failure_Mode[column]['CAPEX_condition_based_maintenance']
                                    
        # Annual OPEX of array (float) [Euro] 
        self.__outputsOfWP6['annualOpexOfArray [Euro]'] = 0
        
        # Information about error (-) [-] 
        self.__outputsOfWP6['error [-]'] = None
        
        for iCnt in range(0,self.__NrOfDevices):
            self.__outputsOfWP6['annualEnergyOfDevices [Wh]'].append(0.0)   
            self.__outputsOfWP6['annualDownTimeOfDevices [h]'].append(0.0)

        # end: Declaration of outputs of WP6 
        #######################################################################                  
                
              
        #######################################################################
        # start: Declaration of variables for logistic 
        
        # Declaration of output of logistic (dict)
        self.__om_logistic = {}
        
        # Declaration of output of logistic (dict)
        self.__OUTPUT_dict_logistic = {}
        
        # Declaration of variable for logistic (class)
        self.__logPhase_om = None

         # Declaration of variable for logistic (?)
        self.__vessels = self.__Logistic_Param['vessels']      
        
        # Declaration of variable for logistic (?)
        self.__equipments = self.__Logistic_Param['equipments']   
        
        # Declaration of variable for logistic (dataframe)
        self.__ports = self.__Logistic_Param['ports']
                               
        # 'Dist_port [km]', 'Port_Index [-]'
        # Information about ports
        self.__portDistIndex = {}
        self.__portDistIndex['inspection'] = []
        self.__portDistIndex['repair']     = []
        
        # Default values for port
        self.__dummyDist_port   = 0.1#190
        self.__dummyPort_Index  = 21 
        
        self.__portDistIndex['inspection'].append(self.__dummyDist_port)
        self.__portDistIndex['inspection'].append(self.__dummyPort_Index)
        
        self.__portDistIndex['repair'].append(self.__dummyDist_port)
        self.__portDistIndex['repair'].append(self.__dummyPort_Index)        
     
        # Declaration of variable for logistic (dict) 
       
        self.__phase_order = self.__Logistic_Param['phase_order']
        self.__site        = self.__Logistic_Param['site']
        self.__metocean    = self.__Logistic_Param['metocean']
        self.__device      = self.__Logistic_Param['device']
        self.__sub_device  = self.__Logistic_Param['sub_device']
        self.__landfall    = self.__Logistic_Param['landfall']
        self.__entry_point = self.__Logistic_Param['entry_point'] 
                
        # Declaration of variable for logistic (?)
        self.__layout = self.__Logistic_Param['layout']           
               
        self.__collection_point    = self.__Logistic_Param['collection_point']
        self.__dynamic_cable       = self.__Logistic_Param['dynamic_cable']
        self.__static_cable        = self.__Logistic_Param['static_cable']
        self.__cable_route         = self.__Logistic_Param['cable_route']
        self.__connectors          = self.__Logistic_Param['connectors']
        self.__external_protection = self.__Logistic_Param['external_protection']
        self.__topology            = self.__Logistic_Param['topology']  
        self.__port_sf             = self.__Logistic_Param['port_sf']
        self.__vessel_sf           = self.__Logistic_Param['vessel_sf']
        self.__eq_sf               = self.__Logistic_Param['eq_sf'] 
        self.__schedule_OLC        = self.__Logistic_Param['schedule_OLC'] 
        self.__other_rates         = self.__Logistic_Param['other_rates'] 
                
        """
         Initialise logistic operations and logistic phase
        """
        #self.__logOp               = logOp_init(self.__schedule_OLC)
        
        # keys of dataframe for logistic functions 
        self.__logisticKeys = ['ID [-]', 'element_type [-]', 'element_subtype [-]', 'element_ID [-]',
                               'depth [m]', 'x coord [m]', 'y coord [m]', 'zone [-]', 't_start [-]',
                               'd_acc [hour]', 'd_om [hour]', 'helideck [-]', 
                               'Hs_acc [m]','Tp_acc [s]', 'Ws_acc [m/s]', 'Cs_acc [m/s]',
                               'Hs_om [m]', 'Tp_om [s]', 'Ws_om [m/s]', 'Cs_om [m/s]', 
                               'technician [-]', 
                               'sp_dry_mass [kg]', 'sp_length [m]', 'sp_width [m]', 'sp_height [m]',
                               'Dist_port [km]', 'Port_Index [-]', 'Bathymetry [m]', 'Soil type [-]', 'Prep_time [h]'             
                               ]
                             
        self.__wp6_outputsForLogistic = pd.DataFrame(index=[0],columns=self.__logisticKeys)
        
        # end: Declaration of variables for logistic    
        #######################################################################        
        
        #######################################################################
        # start: Declaration of variables for RAM 
        
        # This variable will be used for saving of RAM instance.
        self.__ramPTR = None  
        
        # Eleclayout -> radial, singlesidedstring, doublesidedstring, multiplehubs
        self.__eleclayout = self.__RAM_Param['eleclayout']
 
        # systype -> 'tidefloat', 'tidefixed', 'wavefloat', 'wavefixed'
        self.__systype = self.__RAM_Param['systype']
        
        # elechierdict
        self.__elechierdict = self.__RAM_Param['elechierdict']  
        
        # elecbomeg
        self.__elecbomeg    = self.__RAM_Param['elecbomeg'] 
        
        # moorhiereg
        self.__moorhiereg   = self.__RAM_Param['moorhiereg'] 
        
        # moorbomeg
        self.__moorbomeg    = self.__RAM_Param['moorbomeg']  
        
        # userhiereg
        self.__userhiereg   = self.__RAM_Param['userhiereg'] 
        
        # userbomeg
        self.__userbomeg    = self.__RAM_Param['userbomeg'] 
        
        # db
        self.__db           = self.__RAM_Param['db']        
        
        
        # Declaration of output of RAM
        #self.__ram = {}       
       
        # list rsubsysvalues from RAM
        self.__rsubsysvalues = []
                        
        # list rcompvalues from RAM
        self.__rcompvalues = []
        
        
        # end: Declaration of variables for RAM                 
        #######################################################################  


        #######################################################################
        # start: Declaration of variables for arrayClass 
        
        # Instance pointer of arrayClass
        self.__arrayPTR = None

        # end: Declaration of variables for arrayClass                 
        #######################################################################            
        

        #######################################################################
        # start: Declaration of internally parameters for mainCalc 
        
        # Total sea time [hour]     
        self.__totalSeaTimeHour = 0 
      
        # date of depart [datetime]     
        self.__departOpDate = None 
        
        # date of end of operation [datetime]     
        self.__endOpDate = None 
        
        # date of repair action [datetime]     
        self.__repairActionDate = None 

        # error flag [-]     
        self.__errorFlag = False          
        
        # error table [-]             
        errorKeys  = ['error_ID [-]', 'element_ID [-]', 'element_type [-]', 'element_subtype [-]',
                      'FM_ID [-]', 'RA_ID [-]', 'deck area [m^2]', 'deck cargo [t]', 'deck loading [t/m^2]',
                       'sp_dry_mass [kg]', 'sp_length [m]', 'sp_width [m]', 'sp_height [m]']
                    
        self.__errorTable = pd.DataFrame(index=[0],columns= errorKeys)          
              
        # end: Declaration of internally parameters for mainCalc                
        #######################################################################          
  
                
        #######################################################################
        # start: Parameter of Condition based maintenance and Calendar based maintenance
                
        # Calendar based maintenance: Number of parallel actions [-]
        self.__CaBaMa_nrOfMaxActions = 10
        
        # Keys of CaBaMa_eventsTableKeys
        self.__CaBaMa_eventsTableKeys  = ['startActionDate', 'endActionDate', 'currentStartActionDate', 
                                          'currentEndActionDate', 'belongsTo', 'belongsToSort', 'ComponentType', 
                                          'ComponentSubType', 'ComponentID', 'FM_ID', 'indexFM', 'RA_ID', 'logisticCost', 'omCost']
                
        # CaBaMa_eventsTableKeys
        self.__CaBaMa_eventsTable = pd.DataFrame(index=[0],columns=self.__CaBaMa_eventsTableKeys)
               
        # CaBaMa_eventsTableKeys                              
        self.__CaBaMa_outputEventsTableKeys  = ['repairActionRequestDate [-]', 'repairActionDate [-]', 'downtimeDuration [Hour]',
                                                'downtimeDeviceList [-]', 'ComponentType [-]', 'ComponentSubType [-]', 'ComponentID [-]',
                                                'FM_ID [-]', 'RA_ID [-]', 'indexFM [-]',
                                                'costLogistic [Euro]', 'costOM_Labor [Euro]', 'costOM_Spare [Euro]']
                                                       
        self.__CaBaMa_outputEventsTable      = pd.DataFrame(index=[0],columns=self.__CaBaMa_outputEventsTableKeys) 
                                                       
        # init
#        valuesForOutput = ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-']                     
#                                                                                                                                                                      
#        self.__CaBaMa_outputEventsTable.ix[0] = valuesForOutput              
        
       
        # Condition based maintenance: Number of parallel actions [-]
        self.__CoBaMa_nrOfMaxActions = 10
        
        # Keys of CoBaMa_eventsTableKeys
        self.__CoBaMa_eventsTableKeys  = ['startActionDate', 'endActionDate', 'currentStartDate', 'currentEndDate', 
                                          'currentAlarmDate', 'belongsTo', 'ComponentType', 
                                          'ComponentSubType', 'ComponentID', 'FM_ID', 'indexFM', 'RA_ID', 
                                          'threshold', 'failureRate', 'flagCaBaMa']
            
        # CoBaMa_eventsTableKeys
        self.__CoBaMa_eventsTable        = pd.DataFrame(index=[0],columns=self.__CoBaMa_eventsTableKeys)
        
     
                                          
                                          
        # CaBaMa_eventsTableKeys                              
        self.__CoBaMa_outputEventsTableKeys  = ['failureRate [1/year]', 'currentAlarmDate [-]', 'repairActionRequestDate [-]', 'repairActionDate [-]', 'downtimeDuration [Hour]', 
                                                'downtimeDeviceList [-]', 'ComponentType [-]', 'ComponentSubType [-]', 'ComponentID [-]',
                                                'FM_ID [-]', 'RA_ID [-]', 'indexFM [-]',
                                                'costLogistic [Euro]', 'costOM_Labor [Euro]', 'costOM_Spare [Euro]']
                                                                                                                                       
        self.__CoBaMa_outputEventsTable      = pd.DataFrame(index=[0],columns=self.__CoBaMa_outputEventsTableKeys)
        
#        # init
#        valuesForOutput = ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-']                     
#                                                                                                                                                                      
#        self.__CoBaMa_outputEventsTable.ix[0] = valuesForOutput         


              
        # actual index of UnCoMa_eventsTable
        self.__actIdxOfUnCoMa     = 0
        self.__flagCalcUnCoMa     = False
        self.__PrepTimeCalcUnCoMa = 48
        
        # actual index of CaBaMa_eventsTable
        self.__actIdxOfCaBaMa     = 0  
        self.__flagCalcCaBaMa     = False
        self.__PrepTimeCalcCaBaMa = 0
        
        # actual index of CoBaMa_eventsTable
        self.__failureRateFactorCoBaMa         = 0 
        self.__actIdxOfCoBaMa                  = 0 
        self.__flagCalcCoBaMa                  = False
        self.__PrepTimeCalcCoBaMa              = 0
        # in %
        self.__powerDeratingCoBaMa             = 50
        # [hours]
        self.__timeExtensionDeratingCoBaMaHour = 3*30*self.__dayHours  
        
        # end: Declaration of internally parameters for mainCalc                
        ####################################################################### 
                
                
        #######################################################################                  
        # Start: Flags for dtocean_operations test purposes
        
        # self.__integrateSelectPort is True  -> call OM_PortSelection
        # self.__integrateSelectPort is False -> do not call OM_PortSelection, set constant values for port parameters
        self.__integrateSelectPort = self.__Control_Param['integrateSelectPort'] 
                                                         
        # self.__checkNoSolution is True  -> check the feasibility of logistic solution before the simulation 
        # self.__checkNoSolution is False -> do not check the feasibility of logistic solution before the simulation
        self.__checkNoSolution = self.__Control_Param['checkNoSolution']
                        
        # dtocean_operations print flag               
        # self.__dtocean_operations_PRINT_FLAG is True  -> print is allowed inside of dtocean_operations
        # self.__dtocean_operations_PRINT_FLAG is False -> print is not allowed inside of dtocean_operations
        self.__dtocean_operations_PRINT_FLAG = self.__Control_Param['dtocean_operations_PRINT_FLAG'] 
        
        # dtocean-logistics print flag               
        # self.__dtocean_logistics_PRINT_FLAG is True  -> print is allowed inside of dtocean-logistics
        # self.__dtocean_logistics_PRINT_FLAG is False -> print is not allowed inside of dtocean-logistics
        self.__dtocean_logistics_PRINT_FLAG = self.__Control_Param['dtocean_logistics_PRINT_FLAG']
        
        # dtocean_operations test flag               
        # self.__dtocean_operations_TEST_FLAG is True  -> print the results in excel files
        # self.__dtocean_operations_TEST_FLAG is False -> do not print the results in excel files
        self.__dtocean_operations_TEST_FLAG = self.__Control_Param['dtocean_operations_TEST_FLAG']
        
        # Flag read from RAM
        # self.__readFailureRateFromRAM is True  -> Failure rate is read from RAM
        # self.__readFailureRateFromRAM is False -> Failure rate is read from component table (IWES)
        self.__readFailureRateFromRAM = self.__Control_Param['readFailureRateFromRAM']
        
        # Flag ignore weather window
        # self.__ignoreWeatherWindow is True  -> The case "NoWeatherWindowFound" will be ignored in dtocean-operations 
        # self.__ignoreWeatherWindow is False -> The case "NoWeatherWindowFound" wont be ignored in dtocean-operations. In this case the coresponding device/devices will be switched off.
        self.__ignoreWeatherWindow = self.__Control_Param['ignoreWeatherWindow']           
                       
        return   

    def __call__(self):
        
        '''__call__ function: call function
        
        Args:              
            no arguments
        
        Attributes:         
            no attributs 
            
        Returns:
            no returns
        
        '''       
        
        # Execution of functions for the calculation of LCOE
        self.executeCalc()         
 
        return   
          
    def executeCalc(self):
        
        '''executeCalc function: Execution of functions for the calculation of LCOE
                                                      
        Args:              
            no arguments
        
        Attributes:         
            no attributes                  
 
        Returns:
            self.__outputsOfWP6 (dict) : Output of WP6
      
        ''' 
            
        # Initialisation        
        self.__initCalc()
                
        if self.__integrateSelectPort == True or self.__checkNoSolution == True:               
            self.__initCheck()
           
            if self.__errorFlag == True:
                
                # error handling
                self.__outputsOfWP6['error [-]'] = self.__errorTable
                
            else:            
                    
                ComponentType    = ''
                ComponentSubType = ''
                ComponentID      = ''
                RA_ID            = ''  
                FM_ID            = ''
                deck_area        = ''
                deck_cargo       = ''
                deck_loading     = ''
                sp_dry_mass      = ''
                sp_length        = ''
                sp_width         = ''
                sp_height        = ''
                
                values = ['NoError', ComponentID, ComponentType, ComponentSubType, FM_ID, RA_ID,  
                  deck_area, deck_cargo, deck_loading, sp_dry_mass, sp_length, sp_width, sp_height]
                  
                self.__errorTable.ix[0] = values
                
                # noError            
                self.__outputsOfWP6['error [-]'] = self.__errorTable  
            
            return self.__outputsOfWP6
            
            
        ComponentType    = ''
        ComponentSubType = ''
        ComponentID      = ''
        RA_ID            = ''  
        FM_ID            = ''
        deck_area        = ''
        deck_cargo       = ''
        deck_loading     = ''
        sp_dry_mass      = ''
        sp_length        = ''
        sp_width         = ''
        sp_height        = ''
        
        values = ['NoError', ComponentID, ComponentType, ComponentSubType, FM_ID, RA_ID,  
          deck_area, deck_cargo, deck_loading, sp_dry_mass, sp_length, sp_width, sp_height]
          
        self.__errorTable.ix[0] = values
        
        # noError            
        self.__outputsOfWP6['error [-]'] = self.__errorTable              
            
        # calc LCOE of array   
        self.__calcLCOE_OfArray() 
                                                                                            
        return self.__outputsOfWP6
        
        
    # Selection of port for inspection and repair    
    def __initCheck(self): 
        
        '''__initCheck function: Selection of port for inspection and repair and check "NoSolutionsFound"  
                                                      
        Args:              
            no arguments
        
        Attributes:         
            no attributes                  
 
        Returns:
            no returns
      
        ''' 

        dummyCheckNoSolution = True        
        
        # should OM_PortSelection from logistic be called? 
        if self.__integrateSelectPort == True:
                          
            outputsForPortSelection = pd.DataFrame(index=[0],columns=self.__logisticKeys)
                    
            # find the maximum of 'sp_dry_mass [kg]', 'sp_length [m]', 'sp_width [m]', 'sp_height [m]'
            sp_dry_mass_dummy       = 0
            #index_sp_dry_mass_dummy = 0
            
            sp_length_dummy         = 0
            #index_sp_length_dummy   = 0
            
            sp_width_dummy          = 0
            #index_sp_width_dummy    = 0
     
            sp_height_dummy         = 0
            #index_sp_height_dummy   = 0
           
            self.__portDistIndex['inspection'] = []
            self.__portDistIndex['repair']     = []
                                  
            for iCnt in range(0,len(self.__eventsTableNoPoisson)):             
                
                # actualIndexOfRepairTable is determined
                # do the the reapir   
                ComponentType       = self.__eventsTableNoPoisson.ComponentType[iCnt]
                ComponentSubType    = self.__eventsTableNoPoisson.ComponentSubType[iCnt]
                ComponentID         = self.__eventsTableNoPoisson.ComponentID[iCnt]
                RA_ID               = self.__eventsTableNoPoisson.RA_ID[iCnt]  
                FM_ID               = self.__eventsTableNoPoisson.FM_ID[iCnt]     
                belongsTo           = self.__eventsTableNoPoisson.belongsTo[iCnt]
                                  
                indexFM             = self.__eventsTableNoPoisson.indexFM[iCnt]
                CompIDWithIndex     = ComponentID + '_' + str(indexFM)
                                                 
                # max of values
                sp_dry_mass = self.__Failure_Mode[CompIDWithIndex]['spare_mass']
                if(sp_dry_mass_dummy < sp_dry_mass):
                    sp_dry_mass_dummy = sp_dry_mass
                    #index_sp_dry_mass_dummy = iCnt
                            
                sp_length   = self.__Failure_Mode[CompIDWithIndex]['spare_length'] 
                if(sp_length_dummy < sp_length):
                    sp_length_dummy = sp_length
                    #index_sp_length_dummy = iCnt
                            
                sp_width    = self.__Failure_Mode[CompIDWithIndex]['spare_width'] 
                if(sp_width_dummy < sp_width):
                    sp_width_dummy       = sp_width 
                    #index_sp_width_dummy = iCnt
                
                sp_height   = self.__Failure_Mode[CompIDWithIndex]['spare_height']                         
                if(sp_height_dummy < sp_height):
                    sp_height_dummy = sp_height 
                    #index_sp_height_dummy = iCnt
                    
            # Inspection case
            # ********************************************************************* 
            # ********************************************************************* 
            # ********************************************************************* 
            values = ['INS_PORT', '', '', '',
                      '',
                      self.__entry_point['x coord [m]'].ix[0], 
                      self.__entry_point['y coord [m]'].ix[0],
                      self.__entry_point['zone [-]'].ix[0],  
                      '', '', '', '',
                      '', '', '', '',
                      '', '', '', '',
                      '',
                      sp_dry_mass_dummy, sp_length_dummy, sp_width_dummy, sp_height_dummy,
                      '', '','','',0       
                      ] 
                                               
            outputsForPortSelection.ix[0] = values
            
            om_port = select_port_OM.OM_port(outputsForPortSelection, self.__ports)
    
            
            # Check if there is a solution
            # Currently no possibility to check is implemented in logistic, set it to False
            if False:
                
                self.__errorFlag = True
                         
                ComponentType    = ''
                ComponentSubType = ''
                ComponentID      = ''
                RA_ID            = ''  
                FM_ID            = ''
                deck_area        = ''
                deck_cargo       = ''
                deck_loading     = ''
                sp_dry_mass      = ''
                sp_length        = ''
                sp_width         = ''
                sp_height        = ''
                
                values = ['NoInspPortFound', ComponentID, ComponentType, ComponentSubType, FM_ID, RA_ID,  
                  deck_area, deck_cargo, deck_loading, sp_dry_mass, sp_length, sp_width, sp_height]
                  
                self.__errorTable.ix[iCnt] = values 
                dummyCheckNoSolution = False                       

                
            else:
    
                self.__portDistIndex['inspection'].append(om_port['Distance port-site [km]'])
                self.__portDistIndex['inspection'].append(om_port['Port database index [-]'])
                
                             
            # Repair case
            # ********************************************************************* 
            # ********************************************************************* 
            # ********************************************************************* 
            values = ['OM_PORT', '', '', '',
                      '',
                      self.__entry_point['x coord [m]'].ix[0], 
                      self.__entry_point['y coord [m]'].ix[0],
                      self.__entry_point['zone [-]'].ix[0],
                      '', '', '', '',
                      '', '', '', '',
                      '', '', '', '',
                      '',
                      sp_dry_mass_dummy, sp_length_dummy, sp_width_dummy, sp_height_dummy,
                      '', '','','',0        
                      ] 
                      
                                  
            #self.__om_logistic_outputs = pd.DataFrame(index=[0],columns=keys)
            outputsForPortSelection.ix[0] = values 
         
            """
            Port Selection based on input
            """

            om_port = select_port_OM.OM_port(outputsForPortSelection, self.__ports)
            
            # Check if there is a solution
            # Currently no possibility to check is implemented in logistic, set it to False
            if False:
                
                self.__errorFlag = True
                         
                ComponentType    = ''
                ComponentSubType = ''
                ComponentID      = ''
                RA_ID            = ''  
                FM_ID            = ''
                deck_area        = ''
                deck_cargo       = ''
                deck_loading     = ''
                sp_dry_mass      = ''
                sp_length        = ''
                sp_width         = ''
                sp_height        = ''
                
                values = ['NoRepairPortFound', ComponentID, ComponentType, ComponentSubType, FM_ID, RA_ID,  
                  deck_area, deck_cargo, deck_loading, sp_dry_mass, sp_length, sp_width, sp_height]
                  
                self.__errorTable.ix[iCnt] = values 
                
                dummyCheckNoSolution = False     
                
            else:   
                self.__portDistIndex['repair'].append(om_port['Distance port-site [km]'])
                self.__portDistIndex['repair'].append(om_port['Port database index [-]'])

        if self.__checkNoSolution == True and dummyCheckNoSolution == True:

            #eventsTableNoPoisson = self.__eventsTableNoPoisson            
                           
            indexNoSolutionsFound = []

            # NoSolutionsFound case
            # ********************************************************************* 
            # ********************************************************************* 
            # *********************************************************************
            loop = 0         
            for iCnt in range(0,len(self.__eventsTableNoPoisson)): 
                
                ComponentType       = self.__eventsTableNoPoisson.ComponentType[iCnt]
                ComponentSubType    = self.__eventsTableNoPoisson.ComponentSubType[iCnt]
                ComponentID         = self.__eventsTableNoPoisson.ComponentID[iCnt]
                FM_ID               = self.__eventsTableNoPoisson.FM_ID[iCnt]     
                RA_ID               = self.__eventsTableNoPoisson.RA_ID[iCnt]     
                #repairActionEvents  = self.__eventsTableNoPoisson.repairActionEvents[iCnt]
                repairActionEvents  = self.__startOperationDate
                belongsTo           = self.__eventsTableNoPoisson.belongsTo[iCnt]
                repairActionDateStr = repairActionEvents.strftime(self.__strFormat1)                     
                CompIDWithIndex     = ComponentID + '_' + str(self.__eventsTableNoPoisson.indexFM[iCnt])
                
                # for logistic                
                sp_dry_mass = self.__Failure_Mode[CompIDWithIndex]['spare_mass'] 
                sp_length   = self.__Failure_Mode[CompIDWithIndex]['spare_length'] 
                sp_width    = self.__Failure_Mode[CompIDWithIndex]['spare_width'] 
                sp_height   = self.__Failure_Mode[CompIDWithIndex]['spare_height']                                
                
                d_acc       = ''#self.__Repair_Action[CompIDWithIndex]['duration_accessibility'] 
                d_om        = ''#self.__Repair_Action[CompIDWithIndex]['duration_maintenance']
                helideck    = ''#self.__Farm_OM['helideck'] 
                Hs_acc      = ''#self.__Repair_Action[CompIDWithIndex]['wave_height_max_acc'] 
                Tp_acc      = ''#self.__Repair_Action[CompIDWithIndex]['wave_periode_max_acc']  
                Ws_acc      = ''#self.__Repair_Action[CompIDWithIndex]['wind_speed_max_acc']  
                Cs_acc      = ''#self.__Repair_Action[CompIDWithIndex]['current_speed_max_acc'] 
                Hs_om       = ''#self.__Repair_Action[CompIDWithIndex]['wave_height_max_om'] 
                Tp_om       = ''#self.__Repair_Action[CompIDWithIndex]['wave_periode_max_om']  
                Ws_om       = ''#self.__Repair_Action[CompIDWithIndex]['wind_speed_max_om']  
                Cs_om       = ''#self.__Repair_Action[CompIDWithIndex]['current_speed_max_om'] 
                                    
                if 'Insp' in FM_ID:
                    
                    # for logistic
                    technician  = self.__Inspection[CompIDWithIndex]['number_technicians'] + self.__Inspection[CompIDWithIndex]['number_specialists']                     
                    Dist_port   = self.__portDistIndex['inspection'][0]
                    Port_Index  = self.__portDistIndex['inspection'][1]       
                
                else:
                    
                    # for logistic
                    technician  = self.__Repair_Action[CompIDWithIndex]['number_technicians'] + self.__Repair_Action[CompIDWithIndex]['number_specialists']                     
                    Dist_port   = self.__portDistIndex['repair'][0]
                    Port_Index  = self.__portDistIndex['repair'][1]
                                

                if belongsTo == 'Array':
                    
                    depth      = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['depth']
                    x_coord    = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['x coord'] 
                    y_coord    = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['y coord']
                    zone       = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['zone']  
                    Bathymetry = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['Bathymetry']
                    Soil_type  = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['Soil type']                                          
                
                else:
                    
                    depth      = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['depth']
                    x_coord    = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['x coord'] 
                    y_coord    = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['y coord']
                    zone       = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['zone']  
                    Bathymetry = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['Bathymetry']
                    Soil_type  = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['Soil type']                   


                if belongsTo == 'Array':
                    
                    if 'Substation' in ComponentType:
                        ComponentTypeLogistic = 'collection point'
                        ComponentIDLogistic   = ComponentID
                        
                    elif 'subhub' in ComponentType:
                        ComponentTypeLogistic = 'collection point'
                        ComponentIDLogistic   = ComponentID
                        
                    elif 'Export Cable' in ComponentType:
                        ComponentTypeLogistic = 'static cable'
                        ComponentIDLogistic   = int(ComponentID[-3:len(ComponentID)])
                        
                    else:
                        ComponentTypeLogistic = ComponentType
                        ComponentIDLogistic   = ComponentID                        
                
                else:
                    
                    # Adjustmet of the names to logistic
                    # The name of subsystems in logistic and RAM are differnt             
                    if 'Dynamic cable' in ComponentSubType:
                        ComponentTypeLogistic = 'dynamic cable'
                        # problem with logistic database
                        ComponentIDLogistic   = 0#int(ComponentID[-3:len(ComponentID)])
                        
                    elif 'Mooring line' in ComponentSubType:
                        ComponentTypeLogistic = 'mooring line'
                        ComponentIDLogistic   = int(ComponentID[-3:len(ComponentID)])
                        
                    elif 'Foundation' in ComponentSubType:
                        ComponentTypeLogistic = 'foundation'
                        ComponentIDLogistic   = ComponentID
                        
                    else:
                        ComponentTypeLogistic = ComponentType
                        ComponentIDLogistic   = ComponentID
                        
                    if 'device' in ComponentTypeLogistic:
                        ComponentTypeLogistic = 'device'
                
                  
                # Calc logistic functions
                start_time_logistic = timeit.default_timer()                    
                            
                # Values for logistic
                values = [FM_ID, ComponentTypeLogistic, ComponentSubType, ComponentIDLogistic,
                          depth,
                          x_coord, 
                          y_coord,
                          zone,  
                          repairActionDateStr, d_acc, d_om, str(helideck),
                          Hs_acc, Tp_acc, Ws_acc, Cs_acc,
                          Hs_om, Tp_om, Ws_om, Cs_om,
                          technician,
                          sp_dry_mass, sp_length, sp_width, sp_height,
                          Dist_port, Port_Index,
                          Bathymetry,
                          Soil_type,
                          self.__PrepTimeCalcUnCoMa
                          ]                    
                                              
                #self.__om_logistic_outputs = pd.DataFrame(index=[0],columns=keys)
                self.__wp6_outputsForLogistic.ix[0] = values
                                
                # apply dafety factors in vessels parameters
                ports, vessels, equipments = safety_factors(copy.deepcopy(self.__ports), 
                                                            copy.deepcopy(self.__vessels),
                                                            copy.deepcopy(self.__equipments), 
                                                            copy.deepcopy(self.__port_sf), 
                                                            copy.deepcopy(self.__vessel_sf), 
                                                            copy.deepcopy(self.__eq_sf))
                
                # Collecting relevant port information                
                om_port_index = self.__wp6_outputsForLogistic['Port_Index [-]'].ix[0]
                #om_port_distance = self.__wp6_outputsForLogistic['Dist_port [km]'].ix[0]
                om_port = {}
                om_port['Selected base port for installation'] = ports.ix[om_port_index]
            
                """
                 Initialising logistic operations and logistic phase
                """
                logOp = logOp_init(self.__schedule_OLC)                    
                                                    
                logPhase_om = logPhase_om_init(logOp, vessels, equipments, self.__wp6_outputsForLogistic)
                                
                # Select the suitable Log phase id
                log_phase_id = logPhase_select(self.__wp6_outputsForLogistic)
                log_phase = logPhase_om[log_phase_id]
                log_phase.op_ve_init = log_phase.op_ve
            
                """
                 Assessing the O&M logistic phase requested
                """
            
                # Initialising the output dictionary to be passed to the O&M module
                om_log = {'port': om_port,
                          'requirement': {},
                          'eq_select': {},
                          've_select': {},
                          'combi_select': {},
                          'schedule': {},
                          'cost': {},
                          'optimal': {},
                          'risk': {},
                          'envir': {},
                          'findSolution': {}
                          }
            
                # Characterizing the logistic requirements
                om_log['requirement'] = feas_om(log_phase, log_phase_id, self.__wp6_outputsForLogistic, self.__device,
                                                self.__sub_device, self.__collection_point, self.__connectors,
                                                self.__dynamic_cable, self.__static_cable)
            
                # Selecting the maritime infrastructure satisfying the logistic requirements
                om_log['eq_select'], log_phase = select_e(om_log, log_phase)
                om_log['ve_select'], log_phase = select_v(om_log, log_phase)
            
                # Matching requirements to ensure compatiblity of combinations of
                # port/vessel(s)/equipment leading to feasible logistic solutions
                om_log['combi_select'], log_phase, MATCH_FLAG = compatibility_ve(om_log, log_phase,om_port['Selected base port for installation'])
            
                stop_time_logistic = timeit.default_timer()
                if MATCH_FLAG == 'NoSolutions':
                    ves_req = {'deck area [m^2]': om_log['requirement'][5]['deck area'],
                       'deck cargo [t]': om_log['requirement'][5]['deck cargo'],
                       'deck loading [t/m^2]': om_log['requirement'][5]['deck loading']}
                   
                    #om_log['findSolution'] = 'NoSolutionsFound'
                    
                    indexNoSolutionsFound.append([iCnt,ves_req,sp_dry_mass,sp_length,sp_width,sp_height])
                    
                    if self.__dtocean_operations_PRINT_FLAG == True:                                                   
                        print 'WP6: loop = ', loop
                        print 'WP6: ComponentID = ', ComponentID 
                        print 'WP6: RA_ID = ', RA_ID 
                        print 'WP6: FM_ID = ', FM_ID
                        print 'WP6: values = ', values 
                        print 'NoSolution'
                        print 'calcLogistic: Simulation Duration [s]: ' + str(stop_time_logistic - start_time_logistic)
                        print ''
                        print '' 
                '''else:
                    if self.__dtocean_operations_PRINT_FLAG == True:                                                     
                        print 'WP6: loop = ', loop
                        print 'WP6: ComponentID = ', ComponentID 
                        print 'WP6: RA_ID = ', RA_ID 
                        print 'WP6: FM_ID = ', FM_ID
                        print 'WP6: values = ', values 
                        print 'Solution'
                        print 'calcLogistic: Simulation Duration [s]: ' + str(stop_time_logistic - start_time_logistic)
                        print ''
                        print '''''
                                                                
                loop = loop + 1
                                            
            if len(indexNoSolutionsFound) != 0: 
                
                self.__errorFlag = True
                        
                for iCnt in range(0,len(indexNoSolutionsFound)): 
                    
                    index            = indexNoSolutionsFound[iCnt][0]
                    ComponentType    = self.__eventsTableNoPoisson.ComponentType[index]
                    ComponentSubType = self.__eventsTableNoPoisson.ComponentSubType[index]
                    ComponentID      = self.__eventsTableNoPoisson.ComponentID[index]
                    RA_ID            = self.__eventsTableNoPoisson.RA_ID[index]  
                    FM_ID            = self.__eventsTableNoPoisson.FM_ID[index]
                    deck_area        = indexNoSolutionsFound[iCnt][1]['deck area [m^2]']
                    deck_cargo       = indexNoSolutionsFound[iCnt][1]['deck cargo [t]']
                    deck_loading     = indexNoSolutionsFound[iCnt][1]['deck loading [t/m^2]']
                    sp_dry_mass      = indexNoSolutionsFound[iCnt][2]
                    sp_length        = indexNoSolutionsFound[iCnt][3]
                    sp_width         = indexNoSolutionsFound[iCnt][4] 
                    sp_height        = indexNoSolutionsFound[iCnt][5]
                    
                    values = ['NoSolutionsFound', ComponentID, ComponentType, ComponentSubType, FM_ID, RA_ID,  
                      deck_area, deck_cargo, deck_loading, sp_dry_mass, sp_length, sp_width, sp_height]
                      
                    self.__errorTable.ix[iCnt] = values
        return 
        
       
    def __initCalc(self):

        '''__initCalc function: some initialisation calculations  
                                                      
        Args:              
            no arguments
        
        Attributes:         
            no attributes                  
 
        Returns:
            no returns
      
        ''' 
        
        # make an instance of RAM
        testNew = True
        if testNew == False:        
        
            input_variables = Variables(self.__operationTimeYear * self.__yearDays * self.__dayHours,       # mission time in hours
                                        0.4 * self.__operationTimeYear * self.__yearDays * self.__dayHours, # target mean time to failure in hours 
                                        self.__systype,                                                     # Options: 'tidefloat', 'tidefixed', 'wavefloat', 'wavefixed'
                                        self.__eleclayout,                                                  # Options: 'radial', 'singlesidedstring', 'doublesidedstring', 'multiplehubs'  
                                        self.__elechierdict,                                                # electrical system hierarchy 
                                        self.__elecbomeg,                                                   # electrical system bill of materials                   
                                        self.__moorhiereg,                                                  # mooring and foundation system hierarchy
                                        self.__moorbomeg,                                                   # mooring and foundation system bill of materials
                                        self.__userhiereg,                                                  # dummy user-defined hierarchy
                                        self.__userbomeg,                                                   # user-defined bill of materials                          
                                        self.__db) 
                                        
            # new RAM
        else:
            
            input_variables = Variables(self.__operationTimeYear * self.__yearDays * self.__dayHours,       # mission time in hours
                                        0.4 * self.__operationTimeYear * self.__yearDays * self.__dayHours, # target mean time to failure in hours 
                                        self.__systype,                                                     # Options: 'tidefloat', 'tidefixed', 'wavefloat', 'wavefixed'                                   
                                        self.__db,                                                          # user-defined bill of materials 
                                        self.__eleclayout,                                                  # Options: 'radial', 'singlesidedstring', 'doublesidedstring', 'multiplehubs'                                   
                                        self.__elechierdict,                                                # electrical system hierarchy                                     
                                        self.__elecbomeg,                                                   # electrical system bill of materials                                                      
                                        self.__moorhiereg,                                                  # mooring and foundation system hierarchy
                                        self.__moorbomeg,
                                        self.__userhiereg,                                                  # dummy user-defined hierarchy
                                        self.__userbomeg)                                                   # mooring and foundation system bill of materials
                                                                          
        # Make an instance of RAM   
        self.__ramPTR = Main(input_variables)                        
 
        # calculation of RAM      
        self.__ram = self.__calcRAM()    
       
        # make instance of arrayClass
        self.__arrayPTR = array(self.__startOperationDate, self.__operationTimeDay, self.__rcompvalues,
                                self.__rsubsysvalues, self.__eleclayout, self.__systype, self.__UnCoMa_eventsTableKeys,
                                self.__NoPoisson_eventsTableKeys, self.__dtocean_operations_PRINT_FLAG, self.__readFailureRateFromRAM)        
        
        
        # Read from RAM and calculate the poisson events of failure rates 
        self.__arrayDict,self.__UnCoMa_eventsTable, self.__eventsTableNoPoisson = self.__arrayPTR.executeFEM(self.__arrayDict, 
                                                                           self.__UnCoMa_eventsTable,
                                                                           self.__eventsTableNoPoisson,
                                                                           self.__Component,
                                                                           self.__Failure_Mode,
                                                                           self.__Repair_Action,
                                                                           self.__Inspection,
                                                                           self.__annual_Energy_Production_perD) 

        #arrayDict = self.__arrayDict                                                                                                                                    
        
        if self.__Farm_OM['calendar_based_maintenance'] == True or self.__Farm_OM['condition_based_maintenance'] == True:
            
            loopCalendar  = 0
            loopCondition = 0
            #eventsTableNoPoisson = self.__eventsTableNoPoisson            
            
            for iCnt in range(0, len(self.__eventsTableNoPoisson)):
                
                ComponentID        = self.__eventsTableNoPoisson.ComponentID[iCnt]
                ComponentSubType   = self.__eventsTableNoPoisson.ComponentSubType[iCnt]
                ComponentType      = self.__eventsTableNoPoisson.ComponentType[iCnt]
                FM_ID              = self.__eventsTableNoPoisson.FM_ID[iCnt]
                RA_ID              = self.__eventsTableNoPoisson.RA_ID[iCnt]
                belongsTo          = self.__eventsTableNoPoisson.belongsTo[iCnt]
                indexFM            = self.__eventsTableNoPoisson.indexFM[iCnt]
                failureRate        = self.__eventsTableNoPoisson.failureRate[iCnt]
                               
                flagCaBaMa = False
                # ['startActionDate', 'endActionDate', 'currentStartActionDate', 'currentEndActionDate', 'belongsTo', 'belongsToSort', 'ComponentType', 'ComponentSubType', 'ComponentID', 'FM_ID', 'indexFM', 'RA_ID']
                if self.__Farm_OM['calendar_based_maintenance'] == True:
                    
                    if 'device' in belongsTo:
                        belongsToSort = 'device'
                    else:
                        belongsToSort = belongsTo
                    
                    flagDummy = False
                    startActionDate = pd.to_datetime(self.__Component.at['start_date_calendar_based_maintenance',ComponentID]).to_datetime()
                    endActionDate   = pd.to_datetime(self.__Component.at['end_date_calendar_based_maintenance',ComponentID]).to_datetime()
                    interval  = self.__Component.at['interval_calendar_based_maintenance',ComponentID]
                    
                    if type(startActionDate) != datetime.datetime or type(endActionDate) != datetime.datetime or math.isnan(interval) == True:
                        flagDummy = True                    
                                        
                    if flagDummy == False:
                        
                        flagCaBaMa = True
                      
                        if (self.__startOperationDate <= startActionDate and startActionDate <= self.__endOperationDate):
                            
                            startActionDateDummy = startActionDate
                            endActionDateDummy = endActionDate
                                                                                   
                            while startActionDateDummy < self.__endOperationDate:   
                                values = [startActionDateDummy, endActionDateDummy, startActionDateDummy, endActionDateDummy, belongsTo, belongsToSort, ComponentType, ComponentSubType, ComponentID, FM_ID, indexFM, RA_ID, 0, 0]
                                self.__CaBaMa_eventsTable.ix[loopCalendar] = values  
                                loopCalendar = loopCalendar + 1                
                                startActionDateDummy = startActionDateDummy + timedelta(days = interval*self.__yearDays) 
                                endActionDateDummy   = endActionDateDummy   + timedelta(days = interval*self.__yearDays)
                                                 
                if self.__Farm_OM['condition_based_maintenance'] == True: 
                    
                    flagDummy = False
                    startActionDate = pd.to_datetime(self.__Component.at['start_date_calendar_based_maintenance',ComponentID]).to_datetime()
                    endActionDate   = pd.to_datetime(self.__Component.at['end_date_calendar_based_maintenance',ComponentID]).to_datetime()
                    threshold = self.__Component.at['soh_threshold',ComponentID]/100.0
                                        
                    if type(startActionDate) != datetime.datetime or type(endActionDate) != datetime.datetime or threshold < 0 or 1 < threshold or math.isnan(threshold) == True:
                        flagDummy = True
    
                    if flagDummy == False:
                        
                        currentStartActionDate = self.__startOperationDate
                        
                        failureRateDummy = failureRate - failureRate*(self.__failureRateFactorCoBaMa/100.0)
                                               
                        poissonValue = poissonProcess(currentStartActionDate, self.__operationTimeDay, failureRateDummy/self.__yearDays)
                        
                        self.__arrayDict[ComponentID]['CoBaMa_FR List'][indexFM-1] = failureRateDummy
                        self.__arrayDict[ComponentID]['CoBaMa_initOpEventsList'][indexFM-1] = poissonValue
                        
                        if 0 < len(poissonValue):
                         
                            currentEndActionDate = poissonValue[0]
                            dummy = (((currentEndActionDate - currentStartActionDate).total_seconds()/3600)*(1.0-threshold))  
                            AlarmDate = self.__startOperationDate + timedelta(hours = dummy)       
                            
                            values = [startActionDate, endActionDate, currentStartActionDate, currentEndActionDate,
                                      AlarmDate, belongsTo, ComponentType, ComponentSubType, ComponentID,
                                      FM_ID, indexFM, RA_ID, threshold, failureRateDummy, flagCaBaMa]
                            self.__CoBaMa_eventsTable.ix[loopCondition] = values  
                            loopCondition = loopCondition + 1   
                                                                              
            # sort of calendar_based_maintenance
            if self.__Farm_OM['calendar_based_maintenance'] == True and loopCalendar != 0:                           
                                               
                # 1: sort of CaBaMa_eventsTable                
                self.__CaBaMa_eventsTable.sort(columns=['startActionDate', 'ComponentSubType', 'FM_ID'], inplace=True)
                
                # 2: sort of CaBaMa_eventsTable 
                self.__CaBaMa_eventsTable.sort(columns=['startActionDate', 'belongsToSort'], inplace=True)
               
                # start index with 0
                self.__CaBaMa_eventsTable.reset_index(drop=True, inplace=True)
                            
            # sort of condition_based_maintenance
            if self.__Farm_OM['condition_based_maintenance'] == True and 0 < len(self.__CoBaMa_eventsTable):                 
                
                # sort of CoBaMa_eventsTable                
                self.__CoBaMa_eventsTable.sort(columns=['currentAlarmDate'], inplace=True)
                
                # start index with 0
                self.__CoBaMa_eventsTable.reset_index(drop=True, inplace=True)
                

        #CoBaMa_eventsTable = self.__CoBaMa_eventsTable
        #CaBaMa_eventsTable = self.__CaBaMa_eventsTable
        
        if self.__Farm_OM['corrective_maintenance'] == True and 0 < len(self.__UnCoMa_eventsTable):  
            # remove the same entries from self.__UnCoMa_eventsTable in case of condition_based_maintenance
            if self.__Farm_OM['condition_based_maintenance'] == True and 0 < len(self.__CoBaMa_eventsTable):
                for iCnt in range(0, len(self.__CoBaMa_eventsTable)):
                   
                    belongsTo          = self.__CoBaMa_eventsTable.belongsTo[iCnt]
                    ComponentType      = self.__CoBaMa_eventsTable.ComponentType[iCnt]
                    ComponentSubType   = self.__CoBaMa_eventsTable.ComponentSubType[iCnt]           
                    ComponentID        = self.__CoBaMa_eventsTable.ComponentID[iCnt]
                    indexFM            = self.__CoBaMa_eventsTable.indexFM[iCnt]               
                    FM_ID              = self.__CoBaMa_eventsTable.FM_ID[iCnt]
                    RA_ID              = self.__CoBaMa_eventsTable.RA_ID[iCnt]
                    
                    dummyTable = self.__UnCoMa_eventsTable.loc[(self.__UnCoMa_eventsTable['belongsTo'] == belongsTo) & \
                    (self.__UnCoMa_eventsTable['ComponentType'] == ComponentType) & \
                    (self.__UnCoMa_eventsTable['ComponentSubType'] == ComponentSubType) & \
                    (self.__UnCoMa_eventsTable['ComponentID'] == ComponentID) & \
                    (self.__UnCoMa_eventsTable['indexFM'] == indexFM) & \
                    (self.__UnCoMa_eventsTable['FM_ID'] == FM_ID) & \
                    (self.__UnCoMa_eventsTable['RA_ID'] == RA_ID)] 
                    
                    self.__UnCoMa_eventsTable.drop(dummyTable.index, inplace = True)
                    
                # start index with 0
                self.__UnCoMa_eventsTable.reset_index(drop=True, inplace=True)
                         
            # change of self.__UnCoMa_eventsTable concerning
            for iCnt in range(0, len(self.__UnCoMa_eventsTable)):
                
                # shift repairActionEvents  
                failureEvents   = self.__UnCoMa_eventsTable.failureEvents[iCnt]
                ComponentID     = self.__UnCoMa_eventsTable.ComponentID[iCnt]
                FM_ID           = self.__UnCoMa_eventsTable.FM_ID[iCnt]    
                indexFM         = self.__UnCoMa_eventsTable.indexFM[iCnt]
                CompIDWithIndex = ComponentID + '_' + str(indexFM)
                  
                shiftHoursDummy1 = 0  
                logic = 'Insp' in FM_ID
                
                if not logic:
                    
                    # repairAction
                    shiftHoursDummy1 = self.__Repair_Action[CompIDWithIndex]['delay_spare']
                    shiftHoursDummy2 = self.__Repair_Action[CompIDWithIndex]['delay_crew'] + self.__Repair_Action[CompIDWithIndex]['delay_organisation'] 
                else:
                    # inspection
                    shiftHoursDummy1 = 0
                    shiftHoursDummy2 = self.__Inspection[CompIDWithIndex]['delay_crew'] + self.__Inspection[CompIDWithIndex]['delay_organisation'] 
                    
                shiftHours       = float (max(shiftHoursDummy1,shiftHoursDummy2))  
                shiftDate        = failureEvents + timedelta(hours = shiftHours) 
                self.__UnCoMa_eventsTable.loc[iCnt, 'repairActionEvents'] = shiftDate
    
            # sort of eventsTable
            self.__UnCoMa_eventsTable.sort(columns=self.__UnCoMa_eventsTableKeys[1], inplace=True)      
            
            # start index with 0
            self.__UnCoMa_eventsTable.reset_index(drop=True, inplace=True)
                        
        return
               
    
    # write the operation times of Device (downtime and operation)        
    def __postCalculation(self):
                
        '''__postCalculation function: some post calculations  
                                                      
        Args:              
            no arguments
        
        Attributes:         
            no attributes                  
 
        Returns:
            no returns
      
        ''' 

        # Calculation of the 
        # self.__outputsOfWP6['lcoeOfArray [Euro/KWh]'] : LCOE of array (float) [Euro/kWh]                
        # self.__outputsOfWP6['annualEnergyOfDevices [Wh]'] : Annual energy of each devices (list of float) [Wh] 
        # self.__outputsOfWP6['annualDownTimeOfDevices [h]'] : Annual down time of each devices (list of float) [h] 
        # self.__outputsOfWP6['annualEnergyOfArray [Wh]'] : Annual energy of array (float) [Wh]                  
        # self.__outputsOfWP6['annualCapexOfArray [Euro]'] : Annual CAPEX of array in case of condition based maintenance strategy (float) [Euro/kWh]                 
        # self.__outputsOfWP6['annualOpexOfArray [Euro]'] : Annual OPEX of array (float) [Euro/kWh] 
        
        dummyOpexAll = 0
        dummyEnergyAll = 0
        dummyDownTime = 0
        #dummyDownTimeAll = 0
        
        #arrayDict = self.__arrayDict
        
        keys = self.__arrayDict.keys()   
        
        for iCnt in range(0,len(keys)): 
            
            # calculation of Opex 
            logic = 'Hydrodynamic' in keys[iCnt] or 'Pto' in keys[iCnt] or \
            'Control' in keys[iCnt] or 'Support structure' in keys[iCnt] or 'Mooring line' in keys[iCnt] or \
            'Foundation' in keys[iCnt] or 'Dynamic cable' in keys[iCnt] or 'Array elec sub-system' in keys[iCnt]
            
            # OPEX of the all components of array and all devices                                 
            if not logic:

                # corrective_maintenance
                if self.__Farm_OM['corrective_maintenance'] == True:
                
                    for iCnt1 in range(0,len(self.__arrayDict[keys[iCnt]]['UnCoMaCostOM'])):
                        dummyOpexAll = dummyOpexAll + self.__arrayDict[keys[iCnt]]['UnCoMaCostOM'][iCnt1]
                                                
                    for iCnt1 in range(0,len(self.__arrayDict[keys[iCnt]]['UnCoMaCostLogistic'])):
                        dummyOpexAll = dummyOpexAll + self.__arrayDict[keys[iCnt]]['UnCoMaCostLogistic'][iCnt1]
                        
                # condition_based_maintenance    
                if self.__Farm_OM['condition_based_maintenance'] == True:
                
                    for iCnt1 in range(0,len(self.__arrayDict[keys[iCnt]]['CoBaMaCostOM'])):
                        dummyOpexAll = dummyOpexAll + self.__arrayDict[keys[iCnt]]['CoBaMaCostOM'][iCnt1]
                                                
                    for iCnt1 in range(0,len(self.__arrayDict[keys[iCnt]]['CoBaMaCostLogistic'])):
                        dummyOpexAll = dummyOpexAll + self.__arrayDict[keys[iCnt]]['CoBaMaCostLogistic'][iCnt1]                    
                    
                # calendar_based_maintenance
                if self.__Farm_OM['calendar_based_maintenance'] == True:
                
                    for iCnt1 in range(0,len(self.__arrayDict[keys[iCnt]]['CaBaMaCostOM'])):
                        dummyOpexAll = dummyOpexAll + self.__arrayDict[keys[iCnt]]['CaBaMaCostOM'][iCnt1]
                                                
                    for iCnt1 in range(0,len(self.__arrayDict[keys[iCnt]]['CaBaMaCostLogistic'])):
                        dummyOpexAll = dummyOpexAll + self.__arrayDict[keys[iCnt]]['CaBaMaCostLogistic'][iCnt1]                    
                                        
            
            # calculation of downtime 
            if 'device' in keys[iCnt]:
                
                dummyDownTime = 0
                    
                # corrective_maintenance
                if self.__Farm_OM['corrective_maintenance'] == True:
                
                    for iCnt1 in range(0,len(self.__arrayDict[keys[iCnt]]['UnCoMaOpEventsDuration'])):
                        dummyDownTime = dummyDownTime + self.__arrayDict[keys[iCnt]]['UnCoMaOpEventsDuration'][iCnt1]
                            
                # condition_based_maintenance    
                if self.__Farm_OM['condition_based_maintenance'] == True:
                
                    for iCnt1 in range(0,len(self.__arrayDict[keys[iCnt]]['CoBaMaOpEventsDuration'])):
                        dummyDownTime = dummyDownTime + self.__arrayDict[keys[iCnt]]['CoBaMaOpEventsDuration'][iCnt1]  
                    
                # calendar_based_maintenance
                if self.__Farm_OM['calendar_based_maintenance'] == True:
                
                    for iCnt1 in range(0,len(self.__arrayDict[keys[iCnt]]['CaBaMaOpEventsDuration'])):
                        dummyDownTime = dummyDownTime + self.__arrayDict[keys[iCnt]]['CaBaMaOpEventsDuration'][iCnt1]
                    
                    
                self.__arrayDict[keys[iCnt]]['DownTime'] = dummyDownTime
                
                powerWP2 = float(self.__arrayDict[keys[iCnt]]['AnnualEnergyWP2']) / (self.__dayHours*self.__yearDays)
                
                deviceOperationTime = self.__operationTimeDay*self.__dayHours - dummyDownTime
                # for missionTime [year] 
                energyPerDevice = powerWP2 * deviceOperationTime
                
                if self.__operationTimeYear != 0: 
                    self.__arrayDict[keys[iCnt]]['AnnualEnergyWP6'] = float(energyPerDevice) / self.__operationTimeYear
                
                else: 
                    self.__arrayDict[keys[iCnt]]['AnnualEnergyWP6'] = 0.0
                
         
                index = int(keys[iCnt].rsplit('device')[1])-1
                
                # list -> Annual energy of each devices [Wh]
                self.__outputsOfWP6['annualEnergyOfDevices [Wh]'][index] = self.__arrayDict[keys[iCnt]]['AnnualEnergyWP6']
                
                # list -> annualDownTimeOfDevices [h]
                if self.__operationTimeYear != 0:                 
                    self.__outputsOfWP6['annualDownTimeOfDevices [h]'][index] = round(float(dummyDownTime) / self.__operationTimeYear,0)
                else:
                    self.__outputsOfWP6['annualDownTimeOfDevices [h]'][index] = 0.0
                
                                
                dummyEnergyAll = dummyEnergyAll + energyPerDevice
                 
                self.__outputsOfWP6['annualEnergyOfDevices [Wh]'][index] = round(self.__outputsOfWP6['annualEnergyOfDevices [Wh]'][index] ,0)
                
 
        # float -> Annual energy of array [Wh]  
        if self.__operationTimeYear != 0:     
            self.__outputsOfWP6['annualEnergyOfArray [Wh]'] = float(dummyEnergyAll) / self.__operationTimeYear
        else:     
            self.__outputsOfWP6['annualEnergyOfArray [Wh]'] = 0.0            
            
        
        # float -> Annual OPEX of array in case of condition based maintenance strategy [Euro]
        if self.__operationTimeYear != 0: 
            self.__outputsOfWP6['annualOpexOfArray [Euro]'] = float(dummyOpexAll) / self.__operationTimeYear
        else: 
            self.__outputsOfWP6['annualOpexOfArray [Euro]'] = 0.0
        
        # float -> Annual CAPEX of array in case of condition based maintenance strategy [Euro]
        self.__outputsOfWP6['CapexOfArray [Euro]'] = round(self.__outputsOfWP6['CapexOfArray [Euro]'],1)
        
        # LCOE of array [Euro/kWh]
        if (self.__outputsOfWP6['annualEnergyOfArray [Wh]']/1000.0) != 0:
            self.__outputsOfWP6['lcoeOfArray [Euro/KWh]'] = float(self.__outputsOfWP6['annualOpexOfArray [Euro]']) / (self.__outputsOfWP6['annualEnergyOfArray [Wh]']/1000.0)
        else:
            self.__outputsOfWP6['lcoeOfArray [Euro/KWh]'] = 0.0       
        
        self.__outputsOfWP6['lcoeOfArray [Euro/KWh]']   = round(self.__outputsOfWP6['lcoeOfArray [Euro/KWh]'],4)
        self.__outputsOfWP6['annualEnergyOfArray [Wh]'] = round(self.__outputsOfWP6['annualEnergyOfArray [Wh]'],0)
        self.__outputsOfWP6['annualOpexOfArray [Euro]'] = round(self.__outputsOfWP6['annualOpexOfArray [Euro]'],0)
        
        
        # Pandas series -> Signals for environmental assessment.
        if self.__Farm_OM['corrective_maintenance'] == True:            
            self.__outputsOfWP6['env_assess [-]']['UnCoMa_eventsTable'] = pd.Series(self.__UnCoMa_dictEnvAssess)
        
        if self.__Farm_OM['calendar_based_maintenance'] == True:
         self.__outputsOfWP6['env_assess [-]']['CaBaMa_eventsTable'] = pd.Series(self.__CaBaMa_dictEnvAssess)
        
        if self.__Farm_OM['condition_based_maintenance'] == True:
            self.__outputsOfWP6['env_assess [-]']['CoBaMa_eventsTable'] = pd.Series(self.__CoBaMa_dictEnvAssess)
          
        
        # for maintenance plans
        self.__outputsOfWP6['eventTables [-]']['UnCoMa_eventsTable'] = self.__UnCoMa_outputEventsTable
        self.__outputsOfWP6['eventTables [-]']['CoBaMa_eventsTable'] = self.__CoBaMa_outputEventsTable
        self.__outputsOfWP6['eventTables [-]']['CaBaMa_eventsTable'] = self.__CaBaMa_outputEventsTable
        
        return 
    
    # Update poisson events    
    def __updatePoissonEvents(self):
              
        '''__updatePoissonEvents function: Updates the poisson events
                                                      
        Args:              
            no arguments
        
        Attributes:         
            no attributes                  
 
        Returns:
            no returns
      
        ''' 
 
        belongsTo        = self.__UnCoMa_eventsTable.belongsTo[0]
        ComponentID      = self.__UnCoMa_eventsTable.ComponentID[0]
        
        #array = self.__arrayDict
        #event = self.__UnCoMa_eventsTable
	
        if belongsTo == 'Array' and 'All' in  self.__arrayDict[ComponentID]['Breakdown']:	
            # shift of the rows of eventTables                                                          
            for iCnt in range(self.__actIdxOfUnCoMa+1, len(self.__UnCoMa_eventsTable)):                 
                
                shiftDate = self.__UnCoMa_eventsTable.failureEvents[iCnt] + timedelta(hours = self.__totalSeaTimeHour) 
                self.__UnCoMa_eventsTable.loc[iCnt, 'failureEvents'] = shiftDate 
                
                shiftDate = self.__UnCoMa_eventsTable.repairActionEvents[iCnt] + timedelta(hours = self.__totalSeaTimeHour) 
                self.__UnCoMa_eventsTable.loc[iCnt, 'repairActionEvents'] = shiftDate 
                
        else:
            # shift of the rows of eventTables                                                          
            for iCnt in range(self.__actIdxOfUnCoMa+1, len(self.__UnCoMa_eventsTable)): 
                if self.__UnCoMa_eventsTable.loc[iCnt, 'ComponentID'] == ComponentID and self.__UnCoMa_eventsTable.loc[iCnt, 'belongsTo'] in self.__arrayDict[ComponentID]['Breakdown']:                                  
                    
                    shiftDate = self.__UnCoMa_eventsTable.failureEvents[iCnt] + timedelta(hours = self.__totalSeaTimeHour) 
                    self.__UnCoMa_eventsTable.loc[iCnt, 'failureEvents'] = shiftDate
                    
                    shiftDate = self.__UnCoMa_eventsTable.repairActionEvents[iCnt] + timedelta(hours = self.__totalSeaTimeHour) 
                    self.__UnCoMa_eventsTable.loc[iCnt, 'repairActionEvents'] = shiftDate
                    
        # sort of eventsTable
        self.__UnCoMa_eventsTable.sort(columns=self.__UnCoMa_eventsTableKeys[1], inplace=True)      
                        
        return
                  
    def __calcCostOfOM(self, FM_ID, CompIDWithIndex):
        
        '''__calcCostOfOM function: calculation of the cost of O&M 
                                                      
        Args:              
            FM_ID           : id of the failure mode  
            CompIDWithIndex : component id with index 
        
        Attributes:         
            no attributes                  
 
        Returns:
            omCostValueSpare : cost of spare
            omCostValue      : cost of spare and labor 
      
        ''' 
        

        # summer
        self.__summerTime = False 
        
        # winter
        self.__winterTime = False                               
            
          # repairActionDate is in summer time or winter time  
        if self.__repairActionDate.month in [3, 4, 5, 6, 7, 8]:
            self.__summerTime = True
               
        else:  
            self.__winterTime = True
                                                                                           
        self.__totalWeekEndWorkingHour = 0
        self.__totalNotWeekEndWorkingHour = 0               
        self.__totalNightWorkingHour = 0
        self.__totalDayWorkingHour = 0 
        
        if  self.__summerTime == True and self.__Farm_OM['workdays_summer'] <= 7:
            divMod = divmod(self.__totalSeaTimeHour/self.__dayHours, self.__Farm_OM['workdays_summer'])
            self.__totalNotWeekEndWorkingHour = divMod[0] * self.__dayHours
            self.__totalWeekEndWorkingHour = self.__totalSeaTimeHour - self.__totalNotWeekEndWorkingHour
                            
        if  self.__winterTime == True and self.__Farm_OM['workdays_winter'] <= 7:
            divMod = divmod(self.__totalSeaTimeHour/self.__dayHours, self.__Farm_OM['workdays_winter'])
            self.__totalNotWeekEndWorkingHour = divMod[0] * self.__dayHours
            self.__totalWeekEndWorkingHour = self.__totalSeaTimeHour - self.__totalNotWeekEndWorkingHour
                        
        # calc of self.__totalDayWorkingHour and self.__totalNightWorkingHour
        dummyDayWorkingDate = datetime.datetime(self.__departOpDate.year, self.__departOpDate.month, self.__departOpDate.day) + timedelta(hours = self.__startDayWorkingHour)
        dummyNightWorkingDate = datetime.datetime(self.__departOpDate.year, self.__departOpDate.month, self.__departOpDate.day) + timedelta(hours = self.__startDayWorkingHour+12)
        
        diffHour = (self.__departOpDate - dummyDayWorkingDate).total_seconds() // 3600
        
        if 0 <= diffHour and diffHour < 12:
            # self.__totalDayWorkingHour
            workingHourRelToDiffHour = (self.__endOpDate - dummyDayWorkingDate).total_seconds() // 3600
            divMod = divmod(workingHourRelToDiffHour, self.__dayHours)
            
            self.__totalDayWorkingHour = (divMod[0]*self.__dayHours/2.0)
            
            if divMod[1] <= 12:
                self.__totalDayWorkingHour = self.__totalDayWorkingHour + divMod[1]
            else:
                self.__totalDayWorkingHour = self.__totalDayWorkingHour + self.__dayHours/2.0
                               
            self.__totalDayWorkingHour = self.__totalDayWorkingHour- diffHour
            self.__totalNightWorkingHour = self.__totalSeaTimeHour - self.__totalDayWorkingHour
        
        else:
            # self.__totalNightWorkingHour
            workingHourRelToDiffHour = (self.__endOpDate - dummyNightWorkingDate).total_seconds() // 3600
            divMod = divmod(workingHourRelToDiffHour, self.__dayHours)
            
            self.__totalNightWorkingHour = (divMod[0]*self.__dayHours/2.0)
            
            if divMod[1] <= 12:
                self.__totalNightWorkingHour = self.__totalNightWorkingHour + divMod[1]
            else:
                self.__totalNightWorkingHour = self.__totalNightWorkingHour + self.__dayHours/2.0
                               
            self.__totalNightWorkingHour = self.__totalNightWorkingHour- diffHour
            self.__totalDayWorkingHour = self.__totalSeaTimeHour - self.__totalNightWorkingHour              
 
        
        
        totalDummy = self.__totalWeekEndWorkingHour + self.__totalNotWeekEndWorkingHour
        
        if(self.__totalWeekEndWorkingHour + self.__totalNotWeekEndWorkingHour != 0):
            nightNotWeekend = self.__totalNightWorkingHour*self.__totalNotWeekEndWorkingHour/totalDummy
            nightWeekend    = self.__totalNightWorkingHour*self.__totalWeekEndWorkingHour/totalDummy

            dayNotWeekend   = self.__totalDayWorkingHour*self.__totalNotWeekEndWorkingHour/totalDummy
            dayWeekend      = self.__totalDayWorkingHour*self.__totalWeekEndWorkingHour/totalDummy
        else:
            nightNotWeekend = 0.0
            nightWeekend    = 0.0

            dayNotWeekend   = 0.0
            dayWeekend      = 0.0
            
        if 'Insp' in FM_ID:
            number_technicians = self.__Inspection[CompIDWithIndex]['number_technicians'] 
            number_specialists = self.__Inspection[CompIDWithIndex]['number_specialists'] 
        
        else:
            number_technicians = self.__Repair_Action[CompIDWithIndex]['number_technicians'] 
            number_specialists = self.__Repair_Action[CompIDWithIndex]['number_specialists']   
            
        wage_specialist_day   = self.__Farm_OM['wage_specialist_day'] 
        wage_specialist_night = self.__Farm_OM['wage_specialist_night'] 
        wage_technician_day   = self.__Farm_OM['wage_technician_day'] 
        wage_technician_night = self.__Farm_OM['wage_technician_night'] 
        
        # cost of OM for the current action [unit]
        cost_spare         = self.__Failure_Mode[CompIDWithIndex]['cost_spare'] 
        cost_spare_transit = self.__Failure_Mode[CompIDWithIndex]['cost_spare_transit'] 
        cost_spare_loading = self.__Failure_Mode[CompIDWithIndex]['cost_spare_loading'] 
    
        # cost of spare
        omCostValueSpare = cost_spare + cost_spare_transit + cost_spare_loading
        omCostValue      = omCostValueSpare
        
        # Assumption
        wage_specialist_weekend = wage_specialist_night 
        wage_technician_weekend = wage_technician_night 
        
        # cost of specialists
        omCostValue = omCostValue + number_specialists*wage_specialist_day*dayNotWeekend
        omCostValue = omCostValue + number_specialists*wage_specialist_weekend*dayWeekend                
        omCostValue = omCostValue + number_specialists*wage_specialist_night*nightNotWeekend
        omCostValue = omCostValue + number_specialists*wage_specialist_weekend*nightWeekend                  
        
        # cost of technicians
        omCostValue = omCostValue + number_technicians*wage_technician_day*dayNotWeekend
        omCostValue = omCostValue + number_technicians*wage_technician_weekend*dayWeekend
        omCostValue = omCostValue + number_technicians*wage_technician_night*nightNotWeekend
        omCostValue = omCostValue + number_technicians*wage_technician_weekend*nightWeekend
     
        return omCostValueSpare, omCostValue
        
    def __calcLCOE_OfOM(self):
        
        '''__calcLCOE_OfOM function: estimation of the LCOE of O&M
                                                      
        Args:              
            no arguments  
        
        Attributes:         
            no attributes                  
 
        Returns:
            no returns
      
        '''

        #CoBaMa_eventsTable   = self.__CoBaMa_eventsTable
        #CaBaMa_eventsTable   = self.__CaBaMa_eventsTable
        #UnCoMa_eventsTable   = self.__UnCoMa_eventsTable
        #eventsTableNoPoisson = self.__eventsTableNoPoisson 
        #arrayDict = self.__arrayDict
                                          
        
        # set the index of the tables to zero        
        self.__actIdxOfUnCoMa = 0
        self.__actIdxOfCaBaMa = 0
        self.__actIdxOfCoBaMa = 0 
        
        # set the local loops to zero
        loop = 0
        loopValuesForOutput_UnCoMa = 0 
        loopValuesForOutput_CaBaMa = 0  
        loopValuesForOutput_CoBaMa = 0  
        flagFirstLoop = False         
        
        # total action delay 
        self.__totalActionDelayHour = 0
        
        # actual action delay 
        self.__actActionDelayHour = 0
        
        # set the flags to False        
        flagCalcUnCoMa = False
        flagCalcCaBaMa = False
        flagCalcCoBaMa = False
                
        # Initialisation of the calculation flags
        if self.__Farm_OM['calendar_based_maintenance'] == True:
            flagCalcCaBaMa = True
            
        else:
            
            if self.__Farm_OM['corrective_maintenance'] == True:
                flagCalcUnCoMa = True  
                
            else:
                if self.__Farm_OM['condition_based_maintenance'] == True:
                    flagCalcCoBaMa = True       
                               
        # calculation loop
        while flagCalcUnCoMa == True or flagCalcCaBaMa == True or flagCalcCoBaMa == True: 
                                                    
              
            # condition based maintenance
            if self.__Farm_OM['condition_based_maintenance'] == True and flagCalcCoBaMa == True: 
                                
                # break condition
                if len(self.__CoBaMa_eventsTable) <= self.__actIdxOfCoBaMa:
                    flagCalcCoBaMa = False
                    continue                                               
                
                start_time_CoBaMa = timeit.default_timer()
                                
                startActionDate  = self.__CoBaMa_eventsTable.startActionDate[self.__actIdxOfCoBaMa]
                #endActionDate    = self.__CoBaMa_eventsTable.endActionDate[self.__actIdxOfCoBaMa]
                currentStartDate = self.__CoBaMa_eventsTable.currentStartDate[self.__actIdxOfCoBaMa]
                currentEndDate   = self.__CoBaMa_eventsTable.currentEndDate[self.__actIdxOfCoBaMa]
                currentAlarmDate = self.__CoBaMa_eventsTable.currentAlarmDate[self.__actIdxOfCoBaMa]
                belongsTo        = str(self.__CoBaMa_eventsTable.belongsTo[self.__actIdxOfCoBaMa])                          
                ComponentType    = str(self.__CoBaMa_eventsTable.ComponentType[self.__actIdxOfCoBaMa])
                ComponentSubType = str(self.__CoBaMa_eventsTable.ComponentSubType[self.__actIdxOfCoBaMa])
                ComponentID      = str(self.__CoBaMa_eventsTable.ComponentID[self.__actIdxOfCoBaMa])
                FM_ID            = str(self.__CoBaMa_eventsTable.FM_ID[self.__actIdxOfCoBaMa])     
                RA_ID            = str(self.__CoBaMa_eventsTable.RA_ID[self.__actIdxOfCoBaMa]) 
                threshold        = self.__CoBaMa_eventsTable.threshold[self.__actIdxOfCoBaMa]
                failureRate      = self.__CoBaMa_eventsTable.failureRate[self.__actIdxOfCoBaMa]
                flagCaBaMa       = self.__CoBaMa_eventsTable.flagCaBaMa[self.__actIdxOfCoBaMa]
                indexFM          = self.__CoBaMa_eventsTable.indexFM[self.__actIdxOfCoBaMa]
                CompIDWithIndex  = ComponentID + '_' + str(indexFM)
                
                #currentEndDateStr       = currentEndDate.strftime(self.__strFormat1)
                #self.__repairActionDate = datetime.datetime.strptime(str(currentEndDate), self.__strFormat2)
                #failureDate             = currentEndDate

                currentAlarmDateStr = currentAlarmDate.strftime(self.__strFormat1)                   
                self.__repairActionDate = datetime.datetime.strptime(str(currentAlarmDate), self.__strFormat2) 
                failureDate = currentAlarmDate
                
                # break condition
                '''if self.__endOperationDate <= currentAlarmDate:
                    flagCalcCoBaMa = False
                    continue'''
                               
                # simulate or not
                simulateFlag = True
                
                if self.__NrOfDevices == self.__NrOfTurnOutDevices:
                    simulateFlag = False
                    
                else:
                    
                  # Set the simulateFlag?
                    if belongsTo == 'Array':
                                             
                        if self.__arrayDict[ComponentID]['CoBaMaNoWeatherWindow'] == True:
                            simulateFlag = False
                             
                    else:
                        
                        if 'device' in ComponentType and self.__arrayDict[ComponentType]['CoBaMaNoWeatherWindow'] == True:
                            simulateFlag = False              
                
                if simulateFlag == False:
                    self.__actIdxOfCoBaMa = self.__actIdxOfCoBaMa + 1
                    
                    if self.__actIdxOfCoBaMa == len(self.__CoBaMa_eventsTable):
                        flagCalcCoBaMa = False
                        loop = 0                   
                else:                
                 
                    if self.__dtocean_operations_PRINT_FLAG == True:
                        
                        print 'WP6: ******************************************************'
                        print 'WP6: actIdxOfCoBaMa = ', self.__actIdxOfCoBaMa
                        print 'WP6: ComponentID    = ', ComponentID 
                        print 'WP6: RA_ID = ', RA_ID 
                        print 'WP6: FM_ID = ', FM_ID
                    
                    # Calculate the cost of operation at alarm date 
                    # independent from inspection or repair action
                    sp_dry_mass = self.__Failure_Mode[CompIDWithIndex]['spare_mass']
                    sp_length   = self.__Failure_Mode[CompIDWithIndex]['spare_length'] 
                    sp_width    = self.__Failure_Mode[CompIDWithIndex]['spare_width'] 
                    sp_height   = self.__Failure_Mode[CompIDWithIndex]['spare_height']                 
                    
                    if 'Insp' in FM_ID:
                        
                        # For logistic
                        d_acc       = self.__Inspection[CompIDWithIndex]['duration_accessibility'] 
                        d_om        = self.__Inspection[CompIDWithIndex]['duration_inspection']   
                        helideck    = self.__Farm_OM['helideck'] 
                        Hs_acc      = self.__Inspection[CompIDWithIndex]['wave_height_max_acc'] 
                        Tp_acc      = self.__Inspection[CompIDWithIndex]['wave_periode_max_acc']  
                        Ws_acc      = self.__Inspection[CompIDWithIndex]['wind_speed_max_acc']  
                        Cs_acc      = self.__Inspection[CompIDWithIndex]['current_speed_max_acc'] 
                        Hs_om       = self.__Inspection[CompIDWithIndex]['wave_height_max_om'] 
                        Tp_om       = self.__Inspection[CompIDWithIndex]['wave_periode_max_om']  
                        Ws_om       = self.__Inspection[CompIDWithIndex]['wind_speed_max_om']  
                        Cs_om       = self.__Inspection[CompIDWithIndex]['current_speed_max_om'] 
                        technician  = self.__Inspection[CompIDWithIndex]['number_technicians'] + self.__Inspection[CompIDWithIndex]['number_specialists'] 
                        
                        Dist_port   = self.__portDistIndex['inspection'][0]
                        Port_Index  = self.__portDistIndex['inspection'][1]       
                    
                    else:
                        
                        # for logistic
                        d_acc       = self.__Repair_Action[CompIDWithIndex]['duration_accessibility'] 
                        d_om        = self.__Repair_Action[CompIDWithIndex]['duration_maintenance']
                        helideck    = self.__Farm_OM['helideck'] 
                        Hs_acc      = self.__Repair_Action[CompIDWithIndex]['wave_height_max_acc'] 
                        Tp_acc      = self.__Repair_Action[CompIDWithIndex]['wave_periode_max_acc']  
                        Ws_acc      = self.__Repair_Action[CompIDWithIndex]['wind_speed_max_acc']  
                        Cs_acc      = self.__Repair_Action[CompIDWithIndex]['current_speed_max_acc'] 
                        Hs_om       = self.__Repair_Action[CompIDWithIndex]['wave_height_max_om'] 
                        Tp_om       = self.__Repair_Action[CompIDWithIndex]['wave_periode_max_om']  
                        Ws_om       = self.__Repair_Action[CompIDWithIndex]['wind_speed_max_om']  
                        Cs_om       = self.__Repair_Action[CompIDWithIndex]['current_speed_max_om'] 
                        technician  = self.__Repair_Action[CompIDWithIndex]['number_technicians'] + self.__Repair_Action[CompIDWithIndex]['number_specialists'] 
                        
                        Dist_port   = self.__portDistIndex['repair'][0]
                        Port_Index  = self.__portDistIndex['repair'][1]
                                          
                    if belongsTo == 'Array':
                        
                        depth      = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['depth']
                        x_coord    = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['x coord'] 
                        y_coord    = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['y coord']
                        zone       = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['zone']  
                        Bathymetry = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['Bathymetry']
                        Soil_type  = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['Soil type']                                          
                    
                    else:
                        
                        depth      = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['depth']
                        x_coord    = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['x coord'] 
                        y_coord    = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['y coord']
                        zone       = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['zone']  
                        Bathymetry = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['Bathymetry']
                        Soil_type  = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['Soil type']  
                        
                           
                    if belongsTo == 'Array':
                        
                        if 'Substation' in ComponentType:
                            ComponentTypeLogistic = 'collection point'
                            ComponentIDLogistic   = ComponentID
                            
                        elif 'subhub' in ComponentType:
                            ComponentTypeLogistic = 'collection point'
                            ComponentIDLogistic   = ComponentID
                            
                        elif 'Export Cable' in ComponentType:
                            ComponentTypeLogistic = 'static cable'
                            ComponentIDLogistic   = int(ComponentID[-3:len(ComponentID)])
                            
                        else:
                            ComponentTypeLogistic = ComponentType
                            ComponentIDLogistic   = ComponentID                        
                    
                    else:
                        
                        # Adjustmet of the names to logistic
                        # The name of subsystems in logistic and RAM are differnt             
                        if 'Dynamic cable' in ComponentSubType:
                            ComponentTypeLogistic = 'dynamic cable'
                            # problem with logistic database
                            ComponentIDLogistic   = 0#int(ComponentID[-3:len(ComponentID)])
                            
                        elif 'Mooring line' in ComponentSubType:
                            ComponentTypeLogistic = 'mooring line'
                            ComponentIDLogistic   = int(ComponentID[-3:len(ComponentID)])
                            
                        elif 'Foundation' in ComponentSubType:
                            ComponentTypeLogistic = 'foundation'
                            ComponentIDLogistic   = ComponentID
                            
                        else:
                            ComponentTypeLogistic = ComponentType
                            ComponentIDLogistic   = ComponentID
                            
                        if 'device' in ComponentTypeLogistic:
                            ComponentTypeLogistic = 'device'
                                                                    
                    # Values for logistic
                    values = [FM_ID, ComponentTypeLogistic, ComponentSubType, ComponentIDLogistic,
                              depth,
                              x_coord, 
                              y_coord,
                              zone,  
                              currentAlarmDateStr, d_acc, d_om, str(helideck),
                              Hs_acc, Tp_acc, Ws_acc, Cs_acc,
                              Hs_om, Tp_om, Ws_om, Cs_om,
                              technician,
                              sp_dry_mass, sp_length, sp_width, sp_height,
                              Dist_port, Port_Index,
                              Bathymetry,
                              Soil_type,
                              self.__PrepTimeCalcCoBaMa
                              ]
                                                                                                 
                    self.__wp6_outputsForLogistic.ix[0] = values
                    
                    # Calc logistic functions
                    start_time_logistic = timeit.default_timer()                    
                    self.__calcLogistic() 
                    stop_time_logistic = timeit.default_timer()
                    
                    if self.__dtocean_operations_PRINT_FLAG == True:
                        print 'calcLogistic: Simulation Duration [s]: ' + str(stop_time_logistic - start_time_logistic)
                        
                        

                    if self.__om_logistic['findSolution'] == 'NoSolutionsFound':
                                                   
                        if self.__dtocean_operations_PRINT_FLAG == True:
                            print 'WP6: ErrorID = NoSolutionsFound!'                                                                     
                            print 'WP6: values = ', values 

                    if self.__om_logistic['findSolution'] == 'SolutionFound' or self.__om_logistic['findSolution'] == 'NoWeatherWindowFound': 
                        
                        if self.__om_logistic['findSolution'] == 'NoWeatherWindowFound':
                            
                            if self.__dtocean_operations_PRINT_FLAG == True:                                                         
                                print 'WP6: ErrorID = NoWeatherWindowFound!'
                                print 'WP6: values = ', values                         
                        
                        if self.__om_logistic['findSolution'] == 'SolutionFound' or (self.__om_logistic['findSolution'] == 'NoWeatherWindowFound' and self.__ignoreWeatherWindow == False):

                            CaBaMaSolution = False
                            
                            if  (self.__om_logistic['findSolution'] == 'NoWeatherWindowFound' and self.__ignoreWeatherWindow == False):
                                                       
                                optLogisticCostValue = 0                            
                                omCostValueSpare     = 0
                                omCostValue          = 0 
                                totalDownTimeHours   = (self.__endOperationDate- failureDate).total_seconds() // 3600
                                self.__departOpDate  = self.__endOperationDate         
                            
                            else:                   
                                                                                                                
                                self.__endOpDate    = datetime.datetime(self.__om_logistic['optimal']['end_dt'].year,
                                                                        self.__om_logistic['optimal']['end_dt'].month,
                                                                        self.__om_logistic['optimal']['end_dt'].day,
                                                                        self.__om_logistic['optimal']['end_dt'].hour,
                                                                        self.__om_logistic['optimal']['end_dt'].minute,
                                                                        0)
                                
                                
                                # In LpM7 case self.__om_logistic['optimal']['depart_dt'] is a dict
                                if type(self.__om_logistic['optimal']['depart_dt']) == dict:
                                    dummy__departOpDate = self.__om_logistic['optimal']['depart_dt']['weather windows depart_dt_replace']
                                    dummy__departOpDate = self.__om_logistic['optimal']['depart_dt']['weather windows depart_dt_retrieve']
                                else:
                                    dummy__departOpDate = self.__om_logistic['optimal']['depart_dt']
                                    
                                self.__departOpDate    = datetime.datetime(dummy__departOpDate.year,
                                                                           dummy__departOpDate.month,
                                                                           dummy__departOpDate.day,
                                                                           dummy__departOpDate.hour,
                                                                           dummy__departOpDate.minute,
                                                                           0)
                                                                                               
                                # total optim cost from logistic            
                                optLogisticCostValue = self.__om_logistic['optimal']['total cost']
                            
                                self.__totalSeaTimeHour   = (self.__endOpDate - self.__departOpDate).total_seconds() // 3600
                                self.__om_logistic['optimal']['schedule sea time'] = self.__totalSeaTimeHour
                                
                                totalDownTimeHours = (self.__endOpDate - currentAlarmDate).total_seconds() // 3600
                                
                                omCostValueSpare, omCostValue = self.__calcCostOfOM(FM_ID, CompIDWithIndex)
                                
                                totalCostCoBaMa = optLogisticCostValue + omCostValue                             
                                
                                
                                # Is there a calandar based maintenance for this Component ID in near future
                                if flagCaBaMa == True or (flagCaBaMa == False and self.__Farm_OM['calendar_based_maintenance'] == True):
                                                        
                                    # find the blocks in CaBaMa
                                    if 'device' in ComponentType:
                                        if flagCaBaMa == True:
                                            CaBaMaTableQueryDeviceID  = ComponentType
                                        else: 
                                            CaBaMaTableQueryDeviceID  = ComponentType[0:-3]
                                        
                                        CaBaMaTableQuerySubSystem = ComponentSubType
                                            
                                    elif 'subhub' in ComponentType:
                                        if flagCaBaMa == True:
                                            CaBaMaTableQueryDeviceID = ComponentType
                                        else:
                                            CaBaMaTableQueryDeviceID = ComponentType[0:-3]
                                    else:                    
                                        CaBaMaTableQueryDeviceID  = 'Array'
                                        CaBaMaTableQuerySubSystem = ComponentType[0:-3]                        
                                                                                    
                                    if 'subhub' in ComponentType:
                                        dummyCaBaMaTable = self.__CaBaMa_eventsTable.loc[(self.__CaBaMa_eventsTable['ComponentType'] == CaBaMaTableQueryDeviceID) & \
                                        (self.__CaBaMa_eventsTable['FM_ID'] == FM_ID) & \
                                        (self.__CaBaMa_eventsTable['indexFM'] == indexFM)]
                                        
                                       
                                    else:
                                        dummyCaBaMaTable = self.__CaBaMa_eventsTable.loc[(self.__CaBaMa_eventsTable['RA_ID'] == RA_ID) & \
                                        (self.__CaBaMa_eventsTable['ComponentSubType'] == CaBaMaTableQuerySubSystem) & \
                                        (self.__CaBaMa_eventsTable['FM_ID'] == FM_ID) & \
                                        (self.__CaBaMa_eventsTable['indexFM'] == indexFM)]
                                    
                                    
                                    indexDummyCaBaMaTable = 0 
                                    # currently only for device. The components of the array will be repaired immediately  
                                    if 1 < len(dummyCaBaMaTable) and 'device' in ComponentType:
                                        
                                        # start index with 0
                                        dummyCaBaMaTable.reset_index(drop=True, inplace=True) 
                                        
                                        for iCnt in range(0,len(dummyCaBaMaTable)):                                
                                            
                                            timeTillStartCaBaMaHour = (dummyCaBaMaTable.currentStartActionDate[iCnt] - currentAlarmDate).total_seconds() // 3600
                                            if timeTillStartCaBaMaHour < self.__timeExtensionDeratingCoBaMaHour:                                                                      
                                                
                                                indexDummyCaBaMaTable = iCnt  
                                                break
                                            
                                        if indexDummyCaBaMaTable != 0:
                                        
                                            # Benefit CoBaMa
                                            dummyCoBaMaEndDate = dummyCaBaMaTable.currentStartActionDate[indexDummyCaBaMaTable]
                                            if currentEndDate <= dummyCaBaMaTable.currentStartActionDate[indexDummyCaBaMaTable]:
                                                dummyCoBaMaEndDate = currentEndDate
                                                
                                            dummyCoBaMaTime        = (dummyCaBaMaTable.currentStartActionDate[indexDummyCaBaMaTable] - dummyCoBaMaEndDate).total_seconds() // 3600
                                            dummyCoBaMaEnergyYield = (dummyCoBaMaTime/(self.__yearDays*self.__dayHours))*self.__annual_Energy_Production_perD(int(ComponentID[-3:len(ComponentID)])) 
                                            dummyCoBaMaMoney       = (dummyCoBaMaEnergyYield/1000.0) * self.__Farm_OM['energy_selling_price'] 
                                            dummyCoBaMaBenefit     = dummyCoBaMaMoney - totalCostCoBaMa
                                            
                                            # Benefit CaBaMa
                                            dummyCaBaMaEndDate = dummyCoBaMaEndDate + timedelta(hours = self.__timeExtensionDeratingCoBaMaHour)
                                            if dummyCaBaMaTable.currentStartActionDate[indexDummyCaBaMaTable] <= dummyCaBaMaEndDate:
                                                dummyCaBaMaEndDate = dummyCaBaMaTable.currentStartActionDate[indexDummyCaBaMaTable]
                                                                
                                            dummyCaBaMaTime        = (dummyCaBaMaTable.currentStartActionDate[indexDummyCaBaMaTable] - dummyCaBaMaEndDate).total_seconds() // 3600
                                            dummyCaBaMaEnergyYield = (dummyCaBaMaTime/(self.__yearDays*self.__dayHours))*self.__annual_Energy_Production_perD(int(ComponentID[-3:len(ComponentID)])) 
                                            dummyCaBaMaEnergyYield = dummyCaBaMaEnergyYield * (self.__powerDeratingCoBaMa/100.0)
                                            dummyCaBaMaMoney       = (dummyCaBaMaEnergyYield/1000.0) * self.__Farm_OM['energy_selling_price'] 
                                            totalCostCaBaMa       = dummyCaBaMaTable.logisticCost[indexDummyCaBaMaTable] + dummyCaBaMaTable.omCost[indexDummyCaBaMaTable]
                                            dummyCaBaMaBenefit     = dummyCaBaMaMoney - totalCostCaBaMa
                                            
                                            # CoBaMa
                                            if dummyCoBaMaBenefit <= dummyCaBaMaBenefit:
                                                CaBaMaSolution = True
                                                                                                                                                                        
                            if CaBaMaSolution == True:
                                
                                newLineCurrentStartDate = dummyCaBaMaTable.currentEndActionDate[indexDummyCaBaMaTable]
                                
                                if flagCaBaMa == True:
                                   
                                    # this component should be repaired in calandar based maintenance in near future                                                                                                      
                                    # Save the cost of operation
                                    if belongsTo == 'Array':
                                         
                                        # Cost
                                        self.__arrayDict[ComponentID]['CoBaMaDeratingCostLogistic'].append(0)
                                        self.__arrayDict[ComponentID]['CoBaMaDeratingCostOM'].append(0)   
                                                                            
                                    else:
                                        
                                        if 'device' in ComponentType:
                                            
                                            # Inspection cost
                                            self.__arrayDict[ComponentType]['CoBaMaCostDeratingLogistic'].append(0)
                                            self.__arrayDict[ComponentType]['CoBaMaDeratingCostOM'].append(0)
                                                           
                                    # Save the information about failure and down time in devices
                                    keys = self.__arrayDict.keys()                    
                                    for iCnt1 in range(0,len(keys)):                       
                                        if 'device' in keys[iCnt1]:
                                            
                                            if 'All' in self.__arrayDict[ComponentID]['Breakdown'] or keys[iCnt1] in self.__arrayDict[ComponentID]['Breakdown']:
                                                # Save the information about failure
                                                self.__arrayDict[keys[iCnt1]]['CoBaMaDeratingOpEvents'].append(currentStartDate)                                         
                                                totalDownTimeHours = (dummyCaBaMaTable.currentEndActionDate[indexDummyCaBaMaTable] - dummyCaBaMaEndDate).total_seconds() // 3600
                                                self.__arrayDict[keys[iCnt1]]['CoBaMaDeratingOpEventsDuration'].append(totalDownTimeHours)                                       
                                                self.__arrayDict[keys[iCnt1]]['CoBaMaDeratingOpEventsIndexFM'].append(indexFM)
                                                self.__arrayDict[keys[iCnt1]]['CoBaMaDeratingOpEventsCausedBy'].append(str(ComponentID)) 
                                                
                                                if not 'device' in ComponentType:
                                                     
                                                    self.__arrayDict[keys[iCnt1]]['CoBaMaDeratingCostLogistic'].append(0.0)
                                                    self.__arrayDict[keys[iCnt1]]['CoBaMaDeratingCostOM'].append(0.0)                 
                                
                                if flagCaBaMa == False and self.__Farm_OM['calendar_based_maintenance'] == True:
                                   
                                    # this component should be repaired with other same components in calandar based maintenance in near future                                                                                                      
                                    # Save the cost of operation
                                    if belongsTo == 'Array':
                                         
                                        # Cost
                                        self.__arrayDict[ComponentID]['CoBaMaDeratingCostLogistic'].append(dummyCaBaMaTable.logisticCost[indexDummyCaBaMaTable])
                                        self.__arrayDict[ComponentID]['CoBaMaCostOM'].append(dummyCaBaMaTable.omCost[indexDummyCaBaMaTable])   
                                        
                                        self.__arrayDict[ComponentType]['CoBaMaDeratingCostLogistic'].append(0)
                                        self.__arrayDict[ComponentType]['CoBaMaDeratingCostOM'].append(0)
                                            
                                    else:
                                        
                                        if 'device' in ComponentType:
                                            
                                            # Inspection cost
                                            self.__arrayDict[ComponentType]['CoBaMaDeratingCostLogistic'].append(dummyCaBaMaTable.logisticCost[indexDummyCaBaMaTable])
                                            self.__arrayDict[ComponentType]['CoBaMaDeratingCostOM'].append(dummyCaBaMaTable.omCost[indexDummyCaBaMaTable])
                                                           
                                    
                                    
                                    # Save the information about failure and down time in devices
                                    keys = self.__arrayDict.keys()                    
                                    for iCnt1 in range(0,len(keys)):                       
                                        if 'device' in keys[iCnt1]:
                                            
                                            if 'All' in self.__arrayDict[ComponentID]['Breakdown'] or keys[iCnt1] in self.__arrayDict[ComponentID]['Breakdown']:
                                                # Save the information about failure
                                                self.__arrayDict[keys[iCnt1]]['CoBaMaDeratingOpEvents'].append(currentStartDate)                                         
                                                totalDownTimeHours = (dummyCaBaMaTable.currentEndActionDate[indexDummyCaBaMaTable] - dummyCaBaMaEndDate).total_seconds() // 3600
                                                self.__arrayDict[keys[iCnt1]]['CoBaMaOpDeratingEventsDuration'].append(totalDownTimeHours)                                       
                                                self.__arrayDict[keys[iCnt1]]['CoBaMaOpDeratingEventsIndexFM'].append(indexFM)
                                                self.__arrayDict[keys[iCnt1]]['CoBaMaOpDeratingEventsCausedBy'].append(str(ComponentID)) 
                                                
                                                if not 'device' in ComponentType:
                                                     
                                                    self.__arrayDict[keys[iCnt1]]['CoBaMaDeratingCostLogistic'].append(0.0)
                                                    self.__arrayDict[keys[iCnt1]]['CoBaMaDeratingCostOM'].append(0.0)                                           
                                              
                            else:
                                
                                newLineCurrentStartDate = self.__endOpDate 
                                
                                # Save the cost of operation
                                if belongsTo == 'Array':
                                     
                                    # Cost
                                    self.__arrayDict[ComponentID]['CoBaMaCostLogistic'].append(round(optLogisticCostValue,1))
                                    self.__arrayDict[ComponentID]['CoBaMaCostOM'].append(round(omCostValue,1))   
                                    
                                    #self.__arrayDict[ComponentType]['CoBaMaCostLogistic'].append(0)
                                    #self.__arrayDict[ComponentType]['CoBaMaCostOM'].append(0)
                                        
                                else:
                                    
                                    if 'device' in ComponentType:
                                        
                                        # Inspection cost
                                        self.__arrayDict[ComponentType]['CoBaMaCostLogistic'].append(round(optLogisticCostValue))
                                        self.__arrayDict[ComponentType]['CoBaMaCostOM'].append(round(omCostValue))
                                                       
                                # Save the information about failure and down time in devices
                                downtimeDeviceList = []
                                keys = self.__arrayDict.keys()                    
                                for iCnt1 in range(0,len(keys)): 
                                    
                                    if 'device' in keys[iCnt1] and self.__arrayDict[keys[iCnt1]]['CoBaMaNoWeatherWindow'] == False:
                                        
                                        if 'All' in self.__arrayDict[ComponentID]['Breakdown'] or keys[iCnt1] in self.__arrayDict[ComponentID]['Breakdown']:
                                            
                                            if self.__om_logistic['findSolution'] == 'NoWeatherWindowFound' and self.__ignoreWeatherWindow == False:
                                                self.__arrayDict[keys[iCnt1]]['CoBaMaNoWeatherWindow'] = True
                                                self.__NrOfTurnOutDevices = self.__NrOfTurnOutDevices + 1
                                            
                                            downtimeDeviceList.append(str(keys[iCnt1]))
                                            # Save the information about failure
                                            self.__arrayDict[keys[iCnt1]]['CoBaMaOpEvents'].append(failureDate)
                                            self.__arrayDict[keys[iCnt1]]['CoBaMaOpEventsDuration'].append(totalDownTimeHours)
                                            self.__arrayDict[keys[iCnt1]]['CoBaMaOpEventsIndexFM'].append(indexFM)
                                            self.__arrayDict[keys[iCnt1]]['CoBaMaOpEventsCausedBy'].append(str(ComponentID)) 
                                            
                                            if not 'device' in ComponentType:
                                                 
                                                self.__arrayDict[keys[iCnt1]]['CoBaMaCostLogistic'].append(0.0)
                                                self.__arrayDict[keys[iCnt1]]['CoBaMaCostOM'].append(0.0)
                                                self.__arrayDict[ComponentID]['CoBaMaNoWeatherWindow'] = True
                                                
                                               
                                                    
                            if CaBaMaSolution == False or (flagCaBaMa == False and self.__Farm_OM['calendar_based_maintenance'] == True):
                                                                                                                
                                valuesForOutput = [failureRate, str(datetime.datetime.strptime(str(currentAlarmDate), self.__strFormat2)),
                                                   str(datetime.datetime.strptime(str(currentAlarmDate), self.__strFormat2)),
                                                   str(self.__departOpDate.replace(second=0)), int(totalDownTimeHours),
                                                   '', ComponentType, ComponentSubType, ComponentID,
                                                   FM_ID, RA_ID, indexFM, int(optLogisticCostValue), 
                                                   int(omCostValue-omCostValueSpare), int(omCostValueSpare)]                                                                                                     
                                                                                    
                                self.__CoBaMa_outputEventsTable.ix[loopValuesForOutput_CoBaMa] = valuesForOutput                                
                                self.__CoBaMa_outputEventsTable.loc[loopValuesForOutput_CoBaMa,'downtimeDeviceList [-]'] = downtimeDeviceList
        
                                # loopValuesForOutput
                                loopValuesForOutput_CoBaMa = loopValuesForOutput_CoBaMa + 1 
                                
                                if self.__om_logistic['findSolution'] == 'SolutionFound':
                                                                                                 
                                    # for environmental team                                                                                                                                
                                    self.__env_assess(loop, failureDate, FM_ID, RA_ID, self.__om_logistic['optimal']['schedule sea time'], 'CoBaMa')
                                   
                                    # loop
                                    loop = loop + 1
                                                                                                                   
                                    # calculate the new entry in self.__CoBaMa_eventsTable                                                     
                                    index = -1
                                    for iCnt2 in range(0,len(self.__arrayDict[ComponentID]['CoBaMa_initOpEventsList'][indexFM-1])):
                                        if newLineCurrentStartDate < self.__arrayDict[ComponentID]['CoBaMa_initOpEventsList'][indexFM-1][iCnt2] and \
                                           currentEndDate < self.__arrayDict[ComponentID]['CoBaMa_initOpEventsList'][indexFM-1][iCnt2]:
                                            index = iCnt2
                                            break
                                   
                                    if index != -1:
                              
                                        # new line for the extension of CoBaMa 
                                        self.__CoBaMa_eventsTable.ix[len(self.__CoBaMa_eventsTable)] = copy.deepcopy(self.__CoBaMa_eventsTable.iloc[self.__actIdxOfCoBaMa,:])
                
                                          
                                        newLineCurrentEndDate = self.__arrayDict[ComponentID]['CoBaMa_initOpEventsList'][indexFM-1][index] 
                                                                
                                        newLineCurrentAlarmDate = newLineCurrentStartDate + timedelta(hours = (((newLineCurrentEndDate - newLineCurrentStartDate).total_seconds()/3600)*(1.0-threshold)))     
                                                                 
                                        self.__CoBaMa_eventsTable.loc[len(self.__CoBaMa_eventsTable)-1,'currentStartDate'] = newLineCurrentStartDate
                                        self.__CoBaMa_eventsTable.loc[len(self.__CoBaMa_eventsTable)-1,'currentEndDate']   = newLineCurrentEndDate 
                                        self.__CoBaMa_eventsTable.loc[len(self.__CoBaMa_eventsTable)-1,'currentAlarmDate'] = newLineCurrentAlarmDate
                                         
                                        
                                        # sort of CoBaMa_eventsTable                
                                        self.__CoBaMa_eventsTable.sort(columns=['currentAlarmDate'], inplace=True)
                                        
                                        # start index with 0
                                        self.__CoBaMa_eventsTable.reset_index(drop=True, inplace=True)
                                                                                                                         
                    # increase the index 
                    self.__actIdxOfCoBaMa = self.__actIdxOfCoBaMa + 1                                
                                  
                    # time consumption CaBaMa 
                    stop_time_CoBaMa = timeit.default_timer()
                    
                    if self.__dtocean_operations_PRINT_FLAG == True:
                        print 'calcCoBaMa: Simulation Duration [s]  : ' + str((stop_time_CoBaMa - start_time_CoBaMa)-(stop_time_logistic - start_time_logistic))
                                         
            # calandar based maintenance 
            # *****************************************************************
            # ***************************************************************** 
            # ***************************************************************** 
            if self.__Farm_OM['calendar_based_maintenance'] == True and flagCalcCaBaMa == True:
                
                start_time_CaBaMa = timeit.default_timer()
                                                                                                                                   
                startActionDate  = self.__CaBaMa_eventsTable.startActionDate[self.__actIdxOfCaBaMa]
                belongsTo        = str(self.__CaBaMa_eventsTable.belongsTo[self.__actIdxOfCaBaMa])
                ComponentType    = str(self.__CaBaMa_eventsTable.ComponentType[self.__actIdxOfCaBaMa])
                ComponentSubType = str(self.__CaBaMa_eventsTable.ComponentSubType[self.__actIdxOfCaBaMa])
                FM_ID            = str(self.__CaBaMa_eventsTable.FM_ID[self.__actIdxOfCaBaMa])     
                indexFM          = self.__CaBaMa_eventsTable.indexFM[self.__actIdxOfCaBaMa] 
                RA_ID            = str(self.__CaBaMa_eventsTable.RA_ID[self.__actIdxOfCaBaMa]) 
                ComponentID      = str(self.__CaBaMa_eventsTable.ComponentID[self.__actIdxOfCaBaMa])
                
                
                #arrayDict = self.__arrayDict
                #CaBaMa_outputEventsTable = self.__CaBaMa_outputEventsTable
                
                                                               
                # find the blocks in CaBaMa
                if 'device' in ComponentType:
                    CaBaMaTableQueryDeviceID  = ComponentType
                    CaBaMaTableQuerySubSystem = ComponentSubType
                        
                elif 'subhub' in ComponentType:
                    CaBaMaTableQueryDeviceID = ComponentType

                else:                    
                    CaBaMaTableQueryDeviceID  = 'Array'
                    CaBaMaTableQuerySubSystem = ComponentType[0:-3]                        
                                                                
                if 'subhub' in ComponentType:
                    dummyCaBaMaTable = self.__CaBaMa_eventsTable.loc[(self.__CaBaMa_eventsTable['ComponentType'] == CaBaMaTableQueryDeviceID) & \
                    (self.__CaBaMa_eventsTable['startActionDate'] == startActionDate) & \
                    (self.__CaBaMa_eventsTable['FM_ID'] == FM_ID) & \
                    (self.__CaBaMa_eventsTable['indexFM'] == indexFM)]                      
                else:
                    dummyCaBaMaTable = self.__CaBaMa_eventsTable.loc[(self.__CaBaMa_eventsTable['RA_ID'] == RA_ID) & \
                    (self.__CaBaMa_eventsTable['ComponentSubType'] == CaBaMaTableQuerySubSystem) & \
                    (self.__CaBaMa_eventsTable['startActionDate'] == startActionDate) & \
                    (self.__CaBaMa_eventsTable['FM_ID'] == FM_ID) & \
                    (self.__CaBaMa_eventsTable['indexFM'] == indexFM)]
                    
                # start index with 0
                dummyCaBaMaTable.reset_index(drop=True, inplace=True)
                
                blockNumberList = []                
                divModBlockNumber = divmod(len(dummyCaBaMaTable), self.__CaBaMa_nrOfMaxActions)
                if 0 < divModBlockNumber[0]:
                    for iCnt in range(0,divModBlockNumber[0]): 
                        blockNumberList.append(self.__CaBaMa_nrOfMaxActions)
                        if iCnt == divModBlockNumber[0] - 1:
                            blockNumberList.append(divModBlockNumber[1])
                else:                
                    blockNumberList.append(divModBlockNumber[1])
                    
                for iCnt in range(0,len(blockNumberList)):  
                                        
                    blockNumber = blockNumberList[iCnt]
                    currentStartActionDate = dummyCaBaMaTable.currentStartActionDate[iCnt*self.__CaBaMa_nrOfMaxActions]
                    currentStartActionDateFormat2 = datetime.datetime.strptime(str(currentStartActionDate), self.__strFormat2)
                    
                    # Date of logistic request
                    self.__repairActionDate = datetime.datetime.strptime(str(currentStartActionDate), self.__strFormat2) 
                    repairActionDateStr     = currentStartActionDate.strftime(self.__strFormat1)
                                        
                    if self.__dtocean_operations_PRINT_FLAG == True:                           
                        print 'WP6: ******************************************************'
                        print 'WP6: actIdxOfCaBaMa = ', self.__actIdxOfCaBaMa
                        print 'WP6: ComponentID = ', ComponentID 
                        print 'WP6: RA_ID = ', RA_ID 
                        print 'WP6: FM_ID = ', FM_ID  
                    
                    # break the while loop if repairActionDate is greater than self.__endOperationDate               
                    if self.__endOperationDate < self.__repairActionDate:
                        flagCalcCaBaMa = False
                        loop = 0
                        
                        if self.__Farm_OM['corrective_maintenance'] == True:
                            flagCalcUnCoMa = True
                            
                        else:                                                        
                            if self.__Farm_OM['condition_based_maintenance'] == True:
                                flagCalcCoBaMa = True                                                                                              
                        break  
                                        
                    ComponentTypeList = []
                    ComponentSubTypeList = []
                    ComponentIDList = []
                    
                    
                    # loop over blockNumber 
                    for iCnt1 in range(0,blockNumber):
                        
                        belongsTo        = dummyCaBaMaTable.belongsTo[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt1]
                        ComponentID      = dummyCaBaMaTable.ComponentID[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt1]
                        CompIDWithIndex  = ComponentID + '_' + str(indexFM)
                        
                        ComponentType    = dummyCaBaMaTable.ComponentType[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt1]
                        ComponentSubType = dummyCaBaMaTable.ComponentSubType[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt1]
                        
                        ComponentTypeList.append(ComponentType)
                        ComponentSubTypeList.append(ComponentSubType)
                        ComponentIDList.append(ComponentID)
                                            
                        if iCnt == 0:
                            # independent from inspection or repair action
                            sp_dry_mass = self.__Failure_Mode[CompIDWithIndex]['spare_mass']
                            sp_length   = self.__Failure_Mode[CompIDWithIndex]['spare_length'] 
                            sp_width    = self.__Failure_Mode[CompIDWithIndex]['spare_width'] 
                            sp_height   = self.__Failure_Mode[CompIDWithIndex]['spare_height']                 
                            
                            if 'Insp' in FM_ID:
                                
                                # For logistic
                                d_acc       = self.__Inspection[CompIDWithIndex]['duration_accessibility'] 
                                d_om        = self.__Inspection[CompIDWithIndex]['duration_inspection']   
                                helideck    = self.__Farm_OM['helideck'] 
                                Hs_acc      = self.__Inspection[CompIDWithIndex]['wave_height_max_acc'] 
                                Tp_acc      = self.__Inspection[CompIDWithIndex]['wave_periode_max_acc']  
                                Ws_acc      = self.__Inspection[CompIDWithIndex]['wind_speed_max_acc']  
                                Cs_acc      = self.__Inspection[CompIDWithIndex]['current_speed_max_acc'] 
                                Hs_om       = self.__Inspection[CompIDWithIndex]['wave_height_max_om'] 
                                Tp_om       = self.__Inspection[CompIDWithIndex]['wave_periode_max_om']  
                                Ws_om       = self.__Inspection[CompIDWithIndex]['wind_speed_max_om']  
                                Cs_om       = self.__Inspection[CompIDWithIndex]['current_speed_max_om'] 
                                technician  = self.__Inspection[CompIDWithIndex]['number_technicians'] + self.__Inspection[CompIDWithIndex]['number_specialists'] 
                                
                                Dist_port   = self.__portDistIndex['inspection'][0]
                                Port_Index  = self.__portDistIndex['inspection'][1]       
                            
                            else:
                                
                                # for logistic
                                d_acc       = self.__Repair_Action[CompIDWithIndex]['duration_accessibility'] 
                                d_om        = self.__Repair_Action[CompIDWithIndex]['duration_maintenance']
                                helideck    = self.__Farm_OM['helideck'] 
                                Hs_acc      = self.__Repair_Action[CompIDWithIndex]['wave_height_max_acc'] 
                                Tp_acc      = self.__Repair_Action[CompIDWithIndex]['wave_periode_max_acc']  
                                Ws_acc      = self.__Repair_Action[CompIDWithIndex]['wind_speed_max_acc']  
                                Cs_acc      = self.__Repair_Action[CompIDWithIndex]['current_speed_max_acc'] 
                                Hs_om       = self.__Repair_Action[CompIDWithIndex]['wave_height_max_om'] 
                                Tp_om       = self.__Repair_Action[CompIDWithIndex]['wave_periode_max_om']  
                                Ws_om       = self.__Repair_Action[CompIDWithIndex]['wind_speed_max_om']  
                                Cs_om       = self.__Repair_Action[CompIDWithIndex]['current_speed_max_om'] 
                                technician  = self.__Repair_Action[CompIDWithIndex]['number_technicians'] + self.__Repair_Action[CompIDWithIndex]['number_specialists'] 
                                
                                Dist_port   = self.__portDistIndex['repair'][0]
                                Port_Index  = self.__portDistIndex['repair'][1]
                            
                                                                           
                            if belongsTo == 'Array':
                                
                                if 'Substation' in ComponentType:
                                    ComponentTypeLogistic = 'collection point'
                                    ComponentIDLogistic   = ComponentID
                                    
                                elif 'subhub' in ComponentType:
                                    ComponentTypeLogistic = 'collection point'
                                    ComponentIDLogistic   = ComponentID
                                    
                                elif 'Export Cable' in ComponentType:
                                    ComponentTypeLogistic = 'static cable'
                                    ComponentIDLogistic   = int(ComponentID[-3:len(ComponentID)])
                                    
                                else:
                                    ComponentTypeLogistic = ComponentType
                                    ComponentIDLogistic   = ComponentID                        
                            
                            else:
                                
                                # Adjustmet of the names to logistic
                                # The name of subsystems in logistic and RAM are differnt             
                                if 'Dynamic cable' in ComponentSubType:
                                    ComponentTypeLogistic = 'dynamic cable'
                                    # problem with logistic database
                                    ComponentIDLogistic   = 0#int(ComponentID[-3:len(ComponentID)])
                                    
                                elif 'Mooring line' in ComponentSubType:
                                    ComponentTypeLogistic = 'mooring line'
                                    ComponentIDLogistic   = int(ComponentID[-3:len(ComponentID)])
                                    
                                elif 'Foundation' in ComponentSubType:
                                    ComponentTypeLogistic = 'foundation'
                                    ComponentIDLogistic   = ComponentID
                                    
                                else:
                                    ComponentTypeLogistic = ComponentType
                                    ComponentIDLogistic   = ComponentID
                                    
                                if 'device' in ComponentTypeLogistic:
                                    ComponentTypeLogistic = 'device'
                    
                                                                                                                                                                            
                        if belongsTo == 'Array':
                            
                            depth      = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['depth']
                            x_coord    = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['x coord'] 
                            y_coord    = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['y coord']
                            zone       = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['zone']  
                            Bathymetry = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['Bathymetry']
                            Soil_type  = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['Soil type']                                          
                        
                        else:
                            
                            depth      = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['depth']
                            x_coord    = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['x coord'] 
                            y_coord    = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['y coord']
                            zone       = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['zone']  
                            Bathymetry = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['Bathymetry']
                            Soil_type  = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['Soil type']
                            
                        # Values for logistic
                        values = [FM_ID, ComponentTypeLogistic, ComponentSubType, ComponentIDLogistic,
                                  depth,
                                  x_coord, 
                                  y_coord,
                                  zone,  
                                  repairActionDateStr, d_acc, d_om, str(helideck),
                                  Hs_acc, Tp_acc, Ws_acc, Cs_acc,
                                  Hs_om, Tp_om, Ws_om, Cs_om,
                                  technician,
                                  sp_dry_mass, sp_length, sp_width, sp_height,
                                  Dist_port, Port_Index,
                                  Bathymetry,
                                  Soil_type,
                                  self.__PrepTimeCalcCaBaMa
                                  ]
                                                                                 
                        #self.__om_logistic_outputs = pd.DataFrame(index=[0],columns=keys)
                        self.__wp6_outputsForLogistic.ix[iCnt1] = values
                        
                        # end of calandar based maintenance 
                        self.__actIdxOfCaBaMa = self.__actIdxOfCaBaMa + 1
                    

                    # Calc logistic functions
                    start_time_logistic = timeit.default_timer()                    
                    self.__calcLogistic() 
                    stop_time_logistic = timeit.default_timer()
                    
                    if self.__dtocean_operations_PRINT_FLAG == True:
                        print 'calcLogistic: Simulation Duration [s]: ' + str(stop_time_logistic - start_time_logistic)
                    
                    
                    # clear wp6_outputsForLogistic
                    if 1 < blockNumber: 
                        self.__wp6_outputsForLogistic.drop(self.__wp6_outputsForLogistic.index[range(blockNumber-1,0,-1)], inplace = True)
                                            
                    if self.__om_logistic['findSolution'] == 'NoSolutionsFound' or self.__om_logistic['findSolution'] == 'NoWeatherWindowFound':
                        
                        if self.__dtocean_operations_PRINT_FLAG == True:
                                                
                            if self.__om_logistic['findSolution'] == 'NoSolutionsFound':
                                 print 'WP6: ErrorID = NoSolutionsFound!'
                                 
                            if self.__om_logistic['findSolution'] == 'NoWeatherWindowFound':
                                 print 'WP6: ErrorID = NoWeatherWindowFound!'
                             
                        optLogisticCostValue = 0
                        omCostValue = 0  
                        totalDownTimeHours = 0
                        self.__endOpDate = currentStartActionDate
         
                    else:
                        
                        self.__endOpDate    = datetime.datetime(self.__om_logistic['optimal']['end_dt'].year,
                                                                self.__om_logistic['optimal']['end_dt'].month,
                                                                self.__om_logistic['optimal']['end_dt'].day,
                                                                self.__om_logistic['optimal']['end_dt'].hour,
                                                                self.__om_logistic['optimal']['end_dt'].minute,
                                                                0)
                                                
                        # In LpM7 case self.__om_logistic['optimal']['depart_dt'] is a dict
                        if type(self.__om_logistic['optimal']['depart_dt']) == dict:
                            dummy__departOpDate = self.__om_logistic['optimal']['depart_dt']['weather windows depart_dt_replace']
                            dummy__departOpDate = self.__om_logistic['optimal']['depart_dt']['weather windows depart_dt_retrieve']
                        else:
                            dummy__departOpDate = self.__om_logistic['optimal']['depart_dt']
                            
                        self.__departOpDate    = datetime.datetime(dummy__departOpDate.year,
                                                                   dummy__departOpDate.month,
                                                                   dummy__departOpDate.day,
                                                                   dummy__departOpDate.hour,
                                                                   dummy__departOpDate.minute,
                                                                   0)
                            
                        # total optim cost from logistic            
                        optLogisticCostValue = self.__om_logistic['optimal']['total cost']
                                                                                        
                        # Calculation of total action time (hour) 
                        # Error in logistic, Therefore calculation in WP6 
                        self.__totalSeaTimeHour   = (self.__endOpDate - self.__departOpDate).total_seconds() // 3600
                        self.__om_logistic['optimal']['schedule sea time'] = self.__totalSeaTimeHour
                        
                        #totalOpTimeHour    = (endOpDate - repairActionEvents).total_seconds() // 3600
                        totalDownTimeHours = (self.__endOpDate - currentStartActionDateFormat2).total_seconds() // 3600
                        
                        omCostValueSpare, omCostValue = self.__calcCostOfOM(FM_ID, CompIDWithIndex)
                        
                      
#                    if flagFirstLoop == False:
#                        currentStartActionDate  = self.__CaBaMa_eventsTable.currentStartActionDate[self.__actIdxOfCaBaMa-1] 
#                        flagFirstLoop = True
#                                                        
#                    else:
#                        currentStartActionDate  = self.__CaBaMa_eventsTable.currentEndActionDate[self.__actIdxOfCaBaMa-blockNumber-1]
#                        self.__CaBaMa_eventsTable.loc[self.__actIdxOfCaBaMa-blockNumber, 'currentStartActionDate'] = currentStartActionDate                    
                        
                    currentStartActionDateFormat2 = datetime.datetime.strptime(str(currentStartActionDate), self.__strFormat2)                  
                    shiftDate = currentStartActionDateFormat2                    
                    
                    currentStartActionDateList = []
                    for iCnt1 in range(0,blockNumber):                                       
                        shiftDate = shiftDate + timedelta(hours = self.__totalSeaTimeHour/float(blockNumber))                            
                        self.__CaBaMa_eventsTable.loc[self.__actIdxOfCaBaMa-blockNumber+iCnt1, 'currentEndActionDate'] = shiftDate 
                        
                        #currentStartActionDateList.append(datetime.datetime.strptime(str(shiftDate.replace(second=0)), self.__strFormat2)) 
                        currentStartActionDateList.append(shiftDate) 
                        
                        if iCnt1 < blockNumber-1:                       
                            self.__CaBaMa_eventsTable.loc[self.__actIdxOfCaBaMa-blockNumber+iCnt1+1, 'currentStartActionDate'] = shiftDate
                                                    
                        self.__CaBaMa_eventsTable.loc[self.__actIdxOfCaBaMa-blockNumber+iCnt1, 'logisticCost'] = round(optLogisticCostValue/float(blockNumber),1)
                        self.__CaBaMa_eventsTable.loc[self.__actIdxOfCaBaMa-blockNumber+iCnt1, 'omCost']       = round(omCostValue,1)
                                                                                              
                    # Save the cost of operation
                    if belongsTo == 'Array':
                        
                        for iCnt1 in range(0,blockNumber): 
                            
                            # Cost
                            self.__arrayDict[dummyCaBaMaTable.ComponentID[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt1]]['CaBaMaCostLogistic'].append(round(optLogisticCostValue/float(blockNumber),1))
                            self.__arrayDict[dummyCaBaMaTable.ComponentID[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt1]]['CaBaMaCostOM'].append(round(omCostValue,1))   
                            
                    else:
                        
                        if 'device' in ComponentType:
                            
                            for iCnt1 in range(0,blockNumber): 
                            
                                # Inspection cost
                                self.__arrayDict[dummyCaBaMaTable.ComponentType[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt1]]['CaBaMaCostLogistic'].append(round(optLogisticCostValue/float(blockNumber),1))
                                self.__arrayDict[dummyCaBaMaTable.ComponentType[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt1]]['CaBaMaCostOM'].append(round(omCostValue,1))
                                
                                                                           
                    # Save the information about failure and down time in devices
                    keys = self.__arrayDict.keys()                    
                    for iCnt1 in range(0,len(keys)):                       
                        
                        if 'device' in keys[iCnt1]:
                                                        
                            shiftDate = currentStartActionDateFormat2
                            for iCnt2 in range(0,blockNumber): 
                                                           
                                if 'All' in self.__arrayDict[dummyCaBaMaTable.ComponentID[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt2]]['Breakdown'] or keys[iCnt1] in self.__arrayDict[dummyCaBaMaTable.ComponentID[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt2]]['Breakdown']:
                                                                         
                                    # Save the information about failure
                                    shiftDate = shiftDate + timedelta(hours = self.__totalSeaTimeHour/float(blockNumber))
                                    self.__arrayDict[keys[iCnt1]]['CaBaMaOpEvents'].append(shiftDate)                                      
                                    self.__arrayDict[keys[iCnt1]]['CaBaMaOpEventsDuration'].append(totalDownTimeHours/float(blockNumber))
                                    self.__arrayDict[keys[iCnt1]]['CaBaMaOpEventsIndexFM'].append(dummyCaBaMaTable.indexFM[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt2])
                                    self.__arrayDict[keys[iCnt1]]['CaBaMaOpEventsCausedBy'].append(str(dummyCaBaMaTable.ComponentID[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt2]+'_CaBaMa') )
                                    
                                    if not 'device' in ComponentType:
                                         
                                        self.__arrayDict[keys[iCnt1]]['CaBaMaCostLogistic'].append(0.0)
                                        self.__arrayDict[keys[iCnt1]]['CaBaMaCostOM'].append(0.0)
                                        
                    # Save the information about failure and down time in devices
                    downtimeDeviceList = []
                    for iCnt2 in range(0,blockNumber): 

                        if 'All' in self.__arrayDict[dummyCaBaMaTable.ComponentID[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt2]]['Breakdown']:
                            dummyList = []
                           
                            keys = self.__arrayDict.keys()                    
                            for iCnt1 in range(0,len(keys)):                       
                                
                                if 'device' in keys[iCnt1]:
                                    dummyList.append(str(keys[iCnt1]))
                            
                            downtimeDeviceList.append(dummyList)
                            
                        else:
                            
#                        if str(dummyCaBaMaTable.ComponentType[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt2]) in self.__arrayDict[dummyCaBaMaTable.ComponentID[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt2]]['Breakdown']:
                            #downtimeDeviceList.append(str(dummyCaBaMaTable.ComponentType[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt2])) 
                            downtimeDeviceList.append(self.__arrayDict[dummyCaBaMaTable.ComponentID[iCnt*self.__CaBaMa_nrOfMaxActions + iCnt2]]['Breakdown'])
                                                          
                    # time consumption CaBaMa 
                    stop_time_CaBaMa = timeit.default_timer()
                    
                    if self.__dtocean_operations_PRINT_FLAG == True:
                        print 'calcCaBaMa: Simulation Duration [s]  : ' + str((stop_time_CaBaMa - start_time_CaBaMa)-(stop_time_logistic - start_time_logistic))
   
                    if self.__om_logistic['findSolution'] == 'SolutionFound':
                                                
                        for iCnt1 in range(0,blockNumber):                     
                                               
                            valuesForOutput = [str(currentStartActionDate), str(currentStartActionDateList[iCnt1]), 
                                               int(totalDownTimeHours/float(blockNumber)), '', str(ComponentTypeList[iCnt1]),
                                               str(ComponentSubTypeList[iCnt1]), str(ComponentIDList[iCnt1]),
                                               FM_ID, RA_ID, indexFM, int(optLogisticCostValue), 
                                               int(omCostValue-omCostValueSpare), int(omCostValueSpare)]                                               
                                                                                                                                                                                          
                            self.__CaBaMa_outputEventsTable.ix[loopValuesForOutput_CaBaMa] = valuesForOutput                           
                            self.__CaBaMa_outputEventsTable.loc[loopValuesForOutput_CaBaMa,'downtimeDeviceList [-]'] = downtimeDeviceList[iCnt1]
                            
                            loopValuesForOutput_CaBaMa = loopValuesForOutput_CaBaMa + 1 
                        
                        # for environmental team                                             
                        self.__env_assess(loop, currentStartActionDate, FM_ID, RA_ID, self.__om_logistic['optimal']['schedule sea time'], 'CaBaMa')                                                                                    
                        loop = loop + 1                                               
                                                                     
                if self.__actIdxOfCaBaMa == len(self.__CaBaMa_eventsTable):
                    flagCalcCaBaMa = False
                    loop = 0
                    
                    if self.__Farm_OM['corrective_maintenance'] == True:
                        flagCalcUnCoMa = True
                            
                    else:                                                        
                        if self.__Farm_OM['condition_based_maintenance'] == True:
                            flagCalcCoBaMa = True                                                                                              
                    continue  
                    
                      
            # unplaned corrective maintenance
            # start
            # *****************************************************************
            # *****************************************************************                        
            if self.__Farm_OM['corrective_maintenance'] == True and flagCalcUnCoMa == True:
                

        
                start_time_UnCoMa = timeit.default_timer()
                
                #UnCoMa_eventsTable = self.__UnCoMa_eventsTable
                #arrayDict = self.__arrayDict
                                
                # actualIndexOfRepairTable is determined
                # do the the reapir   
                ComponentType       = str(self.__UnCoMa_eventsTable.ComponentType[self.__actIdxOfUnCoMa])
                ComponentSubType    = str(self.__UnCoMa_eventsTable.ComponentSubType[self.__actIdxOfUnCoMa])
                ComponentID         = str(self.__UnCoMa_eventsTable.ComponentID[self.__actIdxOfUnCoMa])
                RA_ID               = str(self.__UnCoMa_eventsTable.RA_ID[self.__actIdxOfUnCoMa])  
                FM_ID               = str(self.__UnCoMa_eventsTable.FM_ID[self.__actIdxOfUnCoMa])     
                belongsTo           = str(self.__UnCoMa_eventsTable.belongsTo[self.__actIdxOfUnCoMa])              
                failureEvents       = self.__UnCoMa_eventsTable.failureEvents[self.__actIdxOfUnCoMa]                
                repairActionEvents  = self.__UnCoMa_eventsTable.repairActionEvents[self.__actIdxOfUnCoMa]
                failureRate         = self.__UnCoMa_eventsTable.failureRate[self.__actIdxOfUnCoMa]
                
                
                # simulate or not
                simulateFlag = True
                
                if self.__NrOfDevices == self.__NrOfTurnOutDevices:
                    simulateFlag = False
                    
                else:
                    
                  # set the simulateFlag?
                    if belongsTo == 'Array':
                                             
                        if self.__arrayDict[ComponentID]['UnCoMaNoWeatherWindow'] == True:
                            simulateFlag = False
                             
                    else:
                        
                        if 'device' in ComponentType and self.__arrayDict[ComponentType]['UnCoMaNoWeatherWindow'] == True:
                            simulateFlag = False              
                
                if simulateFlag == False:
                    self.__actIdxOfUnCoMa = self.__actIdxOfUnCoMa + 1
                    
                else:
                                                                
                    # delay of repairActionEvents in repair plan
                    if self.__totalActionDelayHour < 0:
                        shiftDate = self.__UnCoMa_eventsTable.loc[self.__actIdxOfUnCoMa, 'repairActionEvents'] + timedelta(hours = -self.__totalActionDelayHour)
                        self.__UnCoMa_eventsTable.loc[self.__actIdxOfUnCoMa, 'repairActionEvents'] = shiftDate 
                        repairActionEvents = self.__UnCoMa_eventsTable.repairActionEvents[self.__actIdxOfUnCoMa]
                  
                    # failureEvents               
                    failureDate         = datetime.datetime.strptime(str(failureEvents), self.__strFormat2)
                    # Date of logistic request
                    self.__repairActionDate    = datetime.datetime.strptime(str(repairActionEvents), self.__strFormat2) 
                    repairActionDateStr = repairActionEvents.strftime(self.__strFormat1)                     
                    indexFM             = self.__UnCoMa_eventsTable.indexFM[self.__actIdxOfUnCoMa]
                    CompIDWithIndex     = ComponentID + '_' + str(indexFM)
                    
                    # break the while loop if repairActionDate is greater than self.__endOperationDate               
                    if self.__endOperationDate < self.__repairActionDate:
                                                           
                        flagCalcUnCoMa = False 
                        loop = 0
                                
                        if self.__Farm_OM['condition_based_maintenance'] == True:
                            flagCalcCoBaMa = True
                            
                        continue  
                    
                    foundDeleteFlag = False
                    
                    # check the impact of CaBaMa of UnCoMa
                    if self.__Farm_OM['calendar_based_maintenance'] == True:
                        
                        # find the blocks in CaBaMa
                        if 'device' in ComponentType:
                            CaBaMaTableQueryDeviceID  = ComponentType
                            CaBaMaTableQuerySubSystem = ComponentSubType
                                
                        elif 'subhub' in ComponentType:
                            CaBaMaTableQueryDeviceID = ComponentType
        
                        else:                    
                            CaBaMaTableQueryDeviceID  = 'Array'
                            CaBaMaTableQuerySubSystem = ComponentType[0:-3]                        
                                                                        
                        if 'subhub' in ComponentType:
                            dummyCaBaMaTable = self.__CaBaMa_eventsTable.loc[(self.__CaBaMa_eventsTable['ComponentType'] == CaBaMaTableQueryDeviceID) & \
                            (self.__CaBaMa_eventsTable['FM_ID'] == FM_ID) & \
                            (self.__CaBaMa_eventsTable['indexFM'] == indexFM)]
                            
                            if 1 < len(dummyCaBaMaTable):
                                
                                dummyCaBaMaTable.reset_index(drop=True, inplace=True) 
                                                            
                                for iCnt in range(0,len(dummyCaBaMaTable)):
                                    dummyTime = (repairActionEvents - dummyCaBaMaTable.currentEndActionDate[iCnt]).total_seconds() // 3600
                                    if dummyTime < self.__delayEventsAfterCaBaMaHour: 
                                        foundDeleteFlag = True                                    
                                        break
                           
                        else:
                            dummyCaBaMaTable = self.__CaBaMa_eventsTable.loc[(self.__CaBaMa_eventsTable['RA_ID'] == RA_ID) & \
                            (self.__CaBaMa_eventsTable['ComponentSubType'] == CaBaMaTableQuerySubSystem) & \
                            (self.__CaBaMa_eventsTable['FM_ID'] == FM_ID) & \
                            (self.__CaBaMa_eventsTable['indexFM'] == indexFM)]
                            
                            if 1 < len(dummyCaBaMaTable):
                                
                                dummyCaBaMaTable.reset_index(drop=True, inplace=True) 
                                                            
                                for iCnt in range(0,len(dummyCaBaMaTable)):                                
                                    dummyTime = (repairActionEvents - dummyCaBaMaTable.currentEndActionDate[iCnt]).total_seconds() // 3600
                                    if dummyTime < self.__delayEventsAfterCaBaMaHour: 
                                        foundDeleteFlag = True  
                                        break
                    
                    if foundDeleteFlag == True: 
                        self.__actIdxOfUnCoMa = self.__actIdxOfUnCoMa + 1
                                                                 
                    if foundDeleteFlag == False:                
                   
                        if self.__dtocean_operations_PRINT_FLAG == True:
                            
                            print 'WP6: ******************************************************'
                            print 'WP6: actIdxOfUnCoMa = ', self.__actIdxOfUnCoMa
                            print 'WP6: ComponentID = ', ComponentID 
                            print 'WP6: RA_ID = ', RA_ID 
                            print 'WP6: FM_ID = ', FM_ID
        
                            
                            
                        # independent from inspection or repair action
                        sp_dry_mass = self.__Failure_Mode[CompIDWithIndex]['spare_mass']
                        sp_length   = self.__Failure_Mode[CompIDWithIndex]['spare_length'] 
                        sp_width    = self.__Failure_Mode[CompIDWithIndex]['spare_width'] 
                        sp_height   = self.__Failure_Mode[CompIDWithIndex]['spare_height']                 
                        
                        if 'Insp' in FM_ID:
                            
                            # For logistic
                            d_acc       = self.__Inspection[CompIDWithIndex]['duration_accessibility'] 
                            d_om        = self.__Inspection[CompIDWithIndex]['duration_inspection']   
                            helideck    = self.__Farm_OM['helideck'] 
                            Hs_acc      = self.__Inspection[CompIDWithIndex]['wave_height_max_acc'] 
                            Tp_acc      = self.__Inspection[CompIDWithIndex]['wave_periode_max_acc']  
                            Ws_acc      = self.__Inspection[CompIDWithIndex]['wind_speed_max_acc']  
                            Cs_acc      = self.__Inspection[CompIDWithIndex]['current_speed_max_acc'] 
                            Hs_om       = self.__Inspection[CompIDWithIndex]['wave_height_max_om'] 
                            Tp_om       = self.__Inspection[CompIDWithIndex]['wave_periode_max_om']  
                            Ws_om       = self.__Inspection[CompIDWithIndex]['wind_speed_max_om']  
                            Cs_om       = self.__Inspection[CompIDWithIndex]['current_speed_max_om'] 
                            technician  = self.__Inspection[CompIDWithIndex]['number_technicians'] + self.__Inspection[CompIDWithIndex]['number_specialists'] 
                            
                            Dist_port   = self.__portDistIndex['inspection'][0]
                            Port_Index  = self.__portDistIndex['inspection'][1]       
                        
                        else:
                            
                            # for logistic
                            d_acc       = self.__Repair_Action[CompIDWithIndex]['duration_accessibility'] 
                            d_om        = self.__Repair_Action[CompIDWithIndex]['duration_maintenance']
                            helideck    = self.__Farm_OM['helideck'] 
                            Hs_acc      = self.__Repair_Action[CompIDWithIndex]['wave_height_max_acc'] 
                            Tp_acc      = self.__Repair_Action[CompIDWithIndex]['wave_periode_max_acc']  
                            Ws_acc      = self.__Repair_Action[CompIDWithIndex]['wind_speed_max_acc']  
                            Cs_acc      = self.__Repair_Action[CompIDWithIndex]['current_speed_max_acc'] 
                            Hs_om       = self.__Repair_Action[CompIDWithIndex]['wave_height_max_om'] 
                            Tp_om       = self.__Repair_Action[CompIDWithIndex]['wave_periode_max_om']  
                            Ws_om       = self.__Repair_Action[CompIDWithIndex]['wind_speed_max_om']  
                            Cs_om       = self.__Repair_Action[CompIDWithIndex]['current_speed_max_om'] 
                            technician  = self.__Repair_Action[CompIDWithIndex]['number_technicians'] + self.__Repair_Action[CompIDWithIndex]['number_specialists'] 
                            
                            Dist_port   = self.__portDistIndex['repair'][0]
                            Port_Index  = self.__portDistIndex['repair'][1]
                                              
                        if belongsTo == 'Array':
                            
                            depth      = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['depth']
                            x_coord    = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['x coord'] 
                            y_coord    = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['y coord']
                            zone       = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['zone']  
                            Bathymetry = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['Bathymetry']
                            Soil_type  = self.__Simu_Param['arrayInfoLogistic'][ComponentID]['Soil type']                                          
                        
                        else:
                            
                            depth      = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['depth']
                            x_coord    = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['x coord'] 
                            y_coord    = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['y coord']
                            zone       = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['zone']  
                            Bathymetry = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['Bathymetry']
                            Soil_type  = self.__Simu_Param['arrayInfoLogistic'][belongsTo]['Soil type']  
                            
                        if belongsTo == 'Array':
                            
                            if 'Substation' in ComponentType:
                                ComponentTypeLogistic = 'collection point'
                                ComponentIDLogistic   = ComponentID
                                
                            elif 'subhub' in ComponentType:
                                ComponentTypeLogistic = 'collection point'
                                ComponentIDLogistic   = ComponentID
                                
                            elif 'Export Cable' in ComponentType:
                                ComponentTypeLogistic = 'static cable'
                                ComponentIDLogistic   = int(ComponentID[-3:len(ComponentID)])
                                
                            else:
                                ComponentTypeLogistic = ComponentType
                                ComponentIDLogistic   = ComponentID                        
                        
                        else:
                            
                            # Adjustmet of the names to logistic
                            # The name of subsystems in logistic and RAM are differnt             
                            if 'Dynamic cable' in ComponentSubType:
                                ComponentTypeLogistic = 'dynamic cable'
                                # problem with logistic database
                                ComponentIDLogistic   = 0#int(ComponentID[-3:len(ComponentID)])
                                
                            elif 'Mooring line' in ComponentSubType:
                                ComponentTypeLogistic = 'mooring line'
                                ComponentIDLogistic   = int(ComponentID[-3:len(ComponentID)])
                                
                            elif 'Foundation' in ComponentSubType:
                                ComponentTypeLogistic = 'foundation'
                                ComponentIDLogistic   = ComponentID
                                
                            else:
                                ComponentTypeLogistic = ComponentType
                                ComponentIDLogistic   = ComponentID
                                
                            if 'device' in ComponentTypeLogistic:
                                ComponentTypeLogistic = 'device'
          
                        # Values for logistic
                        values = [FM_ID, ComponentTypeLogistic, ComponentSubType, ComponentIDLogistic,
                                  depth,
                                  x_coord, 
                                  y_coord,
                                  zone,  
                                  repairActionDateStr, d_acc, d_om, str(helideck),
                                  Hs_acc, Tp_acc, Ws_acc, Cs_acc,
                                  Hs_om, Tp_om, Ws_om, Cs_om,
                                  technician,
                                  sp_dry_mass, sp_length, sp_width, sp_height,
                                  Dist_port, Port_Index,
                                  Bathymetry,
                                  Soil_type,
                                  self.__PrepTimeCalcUnCoMa
                                  ]
                                                                                                     
                        self.__wp6_outputsForLogistic.ix[0] = values
                                                                    
                        self.__actIdxOfUnCoMa = self.__actIdxOfUnCoMa + 1
                        
                        # Calc logistic functions
                        start_time_logistic = timeit.default_timer()                    
                        self.__calcLogistic() 
                        stop_time_logistic = timeit.default_timer()
                        
                        om_logistic = self.__om_logistic
                                            
                        if self.__dtocean_operations_PRINT_FLAG == True:
                            print 'calcLogistic: Simulation Duration [s]: ' + str(stop_time_logistic - start_time_logistic)
                                                               
                        if self.__om_logistic['findSolution'] == 'NoSolutionsFound':
                                                       
                            if self.__dtocean_operations_PRINT_FLAG == True:
                                print 'WP6: ErrorID = NoSolutionsFound!'                                                                     
                                print 'WP6: values = ', values 
                            
                        if self.__om_logistic['findSolution'] == 'SolutionFound' or self.__om_logistic['findSolution'] == 'NoWeatherWindowFound':
                            
                            if self.__om_logistic['findSolution'] == 'NoWeatherWindowFound':
                                
                                if self.__dtocean_operations_PRINT_FLAG == True:                                                         
                                    print 'WP6: ErrorID = NoWeatherWindowFound!'
                                    print 'WP6: values = ', values 
                              
                            if self.__om_logistic['findSolution'] == 'SolutionFound' or (self.__om_logistic['findSolution'] == 'NoWeatherWindowFound' and self.__ignoreWeatherWindow == False):
                            
                                if  (self.__om_logistic['findSolution'] == 'NoWeatherWindowFound' and self.__ignoreWeatherWindow == False):
                                                           
                                    optLogisticCostValue = 0                            
                                    omCostValueSpare     = 0
                                    omCostValue          = 0 
                                    totalDownTimeHours   = (self.__endOperationDate- failureEvents).total_seconds() // 3600
                                    self.__departOpDate  = self.__endOperationDate
                                                                                                                                 
                                else:
                                
                                    self.__endOpDate    = datetime.datetime(self.__om_logistic['optimal']['end_dt'].year,
                                                                            self.__om_logistic['optimal']['end_dt'].month,
                                                                            self.__om_logistic['optimal']['end_dt'].day,
                                                                            self.__om_logistic['optimal']['end_dt'].hour,
                                                                            self.__om_logistic['optimal']['end_dt'].minute,0)
                                                            
                                    # In LpM7 case self.__om_logistic['optimal']['depart_dt'] is a dict
                                    if type(self.__om_logistic['optimal']['depart_dt']) == dict:
                                        dummy__departOpDate = self.__om_logistic['optimal']['depart_dt']['weather windows depart_dt_replace']
                                        dummy__departOpDate = self.__om_logistic['optimal']['depart_dt']['weather windows depart_dt_retrieve']
                                    else:
                                        dummy__departOpDate = self.__om_logistic['optimal']['depart_dt']
                                    
                                    
                                    self.__departOpDate    = datetime.datetime(dummy__departOpDate.year,
                                                                               dummy__departOpDate.month,
                                                                               dummy__departOpDate.day,
                                                                               dummy__departOpDate.hour,
                                                                               dummy__departOpDate.minute,0)
                                                                                                                                 
                                    # total optim cost from logistic            
                                    optLogisticCostValue = self.__om_logistic['optimal']['total cost']
                                                                                                    
                                    # should the next operation be shifted? Check self.__repairTable 
                                    if self.__actIdxOfUnCoMa < len(self.__UnCoMa_eventsTable) - 1:
                                        self.__actActionDelayHour   = (self.__UnCoMa_eventsTable.repairActionEvents[self.__actIdxOfUnCoMa+1] - self.__endOpDate).total_seconds()/3600 
                                        self.__totalActionDelayHour = self.__totalActionDelayHour + self.__actActionDelayHour
                                                                                 
                                    # Calculation of total action time (hour) 
                                    # Error in logistic, Therefore calculation in WP6 
                                    self.__totalSeaTimeHour   = (self.__endOpDate - self.__departOpDate).total_seconds() // 3600
                                    
                                    self.__om_logistic['optimal']['schedule sea time'] = self.__totalSeaTimeHour
                                                               
                                    totalDownTimeHours = (self.__endOpDate - failureDate).total_seconds() // 3600
                                    
                                    totalWaitingTimeHours = totalDownTimeHours - self.__totalSeaTimeHour
                                    
                                    omCostValueSpare, omCostValue = self.__calcCostOfOM(FM_ID, CompIDWithIndex)
                                                             
                                                                                                              
                                # Save the cost of operation
                                if belongsTo == 'Array':
                                     
                                    # Cost
                                    self.__arrayDict[ComponentID]['UnCoMaCostLogistic'].append(round(optLogisticCostValue,1))
                                    self.__arrayDict[ComponentID]['UnCoMaCostOM'].append(round(omCostValue,1))   
                                        
                                else:
                                    
                                    if 'device' in ComponentType:
                                        
                                        # Inspection cost
                                        self.__arrayDict[ComponentType]['UnCoMaCostLogistic'].append(round(optLogisticCostValue,1))
                                        self.__arrayDict[ComponentType]['UnCoMaCostOM'].append(round(omCostValue,1))
                                                       
                                # Save the information about failure and down time in devices
                                downtimeDeviceList = []
                                keys = self.__arrayDict.keys()
                                

                                for iCnt1 in range(0,len(keys)):                       
                                    
                                    if 'device' in keys[iCnt1] and self.__arrayDict[keys[iCnt1]]['UnCoMaNoWeatherWindow'] == False:
                                        
                                        if 'All' in self.__arrayDict[ComponentID]['Breakdown'] or keys[iCnt1] in self.__arrayDict[ComponentID]['Breakdown']:
                                            
                                            if self.__om_logistic['findSolution'] == 'NoWeatherWindowFound' and self.__ignoreWeatherWindow == False:
                                                self.__arrayDict[keys[iCnt1]]['UnCoMaNoWeatherWindow'] = True
                                                self.__NrOfTurnOutDevices = self.__NrOfTurnOutDevices + 1
                                            
                                            downtimeDeviceList.append(str(keys[iCnt1]))
                                            # Save the information about failure
                                            self.__arrayDict[keys[iCnt1]]['UnCoMaOpEvents'].append(failureDate)
                                            self.__arrayDict[keys[iCnt1]]['UnCoMaOpEventsDuration'].append(totalDownTimeHours)
                                            self.__arrayDict[keys[iCnt1]]['UnCoMaOpEventsIndexFM'].append(indexFM)
                                            self.__arrayDict[keys[iCnt1]]['UnCoMaOpEventsCausedBy'].append(str(ComponentID)) 
                                            
                                            if not 'device' in ComponentType:
                                                 
                                                self.__arrayDict[keys[iCnt1]]['UnCoMaCostLogistic'].append(0.0)
                                                self.__arrayDict[keys[iCnt1]]['UnCoMaCostOM'].append(0.0)                               
                                                self.__arrayDict[ComponentID]['UnCoMaNoWeatherWindow'] = True
                                                                
                                # loopValuesForOutput
                                loopValuesForOutput_UnCoMa = loopValuesForOutput_UnCoMa + 1

                                if self.__om_logistic['findSolution'] == 'SolutionFound':
                                    
                                    # Update poisson events in eventTables
                                    self.__updatePoissonEvents() 
                                    
                                    # for environmental team                                             
                                    self.__env_assess(loop, failureDate, FM_ID, RA_ID, self.__om_logistic['optimal']['schedule sea time'], 'UnCoMa')
                                    
                                    
                                    valuesForOutput = [failureRate, str(failureEvents.replace(second=0)), 
                                                       str(repairActionEvents.replace(second=0)),                                                                                                
                                                       str(self.__departOpDate.replace(second=0)),
                                                       int(totalDownTimeHours), self.__totalSeaTimeHour, totalWaitingTimeHours, 
                                                       '', ComponentType, ComponentSubType, ComponentID,
                                                       FM_ID, RA_ID, indexFM, int(optLogisticCostValue), 
                                                       int(omCostValue-omCostValueSpare), int(omCostValueSpare),
                                                       self.__om_logistic['optimal']['vessel_equipment'][0][0], self.__om_logistic['optimal']['vessel_equipment'][0][1] ] 
                                                                                       
                                    self.__UnCoMa_outputEventsTable.ix[loopValuesForOutput_UnCoMa] = valuesForOutput                                                                
                                    self.__UnCoMa_outputEventsTable.loc[loopValuesForOutput_UnCoMa,'downtimeDeviceList [-]'] = downtimeDeviceList

                                    # loop
                                    loop = loop + 1                
                                                         
                                    # time consumption UnCoMa 
                                    stop_time_UnCoMa = timeit.default_timer()
                                    
                                    if self.__dtocean_operations_PRINT_FLAG == True:
                                        print 'calcUnCoMa: Simulation Duration [s]  : ' + str((stop_time_UnCoMa - start_time_UnCoMa)-(stop_time_logistic - start_time_logistic))
                         
                if self.__actIdxOfUnCoMa == len(self.__UnCoMa_eventsTable):
                    flagCalcUnCoMa = False
                    loop = 0
                    
                    if self.__Farm_OM['condition_based_maintenance'] == True:
                        flagCalcCoBaMa = True 
                        
                    continue
                    
                # unplaned corrective maintenance
                # end
                # *****************************************************************
                # *****************************************************************
                   
                                          
                              
        return 
        
    # function for the __env_assess     
    def __env_assess(self, loop, failureDate, FM_ID, RA_ID, optSeaTime, maintenanceType):
        
        '''Collection of signals for enviroumental assessment 
        
        Args:
            No args
            
        Returns:
            No returns 
        
        ''' 

        # For environmental assessment
        dictEnvAssessDummy = {}
        dictEnvAssessDummy['typeOfvessels [-]']    = []
        dictEnvAssessDummy['nrOfvessels [-]']      = []                      
        dictEnvAssessDummy['timeStampActions [-]'] = failureDate                        
        dictEnvAssessDummy['FM_ID [-]']            = FM_ID
        dictEnvAssessDummy['RA_ID [-]']            = RA_ID  
        dictEnvAssessDummy['duration [h]']         = optSeaTime  
         
        for iCnt1 in range(0,len(self.__om_logistic['optimal']['vessel_equipment'])):                        
            dictEnvAssessDummy['typeOfvessels [-]'].append(self.__om_logistic['optimal']['vessel_equipment'][iCnt1][0])
        
        dictEnvAssessDummy['nrOfvessels [-]'].append(self.__om_logistic['optimal']['vessel_equipment'][iCnt1][1])                           
        
        if maintenanceType == 'UnCoMa': 
            self.__UnCoMa_dictEnvAssess[loop] = dictEnvAssessDummy
            
        if maintenanceType == 'CaBaMa':
            self.__CaBaMa_dictEnvAssess[loop] = dictEnvAssessDummy
        
        if maintenanceType == 'CoBaMa':
            self.__CoBaMa_dictEnvAssess[loop] = dictEnvAssessDummy        
        
        return 
       
    def __calcLCOE_OfArray(self):
         
        '''__calcLCOE_OfArray function: estimation of the of whole array
                                                      
        Args:              
            no arguments  
        
        Attributes:         
            no attributes                  
 
        Returns:
            no returns
      
        '''         
                       
        # calculation of costs
        self.__calcLCOE_OfOM()
                        
        # Calculation after the end of simulation
        self.__postCalculation()
        
        return 
        
        
    # calculation of RAM    
    def __calcRAM(self):
                
        '''__calcRAM function: calls of dtocean-reliability and saves the results 
                                                      
        Args:              
            no arguments  
        
        Attributes:         
            no attributes                  
 
        Returns:
            no returns
      
        '''                 
       
        # Execute call method of RAM 
        self.__ramPTR()  
        
        # list rsubsysvalues from RAM
        self.__rsubsysvalues = self.__ramPTR.rsubsysvalues3
        
        # list rcompvalues from RAM
        self.__rcompvalues = self.__ramPTR.rcompvalues3
                
        return
    
      
    def __calcLogistic(self):
        
        '''__calcLogistic function: calls of dtocean-logistics and saves the results 
                                                      
        Args:              
            no arguments  
        
        Attributes:         
            no attributes                  
 
        Returns:
            no returns
      
        '''                         

        self.__om_logistic = om_logistics_main(copy.deepcopy(self.__vessels), copy.deepcopy(self.__equipments), copy.deepcopy(self.__ports),
                                         self.__schedule_OLC, self.__other_rates, copy.deepcopy(self.__port_sf), copy.deepcopy(self.__vessel_sf), copy.deepcopy(self.__eq_sf),
                                         self.__site, self.__metocean, self.__device, self.__sub_device, self.__entry_point,
                                         self.__layout,
                                         self.__collection_point, self.__dynamic_cable, self.__static_cable, self.__connectors,
                                         self.__wp6_outputsForLogistic,
                                         self.__dtocean_logistics_PRINT_FLAG
                                         )   
                                                                                                                        
        return
        
    # change of labels of tables    
    def __changeOfLabels(self):
        
        '''__changeOfLabels function: changes the labels of some tables 
                                                      
        Args:              
            no arguments  
        
        Attributes:         
            no attributes                  
 
        Returns:
            no returns
      
        '''                      
      
        # Component -> Component_ID
        # Component
        self.__Component.rename(columns=dict(zip(self.__Component.columns, list(self.__Component.loc['Component_ID']))), inplace=True)
                
        # Component -> Component_ID
        # Simu_Param        
        self.__Simu_Param['arrayInfoLogistic'].rename(columns=dict(zip(self.__Simu_Param['arrayInfoLogistic'].columns, list(self.__Simu_Param['arrayInfoLogistic'].loc['Component_ID']))), inplace=True)
                            
        # Repair_Action
        nuOfColumnsRA = self.__Repair_Action.shape[1]
        idListRA      = list(self.__Repair_Action.loc['Component_ID']) 
        fmListRA      = list(self.__Repair_Action.loc['FM_ID'])  
        
        newColumnsRA = []        
        for iCnt in range(0,nuOfColumnsRA):
            newColumnsRA.append('dummy')
        
        # Inspection
        nuOfColumnsInsp = self.__Inspection.shape[1]
        idListInsp      = list(self.__Inspection.loc['Component_ID'])   
        fmListInsp      = list(self.__Inspection.loc['FM_ID'])   
        newColumnsInsp = []        
        for iCnt in range(0,nuOfColumnsInsp):
            newColumnsInsp.append('dummy')
       
        # Failure_Mode
        nuOfColumns = self.__Failure_Mode.shape[1]
        idList = list(self.__Failure_Mode.loc['Component_ID'])
        fmList = list(self.__Failure_Mode.loc['FM_ID'])
        
        newColumns = []
        for iCnt in range(0,nuOfColumns):
            if len(newColumns) == 0:
                newColumns.append(idList[iCnt] + '_1')
              
            else:
                index = 0
                for iCnt1 in range(0,len(newColumns)):
                    if idList[iCnt] == string.rsplit(newColumns[iCnt1],'_')[0]:
                         index = index + 1                
                
                if index == 0:
                    newColumns.append(idList[iCnt] + '_1')
                else:
                    newColumns.append(idList[iCnt] + '_' + str(index + 1))
            

            indexList = -1
            for iCnt1 in range(0,nuOfColumnsRA):
                if idListRA[iCnt1] == idList[iCnt] and fmListRA[iCnt1] == fmList[iCnt]:  
                    indexList = iCnt1
                    break
            if indexList != -1:  
                newColumnsRA[indexList] = newColumns[-1]
            
            indexList = -1
            for iCnt1 in range(0,nuOfColumnsInsp):
                if idListInsp[iCnt1] == idList[iCnt] and fmListInsp[iCnt1] == fmList[iCnt]:  
                    indexList = iCnt1
                    break
            
            if indexList != -1:  
                newColumnsInsp[indexList] = newColumns[-1]
    
        
        # Failure_Mode
        self.__Failure_Mode.rename(columns=dict(zip(self.__Failure_Mode.columns, newColumns)), inplace=True)
        
        # Repair_Action
        self.__Repair_Action.rename(columns=dict(zip(self.__Repair_Action.columns, newColumnsRA)), inplace=True)
        
        # Inspection
        self.__Inspection.rename(columns=dict(zip(self.__Inspection.columns, newColumnsInsp)), inplace=True)
    
        return
