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

def id2code(unitCode, i, nodeType='r'):
    #return unitCode.lower() +'/'+ str(nodeType) + str(i)
    return 'records/'+ unitCode.lower() + '/' + str(i)

######################
## load refernetial ##
######################
    
def create_dossier(fedoraUrl, auth, unit, did='D1', callnr='M.10.01-D2', parent='acv/235', children=[1] ):

    status_codes = []       
    urlRecords = fedoraUrl + 'records/' 
    typesUrl = fedoraUrl + 'types'
    rulesUrl = fedoraUrl + 'rules'
    
    # dossier = AIP
    node_parent = urlRecords + parent
    rId = 'D1' 
    cote = 'M.10.01-D1'

    urlDossier = fedoraUrl + id2code(unit, did, nodeType='r' )
    recordSetType = typesUrl+'/dossier'

    node_children = [ '<'+urlDossier+'/documents/'+str(i)+'>' for i in children ]
    children_str = ', '.join(node_children)
    parts = '<>  <rico:hasOrHadPart> ' + children_str + ' .'

    recordState = fedoraUrl + 'states/open'

    urlDocument = node_children[0]

    headers2 = {"Content-Type": "text/turtle",
               "Link": '<http://fedora.info/definitions/v4/repository#ArchivalGroup>;rel="type"'}
    data = """ <>  <rico:title> '{title}'.
               <>  <rico:hasCreator> '<{creator}>'.
               <>  <rico:hasRecordState>  <{state}>.
               <>  <rico:isRecordSetTypeOf> <{recSetType}>.
               <>  <rico:scopeAndContent>  '{abstract}'.
               <>  <rico:hasOrHadIdentifier>  '{identifier}'.
               <>  <rico:isOrWasPartOf> <{parent}>.
               {parts}
           """.format( title='Le dossier', 
                       abstract='La description du dossier',
                       creator='http://localhost:8080/rest/agents/roche66',
                       parent=node_parent,
                       parts=parts,
                       identifier=cote,
                       state=recordState,
                       recSetType=recordSetType)
    r = requests.put(urlDossier, auth=auth, data=data.encode('utf-8'), headers=headers2)

    status_codes.append(r.status_code)
    return status_codes

def create_document(fedoraUrl, auth, unit, did='1', parent='D1', filename='data\\records\\files\\file.pdf', mimetype='application/pdf', title='A document', description='A PDF document.' ):
    
    status_codes = []
    
    urlDossier = fedoraUrl + id2code( unit, parent, nodeType='r' )
    documentsUrl = urlDossier + '/documents'
    
    headers = {"Content-Type": "text/turtle"}
    data = """ <>  <rico:title> 'documents'.
               <>  <rico:scopeAndContent>   'Docuements container.'.
               """
    r = requests.put(documentsUrl, auth=auth, data=data.encode('utf-8'), headers=headers)
    status_codes.append( r.status_code )
    
    documentUrl = documentsUrl + '/' + did
    instantiationUrl = documentUrl + '/i1'
    #fileUrl = instantiationUrl + '/f1'

    headers = {"Content-Type": "text/turtle"}
    data = """ <>  <rico:title> '{title}'.
               <>  <rico:scopeAndContent>   '{description}'.
               <>  <rico:hasInstantiation> <{instantiation}>.
               """.format(instantiation=instantiationUrl, title=title, description=description)
    r = requests.put(documentUrl, auth=auth, data=data.encode('utf-8'), headers=headers)
    status_codes.append( r.status_code )
    
    headers = {"Content-Type": "text/turtle"}
    data = """ <>  <premis:hasCompositionLevel> "0".
               <>  <premis:orginalName> "{filename}".
               <>  <ebucore:hasMimeType> "{mimetype}".
               <>  <rico:type> <rico:Instantiation>.
               <>  <http://www.w3.org/2004/02/skos/exactMatch> <http://www.nationalarchives.gov.uk/pronom/fmt/95>.
               <>  <rico:type> <premis:file>.
               """.format(instantiation=instantiationUrl, filename=filename, mimetype=mimetype)
    r = requests.put(instantiationUrl, auth=auth, data=data.encode('utf-8'), headers=headers)
    status_codes.append( r.status_code )   
    
    headers3 = {"Content-Type": mimetype,
                "Link" :"<http://www.w3.org/ns/ldp#NonRDFSource>; rel=type"}
    data = open(filename,'rb').read()
    r = requests.put(instantiationUrl+'/binary', auth=auth, data=data, headers=headers3)
    status_codes.append( r.status_code )
    
    return( status_codes )

def blabla():


   

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
                   <>  <rico:hasCreator> '<{creator}>'.
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