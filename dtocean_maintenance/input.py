# -*- coding: utf-8 -*-
"""
This module contains the classes used to collect and modify inputs

.. module:: input
:platform: Windows

.. moduleauthor:: Bahram Panahandeh <bahram.panahandeh@iwes.fraunhofer.de>
                  Mathew Topper <dataonlygreater@gmail.com>
"""

# Built in modules
import logging

# Start logging
module_logger = logging.getLogger(__name__)


class inputOM:

    """
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    #------------------ Input data class
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    Args:
        Farm_OM (dict): This parameter records the O&M general information for
            the farm as whole
        keys:
            calendar_based_maintenance (bool) [-]:
                User input if one wants to consider calendar based maintenance
            condition_based_maintenance (bool) [-]:
                User input if one wants to consider condition based maintenance
            corrective_maintenance (bool) [-]:
                User input if one wants to consider corrective maintenance
            duration_shift (int) [h]:
                Duration of a shift
            helideck (str or bool -> logistic) [-]:
                If there is helideck available or not?
            number_crews_available (int) [-]:
                Number of available crews
            number_crews_per_shift (int) [-]:
                Number of crews per shift
            number_shifts_per_day (int) [-]:
                Number of shifts per day
            wage_specialist_day (float) [€/h]:
                Wage for specialists crew at daytime e.g. diver
            wage_specialist_night (float) [€/h]:
                Wage for specialists crew at night time e.g. diver
            wage_technician_day (float) [€/h]:
                Wage for technicians at daytime
            wage_technician_night (float) [€/h]:
                Wage for technicians at night time
            workdays_summer (int) [-]:
                Working Days per Week during summer
            workdays_winter (int) [-]:
                Working Days per Week during winter

        Component (Pandas DataFrame): This table stores information related to
            the components. A component is any physical object required during
            theoperation of the farm.

        Please note that each defined component will be a column in Pandas
            DataFrame table “Component”

            keys:
                component_id (str) [-]:
                    Id of components
                component_type (str) [-]:
                    Type of components
                component_subtype: (str) [-]:
                    sub type of components
                failure_rate (float) [1/year]:
                    Failure rate of the components
                number_failure_modes (int) [-]:
                    Number of failure modes for this component
                start_date_calendar_based_maintenance (datetime) [-]:
                    Start date of calendar-based maintenance for each year
                end_date_calendar_based_maintenance	 (datetime)	[-]:
                    End date of calendar-based maintenance for each year
                interval_calendar_based_maintenance	int (year) [-]:
                    Interval of calendar-based maintenance
                start_date_condition_based_maintenance (datetime) [-]:
                    Start date of condition-based maintenance for each year
                end_date_condition_based_maintenance (datetime) [-]:
                    End date of condition-based maintenance
                soh_threshold (float) [-]:
                    This parameter belongs to condition based strategy
                is_floating	(bool) [-]:
                    Component is floating and can be towed to port

        Failure_Mode (Pandas DataFrame): This table stores information related
            to the failure modes of components

        Please note that each defined failure mode will be a column in Pandas
            DataFrame table “Failure_Mode”

            keys:
                component_id (str) [-]:
                    Id of component
                fm_id (str) [-]:
                    Id of failure mode
                mode_probability (float) [%]:
                    Probability of occurrence of each failure modes
                spare_mass (float) [kg]:
                    Mass of the spare parts
                spare_height	 (float)	[m]:
                    Height of the spare parts
                spare_width	int (float) [m]:
                    Width of the spare parts
                spare_length (float) [m]:
                    Length of the spare parts
                cost_spare (float) [€]:
                    Cost of the spare parts
                cost_spare_transit	(float) [€]:
                    Cost of the transport of the spare parts
                cost_spare_loading	(float) [€]:
                    Cost of the loading of the spare parts
                lead_time_spare	(bool) [days]:
                    Lead time for the spare parts

        Repair_Action (Pandas DataFrame): This table stores information related
            to the repair actions required for each failure modes

        Please note that each defined repair action will be a column in Pandas
            DataFrame table “Repair_Action”:

            keys:
                component_id (str) [-]:
                    Id of component
                fm_id (str) [-]:
                    Id of failure mode
                duration_maintenance (float) [h]:
                    Duration of time required on site for maintenance
                duration_accessibility (float) [h]:
                    Duration of time required on site to access the component
                    or sub-systems to be repaired or replaced
                interruptable (bool) [-]:
                    Is the failure mode type interruptable or not
                delay_crew (float) [h]:
                    duration of time before the crew is ready
                delay_organisation (float) [h]:
                    duration of time before anything else is ready
                delay_spare	(float) [h]:
                    duration of time before the spare parts are ready
                number_technicians (int) [-]:
                    Number of technicians required to do the O&M
                number_specialists (int) [-]:
                    Number of specialists required to do the O&M
                wave_height_max_acc (float) [m]:
                    wave height max for operational limit conditions during the
                    accessibility
                wave_periode_max_acc (float) [s]:
                    wave period max for operational limit conditions during the
                    accessibility
                wind_speed_max_acc (float) [m/s]:
                    wind speed max for operational limit conditions during the
                    accessibility
                current_speed_max_acc (float) [m/s]:
                    current speed max for operational limit conditions during
                    the accessibility
                wave_height_max_om (float) [m]:
                    wave height max for operational limit conditions during the
                    maintenance action
                wave_periode_max_om (float) [s]:
                    wave period max for operational limit conditions during the
                    maintenance action
                wind_speed_max_om	 (float) [m/s]:
                    wind speed max for operational limit conditions during the
                    maintenance action
                current_speed_max_om (float) [m/s]:
                    current speed max for operational limit conditions during
                    the maintenance action
                requires_lifiting (bool) [-]:
                    Is lifting required?
                requires_divers (bool) [-]:
                    Are divers required?
                requires_towing (bool) [-]:
                    Is towing required?

        Inspection (Pandas DataFrame): This table stores information related to
            the inspections required for each failure modes

        Please note that each defined inspection will be a column in Pandas
            DataFrame table “Repair_Action”:

            keys:
                component_id (str) [-]:
                    Id of component
                fm_id (str) [-]:
                    Id of failure mode
                duration_inspection (float) [h]:
                    Duration of time required on site for inspection
                duration_accessibility (float) [h]:
                    Duration of time required on site to access the component
                    or sub-systems to be repaired or replaced
                delay_crew (float) [h]:
                    duration of time before the crew is ready
                delay_organisation (float) [h]:
                    duration of time before anything else is ready
                number_technicians (int) [-]:
                    Number of technicians required to do the O&M
                number_specialists (int) [-]:
                    Number of specialists required to do the O&M
                wave_height_max_acc (float) [m]:
                    Wave height max for operational limit conditions during the
                    accessibility
                wave_periode_max_acc (float) [s]:
                    Wave period max for operational limit conditions during the
                    accessibility
                wind_speed_max_acc (float) [m/s]:
                    Wind speed max for operational limit conditions during the
                    accessibility
                current_speed_max_acc (float) [m/s]:
                    Current speed max for operational limit conditions during
                    the accessibility
                wave_height_max_om (float) [m]:
                    Wave height max for operational limit conditions during the
                    maintenance action
                wave_periode_max_om (float) [s]:
                    Wave period max for operational limit conditions during the
                    maintenance action
                wind_speed_max_om	 (float) [m/s]:
                    Wind speed max for operational limit conditions during the
                    maintenance action
                current_speed_max_om (float) [m/s]:
                    Current speed max for operational limit conditions during
                    the maintenance action
                requires_lifiting	 (bool) [-]:
                    Is lifting required?
                requires_divers (bool) [-]:
                    Are divers required?


        RAM_Param (dict): This parameter records the information for talking to
            RAM module
            keys:
                calcscenario (str) [-]: scenario for the calculation
                eleclayout (str) [-]: Electrical layout architecture
                pointer (class) [-]: pointer of dtocean-reliability class
                severitylevel (str) [-]: Level of severity
                systype (str) [-]: Type of system

        Logistic_Param (dict): This parameter records the information for
            talking to logistic module
            keys:
                cable_route (DataFrame): logistic parameter
                collection_point (DataFrame): logistic parameter
                connerctors (DataFrame): logistic parameter
                device (DataFrame): logistic parameter
                dynamic_cable (DataFrame): logistic parameter
                equipments (dict): logistic parameter
                external_protection (DataFrame): logistic parameter
                foundation (DataFrame): logistic parameter
                landfall (DataFrame): logistic parameter
                laying_rates (DataFrame): logistic parameter
                layout (DataFrame): logistic parameter
                lease_area (list): logistic parameter
                line (DataFrame): logistic parameter
                metocean (DataFrame): logistic parameter
                other_rates (DataFrame): logistic parameter
                penet_rates (DataFrame): logistic parameter
                ports (DataFrame): logistic parameter
                schedule_OLC (DataFrame): logistic parameter
                site (DataFrame): logistic parameter
                static_cable (DataFrame): logistic parameter
                sub_device (DataFrame): logistic parameter
                topology (DataFrame): logistic parameter
                vessels (dict): logistic parameter

        Simu_Param (dict): This parameter records the general information
            concerning the simulation

            keys:
                Nbodies (int) [-]:
                    Number of devices
                annual_Energy_Production_perD (numpy.ndarray) [Wh]:
                    Annual energy production of each device on the array.
                    The dimension of the array is Nbodies x 1
                arrayInfoLogistic (DataFrame) [-]:
                    Information about component_id, depth, x_coord, y_coord,
                    zone, bathymetry, soil type
                missionTime (float) [year]:
                    Simulation time
                power_prod_perD (numpy.ndarray) [W]:
                    Mean power production per device. The dimension of the
                    array is Nbodies x 1
                startOperationDate (datetime) [-]:
                    Date of simulation start

        Control_Param (dict): This parameter records the O&M module control
            from GUI (to be extended in future)

            keys:
                whichOptim (list) [bool]:
                    Which O&M should be optimised
                        [Unplanned corrective maintenance,
                         Condition based maintenance,
                         Calendar based maintenance]

                checkNoSolution (bool) [-]: see below
                checkNoSolutionWP6Files (bool) [-]: see below
                integrateSelectPort (bool) [-]: see below)

            Note:

                ###############################################################
                ###############################################################
                ###############################################################
                Some of the function developed by logistic takes some times
                for running.

                With the following flags is possible to control the call of
                such functions.

                # Control_Param['integrateSelectPort'] is True ->
                    call OM_PortSelection
                # Control_Param['integrateSelectPort'] is False ->
                    do not call OM_PortSelection, set constant values for port
                    parameters

                # Control_Param['checkNoSolution'] is True  ->
                    check the feasibility of logistic solution before the
                    simulation
                # Control_Param['checkNoSolution'] is False -> do not check
                    the feasibility of logistic solution before the simulation

                ###############################################################
                ###############################################################
                ###############################################################

    Attributes:
        self.__Farm_OM: see above
        self.__Component: see above
        self.__Failure_Mode: see above
        self.__Repair_Action: see above
        self.__Inspection: see above
        self.__RAM_Param: see above
        self.__Logistic_Param: see above
        self.__Simu_Param: see above
        self.__Control_Param: see above
	"""

    def __init__(self, Farm_OM,
                       Component,
                       Failure_Mode,
                       Repair_Action,
                       Inspection,
                       RAM_Param,
                       Logistic_Param,
                       Simu_Param,
                       Control_Param):

        self.__Farm_OM        = Farm_OM
        self.__Component      = Component
        self.__Failure_Mode   = Failure_Mode
        self.__Repair_Action  = Repair_Action
        self.__Inspection     = Inspection
        self.__RAM_Param      = RAM_Param
        self.__Logistic_Param = Logistic_Param
        self.__Simu_Param     = Simu_Param
        self.__Control_Param  = Control_Param

        return

    def get_Farm_OM(self):

        '''get Farm_OM

        Returns:
            Farm_OM (dict): Farm_OM (dict):
                This parameter records the O&M general information for the
                farm as whole

        '''

        return self.__Farm_OM

    # Get component information
    def get_Component(self):

        '''get Component

        Returns:
            Component (Pandas DataFrame):
                This table stores information related to the components. A
                component is any physical object required during the operation
                of the farm.
        '''

        return self.__Component

    # Get failure mode information
    def get_Failure_Mode(self):

        '''get Failure_Mode

        Returns:
            Failure_Mode (Pandas DataFrame):
                This table stores information related to the failure modes of
                components
        '''

        return self.__Failure_Mode

    # Get repair action information
    def get_Repair_Action(self):

        '''get Repair_Action

        Returns:
            Repair_Action (Pandas DataFrame):
                This table stores information related to the repair actions
                required for each failure modes
        '''

        return self.__Repair_Action

    # Get inspection information
    def get_Inspection(self):

        '''get Inspection

        Returns:
            Inspection (Pandas DataFrame):
                This table stores information related to the inspections
                required for each failure modes
        '''

        return self.__Inspection

    # Get RAM information
    def get_RAM_Param(self):

        '''get RAM_Param

        Returns:
            RAM_Param (dict): This parameter records the information for
            talking to RAM module
        '''

        return self.__RAM_Param

    # Get logistic information
    def get_Logistic_Param(self):

        '''get Logistic_Param

        Returns:
            Logistic_Param (dict): This parameter records the information for
        talking to logistic module
        '''

        return self.__Logistic_Param

    # Get simulation information
    def get_Simu_Param(self):

        '''get Simu_Param

        Returns:
            Simu_Param (dict): This parameter records the information of
            simulation
        '''

        return self.__Simu_Param

    # Get control information from GUI
    def get_Control_Param(self):

        '''get Control_Param

        Args:
          No args

        Returns:
            Control_Param (dict): This parameter records the O&M module control
            from GUI
        '''

        return self.__Control_Param

    # no implemented
    def checkInput(self):

        """
        Used to assess the validity of the input given to the WP6
        prior to perform any calculation. NOT IMPLEMENTED

        Returns:
            status (int):
                identify whether an error is found (status<0) or not (status=0)
            errStr (list):
                error strings appended during the error occurence.
        """
        errStr = []
        status = 0

        return NotImplemented
