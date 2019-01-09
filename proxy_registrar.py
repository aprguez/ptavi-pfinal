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
    database = listaXML[1][1]['path']
    fichero = open(database, "w")
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
    
    def handle(self):
        """
        Metodo handle
        """
        while 1:
            line = self.rfile.read()
            print(line)
            if not line:
                break
            metodo = line.split()
            print("RECIBIDO" + line)
            IP = self.client_address[0]
            PORT = self.client_address[1]
            if metodo[0] == "REGISTER":
                evento = " Received from " + IP + ":"
                evento += str(PORT) + ": " + line
                log("", hora, evento)
                direccion = metodo[1]
                direccion = direccion.split(":")
                print(direccion)
                expires = metodo[4]
                print(expires)
                dir_sip = direccion[1]
                port = direccion[2]
                ip = self.client_address[0]
                hora = time.time()
                horalim = time.time() + float(expires)
                self.dicc_user[dir_sip] = [ip, port, hora, expires]
                print(self.dicc_user[dir_sip])
                RESPUESTA = "SIP/2.0 200 OK \r\n\r\n"
                print(RESPUESTA)
                self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                evento = " Sent to " + IP + ":"
                evento += str(port_log) + ": " + RESPUESTA
                log("", hora, evento)
                if expires == "0":
                    del self.dicc_user[(dir_sip)]
                self.register2file()
            
              elif metodo[0] == "INVITE":
                evento = " Received from " + IP + ":"
                evento += str(PORT) + ": " + line
                log("", hora, evento)
                destino = metodo[1]
                destino = destino.split(":")
                destino_sip = destino[1]
                destino_port = ""
                destino_ip = ""
                exito = False
                for user in self.dicc_user.keys():
                    if user == destino_sip:
                        destino_port = self.dicc_user[destino_sip][1]
                        destino_ip = self.dicc_user[destino_sip][0]
                        
