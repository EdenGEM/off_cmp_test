#!/usr/local/bin//python 
#-*-coding:UTF-8 -*-
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
import conf
import commands
import requests
import cgi,cgitb
from DBHandle import DBHandle

reload(sys);
exec("sys.setdefaultencoding('utf-8')");

class RespCmp:
    qid_dic=dict()
    delete=0

    def __init__(self,kDate="",kType="",kNum="",kQid="",kCmp1="",kCmp2="",Mail=""):
        self.kDate=kDate
        self.kType=kType
        self.kNum=kNum
        self.kQid=kQid
        self.kCmp1=kCmp1
        self.kCmp2=kCmp2
        self.Mail=Mail
    def LoadReqAndRespByPatch(self):
        print "before LoadReqAndRespByPatch"
        print "before Load"
        self.__Load()
        print "before Parsereq"
        self.__Parsereq()
        print "before Store"
        self.__Store()
        print "LoadReqAndRespByPatch ok"



    def LoadReqAndRespByQid(self):
        print "before LoadReqAndRespByQid"
        kQid=self.kQid
        tt=int(kQid)
        kDate=time.strftime("%Y%m%d",time.localtime(tt/1000))
        print kDate
        self.kDate=kDate
        self.kType=self.__Load()
        print "load self.kType=%s"%self.kType
        self.__Parsereq()
        print "LoadReqAndRespByQid ok"



    def CmpInfoByPatch(self):
        print "before CmpInfoByPatch"
        self.__Fetch()
        self.__GetResp()
        print "CmpInfoByPatch ok"
        self.__mymail(self.qid_dic)
    def __mymail(self,Dict):
        html='''
        <html><body>
        <h1 align="center">diff %s_%s</h1>
        <table border='1' align="center">
        <tr><th>%s_qid</th><th>%s_qid</th><th>diff</th></tr>
        '''%(self.kCmp1,self.kCmp2,self.kCmp1,self.kCmp2)
        flag=0
        if self.kQid:
            by="qid"
        else:
            by="patch"
        for qid,item in Dict.items():
            if "difference" in item:
                flag=1
                html+='''
                <tr>
                    <td>
                    <a href="http://10.10.169.10:8000/cgi-bin/index.py?qid=%s&env=%s&by=%s" target="_blank">%s</a>
                    </td>
                    <td>
                    <a href="http://10.10.169.10:8000/cgi-bin/index.py?qid=%s&env=%s&by=%s" target="_blank">%s</a>
                    </td>
                    <td>%s</td>
                </tr>
                '''%(item["cmp1_qid"],self.kCmp1,by,item["cmp1_qid"],item["cmp2_qid"],self.kCmp2,by,item["cmp2_qid"],item["difference"])
        if flag==0:
            html='''
            <html><body>
            <h1 align="center">No data</h1>
            </body></html>
            '''
        else:
            html+='</table>'
            html+='</body></html>'
        with io.open('./report.html','w',encoding='utf-8') as f:
            f.write((html).decode('utf-8'))
        print "Report ok"
        Dir=commands.getoutput('pwd')
        Report=Dir+"/report.html"
        print Report
        mailto=self.Mail
        commands.getoutput('mioji-mail -m '+mailto+' -b "CmpInfo" -f '+Report+' -h 123')
        print "mail ok"

    def CmpInfoByQid(self):
        qid_dic=self.qid_dic
        kCmp1=self.kCmp1
        kCmp2=self.kCmp2
        qid=self.kQid
        Senv_req="%s_req"%kCmp1
        Senv_resp="%s_resp"%kCmp1
        Senv_eid="%s_eid"%kCmp1
        Denv_req="%s_req"%kCmp2
        Denv_resp="%s_resp"%kCmp2
        Denv_eid="%s_eid"%kCmp2
        Denv_qid="%s_qid"%kCmp2
        
        qid_dic[qid]["cmp1_qid"]=qid_dic[qid]["qid"]
        qid_dic[qid]["cmp2_qid"]=qid_dic[qid][Denv_qid]
        qid_dic[qid]["cmp1_resp"]=qid_dic[qid][Senv_resp]
        qid_dic[qid]["cmp2_resp"]=qid_dic[qid][Denv_resp]
        qid_dic[qid]["difference"]=""
        if qid_dic[qid]["cmp1_resp"]=="" and qid_dic[qid]["cmp2_resp"]=="":
            qid_dic[qid]["difference"]="all no response"
        elif qid_dic[qid]["cmp1_resp"]=="":
            qid_dic[qid]["difference"]="%s: no response"%kCmp1
        elif qid_dic[qid]["cmp2_resp"]=="":
            qid_dic[qid]["difference"]="%s: no response"%kCmp2
        conn=DBHandle(conf.Storehost,conf.Storeuser,conf.Storepasswd,conf.Storedb)
        cmp1_qid="%s_qid"%kCmp1
        cmp2_qid="%s_qid"%kCmp2
        cmp1_resp="%s_resp"%kCmp1
        cmp2_resp="%s_resp"%kCmp2

        sqlstr="replace into all_about (date,\
                req_type,\
                %s,\
                %s,\
                %s,\
                %s) "%(cmp1_qid,cmp2_qid,cmp1_resp,cmp2_resp)

        sqlstr+="values(%s,%s,%s,%s,%s,%s)"
        args=[]
        T=(self.kDate,\
                self.kType,\
                qid_dic[qid]["cmp1_qid"],\
                qid_dic[qid]["cmp2_qid"],\
                qid_dic[qid]["cmp1_resp"],\
                qid_dic[qid]["cmp2_resp"])
        args.append(T)
        conn.do(sqlstr,T)
        print self.kType
        print "qid Store ok"
        if qid_dic[qid]["difference"]=="":
            eid1=""
            eid2=""
            try:
#                tmp=json.loads(resp1)
                tmp=json.loads(qid_dic[qid]["cmp1_resp"])
                eid1=tmp["error"]["error_id"]
            except:
                print "no match eid1"
            try:
                tmp=json.loads(qid_dic[qid]["cmp2_resp"])
                eid2=tmp["error"]["error_id"]
            except:
                print "no match eid2"
            qid_dic[qid]["cmp1_eid"]=eid1
            qid_dic[qid]["cmp2_eid"]=eid2
            print "beforeCmpInfoByQid"
            if qid_dic[qid]["cmp1_eid"]!=0:
                qid_dic[qid]["difference"]="%s's eid =%s"%(kCmp1,eid1)
            elif qid_dic[qid]["cmp1_eid"]==qid_dic[qid]["cmp2_eid"]:
                qid_dic[qid]["difference"]=self.__CmpInfo(qid_dic[qid]["cmp1_resp"],qid_dic[qid]["cmp2_resp"])
            else:
                qid_dic[qid]["difference"]="%s's eid =%s"%(kCmp2,eid2)
        print "CmpInfoByQid ok"
        self.__mymail(qid_dic)
        '''
        if qid_dic[qid]["difference"]!="all is the same":
            with io.open('./diff_one_qid','w',encoding='utf-8') as f:
                f.write(("result=%s\n"%qid_dic[qid]["difference"]).decode('utf-8'))
                f.write(("%s_resp=%s\n"%(kCmp1,qid_dic[qid]["cmp1_resp"])).decode('utf-8'))
                f.write(("%s_resp=%s\n"%(kCmp2,qid_dic[qid]["cmp2_resp"])).decode('utf-8'))
        '''


    def __Load(self):
        print "in Load"
        kDate=self.kDate
        kType=self.kType
        kNum=self.kNum
        kQid=self.kQid
        qid_dic=self.qid_dic
        print type(kQid)
        if kQid:
            Senv=self.kCmp1
            Senv_req="%s_req"%Senv
            Senv_resp="%s_resp"%Senv
            Senv_eid="%s_eid"%Senv

            dbb="logQuery_%s"%Senv
            print dbb
            conn=DBHandle(conf.Loadhost,conf.Loaduser,conf.Loadpasswd,dbb)
            sqlstr="select req_params from nginx_api_log_%s where qid=%s and log_type='13' and req_type in('s125','s127','s128','s129' ,'s130' ,'p101' ,'p104' ,'p105','b116');"%(kDate,kQid)
            reqs=conn.do(sqlstr)
            print sqlstr
    #        print reqs
            qid_dic[kQid]=dict()
            qid_dic[kQid]["qid"]=kQid
            qid_dic[kQid][Senv_req]=reqs[0]["req_params"]
            pat_type=re.compile(r'type=(\w+)&')
            match_type=pat_type.search(reqs[0]["req_params"])
            if match_type:
                kType=match_type.group(1)
                print "find type=%s"%kType
            else:
                print "no find type"
                return 
            print"in select"
            sqlstr="select id from nginx_api_log_%s where qid=%s and log_type='14' and req_type in('s125' ,'s127','s128','s129','s130' ,'p101','p104','p105' ,'b116');"%(kDate,kQid)
            print sqlstr
            ids=conn.do(sqlstr)
    #        print "results=%s"%ids
            sqlstr="select response from nginx_api_resp_%s where id=%s;"%(kDate,ids[0]["id"])
            print sqlstr
            resp=conn.do(sqlstr)
            qid_dic[kQid][Senv_resp]=resp[0]["response"]
    #        print "resp=%s"%resp
            try:
                tmp=json.loads(resp[0]["response"])
    #            print "tmp=%s"%tmp
            except:
                print "pass this resp"
                return kType 

            if "error" not in tmp:
                qid_dic[kQid][Senv_eid]=""
                print "%s don't have error"%kQid
                return kType

            eid=tmp["error"]["error_id"]
            qid_dic[kQid][Senv_eid]=eid
            print "find type1=%s"%kType
            return kType

        else:
            conn=DBHandle(conf.Loadhost,conf.Loaduser,conf.Loadpasswd,'logQuery_online')
            sqlstr="select qid,req_params from nginx_api_log_%s where req_type='%s' and log_type='13' group by qid having count(*)=1 order by rand() limit %d"%(kDate,kType,kNum)
            print sqlstr
            qids=conn.do(sqlstr)
            print"in select"
            sqlstr="select qid,id from nginx_api_log_%s where req_type='%s' and log_type='14' and qid in("%(kDate,kType)
            
            for i,row in enumerate(qids):
                qid=row["qid"]
                qid_dic[qid]=dict()
                qid_dic[qid]["qid"]=qid
                qid_dic[qid]["req_type"]=kType
                print row["qid"]
                print "yuan_req:%s"%row["req_params"]
                qid_dic[qid]["ori_req"]=row["req_params"]
                if i == len(qids) - 1:
                    sqlstr+="%s"%row["qid"]
                else:
                    sqlstr+="%s,"%row["qid"]
            sqlstr+=");"
            ids=conn.do(sqlstr)
            print sqlstr
            id_dic=dict()
            sqlstr="select id,response from nginx_api_resp_%s where id in ("%kDate
            for i,row in enumerate(ids):
                id_dic[row["id"]]=row["qid"]
#                print "%s_%s"%(row["id"],row["qid"])
                if i == len(ids) - 1:
                    sqlstr+="%s"%row["id"]
                else:
                    sqlstr+="%s,"%row["id"]
            sqlstr+=");"
            print sqlstr
            resps=conn.do(sqlstr)
            for i,row in enumerate(resps):
                print "GEMresp"
                qidd=id_dic[row["id"]]
#                print "%s_%s"%(row["id"],qidd)
                if row["response"]=="":
                    pop_item=qid_dic.pop(qidd)
                    self.delete+=1
                    print "no response_delete=%d"%(self.delete)
                    continue
                resp=row["response"]
                qid_dic[qidd]["on_resp"]=resp 
                print "qid=%s"%qidd
                print resp
                try:
                    tmp=json.loads(resp)
                except:
                    print "pass this resp"
                    pop_item=qid_dic.pop(qidd)
                    self.delete+=1
                    print "resp_loads_error,delete=%d"%(self.delete)
                    continue;

                if "error" not in tmp:
                    pop_item=qid_dic.pop(qidd)
                    self.delete+=1
                    print "no error_delete=%d"%(self.delete)
                    continue;
                try:
                    eid=tmp["error"]["error_id"]
                except:
                    print "error_id 字段有误"
                    eid=""
                print "on_eid=%s"%eid
                qid_dic[qidd]["on_eid"]=eid
        self.qid_dic=qid_dic

    def __Query(self,qid,env,req):
        qid_dic=self.qid_dic
        env_qid="%s_qid"%env
        env_resp="%s_resp"%env
        env_req="%s_req"%env
        env_eid="%s_eid"%env
        print "in Query"
        cur_qid=int(round(time.time()*1000))
        qid_dic[qid][env_qid]=cur_qid
        print "qid=%s"%qid
        ziduan="qid="+str(cur_qid)
        originqid=r'qid=(\d+)'
        req=re.sub(originqid,ziduan,req)
    #    print "%s=%s"%(env_req,req)
        print  10 * "*"
        qid_dic[qid][env_req]=req
        if env=="test":
            url="http://10.10.135.140:92/?"+req
        elif env=="test1":
            url="http://10.10.135.140:9292/?"+req
        elif env=="online":
            url="http://10.10.135.140:93/?"+req
        else:
            url="http://10.10.135.140:91/?"+req
    #    print "%s_url=%s"%(env,url)

        try:
            r=requests.get(url)
            resps=r.text
            r.raise_for_status()
            print "%s=%s"%(env_resp,resps)
            qid_dic[qid][env_resp]=resps
    #        print resps
            tmp=json.loads(resps)
            new_eid=tmp["error"]["error_id"]
            print "%s=%s"%(env_eid,new_eid)
            qid_dic[qid][env_eid]=new_eid
        except (requests.RequestException) as e:
            print "requesterror:"
            print e
            qid_dic[qid][env_resp]=""
            qid_dic[qid][env_eid]=None

        except Exception:
            print "url request timeout~"
            qid_dic[qid][env_resp]=""
            qid_dic[qid][env_eid]=None
        self.qid_dic=qid_dic

    def __Parsereq(self):
        kQid=self.kQid
        qid_dic=self.qid_dic
        
        print "in parser"
        if kQid:
            Senv=self.kCmp1
            Denv=self.kCmp2
            Senv_req="%s_req"%Senv
            Senv_resp="%s_resp"%Senv
            req=qid_dic[kQid][Senv_req]
            ori_uid=re.compile(r'&uid=(.+)&')
            ziduan="&uid=caoxiaolan&"
            req=re.sub(ori_uid,ziduan,req)
            print "query_req=%s"%req
            print "%s_resp=%s"%(Senv,qid_dic[kQid][Senv_resp])
            self.__Query(kQid,Denv,req)
        else:
            for qid,item in qid_dic.items():
                if "qid" not in qid_dic[qid] or "ori_req" not in qid_dic[qid] or "on_eid" not in qid_dic[qid]:
                    pop_item=qid_dic.pop(qid);
                    self.delete+=1
                    print "T,delete=%d"%(self.delete)
                    continue;
                if qid_dic[qid]["on_eid"]!=0:
                    pop_item=qid_dic.pop(qid)
                    self.delete+=1
                    print "on_eid!=0,delete=%d"%(self.delete)
                    continue;
                req=qid_dic[qid]["ori_req"]
                ori_uid=re.compile(r'&uid=(.+)&')
                ziduan="&uid=caoxiaolan&"
                req=re.sub(ori_uid,ziduan,req)
                print "query_req=%s"%req
                self.__Query(qid,"test",req)
                self.__Query(qid,"test1",req)
                self.__Query(qid,"offline",req)

#    def Store(kDate,kType):
    def __Store(self):
        qid_dic=self.qid_dic
        kDate=self.kDate
        kType=self.kType
        print "self.kType=%s"%self.kType
        conn=DBHandle(conf.Storehost,conf.Storeuser,conf.Storepasswd,conf.Storedb)
        print "before store"
        sqlstr="replace into all_about (date,\
                req_type,\
                online_qid,\
                online_req,\
                online_resp,\
                online_eid,\
                test_qid,\
                test_resp,\
                test_eid,\
                test1_qid,\
                test1_resp,\
                test1_eid,\
                offline_qid,\
                offline_resp,\
                offline_eid) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        args=[]
        for qid,item in qid_dic.items():
            print "in store"
            T=(kDate,\
                    kType,\
                    item["qid"],\
                    item["ori_req"],\
                    item["on_resp"],\
                    item["on_eid"],\
                    item["test_qid"],\
                    item["test_resp"],\
                    item["test_eid"],\
                    item["test1_qid"],\
                    item["test1_resp"],\
                    item["test1_eid"],\
                    item["offline_qid"],\
                    item["offline_resp"],\
                    item["offline_eid"])
            args.append(T)
        conn.do(sqlstr,args)
        print "after store"
    def __Fetch(self):
        self.qid_dic=dict()
        qid_dic=self.qid_dic
        kCmp1=self.kCmp1
        kCmp2=self.kCmp2
        kDate=self.kDate
        kType=self.kType
        kNum=self.kNum
        kCmp1_qid="%s_qid"%kCmp1
        kCmp1_resp="%s_resp"%kCmp1
        kCmp1_eid="%s_eid"%kCmp1
        kCmp2_qid="%s_qid"%kCmp2
        kCmp2_resp="%s_resp"%kCmp2
        kCmp2_eid="%s_eid"%kCmp2
        if kCmp1!="online":
            order=kCmp1
        else:
            order=kCmp2
            
        conn=DBHandle(conf.Storehost,conf.Storeuser,conf.Storepasswd,conf.Storedb)
        sqlstr="select online_qid,online_req,%s_qid,%s_resp,%s_eid,%s_qid,%s_resp,%s_eid from test.all_about where date=%s and req_type='%s' group by online_qid order by %s_qid desc limit %d;"%(kCmp1,kCmp1,kCmp1,kCmp2,kCmp2,kCmp2,kDate,kType,order,kNum-self.delete)
        print sqlstr
        rows=conn.do(sqlstr)
        for row in rows:
            qid=row["online_qid"]
            qid_dic[qid]=dict()
            qid_dic[qid]["qid"]=qid
            qid_dic[qid]["on_req"]=row["online_req"]
            qid_dic[qid]["cmp1_qid"]=row[kCmp1_qid]
            qid_dic[qid]["cmp1_resp"]=row[kCmp1_resp]
            qid_dic[qid]["cmp1_eid"]=row[kCmp1_eid]
            qid_dic[qid]["cmp2_qid"]=row[kCmp2_qid]
            qid_dic[qid]["cmp2_resp"]=row[kCmp2_resp]
            qid_dic[qid]["cmp2_eid"]=row[kCmp2_eid]

        self.qid_dic=qid_dic
        

    def __GetResp(self):
        qid_dic=self.qid_dic
        kCmp1=self.kCmp1
        kCmp2=self.kCmp2
        
        with io.open('./diff_error','w') as fp:
            for qid,item in qid_dic.items():
                if qid_dic[qid]["cmp1_resp"]=="" and qid_dic[qid]["cmp2_resp"]=="":
                    pop_item=qid_dic.pop(qid)
                    print "pop: no resp"
                    continue;
                elif qid_dic[qid]["cmp1_resp"]=="":
                    result="%s: no resp"%kCmp1
                    qid_dic[qid]["difference"]=result
                    continue;
                elif qid_dic[qid]["cmp2_resp"]=="":
                    result="%s: no resp"%kCmp2
                    qid_dic[qid]["difference"]=result
                    continue;
                if qid_dic[qid]["cmp1_eid"]=="" and qid_dic[qid]["cmp2_eid"]=="":
                    print "pop: no eid"
                    pop_item=qid_dic.pop(qid)
                    continue;
                elif qid_dic[qid]["cmp1_eid"]=="":
                    result="%s: no eid"%kCmp1
                    qid_dic[qid]["difference"]=result
                    continue;
                elif qid_dic[qid]["cmp2_eid"]=="":
                    result="%s: no eid"%kCmp2
                    qid_dic[qid]["difference"]=result
                    continue;

                if qid_dic[qid]["cmp1_eid"]==qid_dic[qid]["cmp2_eid"]:
                    print "on_req=%s"%(qid_dic[qid]["on_req"])
                    print "%s_resp=%s"%(kCmp1,qid_dic[qid]["cmp1_resp"])
                    print "%s_resp=%s"%(kCmp2,qid_dic[qid]["cmp2_resp"])
                    result=self.__CmpInfo(qid_dic[qid]["cmp1_resp"],qid_dic[qid]["cmp2_resp"])
                    print "result=%s"%result

                    if result!="all is the same":
                        qid_dic[qid]["difference"]=result

                else:
                    fp.write(("qid=%s\n"%qid).decode('utf-8'))
                    fp.write(("cmp1_qid=%s\n"%item["cmp1_qid"]).decode('utf-8'))
                    fp.write(("cmp2_qid=%s\n"%item["cmp2_qid"]).decode('utf-8'))
                    print "error_id diff, go diff_error"
                    fp.write(("on_req=%s\n"%item["on_req"]).decode('utf-8'))
                    fp.write(("cmp1_eid=%s\n"%item["cmp1_eid"]).decode('utf-8'))
                    fp.write(("cmp2_eid=%s\n"%item["cmp2_eid"]).decode('utf-8'))
                    fp.write(("cmp1_resp=%s\n"%item["cmp1_resp"]).decode('utf-8'))
                    fp.write(("cmp2_resp=%s\n"%item["cmp2_resp"]).decode('utf-8'))
        '''
        with io.open('./difference','w') as fp:
            for qid,item in qid_dic.items():
                if "difference" not in qid_dic[qid]:
                    continue;
                else:
                    fp.write(("qid=%s\n"%qid).decode('utf-8'))
                    fp.write(("cmp1_qid=%s\n"%qid_dic[qid]["cmp1_qid"]).decode('utf-8'))
                    fp.write(("cmp2_qid=%s\n"%qid_dic[qid]["cmp2_qid"]).decode('utf-8'))
                    fp.write(("diff=%s\n"%qid_dic[qid]["difference"]).decode('utf-8'))
                    fp.write(("cmp1_resp=%s\n"%qid_dic[qid]["cmp1_resp"]).decode('utf-8'))
                    fp.write(("cmp2_resp=%s\n"%qid_dic[qid]["cmp2_resp"]).decode('utf-8'))
        '''
        self.qid_dic=qid_dic

    def __CmpProduct(self,cmp1resp,cmp2resp):
        kCmp1=self.kCmp1
        kCmp2=self.kCmp2
        result="all is the same"
        if "product" not in cmp1resp["data"] and "product" not in cmp2resp["data"]:
            return result
        elif "product" not in cmp1resp["data"]:
            result="%s: no product"%kCmp1
            return result
        elif "product" not in cmp2resp["data"]:
            result="%s: no product"%kCmp2
            return result
        cmp1_product=cmp1resp["data"]["product"]
        cmp2_product=cmp2resp["data"]["product"]
        if len(cmp1_product)!=len(cmp2_product):
            if len(cmp1_product)>len(cmp2_product):
                result="%s don't have "%kCmp1
                for key in cmp1_product:
                    if key not in cmp2_product:
                        result+="%s "%key
            else:
                result="%s don't have "%kCmp2
                for key in cmp2_product:
                    if key not in cmp1_product:
                        result+=" %s"%key
            return result

        print "before the key of product cmp"
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

    def __CmpView(self,cmp1_view,cmp2_view,cidx):
        cmp1_days=cmp1_view["summary"]["days"]
        cmp2_days=cmp2_view["summary"]["days"]
        result="all is the same"
        print "cmp1_days=%s"%cmp1_days
        print "cmp2_days=%s"%cmp2_days
        if cmp1_days=='None' and cmp2_days=='None':
            return result
        elif cmp1_days=='None':
            result="%s: days_list[%d] is None"%(self.kCmp1,cidx+1)
        elif cmp2_days=='None':
            result="%s: days_list[%d] is None"%(self.kCmp2,cidx+1)
#        if type(cmp1_days)=='NoneType' or type(cmp2_days)=='NoneType':
#            return result
        if len(cmp1_days)!=len(cmp2_days):
            result="length_days"
            return result
        else:
            didx=0
            while didx<len(cmp1_days):
                cmp1_pois=cmp1_days[didx]["pois"]
                cmp2_pois=cmp2_days[didx]["pois"]
                if len(cmp1_pois)!=len(cmp2_pois):
                    result="length_pois of list[%d]day[%d]"%(cidx+1,didx+1)
                    return result
                else:
                    vidx=0
                    z=0
                    while vidx<len(cmp1_pois):
                        cmp1_id=cmp1_pois[vidx]["id"]
                        cmp2_id=cmp2_pois[vidx]["id"]
                        cmp1_pdur=cmp1_pois[vidx]["pdur"]
                        cmp2_pdur=cmp2_pois[vidx]["pdur"]
                        if cmp1_id != cmp2_id:
                            if cidx!=-1:
                                result="id_list[%d]day[%d]pois[%d]"%(cidx+1,didx+1,vidx+1)
                            else:
                                result="id_day[%d]pois[%d]"%(didx+1,vidx+1)
                            return result
                        elif cmp1_pdur != cmp2_pdur:
                            z+=1
                            if(z>5):
                                vidx+=1
                                continue;
                            if z==1:
                                if cidx!=-1:
                                    result="pdur_list[%d]day[%d]pois[%d]"%(cidx+1,didx+1,vidx+1)
                                else:
                                    result="pdur_day[%d]pois[%d]"%(didx+1,vidx+1)
                            else:
                                if cidx!=-1:
                                    result+=", pdur_list[%d]day[%d]pois[%d]"%(cidx,didx+1,vidx+1)
                                else:
                                    result+=", pdur_day[%d]pois[%d]"%(didx+1,vidx+1)
                        vidx+=1
                didx+=1
            return result
    def __CmpInfo(self,cmp1resp,cmp2resp):
        kCmp1=self.kCmp1
        kCmp2=self.kCmp2
        kType=self.kType
        print "cmpinfo_self.kType=%s"%self.kType
        #s128,s130 不一定有city //data->city->view->summary->days->pois
        #s127                   //data->list->view->summary->days->pois
        #s125                   //data->view->summary->days->pois
        cmp1resp=json.loads(cmp1resp);
        cmp2resp=json.loads(cmp2resp)
        if "data" not in cmp1resp and "data" not in cmp2resp:
            result="all is the same"
            return result
        elif "data" not in cmp1resp:
            result="%s: no data"%kCmp1
            return result
        elif "data" not in cmp2resp:
            result="%s: no data"%kCmp2
            return result

        if cmp1resp["data"] is None and cmp2resp["data"] is None:
            result="all is the same"
            return result
        elif cmp1resp["data"] is None:
            result="%s: data is None"%kCmp1
            return result
        elif cmp2resp["data"] is None:
            result="%s: data is None"%kCmp2
            return result
        print "before product cmp"
        result=self.__CmpProduct(cmp1resp,cmp2resp)
        if result!="all is the same":
            return result
        print "before view cmp"
        if kType=="s127":
            print "in s127 view_cmp"
            if "list" not in cmp1resp["data"] and "list" not in cmp2resp["data"]:
                return result
            elif "list" not in cmp1resp["data"]:
                result="%s: no list"%kCmp1
                return result
            elif "list" not in cmp2resp["data"]:
                result="%s: no list"%kCmp2
                return result
            if len(cmp1resp["data"]["list"])!=len(cmp2resp["data"]["list"]):
                result="length_list"
                return result
            i=0
            while i<len(cmp1resp["data"]["list"]):
                cmp1_view=cmp1resp["data"]["list"][i]["view"]
                cmp2_view=cmp2resp["data"]["list"][i]["view"]
                if cmp1_view is None and cmp2_view is None:
                    i+=1
                    continue;
                elif cmp1_view is None and cmp2_view!=None:
                    print "cmp1_view is null"
                    result="%s: view_list[%d] is None"%(kCmp1,i+1)
                    return result
                elif cmp1_view!=None and cmp2_view is None:
                    result="%s: view_list[%d] is None"%(kCmp2,i+1)
                    return result

                else:
                    print "before CmpView"
                    result=self.__CmpView(cmp1_view,cmp2_view,i)
                i+=1
            return result

        elif kType=="s125":
            print "in s125 view_cmp"
            if "view" not in cmp1resp["data"] and "view" not in cmp2resp["data"]:
                return result
            elif "view" not in cmp1resp["data"]:
                result="%s: no view"%kCmp1
                return result
            elif "view"  not in cmp2resp["data"]:
                result="%s: no view"%kCmp2
                return result
            cmp1_view=cmp1resp["data"]["view"]
            cmp2_view=cmp2resp["data"]["view"]
            result=self.__CmpView(cmp1_view,cmp2_view,-1)
            return result
        else:
            print "before s128 or s130 view_cmp"
            if "city" not in cmp1resp["data"] and "city" not in cmp2resp["data"]:
                return result
            elif "city" not in cmp1resp["data"]:
                result="%s: no city"%kCmp1
                return result
            elif "city" not in cmp2resp["data"]:
                result="%s: no city"%kCmp2
                return result

            if "view" not in cmp1resp["data"]["city"] or cmp1resp["data"]["city"]["view"] is None and ("view" not in cmp2resp["data"]["city"] or cmp2resp["data"]["city"]["view"] is None ):
                return result
            elif "view" not in cmp1resp["data"]["city"] or cmp1resp["data"]["city"]["view"] is None:
                result="%s: no view"%kCmp1
                return result
            elif "view" not in cmp2resp["data"]["city"] or cmp2resp["data"]["city"]["view"] is None :
                result="%s: no view"%kCmp2
                return result
            cmp1_view=cmp1resp["data"]["city"]["view"]
            cmp2_view=cmp2resp["data"]["city"]["view"]
            print "before CmpView"
            result=self.__CmpView(cmp1_view,cmp2_view,-1)
            return result


