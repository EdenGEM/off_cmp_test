#!/usr/bin/env python
#coding=utf-8

import time
import datetime
import os
import os.path
import json
import MySQLdb
import re
import sys
import optparse
import io
import urllib2
reload(sys);
exec("sys.setdefaultencoding('utf-8')");

qid_dic=dict()

def Report():
    global qid_dic
    print "global"
    dbb="logQuery_%s"%kEnv
    conn=MySQLdb.connect(host='10.10.107.246',user='reader',passwd='miaoji1109',db=dbb,port=3306, charset="utf8")
    print dbb
    cur=conn.cursor()
    try:
        sqlstr="select req_params from nginx_api_log_%s where qid=%s and log_type='13' and req_type in('s125','s127','s128','s129' ,'s130' ,'p101' ,'p104' ,'p105','b116');"%(kDate,kQid)
        print sqlstr
        cur.execute(sqlstr)
        conn.commit()
        row=cur.fetchone()
        qid_dic[kQid]=dict()
        qid_dic[kQid]["req"]=row
        print "row=%s"%row
        print"in select \n"
        sqlstr="select id from nginx_api_log_%s where qid=%s and log_type='14' and req_type in('s125' ,'s127','s128','s129','s130' ,'p101','p104','p105' ,'b116');"%(kDate,kQid)
        print sqlstr
        cur.execute(sqlstr)
        conn.commit()
        ids=cur.fetchone()
        print "ids=%s"%ids
        sqlstr="select response from nginx_api_resp_%s where id=%s;"%(kDate,ids[0])
        print sqlstr
        cur.execute(sqlstr)
        conn.commit()
        resp=cur.fetchone()
        qid_dic[kQid]["resp"]=resp
    except (MySQLdb.Error) as e:
        print'Got error {!r}, errno is {}'.format(e, e.args[0])
    cur.close()
    conn.close()

    conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='',db='test',port=3306, charset="utf8")
    cur=conn.cursor()
    try:
        sqlstr="replace into error_qid values(%(env)s,%(date)s,%(qid)s,%(req)s,%(resp)s)"
        T={"env":kEnv,"date":kDate,"qid":kQid,"req":qid_dic[kQid]["req"],"resp":qid_dic[kQid]["resp"]}
        cur.execute(sqlstr,T)
        conn.commit()
    except (MySQLdb.Error) as e:
        print 'Got error {!r},errno is{}'.format(e,e.args[0])

    cur.close()
    conn.close()


kQid=1504503138335
kEnv="online"
def main():
    global kDate
    global kQid
    global kEnv
    parser = optparse.OptionParser()
    parser.add_option('-q', '--qid', help = 'run qid like 1504490041011')
    parser.add_option('-e', '--env', type="string",default="online",help = 'run env like online')
    opt, args = parser.parse_args()
    tt=int(opt.qid)
    kDate=time.strftime("%Y%m%d",time.localtime(tt/1000))
    print kDate
    if opt.env=="online" or opt.env=="offline" or opt.env=="test" or opt.env=="test1":
        kEnv=opt.env
    else:
        print "Error Format env"
        return 
    if len(opt.qid)!=13:
        print "Error Format qid"
        return
    else:
        kQid=opt.qid
    Report();

main()

