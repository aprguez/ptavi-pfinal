#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 03:44:22 2019

@author: gugom
"""

import socketserver
import socket
import sys
import time


from xml.sax import make_parser
from xml.sax.handler import ContentHandler


def log(formato, hora, evento):
    fich = listaXML[2][1]['path']
    fich_log = open(fich, 'a')
    hora = time.gmtime(hora)
    evento = evento.replace('\r\n', ' ')
    fich_log.write(evento + '\r\n')
    fich_log.close()


if len(sys.argv) == 2:
    XML = sys.argv[1]
else:
    sys.exit('Usage: python3 proxy_registrar.py config')


class ExtraerXML (ContentHandler):
    def __init__(self):
        self.taglist = []
        self.tags = [
            'server', 'database', 'log']
        self.diccattributes = {
            'server': ['name', 'ip', 'puerto'],
            'database': ['path', 'passwdpath'],
            'log': ['path']}

    def startElement(self, tag, attrs):
        if tag in self.tags:
            dictionary = {}
            for attribute in self.diccattributes[tag]:
                if attribute == 'ip':
                    dictionary[attribute] = attrs.get(attribute, "")
                    ip_server = dictionary[attribute]
                    if ip_server == "":
                        ip_server = "127.0.0.1"
                else:
                    dictionary[attribute] = attrs.get(attribute, "")
            self.taglist.append([tag, dictionary])

    def get_tags(self):
        return self.taglist


parser = make_parser()
XMLHandler = ExtraerXML()
parser.setContentHandler(XMLHandler)
parser.parse(open(XML))
listaXML = XMLHandler.get_tags()
NAME = listaXML[0][1]['name']
UA_PORT = int(listaXML[0][1]['puerto'])
UA_IP = listaXML[0][1]['ip']


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """Register SIP"""

    dicc_user = {}

    def register2file(self):
        """
        Método que imprime en un fichero el contenido del diccionario
        """
        fichero = "registered.txt"
        fichero = open(fichero, "w")
        cadena = "User\tIP\tPort\tRegistered\tExpires\r\n"
        for user in self.dicc_user.keys():
            expires = self.dicc_user[user][3]
            IP = self.dicc_user[user][0]
            PORT = self.dicc_users[user][1]
            seg_1970_reg = self.dicc_user[user][2]
            cadena += (user + "\t" + IP + "\t" + str(PORT) + "\t" +
                       str(seg_1970_reg) + "\t" + str(expires) + "\r\n")
        fichero.write(cadena)
        fichero.close

    def handle(self):
        """
        Metodo handle
        """
        while 1:
            line = self.rfile.read()
            if not line:
                break
            print("RECIBIDO")
            metodo = line.split()
            IP = self.client_address[0]
            PORT = self.client_address[1]
            if metodo[0] == "REGISTER":
                hora = time.time()
                evento = " Received from " + IP + ":"
                evento += str(PORT) + ": " + line
                log("", evento)
                direccion = metodo[1]
                direccion = direccion.split(":")
                print(direccion)
                expires = metodo[4]
                print(expires)
                dir_sip = direccion[1]
                port = direccion[2]
                ip = self.client_address[0]
                hora = time.time()
                self.dicc_user[dir_sip] = [ip, port, hora, expires]
                print(self.dicc_user[dir_sip])
                RESPUESTA = "SIP/2.0 200 OK \r\n\r\n"
                print(RESPUESTA)
                self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                evento = " Sent to " + IP + ":"
                evento += str(PORT) + ": " + RESPUESTA
                log("", evento)
                if expires == "0":
                    del self.dicc_user[(dir_sip)]
                self.register2file()

            elif metodo[0] == "INVITE":
                evento = " Received from " + IP + ":"
                evento += str(PORT) + ": " + line
                log("", evento)
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
                        exito = True
                if exito:
                    my_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET,
                                         socket.SO_REUSEADDR, 1)
                    my_socket.connect((destino_ip, int(destino_port)))
                    print("CONECTADO")
                    my_socket.send(line)
                    evento = " Sent to " + destino_ip + ":"
                    evento += destino_port + ": " + line
                    log("", evento)
                    data = my_socket.recv(1024)
                    evento = " Received from " + destino_ip + ":"
                    evento += destino_port + ": " + data
                    log("", evento)
                    print(data)
                    self.wfile.write(data)
                    evento = " Sent to " + IP + ":"
                    evento += str(PORT) + ": " + data
                    log("", evento)
                    my_socket.close
                else:
                    evento = " Error: SIP/2.0 404 User Not Found"
                    log("", evento)
                    self.wfile.write("SIP/2.0 404 User Not Found\r\n\r\n")

            elif metodo[0] == "BYE" or metodo[0] == "ACK":
                evento = " Received from " + IP + ":"
                evento += str(PORT) + ": " + line
                log("", evento)
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
                        exito = True
                if exito:
                    print("REENVIAMOS 200 OK")
                    my_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET,
                                         socket.SO_REUSEADDR, 1)
                    my_socket.connect((destino_ip, int(destino_port)))
                    print("CONECTADO")
                    my_socket.send(line)
                    evento = " Sent to " + destino_ip + ":"
                    evento += destino_port + ": " + line
                    log("", evento)
                    data = my_socket.recv(1024)
                    print(data)
                    self.wfile.write(data)
                    my_socket.close
            elif metodo[0] == "CANCEL" or metodo[0] == "OPTIONS":
                evento = " Error: SIP/2.0 405 Method Not Allowed"
                log("", evento)
                self.wfile.write("SIP/2.0 405 Method Not Allowed\r\n\r\n")
                evento = " Sent to " + IP + ":"
                evento += str(PORT) + ": " + line
                log("", evento)
            else:
                evento = " Error: " + "SIP/2.0 400 Bad Request"
                log("", evento)
                self.wfile.write("SIP/2.0 400 Bad Request\r\n\r\n")
                evento = " Sent to " + IP + ":"
                evento += str(PORT) + ": " + line
                log(evento)


if __name__ == "__main__":
    serv = socketserver.UDPServer((UA_IP, int(UA_PORT)),
                                  SIPRegisterHandler)
    print("Server ServidorAlex listening at port 7055...")
    serv.allow_reuse_address = True
    serv.serve_forever()
    serv.close()
