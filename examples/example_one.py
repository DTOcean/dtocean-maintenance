# -*- coding: utf-8 -*-
"""This file simulates a simple interface between core and dtocean-maintenance

.. module:: coreSimu
   :platform: Windows
   :synopsis: simulation of a simple interface between core and WP6 module for test purposes
   
.. moduleauthor:: Bahram Panahandeh <bahram.panahandeh@iwes.fraunhofer.de>
                  Mathew Topper <dataonlygreater@gmail.com>
"""

import os
import sys
import time
import pickle
import random
import logging
import datetime

import pandas as pd
import numpy as np

from dtocean_logistics.load import load_phase_order_data, load_time_olc_data
from dtocean_logistics.load import load_eq_rates
from dtocean_logistics.load import load_sf
from dtocean_logistics.load import load_vessel_data, load_equipment_data
from dtocean_logistics.load import load_port_data
from dtocean_logistics.load.wp_bom import (load_user_inputs,
                                           load_hydrodynamic_outputs)
from dtocean_logistics.load.wp_bom import load_electrical_outputs

from dtocean_maintenance.main import LCOE_Optimiser
from dtocean_maintenance.input import inputOM

module_logger = logging.getLogger(__name__)


# dummy function to load files from the database folder of reliability    
def database_reliability(file):
    
    '''dummy function, shortcut function to load files from the database folder 
    
    Args:
        file (string)    : The name of file to read from.
        
    Attributes:         
        no attributes                      
 
    Returns:
        db_path (string) : Path to excel files 
    
    '''             
   
    # Set directory paths for loading inputs
    mod_path = os.path.dirname(os.path.realpath(__file__)) 

    if 'coreSimu' in sys.argv[0] or 'coresimu' in sys.argv[0]:
        fpath = os.path.join('..\\tests\databases\dtocean-reliability',
                             '{0}'.format(file)) 
       
    else:
        fpath = os.path.join('databases\dtocean-reliability',
                             '{0}'.format(file))
        
    db_path = os.path.join(mod_path, fpath)
    return db_path
    
# dummy function to load files from the database folder of logistic     
def database_logistic(file):
    
    '''dummy function, shortcut function to load files from the database folder 
    
    Args:
        file (string)    : The name of file to read from.
        
    Attributes:         
        no attributes                      
        
    Returns:
        db_path (string) : Path to excel files 
    
    '''             
   
    # Set directory paths for loading inputs
    mod_path = os.path.dirname(os.path.realpath(__file__)) 

    if 'coreSimu' in sys.argv[0] or 'coresimu' in sys.argv[0]:
        fpath = os.path.join('..\\tests\databases\dtocean-logistics',
                             '{0}'.format(file))
       
    else:
        fpath = os.path.join('databases\dtocean-logistics',
                             '{0}'.format(file))
                  
    db_path = os.path.join(mod_path, fpath)
    
    return db_path  
    
    
# dummy function to to load files from the database folder of operations     
def database_operations(file, mode):
    
    '''dummy function, shortcut function to load files from the database folder 
    
    Args:
        file (string)    : The name of file to read from.
        
    Attributes:         
        no attributes                      
 
    Returns:
        db_path (string) : Path to excel files 
    
    '''                
    # Set directory paths for loading inputs
    mod_path = os.path.dirname(os.path.realpath(__file__)) 

    if 'coreSimu' in sys.argv[0] or 'coresimu' in sys.argv[0]:
        fpath = os.path.join('..\\tests\databases\dtocean-maintenance',
                             '{0}'.format(file))
       
    else:
        fpath = os.path.join('databases\dtocean-maintenance',
                             '{0}'.format(file))      
                
    db_path = os.path.join(mod_path, fpath)
    
    returnValue = [] 
    
    if mode == 'Farm_OM':
        # Transform the .xls database into panda table
        excel = pd.ExcelFile(db_path)
    
        # Collect data from a particular tab
        returnValue.append(excel.parse('FarmOM', header=0, index_col=0))
        
    else:
        # Transform the .xls database into panda table
        excel = pd.ExcelFile(db_path)
    
        # Collect data from a particular tab
        returnValue.append(excel.parse('Components', header=0, index_col=0))
        returnValue.append(excel.parse('FailureModes', header=0, index_col=0))
        returnValue.append(excel.parse('RepairActions', header=0, index_col=0))
        returnValue.append(excel.parse('Inspections', header=0, index_col=0))            
           
    return returnValue

def test(): 

    # parameters of dtocean-operations
    # *****************************************************************************
    # *****************************************************************************
    # *****************************************************************************    
    # declaration      
    Farm_OM = {}
    Component = {}
    Failure_Mode = {}
    Repair_Action = {}
    Inspection = {}
    RAM_Param = {}
    Logistic_Param = {}
    Simu_Param = {}
    Control_Param = {}
    
    # load the core data
    #dataCore = pickle.load(open( "fixed_tidal_electrical_reliability_inputs.pkl", "rb" )) 
    
    
    ###############################################################################
    ###############################################################################
    ###############################################################################
    # Some of the function developed by logistic takes some times for running. 
    # With the following flags is possible to control the call of such functions.
    
    # flag: integrateSelectPort
    # Control_Param['integrateSelectPort'] is True  -> call OM_PortSelection
    # Control_Param['integrateSelectPort'] is False -> do not call OM_PortSelection, set constant values for port parameters
    Control_Param['integrateSelectPort'] = False 
    
    # flag: checkNoSolution
    # Control_Param['checkNoSolution'] is True  -> check the feasibility of logistic solution before the simulation 
    # Control_Param['checkNoSolution'] is False -> do not check the feasibility of logistic solution before the simulation
    Control_Param['checkNoSolution'] = False 
    
    # flag: dtocean_maintenance print flag               
    # Control_Param['dtocean_maintenance_PRINT_FLAG'] is True  -> print is allowed inside of dtocean_maintenance
    # Control_Param['dtocean_maintenance_PRINT_FLAG'] is False -> print is not allowed inside of dtocean_maintenance
    Control_Param['dtocean_maintenance_PRINT_FLAG'] = False 
    
    # flag: dtocean-logistics print flag               
    # Control_Param['dtocean_logistics_PRINT_FLAG'] is True  -> print is allowed inside of dtocean-logistics
    # Control_Param['dtocean_logistics_PRINT_FLAG'] is False -> print is not allowed inside of dtocean-logistics
    Control_Param['dtocean_logistics_PRINT_FLAG'] = False
    
    # flag: dtocean_maintenance test flag               
    # Control_Param['dtocean_maintenance_TEST_FLAG'] is True  -> print the results in excel files
    # Control_Param['dtocean_maintenance_TEST_FLAG'] is False -> do not print the results in excel files
    Control_Param['dtocean_maintenance_TEST_FLAG'] = True 
    
    # Flag: read from RAM
    # Control_Param['readFailureRateFromRAM'] is True  -> Failure rate is read from RAM
    # Control_Param['readFailureRateFromRAM'] is False -> Failure rate is read from component table (IWES)
    Control_Param['readFailureRateFromRAM'] = True 
    
    # flag: ignore weather window in case of corrective_maintenance and condition_based_maintenance  
    # Control_Param['ignoreWeatherWindow'] is True  -> The case "NoWeatherWindowFound" will be ignored in dtocean-operations 
    # Control_Param['ignoreWeatherWindow'] is False -> The case "NoWeatherWindowFound" wont be ignored in dtocean-operations. In this case the coresponding device/devices will be switched off.
    # This flag is internally set to True in case of calendar_based_maintenance    
    Control_Param['ignoreWeatherWindow'] = True 
    
    ###############################################################################
    ###############################################################################
    ############################################################################### 
         
    # Decision parameter
    # read from the files
    farmFile = 'farm_om.xlsx'
    
    # 'tidefloat', 'tidefixed', 'wavefloat', 'wavefixed'
    systype = 'tidefloat'        
           
    # radial, singlesidedstring, doublesidedstring, multiplehubs 
    eleclayout = 'multiplehubs'
    
    # which file should be read
    if systype == 'tidefloat':
        systypeFile = 'tide_floating.xlsx'
        
    elif systype == 'tidefixed':
        systypeFile = 'tide_fixed.xlsx'
        
    elif systype == 'wavefloat':
        systypeFile = 'wave_floating.xlsx'
        
    else:
        systypeFile = 'wave_fixed.xlsx'    
                   
    if eleclayout == 'radial':
        eleclayoutFile = 'radial.xlsx'
        
    if eleclayout == 'singlesidedstring':
        eleclayoutFile = 'single-sided-string.xlsx'
        
    if eleclayout == 'doublesidedstring':
        eleclayoutFile = 'double-sided-string.xlsx'
        
    if eleclayout == 'multiplehubs':
        eleclayoutFile = 'multiplehubs.xlsx'
          
    farmTable       = database_operations(farmFile,'Farm_OM')
    systypeTable    = database_operations(systypeFile, systype)
    eleclayoutTable = database_operations(eleclayoutFile, eleclayout)
    
    # Farm_OM
    Farm_OM['wage_specialist_day']         = farmTable[0]['wage_specialist_day [Euro/h]'].ix[1]
    Farm_OM['wage_specialist_night']       = farmTable[0]['wage_specialist_night [Euro/h]'].ix[1]
    Farm_OM['wage_technician_day']         = farmTable[0]['wage_technician_day [Euro/h]'].ix[1]
    Farm_OM['wage_technician_night']       = farmTable[0]['wage_technician_night [Euro/h]'].ix[1]
    Farm_OM['duration_shift']              = farmTable[0]['duration_shift [h]'].ix[1]
    Farm_OM['number_shifts_per_day']       = farmTable[0]['number_shifts_per_day [-]'].ix[1]
    Farm_OM['workdays_summer']             = farmTable[0]['workdays_summer [-]'].ix[1]
    Farm_OM['workdays_winter']             = farmTable[0]['workdays_winter [-]'].ix[1]
    Farm_OM['number_crews_per_shift']      = farmTable[0]['number_crews_per_shift [-]'].ix[1]
    Farm_OM['number_crews_available']      = farmTable[0]['number_crews_available [-]'].ix[1]
    Farm_OM['helideck']                    = farmTable[0]['helideck [-]'].ix[1]
    Farm_OM['corrective_maintenance']      = farmTable[0]['corrective_maintenance [-]'].ix[1]
    Farm_OM['condition_based_maintenance'] = farmTable[0]['condition_based_maintenance [-]'].ix[1]
    Farm_OM['calendar_based_maintenance']  = farmTable[0]['calendar_based_maintenance [-]'].ix[1]
    
    # Energy selling price [€/kWh]
    Farm_OM['energy_selling_price'] = 0.2
    
    del farmTable
    
    
    # Simu_Param
    # Full Load Hours [h]
    # dummy value for test purposes
    fullLoadHours = 5000
    
    # Average Power [W]
    # dummy value for test purposes
    avePower = 684931.5  
    
    # Simu_Param contains parameters from WP3 and Core 
    # startOperationDate [-]
    Simu_Param['startOperationDate'] = datetime.datetime(2016,01,01)
    
    # missionTime [year]
    Simu_Param['missionTime'] = 20.0
    
    # Number of devives [-]
    Simu_Param['Nbodies'] = 3
    
    # Number of multiplehubs 
    if eleclayout == 'multiplehubs':
        NMultiplehubs =3
      
    
    #SeaGen Generator  
    #Rated Power [MW] 1.2 
    #Full Load hours 5000 
    #Energy [MWh] 6000 
    #Avg Power [W] 684931.5068 
    
    
    # This information is coming from WP3. Use the random values in coreSimu    
    arrayDummy1 = []
    arrayDummy2 = []
    for iCnt in range(0,Simu_Param['Nbodies']):
        arrayDummy1.append(avePower*random.randint(95, 105)/100.0)
        arrayDummy2.append(arrayDummy1[iCnt]*fullLoadHours)
    
    Simu_Param['power_prod_perD']               = np.array(arrayDummy1)
    Simu_Param['annual_Energy_Production_perD'] = np.array(arrayDummy2)
    
    del arrayDummy1, arrayDummy2 
    
    # This information is coming from WP3. Use the random values in coreSimu    
    # units [[-], [m], [m], [m], [-], [m], [-]]                       
    arrayInfoLogistic = ['Component_ID', 'depth', 'x coord', 'y coord', 'zone', 'Bathymetry', 'Soil type']
    
    dummyDict = {}
    loop = 0
    
    for iCnt in range(0,Simu_Param['Nbodies']):
        
        depth      = random.randint(10,30)
        x_oord     = random.randint(367000,368000)
        y_coord    = random.randint(6125000,6130000)
        Bathymetry = random.randint(80,120)
        
        if random.randint(0,1) == 0:
            zone      = '30 U'
            Soil_type = 'SC'
            
        else: 
            zone = '31 U'           
            Soil_type = 'MS'
    
        loop = loop + 1 
        dummyDict['Component' + str(loop)] = ['device'+'{:03d}'.format(iCnt+1), depth, x_oord, y_coord, zone, Bathymetry, Soil_type]
                 
    loop = loop + 1 
    dummyDict['Component' + str(loop)] = ['Export Cable'+'{:03d}'.format(1), depth, x_oord, y_coord, zone, Bathymetry, Soil_type]
    
    loop = loop + 1 
    dummyDict['Component' + str(loop)] = ['Substation'+'{:03d}'.format(1), depth, x_oord, y_coord, zone, Bathymetry, Soil_type]
    
    if eleclayout == 'multiplehubs':
        for iCnt in range(0,NMultiplehubs):
            loop = loop + 1 
            dummyDict['Component' + str(loop)] = ['subhub'+'{:03d}'.format(iCnt+1), depth, x_oord, y_coord, zone, Bathymetry, Soil_type]
         
    Simu_Param['arrayInfoLogistic'] = pd.DataFrame(dummyDict, index = arrayInfoLogistic)
    
    del arrayInfoLogistic, depth, x_oord, y_coord, Bathymetry, zone, Soil_type     
    
    # Control_Param
    # [unplaned corrective maintenance, condition based maintenance, calandar based maintenance]  
    # may be will be removed at the end of development
    Control_Param['whichOptim'] = [True, False, False]
    
     
    # farmTable[0] -> Components   
    # farmTable[1] -> FailureModes 
    # farmTable[2] -> RepairActions   
    # farmTable[3] -> Inspections     
    
    # Component
    # component_type is related hier to a component which should be maintained in a defined level
    # see the definitions in logistic function
    # 1	Element type	element_type	[-]	string	Element type list includes all array sub-component: device; mooring line; foundation; static cable; dynamic cable, collection point
    # 2	Element subtype	element_subtype	[-]	string	Element sub-type is only required when the element type is device. It corresponds to one of the four sub-systems of the device, i.e: hydrodynamic; pto; control; support structure
    # 3	Element ID number	element_ID	[-]	string	ID number of the element under consideration should match with those defined in WP1, WP2, WP3 & WP4
    
    
    ComponentKeys = ['Component_ID', 'Component_type', 'Component_subtype', 'failure_rate', 'number_failure_modes', 'start_date_calendar_based_maintenance', 'end_date_calendar_based_maintenance',
                     'interval_calendar_based_maintenance', 'start_date_condition_based_maintenance', 'end_date_condition_based_maintenance',
                     'soh_threshold', 'is_floating']
                                      
    loop = 0
    dummyDict = {}
    
    # device related
    for iCnt in range(0,Simu_Param['Nbodies']):                      
        for iCnt1 in range(0,len(systypeTable[0])):
            Component_ID                           = systypeTable[0]['Component_ID [-]'].ix[iCnt1+1]
            Component_type                         = systypeTable[0]['Component_type [-]'].ix[iCnt1+1] 
            Component_subtype                      = systypeTable[0]['Component_subtype [-]'].ix[iCnt1+1] 
            failure_rate                           = systypeTable[0]['failure_rate [1/y]'].ix[iCnt1+1] 
            number_failure_modes                   = systypeTable[0]['number_failure_modes [-]'].ix[iCnt1+1]  
            
            if type(systypeTable[0]['start_date_calendar_based_maintenance [-]'].ix[iCnt1+1]) == unicode:
                start_date_calendar_based_maintenance  = datetime.datetime.strptime(systypeTable[0]['start_date_calendar_based_maintenance [-]'].ix[iCnt1+1],"%Y-%m-%d") 
            else:
                start_date_calendar_based_maintenance  = ''   
                
            if type(systypeTable[0]['end_date_calendar_based_maintenance [-]'].ix[iCnt1+1]) == unicode:
                end_date_calendar_based_maintenance  = datetime.datetime.strptime(systypeTable[0]['end_date_calendar_based_maintenance [-]'].ix[iCnt1+1],"%Y-%m-%d") 
            else:
                end_date_calendar_based_maintenance  = ''   
    
            interval_calendar_based_maintenance    = systypeTable[0]['interval_calendar_based_maintenance [y]'].ix[iCnt1+1]        
            
            if type(systypeTable[0]['start_date_condition_based_maintenance [-]'].ix[iCnt1+1]) == unicode:
                start_date_condition_based_maintenance  = datetime.datetime.strptime(systypeTable[0]['start_date_condition_based_maintenance [-]'].ix[iCnt1+1],"%Y-%m-%d") 
            else:
                start_date_condition_based_maintenance  = ''   
                
            if type(systypeTable[0]['end_date_condition_based_maintenance [-]'].ix[iCnt1+1]) == unicode:
                end_date_condition_based_maintenance  = datetime.datetime.strptime(systypeTable[0]['end_date_condition_based_maintenance [-]'].ix[iCnt1+1],"%Y-%m-%d") 
            else:
                end_date_condition_based_maintenance  = ''           
                
            soh_threshold                          = systypeTable[0]['soh_threshold [%]'].ix[iCnt1+1] 
            is_floating                            = systypeTable[0]['is_floating [-]'].ix[iCnt1+1] 
    
            loop = loop + 1 
            dummyDict['Component' + str(loop)] = [Component_ID +'{:03d}'.format(iCnt+1), Component_type +'{:03d}'.format(iCnt+1), \
            Component_subtype, failure_rate, number_failure_modes, start_date_calendar_based_maintenance, end_date_calendar_based_maintenance, \
            interval_calendar_based_maintenance, start_date_condition_based_maintenance, end_date_condition_based_maintenance, \
            soh_threshold, is_floating]
    
    # array related        
    for iCnt in range(0,len(eleclayoutTable[0])):
        Component_ID                           = eleclayoutTable[0]['Component_ID [-]'].ix[iCnt+1]
        Component_type                         = eleclayoutTable[0]['Component_type [-]'].ix[iCnt+1] 
        Component_subtype                      = eleclayoutTable[0]['Component_subtype [-]'].ix[iCnt+1] 
        failure_rate                           = eleclayoutTable[0]['failure_rate [1/y]'].ix[iCnt+1] 
        number_failure_modes                   = eleclayoutTable[0]['number_failure_modes [-]'].ix[iCnt+1] 
        
       
        if type(eleclayoutTable[0]['start_date_calendar_based_maintenance [-]'].ix[iCnt+1]) == unicode:
            start_date_calendar_based_maintenance  = datetime.datetime.strptime(eleclayoutTable[0]['start_date_calendar_based_maintenance [-]'].ix[iCnt+1],"%Y-%m-%d") 
        else:
            start_date_calendar_based_maintenance  = ''   
            
        if type(eleclayoutTable[0]['end_date_calendar_based_maintenance [-]'].ix[iCnt+1]) == unicode:
            end_date_calendar_based_maintenance  = datetime.datetime.strptime(eleclayoutTable[0]['end_date_calendar_based_maintenance [-]'].ix[iCnt+1],"%Y-%m-%d") 
        else:
            end_date_calendar_based_maintenance  = ''   
        
        interval_calendar_based_maintenance    = eleclayoutTable[0]['interval_calendar_based_maintenance [y]'].ix[iCnt+1]
            
        if type(eleclayoutTable[0]['start_date_condition_based_maintenance [-]'].ix[iCnt+1]) == unicode:
            start_date_condition_based_maintenance  = datetime.datetime.strptime(eleclayoutTable[0]['start_date_condition_based_maintenance [-]'].ix[iCnt+1],"%Y-%m-%d") 
        else:
            start_date_condition_based_maintenance  = ''   
            
        if type(eleclayoutTable[0]['end_date_condition_based_maintenance [-]'].ix[iCnt+1]) == unicode:
            end_date_condition_based_maintenance  = datetime.datetime.strptime(eleclayoutTable[0]['end_date_condition_based_maintenance [-]'].ix[iCnt+1],"%Y-%m-%d") 
        else:
            end_date_condition_based_maintenance  = ''    
                                                                     
        soh_threshold                          = eleclayoutTable[0]['soh_threshold [%]'].ix[iCnt+1] 
        is_floating                            = eleclayoutTable[0]['is_floating [-]'].ix[iCnt+1] 
        
        if 'subhub' in Component_ID:
            for iCnt1 in range(0,NMultiplehubs):
                loop = loop + 1 
                dummyDict['Component' + str(loop)] = [Component_ID +'{:03d}'.format(iCnt1+1), Component_type +'{:03d}'.format(iCnt1+1), \
                Component_subtype, failure_rate, number_failure_modes, start_date_calendar_based_maintenance, end_date_calendar_based_maintenance, \
                interval_calendar_based_maintenance, start_date_condition_based_maintenance, end_date_condition_based_maintenance, \
                soh_threshold, is_floating]   
    
        else:
            loop = loop + 1 
            dummyDict['Component' + str(loop)] = [Component_ID +'{:03d}'.format(1), Component_type +'{:03d}'.format(1), \
            Component_subtype, failure_rate, number_failure_modes, start_date_calendar_based_maintenance, end_date_calendar_based_maintenance, \
            interval_calendar_based_maintenance, start_date_condition_based_maintenance, end_date_condition_based_maintenance, \
            soh_threshold, is_floating]   
                   
    Component = pd.DataFrame(dummyDict, index = ComponentKeys) 
    
    # only for test simplification
    if loop !=0: 
        del ComponentKeys, Component_ID, Component_subtype, Component_type, failure_rate, number_failure_modes, start_date_calendar_based_maintenance, \
            end_date_calendar_based_maintenance, interval_calendar_based_maintenance, start_date_condition_based_maintenance, \
            end_date_condition_based_maintenance, soh_threshold, is_floating
    
    # Failure_Mode
    Failure_ModeKeys = ['Component_ID', 'FM_ID', 'mode_probability', 'spare_mass', 'spare_height', 'spare_width', 'spare_length', 'cost_spare',
                        'cost_spare_transit', 'cost_spare_loading', 'lead_time_spare', 'CAPEX_condition_based_maintenance']                        
    loop = 0
    dummyDict = {}
    
        
    # device related
    for iCnt in range(0,Simu_Param['Nbodies']):
        for iCnt1 in range(0,len(systypeTable[1])):
            Component_ID                      = systypeTable[1]['Component_ID [-]'].ix[iCnt1+1]
            FM_ID                             = systypeTable[1]['FM_ID [-]'].ix[iCnt1+1] 
            mode_probability                  = systypeTable[1]['mode_probability [%]'].ix[iCnt1+1] 
            spare_mass                        = systypeTable[1]['spare_mass [kg]'].ix[iCnt1+1] 
            spare_height                      = systypeTable[1]['spare_height [m]'].ix[iCnt1+1] 
            spare_width                       = systypeTable[1]['spare_width [m]'].ix[iCnt1+1] 
            spare_length                      = systypeTable[1]['spare_length [m]'].ix[iCnt1+1] 
            cost_spare                        = systypeTable[1]['cost_spare [Euro]'].ix[iCnt1+1] 
            cost_spare_transit                = systypeTable[1]['cost_spare_transit [Euro]'].ix[iCnt1+1] 
            cost_spare_loading                = systypeTable[1]['cost_spare_loading [Euro]'].ix[iCnt1+1] 
            lead_time_spare                   = systypeTable[1]['lead_time_spare [h]'].ix[iCnt1+1] 
            CAPEX_condition_based_maintenance = systypeTable[1]['CAPEX_condition_based_maintenance [Euro]'].ix[iCnt1+1] 
            
            loop = loop + 1 
            dummyDict['Failure_Mode' + str(loop)] = [Component_ID +'{:03d}'.format(iCnt+1), FM_ID, \
            mode_probability, spare_mass, spare_height, spare_width, spare_length, \
            cost_spare, cost_spare_transit, cost_spare_loading, lead_time_spare, CAPEX_condition_based_maintenance]
            
    # array related        
    for iCnt in range(0,len(eleclayoutTable[1])):
        Component_ID                      = eleclayoutTable[1]['Component_ID [-]'].ix[iCnt+1]
        FM_ID                             = eleclayoutTable[1]['FM_ID [-]'].ix[iCnt+1] 
        mode_probability                  = eleclayoutTable[1]['mode_probability [%]'].ix[iCnt+1] 
        spare_mass                        = eleclayoutTable[1]['spare_mass [kg]'].ix[iCnt+1] 
        spare_height                      = eleclayoutTable[1]['spare_height [m]'].ix[iCnt+1] 
        spare_width                       = eleclayoutTable[1]['spare_width [m]'].ix[iCnt+1] 
        spare_length                      = eleclayoutTable[1]['spare_length [m]'].ix[iCnt+1] 
        cost_spare                        = eleclayoutTable[1]['cost_spare [Euro]'].ix[iCnt+1] 
        cost_spare_transit                = eleclayoutTable[1]['cost_spare_transit [Euro]'].ix[iCnt+1] 
        cost_spare_loading                = eleclayoutTable[1]['cost_spare_loading [Euro]'].ix[iCnt+1] 
        lead_time_spare                   = eleclayoutTable[1]['lead_time_spare [h]'].ix[iCnt+1]
        CAPEX_condition_based_maintenance = eleclayoutTable[1]['CAPEX_condition_based_maintenance [Euro]'].ix[iCnt+1]     
        
        if 'subhub' in Component_ID:
            for iCnt1 in range(0,NMultiplehubs):
                loop = loop + 1 
                dummyDict['Failure_Mode' + str(loop)] = [Component_ID +'{:03d}'.format(iCnt1+1), FM_ID, \
                mode_probability, spare_mass, spare_height, spare_width, spare_length, \
                cost_spare, cost_spare_transit, cost_spare_loading, lead_time_spare, CAPEX_condition_based_maintenance]        
        else:
            loop = loop + 1 
            dummyDict['Failure_Mode' + str(loop)] = [Component_ID +'{:03d}'.format(1), FM_ID, \
            mode_probability, spare_mass, spare_height, spare_width, spare_length, \
            cost_spare, cost_spare_transit, cost_spare_loading, lead_time_spare, CAPEX_condition_based_maintenance]
    
                   
    Failure_Mode = pd.DataFrame(dummyDict, index = Failure_ModeKeys) 
    
    # only for test simplification
    if loop !=0:                                                       
        del Failure_ModeKeys, Component_ID, FM_ID, mode_probability, spare_mass, spare_height, spare_width, \
            spare_length, cost_spare, cost_spare_transit, cost_spare_loading, lead_time_spare, CAPEX_condition_based_maintenance
    
    
    # Repair_Action
    Repair_ActionKeys = ['Component_ID', 'FM_ID', 'duration_maintenance', 'duration_accessibility', 'interruptable', 'delay_crew', 'delay_organisation', 'delay_spare',
                         'number_technicians', 'number_specialists', 'wave_height_max_acc', 'wave_periode_max_acc', 'wind_speed_max_acc', 'current_speed_max_acc', 'wave_height_max_om',
                         'wave_periode_max_om', 'wind_speed_max_om', 'current_speed_max_om', 'requires_lifiting', 'requires_divers', 'requires_towing']
                                              
    loop = 0
    dummyDict = {}
    
    
    # device related
    for iCnt in range(0,Simu_Param['Nbodies']):
        for iCnt1 in range(0,len(systypeTable[2])):
            Component_ID           = systypeTable[2]['Component_ID [-]'].ix[iCnt1+1]
            FM_ID                  = systypeTable[2]['FM_ID [-]'].ix[iCnt1+1] 
            duration_maintenance   = systypeTable[2]['duration_maintenance [h]'].ix[iCnt1+1] 
            duration_accessibility = systypeTable[2]['duration_accessibility [h]'].ix[iCnt1+1] 
            interruptable          = systypeTable[2]['interruptable [-]'].ix[iCnt1+1] 
            delay_crew             = systypeTable[2]['delay_crew [h]'].ix[iCnt1+1] 
            delay_organisation     = systypeTable[2]['delay_organisation [h]'].ix[iCnt1+1] 
            delay_spare            = systypeTable[2]['delay_spare [h]'].ix[iCnt1+1] 
            number_technicians     = systypeTable[2]['number_technicians [-]'].ix[iCnt1+1] 
            number_specialists     = systypeTable[2]['number_specialists [-]'].ix[iCnt1+1] 
            wave_height_max_acc    = systypeTable[2]['wave_height_max_acc [m]'].ix[iCnt1+1] 
            wave_periode_max_acc   = systypeTable[2]['wave_periode_max_acc [s]'].ix[iCnt1+1] 
            wind_speed_max_acc     = systypeTable[2]['wind_speed_max_acc [m/s]'].ix[iCnt1+1] 
            current_speed_max_acc  = systypeTable[2]['current_speed_max_acc [m/s]'].ix[iCnt1+1]
            wave_height_max_om     = systypeTable[2]['wave_height_max_om [m]'].ix[iCnt1+1] 
            wave_periode_max_om    = systypeTable[2]['wave_periode_max_om [s]'].ix[iCnt1+1] 
            wind_speed_max_om      = systypeTable[2]['wind_speed_max_om [m/s]'].ix[iCnt1+1] 
            current_speed_max_om   = systypeTable[2]['current_speed_max_om [m/s]'].ix[iCnt1+1] 
            requires_lifiting      = systypeTable[2]['requires_lifiting [-]'].ix[iCnt1+1] 
            requires_divers        = systypeTable[2]['requires_divers [-]'].ix[iCnt1+1] 
            requires_towing        = systypeTable[2]['requires_towing [-]'].ix[iCnt1+1] 
    
    
            loop = loop + 1 
            dummyDict['Repair_Action' + str(loop)] = [Component_ID +'{:03d}'.format(iCnt+1), FM_ID, \
            duration_maintenance, duration_accessibility, interruptable, delay_crew, delay_organisation, \
            delay_spare, number_technicians, number_specialists, wave_height_max_acc, wave_periode_max_acc, wind_speed_max_acc, current_speed_max_acc, \
            wave_height_max_om, wave_periode_max_om, wind_speed_max_om, current_speed_max_om, requires_lifiting, requires_divers, requires_towing ]
            
    # array related 
    for iCnt in range(0,len(eleclayoutTable[2])):
        Component_ID           = eleclayoutTable[2]['Component_ID [-]'].ix[iCnt+1]
        FM_ID                  = eleclayoutTable[2]['FM_ID [-]'].ix[iCnt+1] 
        duration_maintenance   = eleclayoutTable[2]['duration_maintenance [h]'].ix[iCnt+1] 
        duration_accessibility = eleclayoutTable[2]['duration_accessibility [h]'].ix[iCnt+1] 
        interruptable          = eleclayoutTable[2]['interruptable [-]'].ix[iCnt+1] 
        delay_crew             = eleclayoutTable[2]['delay_crew [h]'].ix[iCnt+1] 
        delay_organisation     = eleclayoutTable[2]['delay_organisation [h]'].ix[iCnt+1] 
        delay_spare            = eleclayoutTable[2]['delay_spare [h]'].ix[iCnt+1] 
        number_technicians     = eleclayoutTable[2]['number_technicians [-]'].ix[iCnt+1] 
        number_specialists     = eleclayoutTable[2]['number_specialists [-]'].ix[iCnt+1] 
        wave_height_max_acc    = eleclayoutTable[2]['wave_height_max_acc [m]'].ix[iCnt+1] 
        wave_periode_max_acc   = eleclayoutTable[2]['wave_periode_max_acc [s]'].ix[iCnt+1] 
        wind_speed_max_acc     = eleclayoutTable[2]['wind_speed_max_acc [m/s]'].ix[iCnt+1] 
        current_speed_max_acc  = eleclayoutTable[2]['current_speed_max_acc [m/s]'].ix[iCnt+1]
        wave_height_max_om     = eleclayoutTable[2]['wave_height_max_om [m]'].ix[iCnt+1] 
        wave_periode_max_om    = eleclayoutTable[2]['wave_periode_max_om [s]'].ix[iCnt+1] 
        wind_speed_max_om      = eleclayoutTable[2]['wind_speed_max_om [m/s]'].ix[iCnt+1] 
        current_speed_max_om   = eleclayoutTable[2]['current_speed_max_om [m/s]'].ix[iCnt+1] 
        requires_lifiting      = eleclayoutTable[2]['requires_lifiting [-]'].ix[iCnt+1] 
        requires_divers        = eleclayoutTable[2]['requires_divers [-]'].ix[iCnt+1] 
        requires_towing        = eleclayoutTable[2]['requires_towing [-]'].ix[iCnt+1] 
    
        if 'subhub' in Component_ID:
            for iCnt1 in range(0,NMultiplehubs):
                loop = loop + 1 
                dummyDict['Repair_Action' + str(loop)] = [Component_ID +'{:03d}'.format(iCnt1+1), FM_ID, \
                duration_maintenance, duration_accessibility, interruptable, delay_crew, delay_organisation, \
                delay_spare, number_technicians, number_specialists, wave_height_max_acc, wave_periode_max_acc, wind_speed_max_acc, current_speed_max_acc, \
                wave_height_max_om, wave_periode_max_om, wind_speed_max_om, current_speed_max_om, requires_lifiting, requires_divers, requires_towing]       
        else:
            loop = loop + 1 
            dummyDict['Repair_Action' + str(loop)] = [Component_ID +'{:03d}'.format(1), FM_ID, \
            duration_maintenance, duration_accessibility, interruptable, delay_crew, delay_organisation, \
            delay_spare, number_technicians, number_specialists, wave_height_max_acc, wave_periode_max_acc, wind_speed_max_acc, current_speed_max_acc, \
            wave_height_max_om, wave_periode_max_om, wind_speed_max_om, current_speed_max_om, requires_lifiting, requires_divers, requires_towing]
    
    Repair_Action = pd.DataFrame(dummyDict, index = Repair_ActionKeys)  
    
    # only for test simplification
    if loop !=0: 
        del Repair_ActionKeys, Component_ID, FM_ID, duration_maintenance, duration_accessibility, interruptable, delay_crew, \
            delay_organisation, delay_spare, number_technicians, number_specialists, wave_height_max_acc, wave_periode_max_acc, \
            wind_speed_max_acc, current_speed_max_acc, wave_height_max_om, wave_periode_max_om, wind_speed_max_om, current_speed_max_om, \
            requires_lifiting, requires_divers, requires_towing
    
    # Inspection
    InspectionKeys = ['Component_ID', 'FM_ID', 'duration_inspection', 'duration_accessibility', 'delay_crew', 'delay_organisation', 'number_technicians', 'number_specialists',
                     'wave_height_max_acc', 'wave_periode_max_acc', 'wind_speed_max_acc', 'current_speed_max_acc', 'wave_height_max_om', 'wave_periode_max_om', 'wind_speed_max_om',
                     'current_speed_max_om', 'requires_lifiting', 'requires_divers']
        
            
    loop = 0
    dummyDict = {}
    
    
    # device related
    for iCnt in range(0,Simu_Param['Nbodies']):
        for iCnt1 in range(0,len(systypeTable[3])):
            Component_ID           = systypeTable[3]['Component_ID [-]'].ix[iCnt1+1]
            FM_ID                  = systypeTable[3]['FM_ID [-]'].ix[iCnt1+1] 
            duration_inspection    = systypeTable[3]['duration_inspection [h]'].ix[iCnt1+1] 
            duration_accessibility = systypeTable[3]['duration_accessibility [h]'].ix[iCnt1+1] 
            delay_crew             = systypeTable[3]['delay_crew [h]'].ix[iCnt1+1] 
            delay_organisation     = systypeTable[3]['delay_organisation [h]'].ix[iCnt1+1] 
            number_technicians     = systypeTable[3]['number_technicians [-]'].ix[iCnt1+1] 
            number_specialists     = systypeTable[3]['number_specialists [-]'].ix[iCnt1+1] 
            wave_height_max_acc    = systypeTable[3]['wave_height_max_acc [m]'].ix[iCnt1+1] 
            wave_periode_max_acc   = systypeTable[3]['wave_periode_max_acc [s]'].ix[iCnt1+1] 
            wind_speed_max_acc     = systypeTable[3]['wind_speed_max_acc [m/s]'].ix[iCnt1+1] 
            current_speed_max_acc  = systypeTable[3]['current_speed_max_acc [m/s]'].ix[iCnt1+1]
            wave_height_max_om     = systypeTable[3]['wave_height_max_om [m]'].ix[iCnt1+1] 
            wave_periode_max_om    = systypeTable[3]['wave_periode_max_om [s]'].ix[iCnt1+1] 
            wind_speed_max_om      = systypeTable[3]['wind_speed_max_om [m/s]'].ix[iCnt1+1] 
            current_speed_max_om   = systypeTable[3]['current_speed_max_om [m/s]'].ix[iCnt1+1] 
            requires_lifiting      = systypeTable[3]['requires_lifiting [-]'].ix[iCnt1+1] 
            requires_divers        = systypeTable[3]['requires_divers [-]'].ix[iCnt1+1] 
    
            loop = loop + 1 
            dummyDict['Inspection' + str(loop)] = [Component_ID +'{:03d}'.format(iCnt+1), FM_ID, \
            duration_inspection, duration_accessibility, delay_crew, delay_organisation, \
            number_technicians, number_specialists, wave_height_max_acc, wave_periode_max_acc, wind_speed_max_acc, current_speed_max_acc, \
            wave_height_max_om, wave_periode_max_om, wind_speed_max_om, current_speed_max_om, requires_lifiting, requires_divers]
            
    # array related 
    for iCnt in range(0,len(eleclayoutTable[3])):
        Component_ID           = eleclayoutTable[3]['Component_ID [-]'].ix[iCnt+1]
        FM_ID                  = eleclayoutTable[3]['FM_ID [-]'].ix[iCnt+1] 
        duration_inspection    = eleclayoutTable[3]['duration_inspection [h]'].ix[iCnt+1] 
        duration_accessibility = eleclayoutTable[3]['duration_accessibility [h]'].ix[iCnt+1] 
        delay_crew             = eleclayoutTable[3]['delay_crew [h]'].ix[iCnt+1] 
        delay_organisation     = eleclayoutTable[3]['delay_organisation [h]'].ix[iCnt+1] 
        number_technicians     = eleclayoutTable[3]['number_technicians [-]'].ix[iCnt+1] 
        number_specialists     = eleclayoutTable[3]['number_specialists [-]'].ix[iCnt+1] 
        wave_height_max_acc    = eleclayoutTable[3]['wave_height_max_acc [m]'].ix[iCnt+1] 
        wave_periode_max_acc   = eleclayoutTable[3]['wave_periode_max_acc [s]'].ix[iCnt+1] 
        wind_speed_max_acc     = eleclayoutTable[3]['wind_speed_max_acc [m/s]'].ix[iCnt+1] 
        current_speed_max_acc  = eleclayoutTable[3]['current_speed_max_acc [m/s]'].ix[iCnt+1]
        wave_height_max_om     = eleclayoutTable[3]['wave_height_max_om [m]'].ix[iCnt+1] 
        wave_periode_max_om    = eleclayoutTable[3]['wave_periode_max_om [s]'].ix[iCnt+1] 
        wind_speed_max_om      = eleclayoutTable[3]['wind_speed_max_om [m/s]'].ix[iCnt+1] 
        requires_lifiting      = eleclayoutTable[3]['requires_lifiting [-]'].ix[iCnt+1] 
        requires_divers        = eleclayoutTable[3]['requires_divers [-]'].ix[iCnt+1] 
        
        
        if 'subhub' in Component_ID:
            for iCnt1 in range(0,NMultiplehubs):
                loop = loop + 1 
                dummyDict['Inspection' + str(loop)] = [Component_ID +'{:03d}'.format(iCnt1+1), FM_ID, \
                duration_inspection, duration_accessibility, delay_crew, delay_organisation, \
                number_technicians, number_specialists, wave_height_max_acc, wave_periode_max_acc, wind_speed_max_acc, current_speed_max_acc, \
                wave_height_max_om, wave_periode_max_om, wind_speed_max_om, current_speed_max_om, requires_lifiting, requires_divers]      
        else:
            loop = loop + 1 
            dummyDict['Inspection' + str(loop)] = [Component_ID +'{:03d}'.format(1), FM_ID, \
            duration_inspection, duration_accessibility, delay_crew, delay_organisation, \
            number_technicians, number_specialists, wave_height_max_acc, wave_periode_max_acc, wind_speed_max_acc, current_speed_max_acc, \
            wave_height_max_om, wave_periode_max_om, wind_speed_max_om, current_speed_max_om, requires_lifiting, requires_divers]  
        
    Inspection = pd.DataFrame(dummyDict, index = InspectionKeys)                                
    
    # only for test simplification
    if loop !=0:              
        del InspectionKeys, loop, iCnt, iCnt1, dummyDict
        del Component_ID, FM_ID, duration_inspection, duration_accessibility, delay_crew, \
            delay_organisation, number_technicians, number_specialists, wave_height_max_acc, wave_periode_max_acc, \
            wind_speed_max_acc, current_speed_max_acc, wave_height_max_om, wave_periode_max_om, wind_speed_max_om, current_speed_max_om, \
            requires_lifiting, requires_divers
            
        del systypeTable, eleclayoutTable
        
    # end
    # *****************************************************************************
    # *****************************************************************************
    # *****************************************************************************
    
    # Read of logistic files
    
    #default_values inputs
    
    #logistic version from 2016_10_20
    Logistic_Param['phase_order']  = load_phase_order_data(database_logistic("installation_order_0.xlsx"))
    Logistic_Param['schedule_OLC'] = load_time_olc_data(database_logistic("operations_time_OLC.xlsx"))
    Logistic_Param['penet_rates'], Logistic_Param['laying_rates'], Logistic_Param['other_rates'] = load_eq_rates(database_logistic("equipment_perf_rates.xlsx"))
    Logistic_Param['port_sf'], Logistic_Param['vessel_sf'], Logistic_Param['eq_sf']              = load_sf(database_logistic("safety_factors.xlsx"))
    # Internal logistic module databases
    Logistic_Param['vessels']               = load_vessel_data(database_logistic("logisticsDB_vessel_python.xlsx"))
    Logistic_Param['equipments']            = load_equipment_data(database_logistic("logisticsDB_equipment_python.xlsx"))
    Logistic_Param['ports']                 = load_port_data(database_logistic("logisticsDB_ports_python.xlsx"))
    
    # E-Mail from pedro.vicente@wavec.org concerning Logistic_Param['entry_point']
    ''' In fact, there was a change in the point which is considered to be the entry point of the lease area. 
    Initially we were using the coordinates of the first device but currently we are using the first point of the lease area, 
    in order not to be dependent of external module output. In that sense, if you compromise to send us in the UTM coordinates 
    this same location, first coordinates point of the lease area, we will adpat the code accordingly and 
    update on BitBucket also by the end of the week'''
    Logistic_Param['site'], Logistic_Param['metocean'], Logistic_Param['device'], Logistic_Param['sub_device'], Logistic_Param['landfall'], Logistic_Param['entry_point'] = load_user_inputs(database_logistic("inputs_user.xlsx"))
    Logistic_Param['layout']                = load_hydrodynamic_outputs(database_logistic("ouputs_hydrodynamic.xlsx"))
    Logistic_Param['collection_point'], Logistic_Param['dynamic_cable'], Logistic_Param['static_cable'], Logistic_Param['cable_route'], Logistic_Param['connectors'], Logistic_Param['external_protection'], Logistic_Param['topology'] = load_electrical_outputs(database_logistic("ouputs_electrical.xlsx"))
    
    
    # RAM_Param
    RAM_Param['severitylevel'] = 'critical'
    RAM_Param['calcscenario'] = 'mean'
    
    # systype -> 'tidefloat', 'tidefixed', 'wavefloat', 'wavefixed'
    RAM_Param['systype'] = systype
    
    # eleclayout -> radial, singlesidedstring, doublesidedstring, multiplehubs   
    RAM_Param['eleclayout'] = eleclayout
    
    dummydb = database_reliability('dummydb.txt')
    
    if RAM_Param['eleclayout'] in ('radial'):      
        dummymoorhiereg   = database_reliability('dummymoorhiereg1.txt')
        dummyelechierdict = database_reliability('dummyelechiereg1.txt')
        dummyuserhiereg   = database_reliability('dummyuserhiereg5.txt')  
        dummymoorbomeg    = database_reliability('dummymoorbomeg1.txt')   
        dummyelecbomeg    = database_reliability('dummyelecbomeg1.txt')  
        dummyuserbomeg    = database_reliability('dummyuserbomeg5.txt') 
        
    if RAM_Param['eleclayout'] in ('singlesidedstring'):
        dummymoorhiereg   = database_reliability('dummymoorhiereg2.txt')
        dummyelechierdict = database_reliability('dummyelechiereg2.txt')
        dummyuserhiereg   = database_reliability('dummyuserhiereg5.txt')  
        dummymoorbomeg    = database_reliability('dummymoorbomeg2.txt')   
        dummyelecbomeg    = database_reliability('dummyelecbomeg2.txt')  
        dummyuserbomeg    = database_reliability('dummyuserbomeg5.txt')  
        
    if RAM_Param['eleclayout'] in ('doublesidedstring'):
        dummymoorhiereg   = database_reliability('dummymoorhiereg3.txt')
        dummyelechierdict = database_reliability('dummyelechiereg3.txt')
        dummyuserhiereg   = database_reliability('dummyuserhiereg5.txt')  
        dummymoorbomeg    = database_reliability('dummymoorbomeg3.txt')   
        dummyelecbomeg    = database_reliability('dummyelecbomeg3.txt')  
        dummyuserbomeg    = database_reliability('dummyuserbomeg5.txt') 
        
    if RAM_Param['eleclayout'] in ('multiplehubs'):
        # Sam's E-Mail from 25.07.2016
        # Referring back to my email on 12th July, ‘..eg6.txt’ refers to a set of fixed devices (i.e. with foundations rather than mooring lines) 
        # with multiple hubs. Furthermore ‘…eg7.txt’ is a radial layout which was used to check that the 
        # new marker numbers in the bill of materials (produced by the WP4 module) did not interfere with the operation of the RAM.
     
        if 'fixed' in systype:
    
            dummymoorhiereg   = database_reliability('dummymoorhiereg6.txt')
            dummyelechierdict = database_reliability('dummyelechiereg6.txt')
            dummyuserhiereg   = database_reliability('dummyuserhiereg6.txt')  
            dummymoorbomeg    = database_reliability('dummymoorbomeg6.txt')   
            dummyelecbomeg    = database_reliability('dummyelecbomeg6.txt')  
            dummyuserbomeg    = database_reliability('dummyuserbomeg6.txt')
            
        else:
            dummymoorhiereg   = database_reliability('dummymoorhiereg4.txt')
            dummyelechierdict = database_reliability('dummyelechiereg4.txt')
            dummyuserhiereg   = database_reliability('dummyuserhiereg4.txt')  
            dummymoorbomeg    = database_reliability('dummymoorbomeg4.txt')   
            dummyelecbomeg    = database_reliability('dummyelecbomeg4.txt')  
            dummyuserbomeg    = database_reliability('dummyuserbomeg4.txt')  
        
    
    RAM_Param['elechierdict'] = eval(open(dummyelechierdict).read())
    RAM_Param['elecbomeg']    = eval(open(dummyelecbomeg).read())
    RAM_Param['moorhiereg']   = eval(open(dummymoorhiereg).read())
    RAM_Param['moorbomeg']    = eval(open(dummymoorbomeg).read())
    RAM_Param['userhiereg']   = eval(open(dummyuserhiereg).read()) 
    RAM_Param['userbomeg']    = eval(open(dummyuserbomeg).read())
    RAM_Param['db']           = eval(open(dummydb).read())
    
                                                                                                       
    #del dummydb, dummymoorhiereg, dummyelechierdict, dummyuserhiereg, dummymoorbomeg, dummyelecbomeg, dummyuserbomeg 
    del dummydb, dummymoorhiereg, dummyelechierdict, dummymoorbomeg, dummyelecbomeg
    del systype, farmFile, eleclayout, systypeFile, eleclayoutFile        
           
    
    # Call inputOM
    inputOMPtr = inputOM(Farm_OM,
                       Component,
                       Failure_Mode,
                       Repair_Action,
                       Inspection,
                       RAM_Param,
                       Logistic_Param,
                       Simu_Param,
                       Control_Param)
    
    with open("oandm_example_inputs.pkl", "wb") as fstream:
        pickle.dump(inputOMPtr, fstream, -1)
                       
    # clear the variables
    del Farm_OM 
    del Component 
    del Failure_Mode 
    del Repair_Action 
    del Inspection 
    del RAM_Param 
    del Logistic_Param 
    del Simu_Param 
    del Control_Param
            
        
    # Call WP6 optimiser
    ptrOptim = LCOE_Optimiser(inputOMPtr)
    del inputOMPtr 
    outputWP6 = ptrOptim()
    return outputWP6 
          
start_time = time.time()

# Call dtocean_maintenance
outputWP6 = test()

if outputWP6['error [-]']['error_ID [-]'][0] == 'NoError':
    # Unit [Euro/kWh] 
    print 'WP6: ***************************************************************'
    print 'WP6: LCOE = ' , outputWP6['lcoeOfArray [Euro/KWh]'], ' [Euro/KWh]'
    
else:
                        
    if outputWP6['error [-]']['error_ID [-]'][0] == 'NoSolutionsFound':
        print 'WP6: ***********************************************************'
        print 'WP6: Problem with feasibility of logistic solution'
        print 'WP6: please see error_ID in outputWP6 for more information'
        
    if outputWP6['error [-]']['error_ID [-]'][0] == 'NoInspPortFound':
        print 'WP6: ***********************************************************'
        print 'WP6: Problem with selection of insoection port\n'
        print 'WP6: please see error_ID in outputWP6 for more information'
        
    if outputWP6['error [-]']['error_ID [-]'][0] == 'NoRepairPortFound':
        print 'WP6: ***********************************************************'
        print 'WP6: Problem with selection of repair port\n'
        print 'WP6: please see error_ID in outputWP6 for more information'        
        
         
print('WP6: --- Required time in seconds ---')
print('WP6: --- %s ---' % (time.time() - start_time))