#!/usr/bin/env python
###############################################################################
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################
 
__author__ = "Joel Boyd"
__copyright__ = "Copyright 2015"
__credits__ = ["Joel Boyd"]
__license__ = "GPL3"
__version__ = "0.0.1"
__maintainer__ = "Joel Boyd"
__email__ = "joel.boyd near uq.net.au"
__status__ = "Development"
 
###############################################################################

import logging
import pickle
import os
from math import sqrt
from network_builder import NetworkBuilder

###############################################################################

class KeggMatrix:
    DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             '..', 
                             'data')
    
    VERSION = os.path.join(DATA_PATH, 'VERSION')
    R2K     = os.path.join(DATA_PATH, 'reaction_to_orthology')
    PICKLE  = 'pickle'
    
    def __init__(self, matrix, transcriptome=None):
        self.VERSION = open(self.VERSION).readline().strip()

        logging.info("Loading reaction to pathway information")
        self.r2k = pickle.load(open('.'.join([self.R2K, 
                                              self.VERSION, self.PICKLE])))
        logging.info("Done")
        
        logging.info("Parsing input matrix: %s" % matrix)
        self.orthology_matrix \
                = self._parse_matrix(matrix)
        logging.info("Done")
        
        logging.info("Calculating reaction abundances")
        self.reaction_matrix \
                = self._calculate_abundances(self.r2k,
                                             self.orthology_matrix)
        logging.info("Done")

    def _parse_matrix(self, matrix):
        
        output_dict = {}
        
        for idx, line in enumerate(open(matrix)):
            sline = line.strip().split('\t')
            
            if idx==0:
                self.sample_names = sline[1:]
                    
                for sample in self.sample_names: 
                    output_dict[sample] = {}
            else:   
                ko_id      = sline[0]
                abundances = sline[1:]
                
                for abundance, sample in zip(abundances, self.sample_names):
                    output_dict[sample][ko_id] = float(abundance)
        return output_dict
    
    def group_abundances(self, samples):

        output_dict = {}        
        for sample in samples:
            new_dict = {key:entry for key,entry in self.reaction_matrix.items() if 
                        key in samples}
            reference_list = new_dict[new_dict.keys()[0]].keys()
            
            for reference in reference_list:
                # If samples are missing from stored data, this will crash 
                try:
                    abundances = [new_dict[sample][reference] for sample in samples]
                    average    = sum(abundances)/float(len(abundances))
                    output_dict[reference] = average
                except:
                    raise Exception("metadata description does not match \
input matrix")
        return output_dict
                          
    def _calculate_abundances(self, reference_dict, matrix_dict):
        
        output_dict_mean   = {}


        for sample, ko_abundances in matrix_dict.items():
            output_dict_mean[sample]   = {}
            
            for reaction, ko_list in reference_dict.items():
                
                abundances = []
                for ko in ko_list:

                    if ko in matrix_dict[sample]:
                        abundances.append(matrix_dict[sample][ko])
                    else:
                        logging.debug("ID not found in input matrix: %s" % ko)
                        
                if any(abundances):
                    abundance_mean = sum(abundances)/len(abundances)
                else:
                    abundance_mean = 0

                output_dict_mean[sample][reaction] = abundance_mean
        
        return output_dict_mean
