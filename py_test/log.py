#!/usr/bin/python
#-*-coding:utf-8-*-
'''
use: from log import info,debug,error
     info("msg....",module='OTHER')
result:
     /var/log/ck/filename
'''
import logging
import logging.handlers
import sys
import os
import re
import time
import datetime
import json
from system_ctl.public_path import VAR_LOG_PATH
#from xml.etree import ElementTree

reload(sys)
sys.setdefaultencoding('utf8')
__logging_initialized = False
LOGGER_JSON="/test/config/test_logger.json"
CriticalLevel=0
ErrorLevel=1
WarnLevel=2
InfoLevel=3
DebugLevel=4

class __SrcFile(object):
    def __init__(self, exclude_files):
        self.files = set()
        for exclude_file in exclude_files:
            if hasattr(exclude_file , 'files') and isinstance(exclude_file.files,set) :
                self.files |= exclude_file.files
            elif isinstance(exclude_file, str):
                self.files |= set([exclude_file])
            else:
                raise TypeError, "exclude_files must be list of str/unicode or __SrcFile, %s " % exclude_files
    def __eq__(self, other):
        return other in self.files

def __fixname(filename):
    if filename.lower().endswith(".pyc") or filename.lower().endswith(".pyo"):
        filename = filename[:-4] + ".py"
    return os.path.normcase(filename)


def get_logfile_path_bak():
    return VAR_LOG_PATH+"/test/test_python.log"
def get_logfile_path():
    from system_ctl.public_path import VAR_LOG_PATH
    log_path = os.path.normpath(sys.argv[0] + ".log").replace("../", "++_")
    while log_path[0] == "/":
        log_path = log_path[1:]
    if log_path == ".log":
        log_path = "python.log"
    log_path = os.path.join(VAR_LOG_PATH, log_path)
    return log_path

class LoggerConfigManager:
    def __init__(self):
        try:
            #such as,self.m_modulelevel={'LOG_CK_DAEMON':[Fasle,1],}
            self.m_modulelevel={}
            self.m_enable= False
            self.m_logsize= 0
            self.ParseLogJson()
        except Exception,e:
            print e
    def ParseLogJson(self):
        try:
            f=open(LOGGER_JSON).read()
            LogConfig=json.loads(f)
            self.m_enable=LogConfig['logkey']['enabled']
            self.m_logsize=int(LogConfig['logfile']['size'])
            modulelist=LogConfig['modules']
            for module in modulelist:
                self.m_modulelevel[module['name']]=[bool(module['enabled']),int(module['level'])]
        except Exception,e:
            self.m_modulelevel={}
            print e
M_LoggerConfigManager=LoggerConfigManager()
def init_logger():
    global __logging_initialized
    global M_LoggerConfigManager
    if  __logging_initialized:
        return False
    log_file_filter  = ".*"
    pat = re.compile(log_file_filter)
    if not pat.match(sys.argv[0]):
        return
    log_file_path = get_logfile_path()
    dir_name = os.path.dirname(log_file_path)
    if not os.path.exists(dir_name):
       os.system("mkdir -p %s" % dir_name)
       os.system("chmod 777 %s >/dev/null 2>&1" % dir_name)

    filehandler = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=M_LoggerConfigManager.m_logsize, backupCount=1)
    filehandler.setLevel(logging.DEBUG)
    logging.getLogger('').setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(process)d:%(filename)s:%(lineno)d:%(asctime)s-%(levelname)s >> %(message)s')
    filehandler.setFormatter(formatter)
    logging.getLogger('').addHandler(filehandler)
    logging._srcfile = __SrcFile([logging._srcfile, __fixname(__file__)])
    __logging_initialized = True
init_logger()

def enableStdoutLog():
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-12s:%(lineno)d %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)



def setLevel(level):
    logging.getLogger('').setLevel(level)



def debug(msg,module='OTHER',stdout=False):
    global M_LoggerConfigManager
    if stdout:
        print(msg)
    if module not in M_LoggerConfigManager.m_modulelevel or (not M_LoggerConfigManager.m_enable) or (not M_LoggerConfigManager.m_modulelevel[module][0]):
        return
    if __logging_initialized and M_LoggerConfigManager.m_modulelevel[module][1]>=DebugLevel:
        logging.debug(msg)

def info(msg,module='OTHER',stdout=False):
    global M_LoggerConfigManager
    if stdout:
        print(msg)
    if module not in M_LoggerConfigManager.m_modulelevel or (not M_LoggerConfigManager.m_enable) or (not M_LoggerConfigManager.m_modulelevel[module][0]):
        return
    if __logging_initialized and M_LoggerConfigManager.m_modulelevel[module][1]>=InfoLevel:
        logging.info(msg)
def warn(msg,module='OTHER',stdout=False):
    global M_LoggerConfigManager
    if stdout:
        print(msg)
    if module not in M_LoggerConfigManager.m_modulelevel or (not M_LoggerConfigManager.m_enable) or (not M_LoggerConfigManager.m_modulelevel[module][0]):
        return
    if __logging_initialized and M_LoggerConfigManager.m_modulelevel[module][1]>=WarnLevel:
        logging.warn(msg)

def error(msg,module='OTHER',stdout=False):
    global M_LoggerConfigManager
    if stdout:
        print(msg)
    if module not in M_LoggerConfigManager.m_modulelevel or (not M_LoggerConfigManager.m_enable) or (not M_LoggerConfigManager.m_modulelevel[module][0]):
        return
    if __logging_initialized and M_LoggerConfigManager.m_modulelevel[module][1]>=ErrorLevel:
        logging.error(msg)

def fatal(msg,module='OTHER',stdout=False):
    global M_LoggerConfigManager
    if stdout:
        print(msg)
    if module not in M_LoggerConfigManager.m_modulelevel or (not M_LoggerConfigManager.m_enable) or (not M_LoggerConfigManager.m_modulelevel[module][0]):
        return
    if __logging_initialized and M_LoggerConfigManager.m_modulelevel[module][1]>=CriticalLevel:
        logging.critical(msg)

def empty_log_file():
    log_file = get_logfile_path()
    try:
        f = open(log_file, 'w')
        f.close()
    except Exception:
        pass
if __name__=="__main__":
    pass

