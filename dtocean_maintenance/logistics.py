"""
@author: WavEC Offshore Renewables, Mathew Topper
email: boris.teillant@wavec.org; paulo@wavec.org, pedro.vicente@wavec.org,
       dataonlygreater@gmail.com

This is the logistics assesmment module.

The module provides an estimation of the predicted performance of feasible
maritime infrastructure solutions that can carry out marine operation
pertaining to the installation of wave and tidal energy arrays.

The final output consists of the solution and equipment and respective
estimated cost to carry out the requested operation. The solution is the one
that minimizes the overall cost.

The module can be described in different core sub-modules:
* Loading input data
* Initialising the logistic classes
* Performing the assessment of all logistic phases sequencially, following
   this steps:
    (i) characterizartion of logistic requirements
    (ii) selection of the maritime infrastructure
    (iii) schedule assessment of the logistic phase
    (iv) cost assessment of the logistic phase
"""

from os import path
import timeit

from dtocean_logistics.phases.operations import logOp_init
from dtocean_logistics.phases.om import logPhase_om_init
from dtocean_logistics.phases.om.select_logPhase import logPhase_select
from dtocean_logistics.feasibility.feasability_om import feas_om
from dtocean_logistics.selection.select_ve import select_e, select_v
from dtocean_logistics.selection.match import compatibility_ve
from dtocean_logistics.performance.optim_sol import opt_sol
from dtocean_logistics.performance.schedule.schedule_om import sched_om
from dtocean_logistics.performance.economic.eco import cost
from dtocean_logistics.outputs.output_processing import out_process
from dtocean_logistics.load.safe_factors import safety_factors


def om_logistics_main(vessels_0,
                      equipments_0,
                      ports_0,
                      schedule_OLC,
                      other_rates,
                      port_sf,
                      vessel_sf,
                      eq_sf,
                      site,
                      metocean,
                      device,
                      sub_device,
                      entry_point,
                      layout,
                      collection_point,
                      dynamic_cable,
                      static_cable,
                      connectors,
                      om,
                      PRINT_FLAG):

    """
    Parameters
    ----------
    vessels(DataFrame): Panda table containing the vessel database

    equipments (DataFrame): Panda table containing the equipment database

    ports (DataFrame): Panda table containing the ports database

    user_inputs (dict):
        dictionnary containing all required inputs to Logistics coming from
        hydrodynamics/end-user:
         'device' (Dataframe): inputs required from the device
         'metocean' (Dataframe): metocean data

    hydrodynamic_outputs (dict):
        dictionnary containing all required inputs to the Logistics module
        coming from the Hydrodynamics module:
         'units' (DataFrame): number of devices
         'position' (DataFrame): UTM position of the devices

    O&M_outputs (dict):
        dictionnary containing all required inputs to logistics coming from
        maintenance module

    'LogPhase1' (DataFrame):
        All inputs required for LpM1 logistic phase as defined by main
        module

    Others...

    Returns
    -------

    install (dict):
        dictionnary compiling all key results obtained from the assessment of
        the logistic phases:

        'requirement' (tuple):
            minimum requirements returned from thefeasibility functions
        'eq_select' (dict):
            list of equipments satisfying the minimum requirements
        've_select' (dict):
            list of vessels satisfying the minimum requirements
        'combi_select' (dict):
            list of solutions passing the compatibility check
        'schedule' (dict): list of parameters with data about time
        'cost'  (dict): vessel equiment and port cost
    
    """


    # # Set directory paths for loading inputs
    mod_path = path.dirname(path.realpath(__file__))


    def database_file(file):
        """
        shortcut function to load files from the database folder
        """
        fpath = path.join('databases', '{0}'.format(file))
        db_path = path.join(mod_path, fpath)
        return db_path


    # apply dafety factors in vessels parameters
#    start_time_sf = timeit.default_timer()

    (ports,
     vessels,
     equipments) = safety_factors(ports_0,
                                  vessels_0,
                                  equipments_0,
                                  port_sf,
                                  vessel_sf,
                                  eq_sf)

#    stop_time_sf = timeit.default_timer()
    # print 'Safety factors simulation time [s]: ' +
    # str(stop_time_sf - start_time_sf)

    start_time = timeit.default_timer()

    if PRINT_FLAG:
        print 'START!'

    # Collecting relevant port information

    om_port_index = om['Port_Index [-]'].ix[0]
#    om_port_distance = om['Dist_port [km]'].ix[0]
    om_port = {}
    om_port['Selected base port for installation'] = ports.ix[om_port_index]

    # Check the presence of the lease area entry point
    
    # if this data does not exit use first position of the site data
    if len(entry_point)==0:
        entry_point['x coord [m]'] = site['x coord [m]'].iloc[0]
        entry_point['y coord [m]'] = site['y coord [m]'].iloc[0]
        entry_point['zone [-]'] = site['zone [-]'].iloc[0]
        entry_point['bathymetry [m]'] = site['bathymetry [m]'].iloc[0]
        entry_point['soil type [-]'] = site['soil type [-]'].iloc[0]


    # Initialising logistic operations and logistic phase
    logOp = logOp_init(schedule_OLC)

    logPhase_om = logPhase_om_init(logOp, vessels, equipments, om)

    # Select the suitable Log phase id
    log_phase_id = logPhase_select(om)
    log_phase = logPhase_om[log_phase_id]
    log_phase.op_ve_init = log_phase.op_ve

    ## Assessing the O&M logistic phase requested

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
    om_log['requirement'] = feas_om(log_phase,
                                    log_phase_id,
                                    om,
                                    device,
                                    sub_device,
                                    collection_point,
                                    connectors,
                                    dynamic_cable,
                                    static_cable)

    # Selecting the maritime infrastructure satisfying the logistic
    # requirements
    om_log['eq_select'], log_phase = select_e(om_log, log_phase)
    om_log['ve_select'], log_phase = select_v(om_log, log_phase)

    # Matching requirements to ensure compatiblity of combinations of
    # port/vessel(s)/equipment leading to feasible logistic solutions
    port = om_port['Selected base port for installation']
    
    (om_log['combi_select'],
     log_phase,
     MATCH_FLAG) = compatibility_ve(om_log, log_phase, port)

    if MATCH_FLAG == 'NoSolutions':
        
        ves_req = {'deck area [m^2]': om_log['requirement'][5]['deck area'],
                   'deck cargo [t]': om_log['requirement'][5]['deck cargo'],
                   'deck loading [t/m^2]':
                                   om_log['requirement'][5]['deck loading']}
            
        if PRINT_FLAG:
            print 'There are no solutions!' + '\n' + 'requirements:'
            print ves_req
            
        om_log['findSolution'] = 'NoSolutionsFound'
        
    else:
        
        # Estimating the schedule associated with all feasible logistic
        # solutions
        (om_log['schedule'],
         log_phase,
         SCHEDULE_FLAG) = sched_om(log_phase,
                                   log_phase_id,
                                   site,
                                   device,
                                   sub_device,
                                   entry_point,
                                   metocean,
                                   layout,
                                   om)

        if SCHEDULE_FLAG == 'NoWWindows':
            
            if PRINT_FLAG: print 'There are no weather windows!'
            om_log['findSolution'] = 'NoWeatherWindowFound'
            
        else:
            
            # Estimating the cost associated with all feasible logistic
            # solutions
            om_log['cost'], log_phase = cost(om_log,
                                             log_phase,
                                             log_phase_id,
                                             other_rates)

            # Identifying the optimal logistic solution as being the least
            # costly one
            om_log['optimal'] = opt_sol(log_phase, log_phase_id)
            om_log['findSolution'] = 'SolutionFound'

            if PRINT_FLAG:
                
                print 'Final Solution Found!'

                print 'Solution Total Cost [EURO]: ' + \
                                str(om_log['optimal']['total cost'])
                print 'Solution Schedule preparation time [h]:' + \
                                str(om_log['optimal']['schedule prep time'])
                print 'Solution Schedule waiting time [h]:' + \
                                str(om_log['optimal']['schedule waiting time'])
                print 'Solution Schedule sea time [h]: ' + \
                                str(om_log['optimal']['schedule sea time'])
                print 'Solution Schedule TOTAL time [h]: ' + \
                            str(om_log['optimal']['schedule prep time'] +
                                om_log['optimal']['schedule waiting time'] +
                                om_log['optimal']['schedule sea time'])

                # print 'Solution VE combination:'
                # print om_log['optimal']['vessel_equipment']

                # OUTPUT_dict = out_process(log_phase, om_log)
                # print OUTPUT_dict

    stop_time = timeit.default_timer()

    if PRINT_FLAG:
        
        print 'Simulation Duration [s]: ' + str(stop_time - start_time)

        print 'om_log[''findSolution'']: ' + om_log['findSolution']
        print 'FINISH!'

    return om_log
