#!/usr/bin/python
# -*- encoding: utf-8 -*-
import sys
import re
from hashlib import md5
import string
import random
from flask import request
from datetime import datetime, timedelta, date
from pprint import pprint

class Validate:
  def __init__(self):
    return
  
  #####################################
  # FORM FIELD VALIDATIONS OPERATIONS #
  #####################################

  # Esta funcion es para utilizarse en el momento de recibir un post para validar sus campos. Es necesario que el modelo esté correctamente declarado en models.py
  def post_required(self, model):
    try:
      for key, value in (request.form).iteritems():
        if key in model['defaults']['required'] and not value:
          raise ValueError('Empty Field')
        if key == 'dni' and key in model['defaults']['required']:
          if not self.dni(value):
            raise ValueError('wrong dni')
        if key == 'email' and key in model['defaults']['required']:
          if not self.email(value):
            raise ValueError('wrong email')
    except Exception as e:
      print 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno), e
      return False
    return True

  def email(self, email):
    # reference: http://emailregex.com
    #match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
    #if match == None:
    #  print('Bad Syntax')
    #  return False
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    if email_regex.match(email) :
      return True
    else:
      return False

  def percentage(self, percentage):
    # remove any character that isn't a number a comma or a dot
    percentage = re.sub('[^0-9|,|.]+', '', percentage)
    return percentage

  def csrf_protect():
    if request.method == "POST":
      token = session.pop('_csrf_token', None)
      if not token or token != request.form.get('_csrf_token'):
        abort(403)

  def dni(self, dni, chars = 6):
    """
    check = re.compile(r"(([X-Z]{1})([-]?)(\d{7})([-]?)([A-Z]{1}))|((\d{8})([-]?)([A-Z]{1}))")
    if check.match(dni):
      print "dni match"
    else:
      print "dni no math"
    """
    try:
      if not dni:
        return False
      if len(dni) < chars:
        return False
      # remove special characters
      dni = re.sub(r'[^\w]', ' ', dni)
      # remove any character that is not a letter or a number
      dni = re.sub('[^A-Za-z0-9]+', '', dni)
      return dni
    except Exception as e:
      print e
      return False

  ############
  # Security #
  ############

  def generate_csrf_token():
    if '_csrf_token' not in session:
      session['_csrf_token'] = os.urandom(24)
    return session['_csrf_token']

  def random_string(self, size=6, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))

  def md5_encode(self, string):
    encoded_string = md5(string).hexdigest()
    return encoded_string

  ###############
  # Date & Time #
  ###############

  # Convert from: date(Day, Month, Year) to date(Year, Month, Day) 
  def convert_date(self, date, indate = '%d-%m-%Y', outdate = '%Y-%m-%d'):
    # mysql format: %Y-%m-%d
    if date is None:
      return None
    try:
      # convert to normal string if unicode
      if isinstance(date, unicode):
        date = str(date)
      # convert to date if is a string
      if type(date) is str:
        date = datetime.strptime(date, indate)
      # convert date format
      date = date.strftime(outdate)
      return date
    except Exception as e:
      print e
      return None

  # Get days between to dates
  def days_between(self, start_day = date.today(), end_day = date.today() - timedelta(days=5) ):
    delta = start_day - end_day
    print delta
    total_days = []
    for i in range(delta.days + 1):
      total_days.append( end_day + timedelta(days=i) )
    days = {
        'start_day' : start_day,
        'end_day' : end_day,
        'total_days' : list(reversed(total_days))
        }
    return days

  # Get X days from now
  def back_in_time(self, start_day = date.today(), n_days = -20):
    end_day = start_day + timedelta(days=n_days)
    delta = start_day - end_day
    total_days = []
    for i in range(delta.days + 1):
      total_days.append( end_day + timedelta(days=i) )
    days = {
        'start_day' : start_day,
        'end_day' : end_day,
        'total_days' : list(reversed(total_days))
        }
    return days

  def format_currency(self, value, currency = 'clp'):
    if 'clp':
      return "${:,.0f}".format(value)
    else:
      return value
