#!/usr/bin/python
# -*- encoding: utf-8 -*-
import sys
from flask import Flask, session, render_template, g

class Sessions:
  user = aseguradora = empresa = permisos = None

  def __init__(self):
    self.db = g.db
    self.check_user()
    return

  def check_user(self):
    if 'user_id' in session:
      # USUARIO
      try:
        user = self.db.read("SELECT * FROM usuarios WHERE id = ?", [ str(session['user_id']) ] )
        self.user = user[0]
      except Exception, e:
        self.user = None
        print 'Sessions: Error on line {}'.format(sys.exc_info()[-1].tb_lineno), e
        session.clear()
        return False
      return False

  def logout_user(self):
    try:
      self.user = None
      session.clear()
    except Exception, exc:
      print exc
      return False
    return True

  # This method convert a Dictionary to an Object
  def convert(self, dictionary):
    for key, value in dictionary.iteritems():
      if isinstance(value, dict):
        dictionary[key] = self.convert(value) 
    return namedtuple('GenericDict', dictionary.keys())(**dictionary)
