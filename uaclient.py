#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 01:46:16 2019

@author: gugom
"""

"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
import os

from xml.sax import make_parser
from xml.sax.handler import ContentHandler


if len(sys.argv) != 4:
    XML = sys.argv[1]
    METODO = sys.argv[2]
    OPTION = sys.argv[3]
else:
    sys.exit('Usage: python uaclient.py config method option')

# clase para XML
class ExtraerXML (ContentHandler):

    def __init__(self):
        self.taglist = []
        self.tags = ['account', 'uaserver', 'rtpaudio', 'regproxy', 'log', 'audio']
        self.atributos = {
            'account': ['username', 'passwd'],
            'uaserver': ['ip', 'puerto'],
            'rtpaudio': ['puerto'],
            'regproxy': ['ip', 'puerto'],
            'log': ['path'],
            'audio': ['path']}

    def startElement(self, tag, attrs):
        diccionario = {}
        if tag in self.tags: 
            for atributo in self.atributos[tag]:
                diccionario[atributo] = attrs.get(atributo, "")
            self.taglist.append([tag, diccionario])

    def get_tags(self):
        return self.lista

parser = make_parser()
XMLHandler = ExtraerXML()
parser.setContentHandler(XMLHandler)
parser.parse(open(XML))
lista = XMLHandler.get_tags()
usuario = lista[0][1]['username']
passwd = list[0][1]['passwd']
uaport = lista[1][1]['puerto']
uaip = lista[1][1]['ip']
audioport = lista[2][1]['puerto']
proxyip = lista[3][1]['ip']
proxyport = int(lista[3][1]['puerto'])

if METODO == 'REGISTER':
    LINE = METODO + " sip:" + usuario + ":" + uaport + " SIP/2.0\r\n"
    LINE += "Expires: " + OPTION + "\r\n"
    
elif METODO == 'INVITE':
    LINE = METODO + " sip:" + OPTION  + " SIP/2.0\r\n"
    LINE += "Content-Type: application/sdp\r\n"
    LINE += "v=0\r\n"
    LINE += "o=" + usuario + " " + uaip + "\r\n"
    LINE += "s=misesion\r\n"
    LINE += "t=0\r\n"
    LINE += "m=audio " + audioport + " RTP\r\n\r\n"
    
elif METODO == 'BYE':
    LINE = METODO + " sip:" + OPTION + " SIP/2.0\r\n\r\n"

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((proxyip, proxyport))

try:
    print("Enviando: " + LINE)
    my_socket.send(LINE)

    data = my_socket.recv(1024)

    print('Recibido -- ', data)

    respuesta = "SIP/2.0 100 Trying\r\n\r\n"
    respuesta += "SIP/2.0 180 Ringing\r\n\r\n"
    respuesta += "SIP/2.0 200 OK\r\n\r\n"

    if data == respuesta:
        
        ACK = "ACK" + " sip:" + usuario + ":" + uaip + " SIP/2.0\r\n\r\n"
        print("Enviando ACK: " + ACK)
        my_socket.send(ACK)
        data = my_socket.recv(1024)

    print("Terminando socket...")
except socket.error:
    print("Error: No server listening at " + uaip + " port " + str(uaport))