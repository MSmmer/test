
#!/usr/bin/env python
#coding:utf-8


'''
add by huanglingzhi
'''

import sys
import json
import time
from hashlib  import md5
from globallogdefine import *
from txsocket import *
from log import debug,info,warn,error

class Msg_Process:
    def __init__(self):
        self.m_recv_count = 0
        self.m_recv_warn_count = 0
        self.m_socket = sSocket(g_SOCKET_IP,g_SOCKET_PORT_MSG_PROCESS)


    def DealMessage(self,result):
        body={}


    def ConstructWarnLog(self,result):
        body={}
        body['module']=g_MODULE_I
        return body


    def Run(self):
        while True:
            sRecvbuff, sRecvlen= self.m_socket.Recv()
            if sRecvlen==0:
                time.sleep(0.05)
                continue
            self.m_recv_count = self.m_recv_count+1
            self.DealMessage(sRecvbuff)


if __name__ == '__main__':
    obj = Msg_Process()
    obj.Run()

