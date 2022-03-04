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
import pandas as pd
from . import nodes

from collections import defaultdict

#############
## helpers ##
#############

def strip_textfield(s):
    if isinstance(s, str):
        return s.strip('"= ')
    else:
        return ''

def id2code(unitCode, i, nodeType='r'):
    #return unitCode.lower() +'/'+ str(nodeType) + str(i)
    return 'records/'+ unitCode.lower() + '/' + str(i)

######################
## load refernetial ##
######################
    
def load_ref(fedoraUrl, auth, unit, unitDesc, version, filename):

    status_codes = []       
    urlRecords = fedoraUrl + 'records/' 
    typesUrl = fedoraUrl + 'types'
    rulesUrl = fedoraUrl + 'rules'
    
    # create unit root
    url = urlRecords + unit.lower()
    title = unit
    if unitDesc is None:
        description = ''
    else:
        description = unitDesc
    childrenStr = url + '/0'
    status_codes.append( nodes.create_basic(url, 
                                            auth, 
                                            title, 
                                            description, 
                                            children=childrenStr) )
                                            
    

    if filename is None:
        f = 'data/acv1.0.0.csv'
    else:
        f = filename
    df = pd.read_csv(f, sep=";")

    if version is None:
        v = '1.0.0'
    else:
        v = version

    df['id'] = df['M1']
    df['parent_id'] = df['M2']
    df['cote'] = df['M3'].apply(strip_textfield).astype(str)
    df['title'] = df['M4'].apply(strip_textfield).astype(str)
    df['abstract'] = df['M5'].apply(strip_textfield).astype(str)
    df['personalData'] = df['M13_ExternalId'].apply(strip_textfield).astype(str)
    df['protection'] = df['M11_ExternalId'].apply(strip_textfield).astype(str)
    df['closingPeriod'] = df['M18.1_ExternalId'].apply(strip_textfield).astype(str)
    df['retentionPeriod'] = df['M22'].apply(strip_textfield).astype(str)

    children = defaultdict(list)
    parents  = defaultdict(list)
    for ix, row in df.iterrows():
        if row['parent_id'] != '-':
            children[int(row['parent_id'])].append(int(row['id']))
            parents[int(row['id'])].append(int(row['parent_id']))

    for ix, row in df.iterrows():
        url = fedoraUrl + id2code(unit.lower(), row['id'] )
        
        # compute parent node
        p_nodes = parents[row['id']]
        if len(p_nodes) == 1:
            if str(p_nodes[0]) != '-':
                node_parent = '<' + fedoraUrl + id2code(unit.lower(), p_nodes[0]) + '>'
            else:
                node_parent = '<' + urlRecords + unit.lower() + '>'
        else:
            node_parent = '<' + urlRecords + unit.lower() + '>'
        
        # compute children node
        node_children = [ '<'+fedoraUrl+id2code(unit.lower(), i)+'>' for i in children[row['id']] ]
        children_str = ', '.join(node_children)
        if not children_str == '':
            parts = '<>  <rico:hasOrHadPart> ' + children_str + ' .' 
        else: 
            parts = ''
            
        # compute recordSetType
        if len(children[row['id']]) > 0:
            recordSetType = typesUrl+'/referential'
        else:
            recordSetType = typesUrl+'/referentialLeaf'
            
        # comput record state
        recordState = fedoraUrl + 'states/open' 
        
        # compute rules
        rP = rulesUrl +'/retentionPeriod' + str(row['retentionPeriod'] +'A')
        cP = rulesUrl +'/closingPeriod'   + str(row['closingPeriod'])
        dP = rulesUrl +'/protection'   + str(row['protection'])
        rules = '<{cP}>, <{rP}> , <{dP}>'.format(cP=cP, rP=rP, dP=dP)
        
        # create rico turtle
        headers = {"Content-Type": "text/turtle"}
        data = """ <>  <rico:title> '{title}'.
                   <>  <rico:hasCreator> <{creator}>.
                   <>  <rico:isRecordSetTypeOf> <{recSetType}>.
                   <>  <rico:scopeAndContent>  '{abstract}'.
                   <>  <rico:hasOrHadIdentifier>  '{identifier}'.
                   <>  <rico:hasRecordState>  <{state}>.
                   <>  <rico:isOrWasPartOf> {parent}.
                   <>  <rico:isOrWasRegulatedBy> {rules}.
                   <>  <premis:version> '{archivalVersion}'.
                   {parts}
               """.format( title=row['title'].replace("'", "\\'"), 
                           abstract=row['abstract'].replace("'", "\\'"), 
                           creator='http://localhost:8080/rest/agents/roche66',
                           parent=node_parent,
                           parts=parts,
                           state=recordState,
                           identifier=row['cote'],
                           recSetType=recordSetType,
                           archivalVersion=v,
                           rules=rules)
        
        # send request to api
        r = requests.put(url, auth=auth, data=data.encode('utf-8'), headers=headers)
        status_codes.append(r.status_code)

    return status_codes