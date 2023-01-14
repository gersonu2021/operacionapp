#!/usr/bin/python
# -*- encoding: utf-8 -*-
import sys
reload(sys)    # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')

import os
import time
from flask import Blueprint, Flask, redirect, url_for, request, render_template, session, Response, g
import json
import urllib2
from settings.config import *
from settings.models import models
from modules.sessions import Sessions
from pprint import pprint

ajax_blueprint = Blueprint('ajax_blueprint', __name__,
                        template_folder='templates')

@ajax_blueprint.route("/ajax/", methods=['GET', 'POST'])
@ajax_blueprint.route("/ajax/<option>", methods=['GET', 'POST'])
def ajax(option = None):
  # Validate
  if option == "validate":
    if request.args.get("type"):
      return str(request.args.get("type"))
    return "Validating"
  pprint (option)
  return render_template('ajax.html')

@ajax_blueprint.route("/ajax/cambiar_aseguradora/", methods=['GET', 'POST'])
def cambiar_aseguradora():
  db = g.db
  user = Sessions().user
  if user['admin']:
    if request.method == 'POST':
      #print request.values
      value = request.form['aseguradora']
      db.mod("UPDATE usuarios SET aseguradora = ?, empresa = ? WHERE id = ?", [int(value), int(value), int(user['id'])] )
  return render_template('ajax.html')

@ajax_blueprint.route("/ajax/enviar-certificado/<id>", methods=['GET', 'POST'])
def enviar_certificado():
  user = Sessions().user
  return render_template('ajax.html')
