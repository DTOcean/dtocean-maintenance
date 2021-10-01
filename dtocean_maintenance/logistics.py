# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Boris Teillant, Paulo Chainho, Pedro Vicente
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

"""
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
    
.. module:: logistics
    :platform: Windows

.. moduleauthor:: Boris Teillant <boris.teillant@wavec.org>
.. moduleauthor:: Paulo Chainho <paulo@wavec.org>
.. moduleauthor:: Pedro Vicente <pedro.vicente@wavec.org>
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import timeit
import logging
from copy import deepcopy

import pandas as pd

from dtocean_logistics.phases import EquipmentType, VesselType
from dtocean_logistics.phases.operations import logOp_init
from dtocean_logistics.phases.om import logPhase_om_init
from dtocean_logistics.phases.om.select_logPhase import logPhase_select
from dtocean_logistics.feasibility.feasability_om import feas_om
from dtocean_logistics.selection.select_ve import select_e, select_v
from dtocean_logistics.selection.match import compatibility_ve
from dtocean_logistics.performance.optim_sol import opt_sol
from dtocean_logistics.performance.schedule.schedule_om import SchedOM
from dtocean_logistics.performance.economic.eco import cost
from dtocean_logistics.load.safe_factors import safety_factors

# Set up logging
module_logger = logging.getLogger(__name__)


class Logistics(object):
    
    def __init__(self, vessels_0,
                       equipments_0,
                       ports_0,
                       port_sf,
                       vessel_sf,
                       eq_sf,
                       schedule_OLC):
        
        (self._ports,
         self._vessels,
         self._equipments) = safety_factors(ports_0,
                                            vessels_0,
                                            equipments_0,
                                            port_sf,
                                            vessel_sf,
                                            eq_sf)
        self._logOp = logOp_init(schedule_OLC)
        self._sched_om = SchedOM()
        
        self._prelog = {}
        self._old_om_log = None
        self._old_phase_id = None
        self._old_element_ids = None
        
        return
    
    def _get_log_phase(self, device,
                             sub_device,
                             collection_point,
                             dynamic_cable,
                             static_cable,
                             connectors,
                             om,
                             om_port):
        
        element_IDs = om['element_ID [-]'].unique()
        assert len(element_IDs) == len(om['element_ID [-]'])
        
        # Initialising logistic operations and logistic phase
        log_phase_id = logPhase_select(om)
        
        if log_phase_id in self._prelog:
            
            for (test_elements,
                 om_log,
                 log_phase, 
                 match_flag) in self._prelog[log_phase_id]:
                
                if set(element_IDs) == set(test_elements):
                    
#                    if (self._old_om_log is not None and
#                        self._old_phase_id == log_phase_id and
#                        self._old_element_ids == set(element_IDs)):
#                        
#                        if not print_sched_pd(om_log,
#                                              self._old_om_log):
#
#                            assert False
#                        
#                        self._old_sched = None
                    
                    return (_copy_om_log(om_log),
                            deepcopy(log_phase),
                            match_flag,
                            log_phase_id)
        
        log_phase = logPhase_om_init(log_phase_id,
                                     self._logOp,
                                     _copy_vessel_dict(self._vessels),
                                     _copy_equipment_dict(self._equipments),
                                     om)
        log_phase.op_ve_init = log_phase.op_ve
        
        ## Assessing the O&M logistic phase requested
        
        # Initialising the output dictionary to be passed to the O&M module
        om_log = {'port': om_port,
                  'requirement': {},
                  'eq_select': {},
                  've_select': {},
                  'combi_select': {},
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
        (om_log['combi_select'],
         log_phase,
         match_flag) = compatibility_ve(om_log, log_phase, om_port)
        
        store_tuple = (element_IDs,
                       _copy_om_log(om_log),
                       deepcopy(log_phase),
                       match_flag)
        
        if log_phase_id in self._prelog:
            self._prelog[log_phase_id].append(store_tuple)
        else:
            self._prelog[log_phase_id] = [store_tuple]
        
#        if self._old_om_log is None:
#            self._old_om_log = deepcopy(om_log)
#            self._old_phase_id = log_phase_id
#            self._old_element_ids = set(element_IDs)
        
        
        return om_log, log_phase, match_flag, log_phase_id
    
    def __call__(self,
                 other_rates,
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
                 print_flag,
                 optimise_delay=False,
                 custom_waiting=None):
        
        start_time = timeit.default_timer()
        
        if print_flag:
            print 'START!'
        
        # Collecting relevant port information
        om_port_index = om['Port_Index [-]'].iloc[0]
        om_port = self._ports.iloc[om_port_index]
        
        (om_log,
         log_phase,
         match_flag,
         log_phase_id) = self._get_log_phase(device,
                                            sub_device,
                                            collection_point,
                                            dynamic_cable,
                                            static_cable,
                                            connectors,
                                            om,
                                            om_port)
        
        if match_flag == 'NoSolutions':
            
            ves_req = {'deck area [m^2]':
                                    om_log['requirement'][5]['deck area'],
                       'deck cargo [t]':
                                   om_log['requirement'][5]['deck cargo'],
                       'deck loading [t/m^2]':
                                   om_log['requirement'][5]['deck loading']}
            
            msg = 'No vessel solutions found. Requirements: {}'.format(ves_req)
            module_logger.warning(msg)
            
            if print_flag:
                print msg
            
            om_log['findSolution'] = 'NoSolutionsFound'
            
        else:
            
            # Estimating the schedule associated with all feasible logistic
            # solutions
            (log_phase,
             schedule_flag) = self._sched_om(log_phase,
                                             log_phase_id,
                                             site,
                                             device,
                                             sub_device,
                                             entry_point,
                                             metocean,
                                             layout,
                                             om,
                                             optimise_delay,
                                             custom_waiting)
            
            if schedule_flag == 'NoWWindows':
                
                msg = 'No weather windows found'
                module_logger.warning(msg)
                
                if print_flag: print msg
                
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
                
                if print_flag:
                    
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
        
        if print_flag:
            
            print 'Simulation Duration [s]: ' + str(stop_time - start_time)
            
            print 'om_log[''findSolution'']: ' + om_log['findSolution']
            print 'FINISH!'
        
        return om_log


def _copy_equipment_dict(old):
    
    new = {}
    
    for k, v in old.iteritems():
        new[k] = EquipmentType(v.id, v.panda.copy())
    
    return new


def _copy_vessel_dict(old):
    
    new = {}
    
    for k, v in old.iteritems():
        new[k] = VesselType(v.id, v.panda.copy())
    
    return new


def _copy_om_log(old):
    
    def _copy_combi_select(old):
        
        new_list = []
        
        for c in old:
            out_dict = {}
            for k_out, v_out in c.iteritems():
                in_dict = {}
                for k_in, v_in in v_out.iteritems():
                    in_dict[k_in] = v_in
                out_dict[k_out] = in_dict
            new_list.append(out_dict)
            
        return new_list
    
    new = {}
    
    for k, v in old.iteritems():
        if k in ["cost", "optimal"]:
            new[k] = {}
        elif k == "combi_select":
            new[k] = _copy_combi_select(v)
        else:
            new[k] = v
    
    return new


def print_sched_pd(new, old):
    
    def print_recursive(new_obj, old_obj):
        
        result = [True]
        
        if isinstance(new_obj, dict):
            for k, v in new_obj.iteritems():
                print "key", k
                if k not in old_obj:
                    print "fail no key"
                    return [False]
                result.extend(print_recursive(v, old_obj[k]))
                    
        elif isinstance(new_obj, list):
            
            if not isinstance(old_obj, list):
                print "fail not list", old_obj
                return [False]
            elif len(new_obj) != len(old_obj):
                print "fail length", len(new_obj), len(old_obj)
                return [False]
            else:
                for i, v in enumerate(new_obj):
                    print "list index", i
                    result.extend(print_recursive(v, old_obj[i]))
                
        else:
            
            if isinstance(new_obj, (pd.DataFrame, pd.Series)):
                if not new_obj.equals(old_obj):
                    print "fail compare"
                    return [False]
                return [True]
            
            if not new_obj == old_obj:
                print "fail compare", new_obj, old_obj
                return [False]
            return [True]
            
        return result
    
    check = []
    
    for k, v in new.iteritems():
        print "key", k
        assert k in old
        old_v = old[k]
        check.extend(print_recursive(v, old_v))
    
    return all(check)
