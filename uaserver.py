#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 02:15:40 2019

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
RTP_PORT = listaXML[2][1]['puerto']
PROXY_IP = listaXML[3][1]['ip']
PROXY_PORT = int(listaXML[3][1]['puerto'])
fich_audio = listaXML[5][1]['path']

if UA_IP == "":
    UA_IP = '127.0.0.1'

def log(formato, hora, evento):
    fich = listaXML[4][1]['path']
    fich_log = open(fich, 'a')
    hora = time.gmtime(hora)
    evento = evento.replace('\r\n', ' ')
    fich_log.write(evento + '\r\n')
    fich_log.close()

class Server_Sip(socketserver.DatagramRequestHandler):
    RECEPTOR = {'IP': "", "PORT": 0}
    print ("INICIO")

    def handle(self):

        while 1:
            mensaje = self.rfile.read()
            line = mensaje.split()
            if not line:
                break
            print(line)
            if line[0] == "INVITE":
                print("INVITE recibido")
                self.receptor["IP"] = line[7]
                self.receptor["PORT"] = line[11]
                print(self.receptor["IP"])
                print(self.receptor["PORT"])
                ENVIO = ("SIP/2.0 100 Trying\r\n\r\nSIP/2.0 180 Ringing"
                           "\r\n\r\nSIP/2.0 200 OK\r\n")
                ENVIO += "Content-type: application/sdp\r\n\r\n"
                ENVIO += "v=0\r\n" + "o=" + NAME + " "
                ENVIO += UA_IP + "\r\n" + "s=finalptavi\r\n" + "t=0\r\n"
                ENVIO += "m=audio " + str(fich_audio) + " RTP\r\n"
                self.wfile.write(ENVIO)
                evento = " Received from " + PROXY_IP + ":"
                evento += str(PROXY_PORT) + ": " + mensaje
                log('', hora, evento)
                evento= " Sent to " + self.receptor["IP"] + ":"
                evento += self.receptor["PORT"] + ": " + ENVIO
                log('', hora, evento)
            elif line[0] == "ACK":
                print("ACK recibido")
                print(self.receptor["IP"])
                print(self.receptor["PORT"])
                evento = " Received from " + PROXY_IP + ":"
                evento += str(PROXY_PORT) + ": " + mensaje
                log('', hora, evento)
                aEjecutar = ('./mp32rtp -i ' + self.receptor["IP"] + ' -p ' +
                             self.receptor["PORT"] + ' < ' + fich_audio)
                print("Vamos a ejecutar", aEjecutar)
                os.system('chmod 755 mp32rtp')
                os.system(aEjecutar)
                print("HECHO")
                evento = " Sent to " + self.receptor["IP"] + ":"
                evento += self.receptor["PORT"] + ": " + "RTP"
                log('', hora, evento)
            elif line[0] == "BYE":
                print("BYE recibido")
                self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                evento = " Received from " + PROXY_IP + ":"
                evento += str(PROXY_PORT) + ": " + mensaje
                log('', hora, evento)
            elif (line[0] == "CANCEL" or line[0] == "REGISTER"
                  or line[0] == "OPTIONS"):
                print("metodo no disponible recibido")
                self.wfile.write("SIP/2.0 405 Method Not Allowed\r\n\r\n")
                evento = " Received from " + PROXY_IP + ":"
                evento += str(PROXY_PORT) + ": " + mensaje
                log('', hora, evento)
            else:
                print("petición incorrecta recibida")
                self.wfile.write("SIP/2.0 400 Bad Request\r\n\r\n")
                evento = " Received from " + PROXY_IP + ":"
                evento += str(PROXY_PORT) + ": " + mensaje
                log('', hora, evento)

if __name__ == "__main__":
    serv = socketserver.UDPServer((UA_IP, int(UA_PORT)), Server_Sip)
    print("Listening...")
    hora = time.time()
    evento = " Listening...  "
    log('', hora, evento)
    serv.serve_forever()
