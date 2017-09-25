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
    conn=MySQLdb.connect(host='10.10.107.246',user='reader',passwd='miaoji1109',db='logQuery_test',port=3306, charset="utf8")
    cur=conn.cursor()
    try:
        sqlstr="select qid,req_params from nginx_api_log_%s where req_type='p104' and log_type='13' group by qid having count(*)=1 order by rand() limit %d"%(kDate,kNum)
        print sqlstr
        cur.execute(sqlstr)
        conn.commit()
        rows=cur.fetchall()
        print"in select \n"
        sqlstr="select id from nginx_api_log_%s where req_type='p104' and log_type='14' and qid in("%kDate
        for i,row in enumerate(rows):
            qid=row[0]
            qid_dic[qid]=dict()
            qid_dic[qid]["qid"]=qid
            url = urllib2.unquote(row[1].decode('utf-8','replace').encode('gbk','replace'))
            print url
            qid_dic[qid]["orireq"]=url
            print "in list"
            print row[0]
            if i == len(rows) - 1:
                sqlstr+="%s"%row[0]
            else:
                sqlstr+="%s,"%row[0]
        sqlstr+=") order by field(qid,"
        for i,row in enumerate(rows):
            if i==0:
                sqlstr+=str(row[0])
            else:
                sqlstr+=","
                sqlstr+=str(row[0])
        sqlstr+=");"
        print sqlstr
        cur.execute(sqlstr)
        conn.commit()
        ids=cur.fetchall()
        sqlstr="select response from nginx_api_resp_%s where id in ("%kDate
        for i,row in enumerate(ids):
            if i == len(ids) - 1:
                sqlstr+="%s"%row[0]
            else:
                sqlstr+="%s,"%row[0]
        sqlstr+=") order by field(id,"
        for i,row in enumerate(ids):
            if i==0:
                sqlstr+=str(row[0])
            else:
                sqlstr+=","
                sqlstr+=str(row[0])
        sqlstr+=");"
        print sqlstr
        cur.execute(sqlstr)
        conn.commit()
        resps=cur.fetchall()
        for i,row in enumerate(resps):
            resp=row[0]
            qid_dic[rows[i][0]]["resp"]=resp
            print "GEMresp"
            print resp
#            log=json.loads(resp)
#            total=log["data"]["list"]["total"]
#            print"total=%s"%total
            pat_total = re.compile(r'{"data":{"list":.+,"total":([0-9]+)')
            match_total = pat_total.search(resp)
            print "match_total"
            print match_total
            if match_total:
                logtotal=match_total.group(1)
                print "logtotal=%s"%logtotal
                qid_dic[rows[i][0]]["total"]=logtotal
#            else:
#                qid_dic[rows[i][0]]["total"]="null"
                
        Parsereq()

        with io.open('./total','w') as fp:
            for qid,item in qid_dic.items():
                if "total" not in qid_dic[qid] or "off_total" not in qid_dic[qid]:
                    continue;
                if "off_resp" not in qid_dic[qid]:
                    print "do not product off_resp in %s"%qid
                    pop_item=qid_dic.pop(qid);
                    continue;
                if qid_dic[qid]["total"]==qid_dic[qid]["off_total"]:
                    continue;
                else:
                    fp.write(("qid=%s\n"%qid).decode('utf-8'))
#                    fp.write(("cqid=%s\n"%item["cqid"]).decode('utf-8'))
                    print "why in this position~"
                    fp.write(("oritotal=%s\n"%item["total"]).decode('utf-8'))
                    fp.write(("off_total=%s\n"%item["off_total"]).decode('utf-8'))
                    fp.write(("test_total=%s\n"%item["test_total"]).decode('utf-8'))
                    fp.write(("ori_req=%s\n"%item["orireq"]).decode('utf-8'))
                    fp.write(("oriresp=%s\n"%item["resp"]).decode('utf-8'))
                    fp.write(("off_resp=%s\n\n"%item["off_resp"]).decode('utf-8'))

        with io.open('./origin','w',encoding='utf-8') as f:
            for qid,item in qid_dic.items():
                if "total" not in qid_dic[qid] or "off_total" not in qid_dic[qid]:
                    continue;
                if "off_resp" not in qid_dic[qid]:
                    print "do not product off_resp in %s"%qid
                    pop_item=qid_dic.pop(qid);
                    continue;
                if qid_dic[qid]["total"]==qid_dic[qid]["off_total"]:
                    continue;
                else:
                    f.write(("%s\n\n"%item["resp"]).decode('utf-8'))
            
        with io.open('./new','w',encoding='utf-8') as h:
            for qid,item in qid_dic.items():
                if "total" not in qid_dic[qid] or "off_total" not in qid_dic[qid]:
                    continue;
                if "off_resp" not in qid_dic[qid]:
                    print "do not product off_resp in %s"%qid
                    pop_item=qid_dic.pop(qid);
                    continue;
                if qid_dic[qid]["total"]==qid_dic[qid]["off_total"]:
                    continue;
                else:
                    h.write(("%s\n\n"%item["off_resp"]).decode('utf-8'))
#                    fp.write(("off_resp=%s\n"%item["off_resp"]).decode('utf-8'))

#                fp.write(item["resp"])
#        with io.open('./req_param','w',encoding='utf-8') as f:
#            for qid,item in qid_dic.items():
#                f.write(item["req"])
        
        cur.close()
        conn.close()
    except (MySQLdb.Error) as e:
        print'Got error {!r}, errno is {}'.format(e, e.args[0])
def Parsereq():
    global qid_dic,off_resp
    print "in parser"
    for qid,item in qid_dic.items():
        if "qid" not in qid_dic[qid] or "orireq" not in qid_dic[qid]:
            pop_item=qid_dic.pop(qid);
            continue;
        cur_qid=int(round(time.time()*1000))
        print "offnew_qid: %s"%cur_qid
        qid_dic[qid]["cqid"]=cur_qid
        ziduan="qid="+str(cur_qid)
        originqid=r'qid=(\d+)'
        req=re.sub(originqid,ziduan,qid_dic[qid]["orireq"])


        print "newreq=%s"%req
        print  10 * "*"
        qid_dic[qid]["req"]=req
#            req="?lang="+str(orireq["lang"])+"&refer_id="+str(reqjson["refer_id"])+"&ccy="+str(reqjson["ccy"])+"&uid="+str(reqjson["uid"])+"&cur_id="+str(reqjson["cur_id"])+"&qid="+str(cur_qid)+"&ptid="+str(reqjson["ptid"])+"&query="+str(reqjson["query"])+"&next_id="+str(reqjson["next_id"])+"&type="+str(reqjson["type"])
        url1="http://10.10.135.140:91/?"+req
        
        try:
            resps=urllib2.urlopen(urllib2.Request(url1),timeout=10).read()
            print "offline_res="
            qid_dic[qid]["off_resp"]=resps
            print resps
#                tmp=json.loads(resps)
#                off_total=tmp["data"]["list"]["total"]
#                print "off_total=%s"%off_total
            pat_to=re.compile(r'{"data":{"list":.+,"total":([0-9]+)')
            match_to=pat_to.search(resps)
            print match_to
            if match_to:
                new_to=match_to.group(1)
                qid_dic[qid]["off_total"]=new_to
        except Exception:
            print "url1 request timeout"
            pass

        cur_qid=int(time.time()*1000)
        print "testnew_qid: %s"%cur_qid
        ziduan="qid="+str(cur_qid)
        originqid=r'qid=(\d+)'
        req=re.sub(originqid,ziduan,qid_dic[qid]["orireq"])
        url2="http://10.10.135.140:92/?"+req

        try:
            resps=urllib2.urlopen(urllib2.Request(url2),timeout=10).read()
            print "test_res="
            print resps
            pat_to=re.compile(r'{"data":{"list":.+,"total":([0-9]+)')
            match_to=pat_to.search(resps)
            print match_to
            if match_to:
                new_to=match_to.group(1)
                qid_dic[qid]["test_total"]=new_to
        except Exception:
            print "url2 request timeout"
            pass
    
kDate = '20170820'
def main():
    global kDate
    global kNum
    parser = optparse.OptionParser()
    parser.add_option('-d', '--date', help = 'run date like 20150101')
    parser.add_option('-n', '--num',type="int",dest="num",default="2", help = 'run case number like 100')
    opt, args = parser.parse_args()
    try:    
        run_day = datetime.datetime.fromtimestamp(time.mktime(time.strptime(opt.date, '%Y%m%d')))
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
    Report();

main()

