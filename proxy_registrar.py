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

parser = make_parser()
XMLHandler = ExtraerXML()
parser.setContentHandler(XMLHandler)
parser.parse(open(XML))
listaXML = XMLHandler.get_tags()
NAME = listaXML[0][1]['username']
passwd = listaXML[0][1]['passwd']
UA_PORT = listaXML[1][1]['puerto']
UA_IP = listaXML[1][1]['ip']

if UA_IP == "":
    UA_IP = '127.0.0.1'

def log(formato, hora, evento):
    fich = listaXML[4][1]['path']
    fich_log = open(fich, 'a')
    hora = time.gmtime(hora)
    evento = evento.replace('\r\n', ' ')
    fich_log.write(evento + '\r\n')
    fich_log.close()

class SIPRegisterHandler(SocketServer.DatagramRequestHandler):
    """Register SIP"""

    dicc_user = {}
    
        def register2file(self):
        """Escribe en el fichero el diccionario"""
        fichero = "registered.txt"
        fichero = open(fichero, "w")
        cadena = "User\tIP\tPort\tRegistered\tExpires\r\n"
        for user in self.dicc_user.keys():
            expires = self.dicc_user[user][3]
            ip = self.dicc_user[user][0]
            port = self.dicc_user[user][1]
            seg_1970_reg = self.dicc_user[user][2]
            cadena += (user + "\t" + ip + "\t" + str(port) + "\t" +
                       str(seg_1970_reg) + "\t" + str(expires) + "\r\n")
        fichero.write(cadena)
        fichero.close