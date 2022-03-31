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
    return 'records/'+ unitCode.lower() + '/dossiers/' + str(i)

######################
## load refernetial ##
######################
    
def create_dossier(fedoraUrl, auth, unit, 
                   did='D1', callnr='M.10.01-D2', parent='acv/referential/235', children=[1],
                   creator = 'agents/roche/66', title='Test title', description='Desc.',
                   transaction = None  ):

    status_codes = []       
    urlRecords = fedoraUrl + 'records/' 
    typesUrl = fedoraUrl + 'types'
    rulesUrl = fedoraUrl + 'rules'
    creatorUrl = fedoraUrl + creator
    
    # dossier = AIP
    node_parent = urlRecords + parent
    rId = 'D1' 
    cote = 'M.10.01-D1'

    urlDossier = fedoraUrl + id2code(unit, did, nodeType='r' ) #'records/'+ unit.lower()+ '/' + did
    recordSetType = typesUrl+'/dossier'

    node_children = []
    for x in children:
        s = '<'+urlDossier+'/documents/'+str(x)+'>'
        node_children.append( s )
    children_str = ', '.join(node_children)
    
    parts = '<>  <rico:hasOrHadPart> ' + children_str + ' .'

    recordState = fedoraUrl + 'states/open'

    urlDocument = node_children[0]

    headers2 = {"Content-Type": "text/turtle",
               "Link": '<http://fedora.info/definitions/v4/repository#ArchivalGroup>;rel="type"'}
               
    if transaction is not None:
        headers2['Atomic-ID']=transaction
        
    data = """ <>  <rico:title> '{title}'.
               <>  <rico:hasCreator> <{creator}>.
               <>  <rico:hasRecordState>  <{state}>.
               <>  <rico:isRecordSetTypeOf> <{recSetType}>.
               <>  <rico:scopeAndContent>  '{abstract}'.
               <>  <rico:hasOrHadIdentifier>  '{identifier}'.
               <>  <rico:isOrWasPartOf> <{parent}>.
               {parts}
           """.format( title=title, 
                       abstract=description,
                       creator=creatorUrl,
                       parent=node_parent,
                       parts=parts,
                       identifier=cote,
                       state=recordState,
                       recSetType=recordSetType)
    r = requests.put(urlDossier, auth=auth, data=data.encode('utf-8'), headers=headers2)
    #print(urlDossier)
    #print(data)
    #print(r.status_code)
    
    status_codes.append(r.status_code)
    return status_codes

def create_document(fedoraUrl, auth, unit, did='1', parent='D1', 
                    filename='data\\records\\files\\file.pdf', 
                    mimetype='application/pdf', instanciation='i1',
                    title='A document', description='A PDF document.',
                    fmtName='PDF/A1', fmtVersion='1.4',
                    fmtRegistry='PRONOM', fmt='fmt/95',
                    envName='Ubuntu', envVersion='22.04',
                    creatingApp='LibreOffice', creatingAppVersion='7.3.1',
                    inhibitorType='AES', inhibitorKey='1af4b6c5d94',
                    transaction = None ):
    
    status_codes = []
    
    urlDossier = fedoraUrl + id2code( unit, parent, nodeType='r' )
    documentsUrl = urlDossier + '/documents'
    typesUrl = fedoraUrl + 'types'
    
    headers = {"Content-Type": "text/turtle"}

    if transaction is not None:
        headers['Atomic-ID']=transaction    
    
    
    data = """ <>  <rico:title> 'documents'.
               <>  <rico:scopeAndContent>   'Docuements container.'.
               """
    r = requests.put(documentsUrl, auth=auth, data=data.encode('utf-8'), headers=headers)
    status_codes.append( r.status_code )
    
    documentUrl = documentsUrl + '/' + did
    instantiationUrl = documentUrl + '/' + instanciation
    #fileUrl = instantiationUrl + '/f1'

    headers = {"Content-Type": "text/turtle"}
    
    if transaction is not None:
        headers['Atomic-ID']=transaction  
        
    data = """ <>  <rico:title> "{title}".
               <>  <rico:scopeAndContent>   "{description}".
               <>  <rico:type> <http://localhost:8080/rest/types/document>.
               <>  <rico:hasInstantiation> <{instantiation}>.
               """.format(instantiation=instantiationUrl, title=title, description=description)
    r = requests.put(documentUrl, auth=auth, data=data.encode('utf-8'), headers=headers)
    status_codes.append( r.status_code )
    #print(data)
    
    headers = {"Content-Type": "text/turtle"}

    if transaction is not None:
        headers['Atomic-ID']=transaction  
        
    data = """ <>  <premis:hasCompositionLevel> "0".
               <>  <premis:orginalName> "{filename}".
               <>  <premis:formatName> "{fmtName}".
               <>  <premis:formatVersion> "{fmtVersion}".
               <>  <premis:formatRegistry> "{fmtRegistry}".
               <>  <premis:formatRegistryKey> <http://www.nationalarchives.gov.uk/pronom/{fmt}>.               
               <>  <premis:environmentName> "{envName}".  
               <>  <premis:environmentVersion> "{envVersion}".
               <>  <premis:creatingApplication> "{creatingApp}".  
               <>  <premis:creatingApplicationVersion> "{creatingAppVersion}".                
               <>  <ebucore:hasMimeType> "{mimetype}".
               <>  <rico:type> <{ricoType}>.
               <>  <rico:type> <premis:representation>.
               """.format(instantiation=instantiationUrl, filename=filename, mimetype=mimetype, ricoType=typesUrl+'/instantiation',
                           fmtName=fmtName, fmtVersion=fmtVersion, fmtRegistry=fmtRegistry, fmt=fmt, envName=envName, envVersion=envVersion, creatingApp=creatingApp, creatingAppVersion=creatingAppVersion)
    r = requests.put(instantiationUrl, auth=auth, data=data.encode('utf-8'), headers=headers)
    status_codes.append( r.status_code )  
    #print(data)
    
    headers3 = {"Content-Type": mimetype,
                "Link" :"<http://www.w3.org/ns/ldp#NonRDFSource>; rel=type"}
                
    if transaction is not None:
        headers3['Atomic-ID']=transaction  
        
    data = open(filename,'rb').read()

    r = requests.put(instantiationUrl+'/binary', auth=auth, data=data, headers=headers3)
    status_codes.append( r.status_code )
    
    return( status_codes )

def load_records(fedoraUrl, auth, unit, creator='agents/roche/66',
                 filename="data\\records\\records.csv"):

    status_codes = []
    df = pd.read_csv(filename, sep=";")
    
    df['id'] = df['id'].astype(str)
    df['type'] = df['type'].astype(str)
    df['callnr'] = df['callnr'].astype(str)
    df['parent'] = df['parent']
    df['title'] = df['title'].astype(str)
    df['description'] = df['description'].astype(str)
    df['instance'] = df['instance'].astype(str)
    df['filename'] = df['filename'].astype(str)
    df['fmt'] = df['fmt'].astype(str)
    df['mimetype'] = df['mimetype'].astype(str)

    dossiers = pd.unique( df['id'] )
        
    for d in dossiers:
        
        # BEGIN TRANSACTION
        #url = "http://localhost:8080/rest/fcr:tx"
        #r = requests.post(url, auth=auth)
        #tx = r.headers['Location']
        #print( 'Begin transaction:', tx )
    
        dossier = df[ df['id'] == d ]
        
        dos = dossier[ dossier['type'] == 'dossier' ]
        docs = dossier[ dossier['type'] == 'document' ]
        doc_ids = docs['callnr'].tolist()
        
        # create dossier
        parent = unit.lower() + '/' + dos['parent'].values[0] #str(int(dos['parent']))
        sc = create_dossier(fedoraUrl, auth, unit, 
                       did=dos['id'].values[0], callnr=dos['callnr'].values[0], 
                       parent=parent, children=doc_ids,
                       creator = creator,
                       title=dos['title'].values[0], description=dos['description'].values[0],
                       transaction = None)
        status_codes += sc
        
        #print(docs)
        for ix, doc in docs.iterrows():
            
            #r = requests.post(tx, auth=auth) # refresh transaction
            
            # create document
            sc = create_document(fedoraUrl, auth, unit, did=doc['callnr'],
                           parent=dos['id'].values[0], filename=doc['filename'], 
                           mimetype=doc['mimetype'],
                           instanciation=doc['instance'],
                           title=doc['title'], description=doc['description'],
                           transaction = None)
            status_codes += sc
    
        # END TRANSACTION    
        #r = requests.put(tx, auth=auth)
        #print( 'Commit transaction:', r.status_code )
                                                      
    return status_codes
    
