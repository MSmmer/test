# -*- coding: gb2312 -*-

from socket import *
from select import *
import time
import logging
import traceback
'''
'''

g_CSOCK_BUFFSIZE = 8192
g_SOCKET_IP="127.0.0.1"
g_SOCKET_PORT_LOGSTASH_CHECK=50001
g_SOCKET_PORT_MSG_PROCESS=50002

class sSocket:
    def __init__(self,ip="127.0.0.1",port=50001):
        self.m_socket = None
        self.m_socket = socket(AF_INET, SOCK_DGRAM)
        self.ip=ip
        self.port=port
        self.m_socket.bind((ip, port))

    def Recv(self):
        strBuff = ''
        try:
            rs,ws,es = select([self.m_socket], [], [], 5)
            if len(rs) != 0 :
                strBuff, addr = self.m_socket.recvfrom(g_CSOCK_BUFFSIZE)
        except Exception, msg:
            logging.debug(msg)
            logging.debug(traceback.format_exc())
        return strBuff, len(strBuff)



class cSocket:
    def __init__(self,ip="127.0.0.1",port=50002):
        self.m_socket = None
        self.m_socket = socket(AF_INET, SOCK_DGRAM)
        self.ip=ip
        self.port=port

    def Send(self,msg):
        if msg:  
            self.m_socket.sendto(msg,(self.ip,self.port))  

