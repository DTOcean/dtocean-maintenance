# -*- coding: utf-8 -*-
"""This module contains the main class of dtocean-operations-and-maintenance
   for optimisation purposes

.. module:: LCOE_Optimiser
   :platform: Windows
   :synopsis: LCOE optimisation computational code for dtocean-operations-and-maintenance
   
.. moduleauthor:: Bahram Panahandeh <bahram.panahandeh@iwes.fraunhofer.de>
"""

# Set up logging
import logging
module_logger = logging.getLogger(__name__)

#from os import path

# Internal module import
from mainCalc import LCOE_Calculator
#from inputOM import inputOM

import sys

class LCOE_Optimiser(object):        
  
    def __init__(self, inputOMPtr):
        
        '''__init__ function: init function of LCOE_Optimiser: entry class of dtocean-operations-and-maintenance module
                                                      
        Args:              
            inputOMPtr (class) : pointer of class inputOM
        
        Attributes:                              
            self.__calcPTR (class)     : Instance pointer of LCOE_Calculator
            self.__inputOMPTR (class)  : Instance pointer of inputOM
            self.__outputsOfWP6 (dict) : Dictionary which contains the outputs of WP6, Optimised LCOE of array [€/kWh], AnnualEnergyOfArray [MWh] etc.  
          
        Returns:
            no returns 
      
        '''                
        
        # Instance pointer of LCOE_Calculator 
        self.__calcPTR = None
        
        # Instance pointer of inputOM
        self.__inputOMPTR = inputOMPtr                     

        # output of WP6
        self.__outputsOfWP6 = {}      
        
        # Make an instance of LCOE_Calculator
        self.__makeInstance()
                                 
        return
        
    def __makeInstance(self):
        
        '''__makeInstance function: makes an instance of class LCOE_Calculator.
                                                      
        Args:              
            no arguments
        
        Attributes:         
            self.__calcPTR (calss) : Instance pointer of LCOE_Calculator                       
 
        Returns:
            no returns 
      
        '''                
            
        self.__calcPTR = LCOE_Calculator(self.__inputOMPTR)
                                                                                 
        return        
        
    def __call__(self):
                
        '''__call__ function: call function
                                                      
        Args:              
            no arguments
        
        Attributes:         
            no attributs                       
 
        Returns:
            self.__outputsOfWP6 (dict) : Output of WP6
      
        '''                
        
        self.executeOptim() 
 
        return self.__outputsOfWP6   
        
        
    def executeOptim(self):
        
        '''executeOptim function: calls LCOE_Calculator for the calculation of LCOE
                                                      
        Args:              
            no arguments
        
        Attributes:         
            self.__outputsOfWP6 (dict) : Output of WP6                  
 
        Returns:
            self.__outputsOfWP6 (dict) : Output of WP6
      
        ''' 
               
        # the optimisation algorithm will be implemented here in a loop
        try:
                    
            self.__outputsOfWP6 = self.__calcPTR.executeCalc() 
                  
        except KeyboardInterrupt:
            
            sys.exit('Interrupt by Keyboard in dtocean_operations')
                                                             
        return self.__outputsOfWP6