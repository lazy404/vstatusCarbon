# coding: utf-8
# Copyright (C) 2007 Michał Grzędzicki
# $Id: log.py 132 2007-11-19 09:44:19Z root $

import config
import syslog

syslog.openlog('vstatusCarbon',0,syslog.LOG_DAEMON)

def LOGD(*args):
    if config.debug:
        syslog.syslog(syslog.LOG_DEBUG, " ".join(map(str,args)))

def LOG(*args):
    syslog.syslog(syslog.LOG_INFO, " ".join(map(str,args)))


def LOGW(*args):
    syslog.syslog(syslog.LOG_WARNING, " ".join(map(str,args)))


def LOGE(*args):
    syslog.syslog(syslog.LOG_ERR, " ".join(map(str,args)))

