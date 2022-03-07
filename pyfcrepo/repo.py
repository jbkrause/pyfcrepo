#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of pyfcrepo.
#
# pyfcrepo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# pyfcrepo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with pyfcrepo. If not, see <https://www.gnu.org/licenses/>
#
# Author : Jan Krause-Bilvin
# First release: 2022-03-03

import requests
from . import nodes

def init_records(fedoraUrl, auth):
    statesUrl = fedoraUrl + 'records'
    status_codes = []
    title = 'Records'
    description = 'Records sets ands records.'
    status_codes.append( nodes.create_basic(statesUrl, auth, title, description) )
    return(status_codes)

def init_types(fedoraUrl, auth):

    typesUrl = fedoraUrl + 'types'
    status_codes = []
    
    title = 'Types'
    description = 'Record types: referential, referentialLeaf, dossier, document'
    status_codes.append( nodes.create_basic(typesUrl, auth, title, description) )

    typeUrl = typesUrl + '/referential'
    title = 'Preservation referential'
    description = 'Comprising a classification plan and management metadata.'
    status_codes.append( nodes.create_basic(typeUrl, auth, title, description, recordType='<rico:RecordSetType>') )
    
    typeUrl = typesUrl + '/referentialLeaf'
    title = 'Preservation referential leaf'
    description = 'Comprising a classification plan tree leaves, i.e. where dossiers are attached.'
    status_codes.append( nodes.create_basic(typeUrl, auth, title, description, recordType='<rico:RecordSetType>') )

    typeUrl = typesUrl + '/dossier'
    title = 'Dossier'
    description = 'Dossier. Must be attached to a referential leaf.'
    status_codes.append( nodes.create_basic(typeUrl, auth, title, description, recordType='<rico:RecordSetType>') )

    typeUrl = typesUrl + '/document'
    title = 'Document'
    description = 'Document. Always part of a dossier.'
    status_codes.append( nodes.create_basic(typeUrl, auth, title, description, recordType='<rico:RecordSetType>') )    
    
    return status_codes

 
def init_states(fedoraUrl, auth):
    
    statesUrl = fedoraUrl + 'states'
    status_codes = []

    title = 'States'
    description = 'Record management states: open or closed.'
    status_codes.append( nodes.create_basic(statesUrl, auth, title, description) )

    ss = ['open', 'closed']
    for i in ss:
        sUrl = statesUrl + '/' + str(i)
        title = 'State ' + i
        description = 'Record management states: {i}.'.format(i=i)
        status_codes.append( nodes.create_basic(sUrl, auth, title, description, recordType="'state'") )
        
    return status_codes
    

def init_rules(fedoraUrl, auth):    

    rulesUrl = fedoraUrl + 'rules'
    status_codes = []

    title = 'Rules'
    description = 'Preservation referential rules.'
    status_codes.append( nodes.create_basic(rulesUrl, auth, title, description) )

    retentionPeriods = [0, 1, 2, 3, 5, 10, 15, 20, 100]
    for i in retentionPeriods:
        ruleUrl = rulesUrl + '/retentionPeriod' + str(i) + 'A'
        title = 'Retention period - ' + str(i) + 'years'
        description = 'The retention period is the duration a dossier is kept before archiving or deletion.'
        status_codes.append( nodes.create_basic(ruleUrl, auth, title, description, recordType=None) )

    closingPeriods = [0, 1, 2, 3, 4, 5]
    for i in closingPeriods:
        ruleUrl = rulesUrl + '/closingPeriod' + str(i) + 'A'
        title = 'Closing period - ' + str(i) + 'years'
        description = 'The closing period is the duration after which a dosier should be closed.'
        status_codes.append( nodes.create_basic(ruleUrl, auth, title, description, recordType=None) )

        
    protections = ['LIBRE', 'ORDINAIRE', 'SPECIAL', 'PROLONGEE']
    delais =      ['0',     '30',         '50',     '100']
    for i,x in enumerate(protections):
        ruleUrl = rulesUrl + '/protection' + str(x)
        title = 'Protection period - ' + str(i) + 'years'
        description = 'The protection period is the duration a dossier may not be communicated to the public without producer authorization.'
        status_codes.append( nodes.create_basic(ruleUrl, auth, title, description, recordType="'protection'") )
        
    return status_codes
