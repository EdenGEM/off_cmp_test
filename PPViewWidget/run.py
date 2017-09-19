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
import final

def main():

    parser = optparse.OptionParser()
    parser.add_option('-d', '--date', help = 'run date like 20150101')
    parser.add_option('-t', '--type', help = 'run type like s125')
    parser.add_option('-n', '--num',type="int",dest="num",default="20", help = 'run case number like 100')
    parser.add_option('-q', '--qid',type="string",dest="qid")
    parser.add_option('-x', '--cmp1', type="string",dest="cmp1",default="online",help='the first cmp_env or source_env')
    parser.add_option('-y', '--cmp2', type="string",dest="cmp2",default="test",help='the second cmp_env or dest_env')
    parser.add_option('-m', '--mail', type="string",dest="mail",help='mail to like caoxiaolan@mioji.com ')
    opt, args = parser.parse_args()
    print opt.date
    print opt.type
    print opt.num
    print opt.qid
    print opt.cmp1
    print opt.cmp2
    print opt.mail
    kQid=""
    kDate=""
    kType=""
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
        if opt.type=="s125" or opt.type=="s127" or  opt.type=="s128" or opt.type=="s130":
            kType=opt.type
        else:
            print "Error Formate type"
            return 
        try:
            kNum=opt.num
        except:
            print "Error Formate case number"
            return
        
    if opt.cmp1 =="online" or opt.cmp1=="test" or opt.cmp1=="test1" or opt.cmp1=="offline":
        kCmp1=opt.cmp1
    else:
        print "Error Format cmp1"
        return
    if opt.cmp2=="online" or opt.cmp2=="test" or opt.cmp2=="test1" or opt.cmp2=="offline":
        kCmp2=opt.cmp2
    else:
        print "Error Format cmp2"
        return 
    a=re.compile(r'(.+)@mioji.com')
    match_mail=a.search(opt.mail)
    print match_mail
    if match_mail:
        Mail=opt.mail
    else:
        print "MailBox Error"
        return 
#    if isinstance(kQid,str):
    Boss=final.RespCmp(kDate,kType,kNum,kQid,kCmp1,kCmp2,Mail)
    if kQid:
        print "in qid"
        Boss.LoadReqAndRespByQid()
        Boss.CmpInfoByQid()
#        LoadAndQuery.LoadReqAndRespByQid(kQid,kCmp1,kCmp2,Mail)
    else:
        print "in patch"
        Boss.LoadReqAndRespByPatch()
        Boss.CmpInfoByPatch()
#        LoadAndQuery.LoadReqAndRespByPatch(kDate,kType,kNum)
#        CmpInfo.CmpInfoByPatch(kDate,kType,kNum,kCmp1,kCmp2,Mail)


if __name__ == "__main__":
    main()


