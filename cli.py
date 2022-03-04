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

import os
import pprint
import configparser
import argparse
from collections import defaultdict
import datetime
import time
import re

import requests

from pyfcrepo import repo
from pyfcrepo import agents
from pyfcrepo import ref
from pyfcrepo import records

pp = pprint.PrettyPrinter(depth=6)

# Parse arguments
usage = '''cli.py ACTION [--unit UNIT] [--file FILE] [--version VERSION]
           action : checkcon | initrepo | loadagents | loadref | updateref\n'''
parser = argparse.ArgumentParser(description='Manage Fedora Commons repository.')
parser.add_argument('action', help='checkcon | initrepo | loadagents | loadref | updateref .')
parser.add_argument('--unit', dest='unitCode', help='Target unit.')
parser.add_argument('--unitDesc', dest='unitDesc', help='Target unit description.')
parser.add_argument('--file', dest='input_file', help='Input file.')
parser.add_argument('--version', dest='version', help='Information package ID, used to generate the primer')

args = parser.parse_args()

# read config
cfg = configparser.ConfigParser()
cfg.read('config.ini')
cfg_set = 'DEFAULT'

# fcrepo access
protocol = cfg[cfg_set]['protocol']
host = cfg[cfg_set]['host']
port = cfg[cfg_set]['port']
user = cfg[cfg_set]['user']
pwd = cfg[cfg_set]['pwd']
fedoraUrl = protocol + '://' + host + ':' + port + '/rest/' 
auth = (user, pwd)

if args.action=='checkcon':
    r = requests.get(fedoraUrl, auth=auth)
    print(r.status_code)
   
elif args.action=='initrepo':
    print('Init repository ...') 
    status_codes = repo.init_records(fedoraUrl=fedoraUrl, auth=auth)
    print('Init records', status_codes)      
    status_codes = repo.init_types(fedoraUrl=fedoraUrl, auth=auth)
    print('Init record types', status_codes)   
    status_codes = repo.init_states(fedoraUrl=fedoraUrl, auth=auth)
    print('Init record states', status_codes)
    status_codes = repo.init_rules(fedoraUrl=fedoraUrl, auth=auth)
    print('Init record mangement rules', status_codes)   
    status_codes = agents.create_root(fedoraUrl=fedoraUrl, auth=auth)
    print('Init agents root', status_codes)
 
elif args.action=='loadagents':
    print('Load agents from {input_file}...'.format(input_file=args.input_file))
    status_codes = agents.load_tree(fedoraUrl=fedoraUrl, auth=auth, filename=args.input_file)
    print('Init record types', status_codes)

elif args.action=='loadref':
    print('Load preservation referential...')
    status_codes = ref.load_ref(fedoraUrl=fedoraUrl, auth=auth, 
                                unit=args.unitCode,  unitDesc=args.unitDesc,
                                version=args.version, filename=args.input_file)
    print('Units', status_codes)

elif args.action=='dossier':
    print('Create dossier...')
    status_codes = records.create_dossier(fedoraUrl=fedoraUrl, auth=auth, 
                                unit=args.unitCode)
    print('Dossier', status_codes)

elif args.action=='document':
    print('Create document...')
    status_codes = records.create_document(fedoraUrl=fedoraUrl, auth=auth, 
                                unit=args.unitCode)
    print('Dossier', status_codes)
    print('Dossier', status_codes)
    
elif args.action=='dossier':
    print('Create dossier...')
    status_codes = records.create_dossier(fedoraUrl=fedoraUrl, auth=auth, 
                                unit=args.unitCode)
    print('Dossier', status_codes)

elif args.action=='loadrecords':
    print('Load records...')
    status_codes = records.load_records(fedoraUrl=fedoraUrl, auth=auth, 
                                unit=args.unitCode)
    print('Dossier', status_codes)
    
else:
    print(usage)


        
