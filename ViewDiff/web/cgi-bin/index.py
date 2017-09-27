#!/usr/local/bin//python
#-*-coding:UTF-8 -*-
import sys
#sys.path.append('/search/caoxiaolan/linshi/ViewDiff/Cmp')
sys.path.append('../')
from DBHandle import DBHandle
import cgi,cgitb
reload(sys);
exec("sys.setdefaultencoding('utf-8')");

form =cgi.FieldStorage()
qid=form.getvalue('qid')
env=form.getvalue('env')
load=form.getvalue('load')
env_resp="%s_resp"%env
conn=DBHandle('10.10.169.10','root','','test')
if load=="resp":
    sqlstr="select %s_resp from all_about where %s_qid=%s;"%(env,env,qid)
    resp=conn.do(sqlstr)
    result=resp[0][env_resp]
else:
    sqlstr="select ori_req from all_about where ori_qid=%s"%(qid)
    req=conn.do(sqlstr)
    result=req[0]["ori_req"]
print """Content-type:text/html\r\n\r\n<html>
	<head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	</head>
	<body>
	    %s
	</body>
</html>"""%result
