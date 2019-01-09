#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 03:44:22 2019

@author: gugom
"""

import socketserver
import sys
import os
import time

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

if len(sys.argv) == 2:
    XML = sys.argv[1]
else:
    sys.exit('Usage: python3 uaserver.py config')

class ExtraerXML (ContentHandler):
    def __init__(self):
        self.taglist = []
        self.tags = [
            'account', 'uaserver', 'rtpaudio', 'regproxy', 'log', 'audio']
        self.diccattributes = {
            'account': ['username', 'passwd'],
            'uaserver': ['ip', 'puerto'],
            'rtpaudio': ['puerto'],
            'regproxy': ['ip', 'puerto'],
            'log': ['path'],
            'audio': ['path']}

    def startElement(self, tag, attrs):
        dictionary = {}
        if tag in self.tags:
            for attribute in self.diccattributes[tag]:
                dictionary[attribute] = attrs.get(attribute, "")
            self.taglist.append([tag, dictionary])

    def get_tags(self):
        return self.taglist