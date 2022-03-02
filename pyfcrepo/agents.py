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

import pandas as pd
import requests
from collections import defaultdict

def create_root(fedoraUrl, auth):

    url = fedoraUrl + 'agents' #unitCode.lower()
    headers = {"Content-Type": "text/turtle"}
    data = """ <>  <rico:title> 'Agents'.
               <>  <rico:scopeAndContent>   'Administrative units, groups, people and software'.
               <>  <rico:hasOrHadPart> <{childrenStr}>.
               """.format( childrenStr= url +'/EDV' )
    r = requests.put(url, auth=auth, data=data.encode('utf-8'), headers=headers)
    return r.status_code


def id2codeA(i, nodeType='r'):
    return 'agents/roche' + str(i)
    
def load_tree(fedoraUrl, auth, filename):

    # Read tree

    df = pd.read_csv(filename, sep=",")

    df['id'] = df['Code']
    df['parent_id'] = df['PARENT']
    df['cote'] = df['Acronyme']
    df['title'] = df['Nom']

    children = defaultdict(list)
    parents  = defaultdict(list)
    for ix, row in df.iterrows():
        if row['parent_id'] != '-':
            children[row['parent_id']].append(row['id'])
            parents[row['id']].append(row['parent_id'])

    # Write tree to Fedora

    for ix, row in df.iterrows():
        
        status_codes = []
        url = fedoraUrl + id2codeA(row['id'] )
        
        # compute parent node
        p_nodes = parents[row['id']]
        if len(p_nodes) >= 1:
            if str(p_nodes[0]) != "-":
                node_parent = '<' + fedoraUrl + id2codeA(p_nodes[0]) + '>'
            else:
                node_parent = '<' + fedoraUrl + 'agents' + '>'
        else:
            #node_parent = '<' + fedoraUrl + unitCode.lower() + '>'
            node_parent = '<' + fedoraUrl + 'agents' + '>'
        
        # compute children node
        node_children = [ '<'+fedoraUrl+id2codeA(i)+'>' for i in children[row['id']] ]
        children_str = ', '.join(node_children)
        if not children_str == '':
            parts = '<>  <rico:hasOrHadPart> ' + children_str + ' .' 
        else: 
            parts = ''
                
        # create rico turtle
        headers = {"Content-Type": "text/turtle"}
        data = """ <>  <rico:title> '{title}'.
                   <>  <rico:hasOrHadIdentifier>  '{identifier}'.
                   <>  <rico:hasRecordState>  <{state}>.
                   <>  <rico:isOrWasPartOf> {parent}.
                   <>  <premis:version> '{archivalVersion}'.
                   {parts}
               """.format( title=row['title'].replace("'", "\\'"),  
                           parent=node_parent,
                           parts=parts,
                           state='http://localhost:8080/rest/states/open',
                           identifier=row['cote'].replace('\n',''),
                           archivalVersion='1.0.0')
        
        # send request to api
        r = requests.put(url, auth=auth, data=data.encode('utf-8'), headers=headers)
        status_codes.append(r.status_code)

    return status_codes


