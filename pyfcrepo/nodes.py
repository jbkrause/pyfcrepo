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

def create_basic(url, auth, title, description, recordType=None, children=None):
    headers = {"Content-Type": "text/turtle"}
    data = """ <>  <rico:title> '{title}'.
               <>  <rico:scopeAndContent>   '{description}'.
               """.format(title=title, description=description)
    if recordType is not None:
        data += '<>  <rico:type>  {recordType}.\n'.format(recordType=recordType)
    if children is not None:
        data += '<>  <rico:hasOrHadPart> <{childrenStr}>.\n'.format(childrenStr=children)
    r = requests.put(url, auth=auth, data=data.encode('utf-8'), headers=headers)
    return r.status_code