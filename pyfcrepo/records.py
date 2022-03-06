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
    
def create_dossier(fedoraUrl, auth, unit, 
                   did='D1', callnr='M.10.01-D2', parent='acv/235', children=[1],
                   creator = 'agents/roche66', title='Test title', description='Desc.'):

    status_codes = []       
    urlRecords = fedoraUrl + 'records/' 
    typesUrl = fedoraUrl + 'types'
    rulesUrl = fedoraUrl + 'rules'
    creatorUrl = fedoraUrl + creator
    
    # dossier = AIP
    node_parent = urlRecords + parent
    rId = 'D1' 
    cote = 'M.10.01-D1'

    urlDossier = fedoraUrl + 'records/'+ unit.lower()+ '/' + did #id2code(unit, did, nodeType='r' )
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
    data = """ <>  <rico:title> '{title}'.
               <>  <rico:hasCreator> '<{creator}>'.
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
                    title='A document', description='A PDF document.' ):
    
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
    instantiationUrl = documentUrl + '/' + instanciation
    #fileUrl = instantiationUrl + '/f1'

    headers = {"Content-Type": "text/turtle"}
    data = """ <>  <rico:title> '{title}'.
               <>  <rico:scopeAndContent>   '{description}'.
               <>  <rico:hasInstantiation> <{instantiation}>.
               """.format(instantiation=instantiationUrl, title=title, description=description)
    r = requests.put(documentUrl, auth=auth, data=data.encode('utf-8'), headers=headers)
    status_codes.append( r.status_code )
    #print(data)
    
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
    #print(data)
    
    headers3 = {"Content-Type": mimetype,
                "Link" :"<http://www.w3.org/ns/ldp#NonRDFSource>; rel=type"}
    data = open(filename,'rb').read()

    r = requests.put(instantiationUrl+'/binary', auth=auth, data=data, headers=headers3)
    status_codes.append( r.status_code )
    
    return( status_codes )

def load_records(fedoraUrl, auth, unit, creator='agents/roche66',
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
        dossier = df[ df['id'] == d ]
        
        dos = dossier[ dossier['type'] == 'dossier' ]
        docs = dossier[ dossier['type'] == 'document' ]
        doc_ids = docs['callnr'].tolist()
        
        # create dossier
        parent = unit.lower() + '/' + str(int(dos['parent']))
        create_dossier(fedoraUrl, auth, unit, 
                       did=dos['id'][0], callnr=dos['callnr'][0], 
                       parent=parent, children=doc_ids,
                       creator = creator,
                       title=dos['title'][0], description=dos['description'][0])
        #print(docs)
        for ix, doc in docs.iterrows():
            # create document
            create_document(fedoraUrl, auth, unit, did=doc['callnr'],
                           parent=dos['id'][0], filename=doc['filename'], 
                           mimetype=doc['mimetype'],
                           instanciation=doc['instance'],
                           title=doc['title'], description=doc['description'])
                                                      
    return status_codes
    
