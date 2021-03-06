#!/usr/bin/python

import re,cgi,cgitb,sys
import os
import urllib
import meowaux as mew
cgitb.enable()

cookie_hash = mew.getCookieHash( os.environ )

if ( ("userId" not in cookie_hash) or ("sessionId" not in cookie_hash)  or
         (mew.authenticateSession( cookie_hash["userId"], cookie_hash["sessionId"] ) == 0) ):
  print "Location:login"
  print
  sys.exit(0)

print "Content-Type: text/html;charset=utf-8"
print

userId = cookie_hash["userId"]
userData = mew.getUser( userId )
userName = userData["userName"]

form = cgi.FieldStorage()
if "foo" in form:
  foo_val = form["foo"].value


message = ""

template = mew.slurp_file("template/newproject.html")
tmp_str = template.replace("<!--USER-->", userName)
tmp_str = tmp_str.replace( "<!--LEFT-->", mew.slurp_file("template/left_template.html") )
tmp_str = tmp_str.replace( "<!--USERINDICATOR-->", mew.userIndicatorString( userId, userName ) )
tmp_str = tmp_str.replace("<!--MESSAGE-->", mew.message( message ) )

analytics = mew.slurp_file("template/analytics_template.html")
tmp_str = tmp_str.replace( "<!--ANALYTICS-->", analytics)




print tmp_str

