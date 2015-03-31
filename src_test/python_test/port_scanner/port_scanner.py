# Readme:        PortScan
# Purpose:
#
# Author:      xxh
#
# Created:     05-12-2011
# Copyright:   (c) xxh 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import socket

def main_1():
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(1000)
   # ip=input('input:(default:127.0.0.1)')
   # if ip=='':
   #     ip='127.0.0.1'
   # s=input('dport:(default:80)')
   # if s=='':
   #     startport=80
   # else:
   #     startport=int(s)

   # s=input('endport:(default:80)')
   # if s=='':
   #     endport=80
   # else:
   #     endport=int(s)
    ip = '127.0.0.1'
    for port in range(440,446):
        print('attempting %d' % port)
        try:
            sk.connect((ip,port))
            print('Server %s port %d OK!' % (ip,port))
        except Exception:
            print('Server %s port %d is not connected!' % (ip,port))
    sk.close()

address='127.0.0.1'
def main():
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    ports = [23, 135, 443, 2321, 1352, 445, 2322, 135, 445, ]
    stop = True
    tag = len(ports)-1
    tag = ports[len(ports)-1]
    while stop:
      for port in ports:
        try:
            s.connect((address, port))
            print '%d is connected!!!!!!!' % port
            s.close()
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
        except Exception,e:
            print '%d is error:%s' % (port, e)
            s.close()
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
        if port == tag:
            stop = False
    s.close()

if __name__ == '__main__':
    main()
