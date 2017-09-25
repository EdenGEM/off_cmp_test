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
import io
import urllib2
import optparse
from DBHandle import DBHandle

reload(sys);
exec("sys.setdefaultencoding('utf-8')");
qid_dic=dict()

def Fetch():
    global gid_dic
    conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='',db='test',port=3306, charset="utf8")
    cur=conn.cursor()
    try:
        sqlstr="select online_qid,online_req,%s_qid,%s_resp,%s_eid,%s_qid,%s_resp,%s_eid from test.all_about where date=%s and req_type='%s' group by online_qid order by rand() limit %d;"%(kCmp1,kCmp1,kCmp1,kCmp2,kCmp2,kCmp2,kDate,kType,kNum)
        print sqlstr
        cur.execute(sqlstr)
        conn.commit()
        rows=cur.fetchall()
        for row in rows:
            qid=row[0]
            qid_dic[qid]=dict()
            qid_dic[qid]["qid"]=qid
            print "qid=%s"%qid
            qid_dic[qid]["on_req"]=row[1]
            qid_dic[qid]["cmp1_qid"]=row[2]
            print "cmp1_resp=%s"%row[3]
            qid_dic[qid]["cmp1_resp"]=row[3]
            qid_dic[qid]["cmp1_eid"]=row[4]
            qid_dic[qid]["cmp2_qid"]=row[5]
            print "cmp2_resp=%s"%row[6]
            qid_dic[qid]["cmp2_resp"]=row[6]
            qid_dic[qid]["cmp2_eid"]=row[7]
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print >> sys.stderr, "Mysql Error %d: %s" % (e.args[0], e.args[1])

def Cmpinfo():
    global qid_dic
    with io.open('./diff_error','w') as fp:
        for qid,item in qid_dic.items():
            print "qid=%s"%qid
            print "on_req=%s"%qid_dic[qid]["on_req"]
#            print qid_dic[qid]["on_req"]
            if qid_dic[qid]["cmp1_resp"]=="" and qid_dic[qid]["cmp2_resp"]=="":
                pop_item=qid_dic.pop(qid)
                continue;
            elif qid_dic[qid]["cmp1_resp"]=="":
                result="%s no resp"%kCmp1
<<<<<<< HEAD
                qid_dic[qid]["difference"]=result
                continue;
            elif qid_dic[qid]["cmp2_resp"]=="":
                result="%s no resp"%kCmp2
                qid_dic[qid]["difference"]=result
                continue;
=======
                return result
            elif qid_dic[qid]["cmp2_resp"]=="":
                result="%s no resp"%kCmp2
                return result
>>>>>>> 0486a98415877aceb0d588d6832b9c9b3a40775a
            if qid_dic[qid]["cmp1_eid"]=="" and qid_dic[qid]["cmp2_eid"]=="":
                pop_item=qid_dic.pop(qid)
                continue;
            elif qid_dic[qid]["cmp1_eid"]=="":
                result="%s no eid"%kCmp1
<<<<<<< HEAD
                qid_dic[qid]["difference"]=result
                continue;
            elif qid_dic[qid]["cmp2_eid"]=="":
                result="%s no eid"%kCmp2
                qid_dic[qid]["difference"]=result
                continue;
=======
                return result
            elif qid_dic[qid]["cmp2_eid"]=="":
                result="%s no eid"%kCmp2
                return result
>>>>>>> 0486a98415877aceb0d588d6832b9c9b3a40775a
#            if qid_dic[qid]["cmp1_resp"]=="" or qid_dic[qid]["cmp2_resp"]=="" or qid_dic[qid]["cmp1_eid"]=="" or qid_dic[qid]["cmp2_eid"]=="":
#                print "one of them have no resp or eid in %s"%qid
#                pop_item=qid_dic.pop(qid);
#                continue;
            if qid_dic[qid]["cmp1_eid"]==qid_dic[qid]["cmp2_eid"]:
                if "data" not in qid_dic[qid]["cmp1_resp"] and "data" not in qid_dic[qid]["cmp2_resp"]:
                    result="all is the same"
<<<<<<< HEAD
                    continue;
                elif "data" not in qid_dic[qid]["cmp1_resp"]:
                    result="%s no data"%kCmp1
                    qid_dic[qid]["difference"]=result
                    continue
                elif "data" not in qid_dic[qid]["cmp2_resp"]:
                    result="%s no data"%kCmp2
                    qid_dic[qid]["difference"]=result
                    continue
=======
                    return result
                elif "data" not in qid_dic[qid]["cmp1_resp"]:
                    result="%s no data"%kCmp1
                    return result
                elif "data" not in qid_dic[qid]["cmp2_resp"]:
                    result="%s no data"%kCmp2
                    return result
>>>>>>> 0486a98415877aceb0d588d6832b9c9b3a40775a

                elif kType=='s125':
                    print "before s125cmp"
                    result=s125_Cmpinfo(qid_dic[qid]["cmp1_resp"],qid_dic[qid]["cmp2_resp"])
                elif kType=='s127':
                    print "before s127cmp"
                    result=s127_Cmpinfo(qid_dic[qid]["cmp1_resp"],qid_dic[qid]["cmp2_resp"])
                elif kType=='s128' or kType=='s130':
                    result=s128_s130_Cmpinfo(qid_dic[qid]["cmp1_resp"],qid_dic[qid]["cmp2_resp"])

                if result!="all is the same":
                    qid_dic[qid]["difference"]=result
                print "result=%s"%result

            else:
                fp.write(("qid=%s\n"%qid).decode('utf-8'))
#                    fp.write(("cqid=%s\n"%item["cqid"]).decode('utf-8'))
                print "why in this position~"
#                fp.write(("error_id=%s\n"%item["error_id"]).decode('utf-8'))
                fp.write(("on_req=%s\n"%item["on_req"]).decode('utf-8'))
                fp.write(("cmp1_eid=%s\n"%item["cmp1_eid"]).decode('utf-8'))
                fp.write(("cmp2_eid=%s\n"%item["cmp2_eid"]).decode('utf-8'))
                fp.write(("cmp1_resp=%s\n"%item["cmp1_resp"]).decode('utf-8'))
                fp.write(("cmp2_resp=%s\n"%item["cmp2_resp"]).decode('utf-8'))

    with io.open('./difference','w') as fp:
        for qid,item in qid_dic.items():
            if "difference" not in qid_dic[qid]:
                continue;
            else:
                fp.write(("qid=%s\n"%qid).decode('utf-8'))
                fp.write(("cmp1_qid=%s\n"%qid_dic[qid]["cmp1_qid"]).decode('utf-8'))
                fp.write(("cmp2_qid=%s\n"%qid_dic[qid]["cmp2_qid"]).decode('utf-8'))
                fp.write(("diff=%s\n"%qid_dic[qid]["difference"]).decode('utf-8'))
                fp.write(("cmp2_resp=%s\n"%qid_dic[qid]["cmp2_resp"]).decode('utf-8'))
                fp.write(("cmp2_resp=%s\n"%qid_dic[qid]["cmp2_resp"]).decode('utf-8'))

    with io.open('./cmp1_resp','w',encoding='utf-8') as f:
        for qid,item in qid_dic.items():
            if "difference" not in qid_dic[qid]:
                continue;
            else:
                f.write(("%s\n"%item["cmp1_resp"]).decode('utf-8'))
    with io.open('./cmp2_resp','w',encoding='utf-8') as f:
        for qid,item in qid_dic.items():
            if "difference" not in qid_dic[qid]:
                continue;
            else:
                f.write(("%s\n"%item["cmp2_resp"]).decode('utf-8'))

def product_cmp(cmp1resp,cmp2resp):
    result="all is the same"
    if "product" not in cmp1resp["data"] and "product" not in cmp2resp["data"]:
#        result="nothing to compare, there are no product"
        return result
    elif "product" not in cmp1resp["data"]:
        result="%s no product"%kCmp1
        return result
    elif "product" not in cmp2resp["data"]:
        result="%s no product"%kCmp2
        return result
    cmp1_product=cmp1resp["data"]["product"]
    cmp2_product=cmp2resp["data"]["product"]
    if len(cmp1_product)!=len(cmp2_product):
        if len(cmp1_product)>len(cmp2_product):
            result="cmp2 don't have"
            for key in cmp1_product:
                if key not in cmp2_product:
                    result+="%s "%key
        else:
            result="cmp1 don't have"
            for key in cmp2_product:
                print key
                if key not in cmp1_product:
                    print key
                    result+=" %s"%key
        return result

#        result="the length of product is not the same"
#        return result
    print "befor the key of product cmp"
    for key in cmp1_product:
        if cmp1_product[key] is None and cmp2_product[key] is None:
            continue;
        elif cmp1_product[key] is None:
            result="%s product[%s] is None"%(kCmp1,key)
            return result
        elif cmp2_product[key] is None:
            result="%s product[%s] is None"%(kCmp2,key)
            return result
        elif cmp1_product[key] != cmp2_product[key]:
            if len(cmp1_product[key])!=len(cmp2_product[key]):
                result="length_product[%s]"%key
                return result
            else:
                kk=1
                for keyi in cmp1_product[key]:
                    if keyi not in  cmp2_product[key] :
                        result="product[%s][%d]"%(key,kk)
                        return result
                    else:
                        kk+=1
        else:
            continue
    return "all is the same"

def s127_Cmpinfo(cmp1resp,cmp2resp):
    #data->list->view->summary->days->pois
    print "cmp1resp=%s"%cmp1resp
    print "cmp2resp=%s"%cmp2resp
    cmp1resp=json.loads(cmp1resp);
    cmp2resp=json.loads(cmp2resp)
    print "in s127cmp"
    print "before product cmp"
    result=product_cmp(cmp1resp,cmp2resp)
    if result!="all is the same":
        return result
    
    print "before list cmp"
    if "list" not in cmp1resp["data"] and "list" not in cmp2resp["data"]:
#        result="nothing to compare, there are no list"
        return result
    elif "list" not in cmp1resp["data"]:
        result="%s no list"%kCmp1
        return result
    elif "list" not in cmp2resp["data"]:
        result="%s no list"%kCmp2
        return result
    if len(cmp1resp["data"]["list"])!=len(cmp2resp["data"]["list"]):
        result="length_list"
        return result
    i=0
    while i<len(cmp1resp["data"]["list"]):
        cmp1_view=cmp1resp["data"]["list"][i]["view"]
        cmp2_view=cmp2resp["data"]["list"][i]["view"]
#        print cmp1_view
        if cmp1_view is None and cmp2_view is None:
            i+=1
            continue;
        elif cmp1_view is None and cmp2_view!=None:
            print "cmp1_view is null"
<<<<<<< HEAD
            result="cmp1_view_list[%d] is None"%(i+1)
            return result
        elif cmp1_view!=None and cmp2_view is None:
            result="cmp2_view_list[%d] is None"%(i+1)
=======
            result="view_list[%d] is None"%(i+1)
            return result
        elif cmp1_view!=None and cmp2_view is None:
            result="view_list[%d] is None"%(i+1)
>>>>>>> 0486a98415877aceb0d588d6832b9c9b3a40775a
            return result

        else:
            z=0
            cmp1_days=cmp1_view["summary"]["days"]
            cmp2_days=cmp2_view["summary"]["days"]
            if len(cmp1_days)!=len(cmp2_days):
                result="length_days"
                return result
            else:
                j=0
                while j<len(cmp1_days):
                    cmp1_pois=cmp1_days[j]["pois"]
                    cmp2_pois=cmp2_days[j]["pois"]
                    if len(cmp1_pois)!=len(cmp2_pois):
                        result="length_pois of list[%d]day[%d]"%(i+1,j+1)
                        return result
#                    z=0
                    else:
                        k=0
                        while k<len(cmp1_pois):
                            cmp1_id=cmp1_pois[k]["id"]
                            cmp2_id=cmp2_pois[k]["id"]
                            cmp1_pdur=cmp1_pois[k]["pdur"]
                            cmp2_pdur=cmp2_pois[k]["pdur"]
                            if cmp1_id != cmp2_id:
                                result="id_list[%d]day[%d]pois[%d]"%(i+1,j+1,k+1)
#                                result="the id of %d pois of %d day of %d list is not the same"%(k+1,j+1,i+1)
                                return result
                            elif cmp1_pdur != cmp2_pdur:
                                z+=1
                                if(z>5):
                                    k+=1
                                    continue;
                                if z==1:
                                    result="pdur_list[%d]day[%d]pois[%d]"%(i+1,j+1,k+1)
                                else:
                                    result+=", pdur_list[%d]day[%d]pois[%d]"%(i+1,j+1,k+1)
#                                result+=", the pdur of %d pois of %d day of %d list is not the same"%(k+1,j+1,i+1)
#                                k+=1
#                                continue
                            k+=1
                    j+=1
        i+=1
    return result
def s125_Cmpinfo(cmp1resp,cmp2resp):
    #不一定有view,//data->view->summary->days->pois
    print "cmp1resp=%s"%cmp1resp
    print "cmp2resp=%s"%cmp2resp
    cmp1resp=json.loads(cmp1resp);
    cmp2resp=json.loads(cmp2resp);
    print "in s125cmp"
    print "before product cmp"
    result=product_cmp(cmp1resp,cmp2resp)
    if result!="all is the same":
        return result

    if "view" not in cmp1resp["data"] and "view" not in cmp2resp["data"]:
#        result="nothing to compare, there are no view"
        return result
    elif "view" not in cmp1resp["data"]:
        result="%s no view"%kCmp1
        return result
    elif  "view" not in cmp2resp["data"]:
        result="%s no view"%kCmp2
        return result
    else:
        print "before view cmp"
        cmp1_view=cmp1resp["data"]["view"]
        cmp2_view=cmp2resp["data"]["view"]
        cmp1_days=cmp1_view["summary"]["days"]
        cmp2_days=cmp2_view["summary"]["days"]
        if len(cmp1_days)!=len(cmp2_days):
            result="length_days"
            return result
        else:
            z=0
            j=0
            while j<len(cmp1_days):
                cmp1_pois=cmp1_days[j]["pois"]
                cmp2_pois=cmp2_days[j]["pois"]
                if len(cmp1_pois)!=len(cmp2_pois):
                    result="length_pois of day[%d]"%(j+1)
                    return result
                else:
                    k=0
                    while k<len(cmp1_pois):
                        cmp1_id=cmp1_pois[k]["id"]
                        cmp2_id=cmp2_pois[k]["id"]
                        cmp1_pdur=cmp1_pois[k]["pdur"]
                        cmp2_pdur=cmp2_pois[k]["pdur"]
                        if cmp1_id != cmp2_id:
                            result="id_day[%d]pois[%d]"%(j+1,k+1)
                            return result
                        elif cmp1_pdur != cmp2_pdur:
                            z+=1
                            if(z>5):
                                k+=1
                                continue;
                            if z==1:
                                result="pdur_day[%d]pois[%d]"%(j+1,k+1)
                            else:
                                result+=", pdur_day[%d]pois[%d]"%(j+1,k+1)
#                            k+=1
#                            continue
                        k+=1
                j+=1

    return result
def s128_s130_Cmpinfo(cmp1resp,cmp2resp):
    #不一定有city,//data->city->view->summary->days->pois
    print "cmp1resp=%s"%cmp1resp
    print "cmp2resp=%s"%cmp2resp
    cmp1resp=json.loads(cmp1resp);
    cmp2resp=json.loads(cmp2resp)
    if kType=='s128':
        print "in s128cmp"
    else:
        print "in s130cmp"
    print "before product cmp"
    result=product_cmp(cmp1resp,cmp2resp)
    if result!="all is the same":
        return result

    if "city" not in cmp1resp["data"] and "city" not in cmp2resp["data"]:
#        result="nothing to compare, there are no city"
        return result
    elif "city" not in cmp1resp["data"]:
        result="%s no city"%kCmp1
        return result
    elif "city" not in cmp2resp["data"]:
        result="%s no city"%kCmp2
        return result
    else:
        if kType=='s128':
            print "s128_viewcmp"
        if kType=='s130':
            print "s130_viewcmp"
        if "view" not in cmp1resp["data"]["city"] or cmp1resp["data"]["city"]["view"] is None and ("view" not in cmp2resp["data"]["city"] or cmp2resp["data"]["city"]["view"] is None ):
#            result="nothing to compare, there are no view"
            return result
        elif "view" not in cmp1resp["data"]["city"] or cmp1resp["data"]["city"]["view"] is None:
            result="%s no view"%kCmp1
            return result
        elif "view" not in cmp2resp["data"]["city"] or cmp2resp["data"]["city"]["view"] is None :
            result="%s no view"%kCmp2
            return result
        cmp1_view=cmp1resp["data"]["city"]["view"]
        cmp2_view=cmp2resp["data"]["city"]["view"]
        cmp1_days=cmp1_view["summary"]["days"]
        cmp2_days=cmp2_view["summary"]["days"]
        if len(cmp1_days)!=len(cmp2_days):
            result="length_days"
            return result
        else:
            z=0
            j=0
            while j<len(cmp1_days):
                cmp1_pois=cmp1_days[j]["pois"]
                cmp2_pois=cmp2_days[j]["pois"]
                if len(cmp1_pois)!=len(cmp2_pois):
                    result="length_pois of day[%d]"%(j+1)
                    return result
                else:
                    k=0
                    while k<len(cmp1_pois):
                        cmp1_id=cmp1_pois[k]["id"]
                        cmp2_id=cmp2_pois[k]["id"]
                        cmp1_pdur=cmp1_pois[k]["pdur"]
                        cmp2_pdur=cmp2_pois[k]["pdur"]
                        if cmp1_id != cmp2_id:
                            result="id_day[%d]pois[%d]"%(j+1,k+1)
                            return result
                        elif cmp1_pdur != cmp2_pdur:
                            z+=1
                            if(z>5):
                                k+=1
                                continue;
                            if z==1:
                                result="pdur_day[%d]pois[%d]"%(j+1,k+1)
                            else:
                                result+=", pdur_day[%d]pois[%d]"%(j+1,k+1)
#                            k+=1
#                            continue;
                        k+=1
                j+=1

    return result


kDate = '20170826'
kNum=20
kType='s125'
kCmp1='test'
kCmp2='test1'
def main():
	global kDate
	global kNum
	global kType
	global kCmp1
	global kCmp2
	parser = optparse.OptionParser()
<<<<<<< HEAD
	parser.add_option('-d', '--date', help = 'run date like 20170826')
=======
	parser.add_option('-d', '--date', help = 'run date like 20180826')
>>>>>>> 0486a98415877aceb0d588d6832b9c9b3a40775a
	parser.add_option('-n', '--num',type="int",dest="num",default="20", help = 'run case num like 100')
	parser.add_option('-t', '--type', type="string",dest="type",default="s125",help = 'run type like s125')
	parser.add_option('-x', '--cmp1', type="string",dest="cmp1",default="test")
	parser.add_option('-y', '--cmp2', type="string",dest="cmp2",default="test1")
	opt, args = parser.parse_args()
        print opt.date
        print opt.num
        print opt.type
        print opt.cmp1
        print opt.cmp2
        kNum=opt.num
	try:	
            run_day = datetime.datetime.fromtimestamp(time.mktime(time.strptime(opt.date, '%Y%m%d')))
            date_str = run_day.strftime('%Y%m%d')
            kDate = date_str;
#		print "kDate=%s"%kDate
	except:
            print "Error Format date"
            return
        if opt.type == "s125" or opt.type=="s127" or opt.type=="s128" or opt.type=="s130":
            kType=opt.type
        else:
            print "Error Format type"
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
<<<<<<< HEAD
	Fetch()
        Cmpinfo()
=======
	Fetch();
        Cmpinfo();
>>>>>>> 0486a98415877aceb0d588d6832b9c9b3a40775a

main()

