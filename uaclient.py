#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 01:46:16 2019

@author: gugom
"""

import socket
import sys
import os
import time

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

# Dirección IP del servidor.
if len(sys.argv) == 4:
    XML = sys.argv[1]
    METODO = sys.argv[2]
    OPCION = sys.argv[3]
else:
    sys.exit("Usage: uaclient.py config method opcion")


# Creamos extraer fichero xml
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


def log(formato, hora, evento):
    fich = listaXML[4][1]['path']
    fich_log = open(fich, 'a')
    hora = time.gmtime(hora)
    evento = evento.replace('\r\n', ' ')
    fich_log.write(evento + '\r\n')
    fich_log.close()


# Según el tipo de método que recibamos (REGISTER, INVITE, BYE)
if len(sys.argv) == 4:
    METODO = sys.argv[2]
    if METODO == "REGISTER" and len(sys.argv) == 4:
        LINE = METODO + " sip:" + NAME + "@" + UA_IP + ":" \
            + UA_PORT + " SIP/2.0\r\n"
        LINE = LINE + "Expires: " + OPCION + "\r\n\r\n"
    elif METODO == "INVITE" and len(sys.argv) == 4:
        SDP = "v=0\r\n" + "o=" + NAME + "@" + UA_IP \
            + " " + UA_IP + "\r\n" + "s=SesionSIP\r\n" \
            + "m=audio " + str(RTP_PORT) + " RTP"
        LINE = METODO + " sip:" + OPCION + " SIP/2.0\r\n"
        LINE += "Content-Type: application/sdp\r\n\r\n"
        LINE += str(SDP)
    elif METODO == "BYE" and len(sys.argv) == 4:
        LINE = METODO + " sip:" + OPCION + " SIP/2.0\r\n\r\n"
    else:
        LINE = METODO + " sip:" + UA_IP \
            + str(UA_PORT) + " SIP/2.0\r\n\r\n"

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((PROXY_IP, int(PROXY_PORT)))

try:
    print("Enviando: " + LINE)
    my_socket.send(bytes(LINE, 'utf-8'))

    data = my_socket.recv(1024)

    if data == "SIP/2.0 200 OK\r\n\r\n":
        evento = " Received from " + str(PROXY_IP) + ":" + str(PROXY_PORT)
        evento += ": " + data + '\r\n'
        hora = time.time()
        log("", hora, evento)
    elif data == "SIP/2.0 405 Method Not Allowed\r\n\r\n":
        evento = " Error: " + data + '\r\n'
        hora = time.time()
        log("", hora, evento)
    elif data == "SIP/2.0 400 Bad Request\r\n\r\n":
        evento = " Error: " + data + '\r\n'
        hora = time.time()
        log("", hora, evento)

    print('Recibido...', data)
    RECIBIDO = data.split()
    print(RECIBIDO)
    if len(RECIBIDO) == 14:
        evento = " Received from " + str(PROXY_IP) + ":" + str(PROXY_PORT)
        evento += ": " + data + '\r\n'
        hora = time.time()
        log("", hora, evento)
        fich_audio = listaXML[5][1]['path']
        SPLIT_RECIBIDO = RECIBIDO[8].split(" ")
        IP_RECIBIDO = SPLIT_RECIBIDO[1]
        SPLIT_RECIBIDO_1 = RECIBIDO[11].split(" ")
        PORT_RECIBIDO = SPLIT_RECIBIDO_1[1]
        ACK = "ACK sip:" + OPCION + " SIP/2.0\r\n\r\n"
        hora = time.time()
        evento = " Sent to " + str(PROXY_IP) + ":" + str(PROXY_PORT) + ": "
        evento += ACK + '\r\n'
        log("", hora, evento)
        print("Enviando ACK: " + ACK)
        my_socket.send(ACK)
        aEjecutar = './mp32rtp -i ' + str(IP_RECIBIDO) + ' -p ' + IP_RECIBIDO
        aEjecutar += " < " + fich_audio
        os.system('chmod 755 mp32rtp')
        os.system(aEjecutar)
        linea = "Envio de RTP"
        evento = " Sent to " + str(IP_RECIBIDO) + ":" + str(IP_RECIBIDO) + ": "
        evento += linea + '\r\n'
        log("", hora, evento)
        data = my_socket.recv(1024)
    print("Terminando socket...")

except socket.error:
    hora = time.time()
    evento = "Error: No server listening at " + UA_IP + " port " + str(UA_PORT)
    log("", hora, evento)
