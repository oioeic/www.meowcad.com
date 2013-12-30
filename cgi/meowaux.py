#!/usr/bin/python

import re
import sys
import os
import redis
import hashlib
import uuid


def slurp_file(fn):
  f = open(fn, "r")
  s = f.read()
  f.close()
  return s

def getCookieHash( environ ):
  cookie_hash = {}
  if 'HTTP_COOKIE' in environ:
    cookies_str = os.environ['HTTP_COOKIE']
    cookies = cookies_str.split('; ')

    for cookie in cookies:
      c = cookie.split('=')
      cookie_hash[ c[0] ] = c[1]

  return cookie_hash


def userIndicatorString( userId, userName ):
  userIndicator = "<b><a href='usersettings' >" # ?userId=" + str(userId) + "'> "
  userIndicator += "[" + str(userName) + "] </a> </b> "
  userIndicator += " &nbsp; &nbsp; <a href='logout'>Logout</a> "
  return userIndicator

def errorMessage( msg ):
  return "<div id='message' class='error-message' >" + str(msg) + "</div>"

def successMessage( msg ):
  return "<div id='message' class='success-message'>" + str(msg) + "</div>"

def warningMessage( msg ):
  return "<div id='message' class='warning-message'>" + str(msg) + "</div>"

def statusMessage( msg ):
  return "<div id='message' class='status-message'>" + str(msg) + "</div>"

def nominalMessage( msg ):
  return "<div id='message' class='nominal-message'>" + str(msg) + "</div>"

# landing place so wanrings don't move all content below it
#
def message( msg ):
  return "<div id='message' class='no-message'>" + str(msg) + "</div>"


def authenticateSession( userId, sessionId ):
  db = redis.Redis()

  hashSessionId = hashlib.sha512( str(userId) + str(sessionId) ).hexdigest()

  if not db.sismember( "sesspool", hashSessionId ):
    return 0

  sessionDat = db.hgetall( "session:" + str(hashSessionId) )
  userDat = db.hgetall( "user:" + str(userId) )

  if ( ("userName" not in userDat) or
       ("userId" not in sessionDat) or
      (sessionDat["userId"] != userId) ):
    return 0;

  return 1

def getUser( userId ):
  db = redis.Redis()
  return db.hgetall( "user:" + str(userId) )

def setUserPassword( userId, password ):
  db = redis.Redis()
  hashPassword = hashlib.sha512( str(userId) + str(password) ).hexdigest()
  return db.hset( "user:" + str(userId), "passwordHash", hashPassword )

def createProject( userId, projectName, permission ):
  db = redis.Redis()

  proj = {}
  proj["id"] = str(uuid.uuid4())
  proj["userId"] = str(userId)
  proj["name"] = str(projectName)
  proj["sch"] = "default"
  proj["brd"] = "default"
  proj["active"] = "1"
  if str(permission) == "world-read":
    proj["permission"] = "world-read"
  else:
    proj["permission"] = "user"
  if not db.hmset( "project:" + proj["id"], proj ):
    return None

  db.rpush( "olio:" + str(userId), proj["id"] )
  
  return proj

def updateProjectPermission( userId, projectId, perm ):
  db = redis.Redis()

  p = "none"
  if perm == "world-read":
    p = "world-read"
  elif perm == "user":
    p = "user"

  proj = db.hgetall( "project:" + str(projectId) )

  if not proj:
    return None
  if proj["userId"] != str(userId):
    return None

  return db.hset( "project:" + str(projectId), "permission", p )


def getProject( projectId ):
  db = redis.Redis()
  return db.hgetall( "project:" + str(projectId) )


def deleteProject( userId, projectId ):
  db = redis.Redis()

  proj = db.hgetall( "project:" + str(projectId) )
  if not proj:
    return None

  if proj["userId"] != str(userId):
    return None

  return db.hset( "project:" + str(projectId), "active", "0" )



def getPortfolio( userId ):
  db = redis.Redis()
  return db.lrange( "olio:" + str(userId), 0, -1 )

def getPortfolios( userId ):
  db = redis.Redis()

  olios = []
  #olios = {}
  olioList = db.lrange( "olio:" + str(userId), 0, -1 )

  

  for projectId in olioList:
    proj = getProject( projectId )
    if ("active" in proj) and (str(proj["active"]) == "1"):
      olios.append( proj )
    #olios[str(projectId)] = getProject(projectId)

  return olios



def getSessions():
  db = redis.Redis()
  return db.smembers( "sesspool" )

def deactivateSession( userId, sessionId ):
  db = redis.Redis()

  hashSessionId = hashlib.sha512( str(userId) + str(sessionId) ).hexdigest()
  db.srem( "sesspool", str(hashSessionId) )
  x = db.hgetall( "session:" + str(hashSessionId) )
  #if "active" not in x: return 0
  db.hset( "session:" + str(hashSessionId), "active", 0 )
  return 1







