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
import time
import hashlib

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

# Dirección IP del servidor.
if len(sys.argv) == 4:
    XML = sys.argv[1]
    METODO = sys.argv[2]
    OPCION = sys.argv[3]
else:
    sys.exit("Usage: uaclient.py config method opcion")

def log(formato, hora, evento):
    fich = listaXML[4][1]['path']
    fich_log = open(fich, 'a')
    hora = time.gmtime(hora)
    evento = evento.replace('\r\n', ' ')
    fich_log.write(evento + '\r\n')
    fich_log.close()

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

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((PROXY_IP, int(PROXY_PORT)))

if UA_IP == "":
    UA_IP = '127.0.0.1'

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

# Envio al log
hora = time.time()
evento = " Sent to " + PROXY_IP + ':' + str(PROXY_PORT) + ':'
evento += LINE
log('', hora, evento)
print("Enviando: " + LINE)
my_socket.send(bytes(LINE, 'utf-8'))
data = my_socket.recv(1024)

print('Recibido -- ', data.decode('utf-8'))
datosrecibidos = data.decode('utf-8')
datos = datosrecibidos.split()
hora = time.time()
evento = " Received from " + PROXY_IP + ':' + str(PROXY_PORT) + ':'
evento += datosrecibidos + '\r\n'
log('', hora, evento)

if METODO == "REGISTER":
    if datos[1] == "401":
        METODO = "REGISTER"
        LINE = METODO + " sip:" + NAME + ":" + UA_PORT
        LINE += ": SIP/2.0" + "\r\n" + "Expires: " + OPCION + "\r\n"
        nonce_completo = datos[6]
        nonce_div = nonce_completo.split('=')
        nonce = nonce_div[1]
        nonce_bytes = bytes(nonce, 'utf-8')
        passwd_bytes = bytes(passwd, 'utf-8')
        m = hashlib.md5()
        m.update(passwd_bytes + nonce_bytes)
        response = m.hexdigest()
        LINE += "Authorization: Digest response= " + str(response)
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        hora = time.time()
        evento = " Sent to " + PROXY_IP + ':' + str(PROXY_PORT) + ':'
        evento += LINE + '\r\n'
        log('', hora, evento)
        data = my_socket.recv(PROXY_PORT)
        print('Recibido -- ', data.decode('utf-8'))
        datosrecibidos = data.decode('utf-8')
        datos = datosrecibidos.split()
        hora = time.time()
        evento = " Received from " + PROXY_IP + ':' + str(PROXY_PORT)
        evento += ':' + datosrecibidos + '\r\n'
        log('', hora, evento)
elif METODO == "INVITE":
    if datos[1] == "100" and datos[4] == "180" and datos[7] == "200":
        ip_servidor = datos[13]
        port_servidor = datos[17]
        METODO = "ACK"
        LINE = METODO + " sip:" + OPCION + " " + "SIP/2.0"
        print("Enviando: " + LINE)
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        aEjecutar = './mp32rtp -i ' + '127.0.0.1'
        aEjecutar += ' -p' + port_servidor + '<'
        aEjecutar += fich_audio
        print("Vamos a ejecutar: ", aEjecutar)
        os.system(aEjecutar)
        hora = time.time()
        evento = " Sent to " + PROXY_IP + ':' + str(PROXY_PORT) + ':'
        evento += aEjecutar + '\r\n'
        log('', hora, evento)

print("Terminando socket...")

# Cerramos todo
my_socket.close()
print("Fin.")
hora = time.time()
evento = " Finishing..."
log('', hora, evento)