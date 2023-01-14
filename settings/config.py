#!/usr/bin/python
# -*- encoding: utf-8 -*-
import os, time, locale
from flask import Flask, g
from datetime import datetime

######################
# LOCALE & TIME ZONE #
######################

#os.environ['TZ'] = 'America/Santiago'
#time.tzset()
#try:
#  locale.setlocale(locale.LC_TIME, "es_ES.utf8")
#except Exception:
#  try:
#    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
#  except Exception:
#    try:
#      locale.setlocale(locale.LC_TIME, "es_ES")
#    except Exception as exc:
#      print exc
localtime = time.strftime('%x %X')
now = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
now_time = datetime.now().strftime('%H:%M:%S')
now_date = datetime.now().strftime('%d-%m-%Y')

######################
# FLASK APP SETTINGS #
######################

APP_TITLE = "App"
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = BASE_DIR.replace("/settings", "")
UPLOAD_FOLDER = BASE_DIR + '/uploads'
app = Flask(__name__, static_folder = BASE_DIR + '/static', static_url_path='/static', template_folder = BASE_DIR + '/templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
if not os.path.exists(app.config['UPLOAD_FOLDER']):
  os.makedirs(app.config['UPLOAD_FOLDER'])
app.secret_key = 'XdkjiouwuiWEREWp_dllRtpsu474_dk843ksd_3454P' 
app.preferred_url_scheme = 'http' # Set http or https
#app.server_name = 'http://127.0.0.1:5000' # Use Absolute URLs instead of Relative URLs in static files

##############
# SMTP EMAIL #
##############

smtp_config = {
  'SMTPserver' : 'smtp.gmail.com:587',
  'sender' :     'rectificadora@cserrano.cl',
  'destination' : ['contacto@magna.cl'],
  'username' : "rectificadora@cserrano.cl",
  'password' : "P1stones$123",
  }

###############
# DEBUG & LOG #
###############

# Custom Logs
if not os.path.exists(BASE_DIR + '/logs'):
  os.makedirs(BASE_DIR + '/logs')
CUSTOM_LOG_FILE_SIZE_LIMIT = 100000000 # in bytes

# Logs Errors and Debug false: log to file. True: log to console and reload on changes.
LOG_ERRORS = True
app.config['DEBUG'] = LOG_ERRORS
app.debug = LOG_ERRORS
app.testing = LOG_ERRORS
app.use_reloader = LOG_ERRORS
app.threaded = True 

# DEBUGIN TO A FILE LOG (app.debug and app.testing must be false)
LOGS_FOLDER = BASE_DIR + "/logs"
if not app.debug:
  import logging
  logging.basicConfig(filename = LOGS_FOLDER + '/errors.log',level=logging.DEBUG)
  #logging.debug('Logging Start')
  logging.info(now)

# Console log display control
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR) # Log errors only
log.disabled = False

############
# DATABASE #
############

# SQLite
"""
if not os.path.exists(BASE_DIR + '/db'):
  os.makedirs(BASE_DIR + '/db')
sqlite_db = {
    'type' : 'sqlite3',
    'file' : BASE_DIR + '/db/db.sqlite'
    }
"""
# mySQL
mysql_db = {
    'type' : 'mysql',
    'db' : 'erpcserrano',
    'user' : 'root',
    'passwd' : '',
    'host' : 'localhost',
    'port' : 3006
    }
