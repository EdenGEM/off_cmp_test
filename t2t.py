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
import requests
from DBHandle import DBHandle
reload(sys);
exec("sys.setdefaultencoding('utf-8')");

qid_dic=dict()
uid=0

def Report():
    global qid_dic
    print "global"
    conn=MySQLdb.connect(host='10.10.107.246',user='reader',passwd='miaoji1109',db='logQuery_online',port=3306, charset="utf8")
    cur=conn.cursor()
    try:
        sqlstr="select qid,req_params from nginx_api_log_%s where req_type='%s' and log_type='13' group by qid having count(*)=1 order by rand() limit %d"%(kDate,kType,kNum)
        print sqlstr
        cur.execute(sqlstr)
        conn.commit()
        rows=cur.fetchall()
        print"in select"
        sqlstr="select id from nginx_api_log_%s where req_type='%s' and log_type='14' and qid in("%(kDate,kType)
        for i,row in enumerate(rows):
            qid=row[0]
            qid_dic[qid]=dict()
            qid_dic[qid]["qid"]=qid
            qid_dic[qid]["req_type"]=kType
            print row[0]
            print "yuan_req:"
            qid_dic[qid]["ori_req"]=row[1]
            print row[1]
            url = urllib2.unquote(row[1].decode('utf-8','replace').encode('gbk','replace'))
<<<<<<< HEAD
=======
#            print "url=%s"%url
#            tmp=url.encode('utf-8')
#            print "tmp=%s"%tmp
>>>>>>> 0486a98415877aceb0d588d6832b9c9b3a40775a
            qid_dic[qid]["on_req"]=url
            print url
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
            print "GEMresp"
            if row[0]=="":
                pop_item=qid_dic.pop(rows[i][0])
                continue;
            resp=row[0]
            qid_dic[rows[i][0]]["on_resp"]=resp
            print resp
<<<<<<< HEAD
            try:
                tmp=json.loads(resp)
            except:
                print "pass this resp"
                pop_item=qid_dic.pop(qid)
                continue;

=======
            tmp=json.loads(resp)
>>>>>>> 0486a98415877aceb0d588d6832b9c9b3a40775a
            if "error" not in tmp:
                pop_item=qid_dic.pop(rows[i][0])
                continue;
            eid=tmp["error"]["error_id"]
            print "on_eid=%s"%eid
            qid_dic[rows[i][0]]["on_eid"]=eid
            '''
            pat_log = re.compile(r'{"data":.+,"error":{"error_id":([0-9]+)')
            match_log = pat_log.search(resp)
            print "match_log"
            print match_log
            if match_log:
                logerror_id=match_log.group(1)
                print "logerror_id=%s"%logerror_id
                qid_dic[rows[i][0]]["error_id"]=logerror_id
            '''    
        Parsereq()
        Store()
#        Cmpinfo()
        cur.close()
        conn.close()
    except (MySQLdb.Error) as e:
        print'Got error {!r}, errno is {}'.format(e, e.args[0])
def Parsereq():
    global qid_dic,new_resp
    print "in parser"
    for qid,item in qid_dic.items():
        if "qid" not in qid_dic[qid] or "on_req" not in qid_dic[qid] or "on_eid" not in qid_dic[qid]:
            pop_item=qid_dic.pop(qid);
            continue;
#        a=type(qid_dic[qid]["on_eid"])
#        print "type(eid)=%s"%a
        if qid_dic[qid]["on_eid"]!=0:
            pop_item=qid_dic.pop(qid)
            continue;

        cur_qid=int(round(time.time()*1000))
        qid_dic[qid]["test_qid"]=cur_qid
        print "qid=%s"%qid
        print "test_qid=%s"%cur_qid
        ziduan="qid="+str(cur_qid)
        originqid=r'qid=(\d+)'
        req=re.sub(originqid,ziduan,qid_dic[qid]["on_req"])
        tmp=r'query=(.+)&refer'
        pat_zi=re.compile(tmp)
        match_zi=pat_zi.search(req)
        print match_zi
        if match_zi:
            zi=match_zi.group(1)
            print "pquery=%s"%zi
            du=zi.replace('&',' ')
            print "du=%s"%du
            du="query="+du+"&refer"
            print "rdu=%s"%du
            req=re.sub(tmp,du,req)
        print "test_req="
        print req
        print  10 * "*"
        qid_dic[qid]["test_req"]=req
        url1="http://10.10.135.140:92/?"+req
#        print "url1=%s"%url1

        try:
#            resps=urllib2.urlopen(urllib2.Request(url1),timeout=10).read()
            r=requests.get(url1)
            resps=r.text
            r.raise_for_status()
            print "test_res="
            qid_dic[qid]["test_resp"]=resps
            print resps
            tmp=json.loads(resps)
            new_eid=tmp["error"]["error_id"]
            print "test_eid=%s"%new_eid
            qid_dic[qid]["test_eid"]=new_eid
        except (requests.RequestException) as e:
            print "requesterror:"
            print e
            qid_dic[qid]["test_resp"]=""
            qid_dic[qid]["test_eid"]=""

        except Exception:
            print "url1 request timeout~"
            qid_dic[qid]["test_resp"]=""
            qid_dic[qid]["test_eid"]=""
#            pass
        cur_qid=int(round(time.time()*1000))
        qid_dic[qid]["test1_qid"]=cur_qid
        print "test1_qid=%s"%cur_qid
        ziduan="qid="+str(cur_qid)
        originqid=r'qid=(\d+)'
        req=re.sub(originqid,ziduan,qid_dic[qid]["on_req"])
        tmp=r'query=(.+)&refer'
        pat_zi=re.compile(tmp)
        match_zi=pat_zi.search(req)
        print match_zi
        if match_zi:
            zi=match_zi.group(1)
            print "pquery=%s"%zi
            du=zi.replace('&',' ')
            print "du=%s"%du
            du="query="+du+"&refer"
            print "rdu=%s"%du
            req=re.sub(tmp,du,req)

        print "test1_req=%s"%req
        print  10 * "*"
        qid_dic[qid]["test1_req"]=req
        url2="http://10.10.135.140:9292/?"+req
        try:
#            resps=urllib2.urlopen(urllib2.Request(url2),timeout=10).read()
            r=requests.get(url2)
            resps=r.text
            r.raise_for_status()
            print "test1_res="
            qid_dic[qid]["test1_resp"]=resps
            print resps
            tmp=json.loads(resps)
            new_eid=tmp["error"]["error_id"]
            print "test1_eid=%s"%new_eid
            qid_dic[qid]["test1_eid"]=new_eid
        except (requests.RequestException) as e:
            print "requesterror:"
            print e
            qid_dic[qid]["test1_resp"]=""
            qid_dic[qid]["test1_eid"]=""
        except Exception:
            print "url2 request timeout~"
            qid_dic[qid]["test1_resp"]=""
            qid_dic[qid]["test1_eid"]=""
#            pass
        cur_qid=int(round(time.time()*1000))
        qid_dic[qid]["off_qid"]=cur_qid
        print "off_qid=%s"%cur_qid
        ziduan="qid="+str(cur_qid)
        originqid=r'qid=(\d+)'
        req=re.sub(originqid,ziduan,qid_dic[qid]["on_req"])
        tmp=r'query=(.+)&refer'
        pat_zi=re.compile(tmp)
        match_zi=pat_zi.search(req)
        print match_zi
        if match_zi:
            zi=match_zi.group(1)
            print "pquery=%s"%zi
            du=zi.replace('&',' ')
            print "du=%s"%du
            du="query="+du+"&refer"
            print "rdu=%s"%du
            req=re.sub(tmp,du,req)
        print "off_req=%s"%req
        print  10 * "*"
        qid_dic[qid]["off_req"]=req
        url3="http://10.10.135.140:91/?"+req
        print "url3=%s"%url3

        try:
#            resps=urllib2.urlopen(urllib2.Request(url1),timeout=10).read()
            r=requests.get(url3)
            resps=r.text
            r.raise_for_status()
            print "off_res="
            qid_dic[qid]["off_resp"]=resps
            print resps
            tmp=json.loads(resps)
            new_eid=tmp["error"]["error_id"]
            print "off_eid=%s"%new_eid
            qid_dic[qid]["off_eid"]=new_eid
        except (requests.RequestException) as e:
            print "requesterror:"
            print e
            qid_dic[qid]["off_resp"]=""
            qid_dic[qid]["off_eid"]=""

        except Exception:
            print "url3 request timeout~"
            qid_dic[qid]["off_resp"]=""
            qid_dic[qid]["off_eid"]=""
#            pass

def Store():
    global kType
    global kDate
    conn=MySQLdb.connect(host='127.0.0.1',user='root',db='test',port=3306, charset="utf8")
    cur=conn.cursor()
    for qid,item in qid_dic.items():
        print "in store"
        try:
#            sqlstr =  cmd + GetSql(item)
            print "big big fire"
<<<<<<< HEAD
=======
#            on_resp=item["on_resp"].replace("'","\\\'")
#            test_resp=item["test_resp"].replace("'","\\\'")
#            test1_resp=item["test1_resp"].replace("'","\\\'")
#            off_resp=item["off_resp"].replace("'","\\\'")
#            sqlstr="REPLACE into test.all_about(date,req_type,on_qid,on_req,on_resp,on_eid,test_qid,test_resp,test_eid,test1_qid,test1_resp,test1_eid,off_qid,off_resp,off_eid) values('%s','%s','%s','%s','%s',%d,'%s','%s',%d,'%s','%s',%d,'%s','%s',%d)"%(kDate,kType,item["qid"],item["ori_req"],on_resp,item["on_eid"],item["test_qid"],test_resp,item["test_eid"],item["test1_qid"],test1_resp,item["test1_eid"],item["off_qid"],off_resp,item["off_eid"])
            
#            sqlstr="replace into test.all_about(date,req_type,on_qid,on_req,on_resp,on_eid,test_qid,test_resp,test_eid,test1_qid,test1_resp,test1_eid,off_qid,off_resp,off_eid) values(%s,%s,%s,%s,%s,%d,%s,%s,%d,%s,%s,%d,%s,%s,%d)"%(kDate,kType,item["qid"],item["on_req"],item["on_resp"],item["on_eid"],item["test_qid"],item["test_resp"],item["test_eid"],item["test1_qid"],item["test1_resp"],item["test1_eid"],item["off_qid"],item["off_resp"],item["off_eid"])
>>>>>>> 0486a98415877aceb0d588d6832b9c9b3a40775a
            sqlstr="replace into test.all_about values(%(date)s,%(req_type)s,%(online_qid)s,%(online_req)s,%(online_resp)s,%(online_eid)s,%(test_qid)s,%(test_resp)s,%(test_eid)s,%(test1_qid)s,%(test1_resp)s,%(test1_eid)s,%(offline_qid)s,%(offline_resp)s,%(offline_eid)s)"

            T={"date":kDate,"req_type":kType,"online_qid":item["qid"],"online_req":item["on_req"],"online_resp":item["on_resp"],"online_eid":item["on_eid"],"test_qid":item["test_qid"],"test_resp":item["test_resp"],"test_eid":item["test_eid"],"test1_qid":item["test1_qid"],"test1_resp":item["test1_resp"],"test1_eid":item["test1_eid"],"offline_qid":item["off_qid"],"offline_resp":item["off_resp"],"offline_eid":item["off_eid"]}
            
            print sqlstr
            cur.execute(sqlstr,T)
            conn.commit()
#            onlinedb.do(sqlstr)
            print "after store"
        except (MySQLdb.Error) as e:
            print'Got error {!r}, errno is {}'.format(e, e.args[0])
    cur.close()
    conn.close()

def product_cmp(testresp,offresp):
    result="all is the same"
    if "product" not in testresp["data"] and "product" not in offresp["data"]:
#        result="nothing to compare, there are no product"
        return result
    elif "product" not in testresp["data"] or "product" not in offresp["data"]:
        result="all is different, mark in one of them don't have product"
        return result
    test_product=testresp["data"]["product"]
    off_product=offresp["data"]["product"]
    if len(test_product)!=len(off_product):
        result="the length of product is not the same"
        return result
    print "befor the key of product cmp"
    for key in test_product:
        if test_product[key] is None and off_product[key] is None:
            continue;
        elif test_product[key] is None or off_product[key] is None:
            result="one of the %s of product is None"%key
            return result
        elif test_product[key] != off_product[key]:
            if len(test_product[key])!=len(off_product[key]):
                result="the length of %s of product is not the same"%key
                return result
            else:
                kk=1
                for keyi in test_product[key]:
                    if keyi not in  off_product[key] :
                        result="the %d of %s of product is not the same"%(kk,key)
                        return result
                    else:
                        kk+=1
        else:
            continue
    return "all is the same"

def Cmpinfo():
    with io.open('./off_error','w') as fp:
        for qid,item in qid_dic.items():
            print "on_resp="
            print qid_dic[qid]["on_resp"]
            if "test_resp" not in qid_dic[qid] or "test1_resp" not in qid_dic[qid]:
                print "do not product new_resp in %s"%qid
                pop_item=qid_dic.pop(qid);
                continue;
            if "test_eid" not in qid_dic[qid] or "test1_eid" not in qid_dic[qid]:
                print "no eid"
                continue;
            elif qid_dic[qid]["test_eid"]==qid_dic[qid]["test1_eid"]:
                if "data" not in qid_dic[qid]["test_resp"] and "data" not in qid_dic[qid]["test1_resp"]:
                    result="all is the same"
                elif "data" not in qid_dic[qid]["test_resp"] or "data" not in qid_dic[qid]["test1_resp"]:
                    result="all is different, one of them do not have data"
                elif kType=='s125':
                    print "before s125cmp"
                    result=s125_Cmpinfo(qid_dic[qid]["test_resp"],qid_dic[qid]["test1_resp"])
                elif kType=='s127':
                    print "before s127cmp"
                    result=s127_Cmpinfo(qid_dic[qid]["test_resp"],qid_dic[qid]["test1_resp"])
                elif kType=='s128' or kType=='s130':
                    result=s128_s130_Cmpinfo(qid_dic[qid]["test_resp"],qid_dic[qid]["test1_resp"])

                if result!="all is the same":
                    qid_dic[qid]["difference"]=result
                print "result=%s"%result

            else:
                fp.write(("qid=%s\n"%qid).decode('utf-8'))
#                    fp.write(("cqid=%s\n"%item["cqid"]).decode('utf-8'))
                print "why in this position~"
#                fp.write(("error_id=%s\n"%item["error_id"]).decode('utf-8'))
                fp.write(("on_req=%s\n"%item["on_req"]).decode('utf-8'))
                fp.write(("test_eid=%s\n"%item["test_eid"]).decode('utf-8'))
                fp.write(("test1_eid=%s\n"%item["test1_eid"]).decode('utf-8'))

    with io.open('./difference','w') as fp:
        for qid,item in qid_dic.items():
            if "difference" not in qid_dic[qid]:
                continue;
            else:
                fp.write(("qid=%s\n"%qid).decode('utf-8'))
                fp.write(("test_qid=%s\n"%qid_dic[qid]["test_qid"]).decode('utf-8'))
                fp.write(("test1_qid=%s\n"%qid_dic[qid]["test1_qid"]).decode('utf-8'))
                fp.write(("the difference is: %s\n"%qid_dic[qid]["difference"]).decode('utf-8'))
    with io.open('./test_resp','w',encoding='utf-8') as f:
        for qid,item in qid_dic.items():
            if "difference" not in qid_dic[qid]:
                continue;
            else:
                f.write(("%s\n"%item["test_resp"]).decode('utf-8'))
    with io.open('./test1_resp','w',encoding='utf-8') as f:
        for qid,item in qid_dic.items():
            if "difference" not in qid_dic[qid]:
                continue;
            else:
                f.write(("%s\n"%item["test1_resp"]).decode('utf-8'))


def s127_Cmpinfo(testresp,offresp):
    #data->list->view->summary->days->pois
    print "testresp=%s"%testresp
    print "offresp=%s"%offresp
    testresp=json.loads(testresp);
    offresp=json.loads(offresp)
    print "loadstestresp=%s"%testresp
    print "in s127cmp"
    print "before product cmp"
    result=product_cmp(testresp,offresp)
    if result!="all is the same":
        return result

    print "before list cmp"
    if "list" not in testresp["data"] and "list" not in offresp["data"]:
#        result="nothing to compare, there are no list"
        return result
    elif "list" not in testresp["data"] or "list" not in offresp["data"]:
        result="all is different, mark in one of them don't have list"
        return result
    if len(testresp["data"]["list"])!=len(offresp["data"]["list"]):
        result="the length of list is not the same"
        return result
    i=0
    while i<len(testresp["data"]["list"]):
        test_view=testresp["data"]["list"][i]["view"]
        off_view=offresp["data"]["list"][i]["view"]
#        print test_view
        if test_view is None and off_view is None:
            i+=1
            continue;
        elif test_view is None and off_view!=None:
            print "test_view is null"
            result="the view of %d list is not the same"%(i+1)
            return result
        elif test_view!=None and off_view is None:
            result="the view of %d list is not the same"%(i+1)
            return result

        else:
            test_days=test_view["summary"]["days"]
            off_days=off_view["summary"]["days"]
            if len(test_days)!=len(off_days):
                result="the length of days is not the same"
                return result
            else:
                j=0
                while j<len(test_days):
                    test_pois=test_days[j]["pois"]
                    off_pois=off_days[j]["pois"]
                    if len(test_pois)!=len(off_pois):
                        result="the length of pois of %d day of %d list is not the same"%(j+1,i+1)
                        return result
                    else:
                        k=0
                        while k<len(test_pois):
                            test_id=test_pois[k]["id"]
                            off_id=off_pois[k]["id"]
                            test_pdur=test_pois[k]["pdur"]
                            off_pdur=off_pois[k]["pdur"]
                            if test_id != off_id:
                                result="the id of %d pois of %d day of %d list is not the same"%(k+1,j+1,i+1)
                                return result
                            elif test_pdur != off_pdur:
                                result+=", the pdur of %d pois of %d day of %d list is not the same"%(k+1,j+1,i+1)
                                k+=1
                                continue
                            k+=1
                    j+=1
        i+=1
    return result
def s125_Cmpinfo(testresp,offresp):
    #不一定有view,//data->view->summary->days->pois
    print "testresp=%s"%testresp
    print "offresp=%s"%offresp
    testresp=json.loads(testresp);
    offresp=json.loads(offresp)
    print "in s125cmp"
    print "before product cmp"
    result=product_cmp(testresp,offresp)
    if result!="all is the same":
        return result

    if "view" not in testresp["data"] and "view" not in offresp["data"]:
#        result="nothing to compare, there are no view"
        return result
    elif "view" not in testresp["data"] or "view" not in offresp["data"]:
        result="all is different, mark in one of them don't have view"
        return result
    else:
        print "s125"
        test_view=testresp["data"]["view"]
        off_view=offresp["data"]["view"]
        test_days=test_view["summary"]["days"]
        off_days=off_view["summary"]["days"]
        if len(test_days)!=len(off_days):
            result="the length of days is not the same"
            return result
        else:
            j=0
            while j<len(test_days):
                test_pois=test_days[j]["pois"]
                off_pois=off_days[j]["pois"]
                if len(test_pois)!=len(off_pois):
                    result="the length of pois of %d day is not the same"%(j+1)
                    return result
                else:
                    k=0
                    while k<len(test_pois):
                        test_id=test_pois[k]["id"]
                        off_id=off_pois[k]["id"]
                        test_pdur=test_pois[k]["pdur"]
                        off_pdur=off_pois[k]["pdur"]
                        if test_id != off_id:
                            result="the id of %d pois of %d day is not the same"%(k+1,j+1)
                            return result
                        elif test_pdur != off_pdur:
                            result+=", the pdur of %d pois of %d day is not the same"%(k+1,j+1)
                            k+=1
                            continue
                        k+=1
                j+=1

    return result
def s128_s130_Cmpinfo(testresp,offresp):
    #不一定有city,//data->city->view->summary->days->pois
    print "testresp=%s"%testresp
    print "offresp=%s"%offresp
    testresp=json.loads(testresp);
    offresp=json.loads(offresp)
    if kType=='s128':
        print "in s128cmp"
    else:
        print "in s130cmp"
    print "before product cmp"
    result=product_cmp(testresp,offresp)
    if result!="all is the same":
        return result

    if "city" not in testresp["data"] and "city" not in offresp["data"]:
#        result="nothing to compare, there are no city"
        return result
    elif "city" not in testresp["data"] or "city" not in offresp["data"]:
        result="all is different, mark in one of them don't have city"
        return result
    else:
        if kType=='s128':
            print "s128_viewcmp"
        if kType=='s130':
            print "s130_viewcmp"
        if "view" not in testresp["data"]["city"] or testresp["data"]["city"]["view"] is None and ("view" not in offresp["data"]["city"] or offresp["data"]["city"]["view"] is None ):
#            result="nothing to compare, there are no view"
            return result
        elif "view" not in testresp["data"]["city"] or "view" not in offresp["data"]["city"] or testresp["data"]["city"]["view"] is None or offresp["data"]["city"]["view"] is None :
            result="all is different, mark in one of them don't have view"
            return result
        test_view=testresp["data"]["city"]["view"]
        off_view=offresp["data"]["city"]["view"]
        test_days=test_view["summary"]["days"]
        off_days=off_view["summary"]["days"]
        if len(test_days)!=len(off_days):
            result="the length of days is not the same"
            return result
        else:
            j=0
            while j<len(test_days):
                test_pois=test_days[j]["pois"]
                off_pois=off_days[j]["pois"]
                if len(test_pois)!=len(off_pois):
                    result="the length of pois of %d day is not the same"%(j+1)
                    return result
                else:
                    k=0
                    while k<len(test_pois):
                        test_id=test_pois[k]["id"]
                        off_id=off_pois[k]["id"]
                        test_pdur=test_pois[k]["pdur"]
                        off_pdur=off_pois[k]["pdur"]
                        if test_id != off_id:
                            result="the id of %d pois of %d day is not the same"%(k+1,j+1)
                            return result
                        elif test_pdur != off_pdur:
                            result+=", the pdur of %d pois of %d day is not the same"%(k+1,j+1)
                            k+=1
                            continue;
                        k+=1
                j+=1

    return result
    
kDate = '20170820'
kType='s125'
kNum=20
def main():
    global kDate
    global kType
    global kNum
    parser = optparse.OptionParser()
    parser.add_option('-d', '--date', help = 'run date like 20150101')
    parser.add_option('-t', '--type', help = 'run type like s125')
    parser.add_option('-n', '--num',type="int",dest="num",default="2", help = 'run case number like 100')
    opt, args = parser.parse_args()
    print opt.date
    print opt.type
    print opt.num
    try:
        kNum=opt.num
    except:
        print "Error Formate case number"
        return
    try:    
        run_day = datetime.datetime.fromtimestamp(time.mktime(time.strptime(opt.date, '%Y%m%d')))
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
    Report();

main()

