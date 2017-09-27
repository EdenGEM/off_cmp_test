#!/usr/bin/python
#coding=utf-8

import io
import os
import re
import sys
import optparse
import time
import datetime
import MySQLdb
import CmpResp

def main():
    fresh=0
    parser = optparse.OptionParser()
    parser.add_option('-d', '--date', help = 'run date like 20150101')
    parser.add_option('-t', '--type', help = 'run type like s125')
    parser.add_option('-n', '--num',type="int",dest="num",default="20", help = 'run case number like 100')
    parser.add_option('-q', '--qid',type="string",dest="qid")
    parser.add_option('-e', '--env', type="string",dest="env",help='the cmp_env run like test/offline or offline')
    parser.add_option('-m', '--mail', type="string",dest="mail",help='mail to like caoxiaolan@mioji.com ')
    opt, args = parser.parse_args()
    print "len of argv=%d"%len(sys.argv)
    print opt.date
    print opt.type
    print opt.num
    print opt.qid
    print opt.env
    print opt.mail
    kQid=""
    kDate=""
#    kType=""
    kNum=""
    if opt.qid:
        print "before qid"
        if len(opt.qid)!=13:
            print "Error Formate qid"
            return 
        else:
            kQid=opt.qid
            print kQid
    else:
        print "before patch"
        try:    
            run_day = datetime.datetime.fromtimestamp(time.mktime(time.strptime(opt.date, '%Y%m%d')))
            print run_day
            date_str = run_day.strftime('%Y%m%d')
            kDate = date_str;
        except:
            print "Error Format date"
            return
        try:
            kNum=opt.num
        except:
            print "Error Formate case number"
            return
    if opt.type=="s125" or opt.type=="s127" or  opt.type=="s128" or opt.type=="s130":
        kType=opt.type
    else:
        print "Error Formate type"
        return 
    a=opt.env.split('/')
    if len(a)==2:
        kCmp1=a[0]
        kCmp2=a[1]
        fresh=1
    else:
        kCmp1="test"
        kCmp2=a[0]
    if kCmp1 not in ("test","test1","offline"):
        print "Error Format cmp1_env"
        return 
    if kCmp2 not in ("test","test1","offline"):
        print "Error Format cmp2_env"
        return
    m=re.compile(r'(.+)@mioji.com')
    match_mail=m.search(opt.mail)
    print match_mail
    if match_mail:
        Mail=opt.mail
    else:
        print "MailBox Error"
        return 
    print "fresh=%d"%fresh
    Boss=CmpResp.RespCmp(kDate,kType,kNum,kQid,kCmp1,kCmp2,Mail,fresh)
    if kQid:
        print "in qid"
        Boss.LoadReqAndRespByQid()
        Boss.CmpInfoByQid()
    else:
        print "in patch"
        Boss.LoadReqAndRespByPatch()
        Boss.CmpInfoByPatch()


if __name__ == "__main__":
    main()


