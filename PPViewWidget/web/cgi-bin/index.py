#!/usr/local/bin//python
#-*-coding:UTF-8 -*-
from DBHandle import DBHandle
import cgi,cgitb
import sys

reload(sys);
exec("sys.setdefaultencoding('utf-8')");

form =cgi.FieldStorage()
qid=form.getvalue('qid')
env=form.getvalue('env')
env_resp="%s_resp"%env
conn=DBHandle('127.0.0.1','root','','test')
sqlstr="select %s_resp from all_about where %s_qid=%s;"%(env,env,qid)
result=conn.do(sqlstr)
resp=result[0][env_resp]
print """Content-type:text/html\r\n\r\n<html>
	<head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	</head>
	<body>
	    %s
	</body>
</html>"""%resp
