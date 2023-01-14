#!/usr/bin/python
# -*- encoding: utf-8 -*-
import sys
reload(sys)    # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')

###########
# IMPORTS #
###########

import os
import time
from flask import Flask, redirect, url_for, request, render_template, session, g
import json
import urllib2
from settings.config import *
from settings.models import models
from modules.sql import Sql
from settings.db_defaults import DB_defaults
from modules.sessions import Sessions
from settings.navigation import navigation
from pprint import pprint

##############
# BLUEPRINTS #
##############

from blueprints.ajax import ajax_blueprint
app.register_blueprint(ajax_blueprint)

from blueprints.login import login_blueprint
app.register_blueprint(login_blueprint)

from blueprints.user_settings import user_settings
app.register_blueprint(user_settings)

from blueprints.ordenes_de_trabajo import ordenes_de_trabajo
app.register_blueprint(ordenes_de_trabajo)

from blueprints.maestros import maestros
app.register_blueprint(maestros)

from blueprints.clientes import clientes
app.register_blueprint(clientes)

from blueprints.inventario import inventario
app.register_blueprint(inventario)

from blueprints.bodega_motores import bodega_motores
app.register_blueprint(bodega_motores)

from blueprints.trabajadores import trabajadores
app.register_blueprint(trabajadores)

from blueprints.marcas_motores import marcas_motores
app.register_blueprint(marcas_motores)

##################
# BEFORE REQUEST #
##################

@app.before_request
def check_login():
  # Database connection settings in config.py
  g.db = Sql(mysql_db)
  g.db.connect()
  g.models = models
  g.db.create_all(models)
  DB_defaults().insert_data(g.db)
  if not Sessions().user and request.path not in [
    '/login/', 
    '/login/recuperar-clave/',
    '/static/img/logo-cserrano.png',
    '/static/img/logo-aera.png'
  ]:
    return redirect(url_for('login_blueprint.login'))

#################
# AFTER REQUEST #
#################

@app.teardown_request
def teardown_request(exception):
  g.db.disconnect()
  return

###############################
# GLOBAL VARIABLES FOR JINJA2 #
###############################

@app.context_processor
def all_templates():
  user = Sessions().user
  #if not user:
  #  return redirect(url_for('login_blueprint.logout'))
  return dict(
    navigation = navigation,
    user = user, 
    APP_TITLE = APP_TITLE,
    now_date = now_date
    )

###############
# MAIN ROUTES #
###############

@app.route("/", methods=['GET', 'POST'])
def main():
  user = Sessions().user
  if user:
    if user['tipo'] == 1:
      return redirect(url_for('ordenes_de_trabajo.main'))
    elif user['tipo'] == 2:
      return redirect(url_for('trabajadores.main'))
    elif user['tipo'] == 3:
      return redirect(url_for('inventario.main'))
    elif user['tipo'] == 4:
      return redirect(url_for('bodega_motores.main'))
  #else:
  #    return redirect(url_for('login_blueprint.logout'))


#########################
# DEFAULT & ERROR PAGES #
#########################

@app.route("/en-construccion")
def en_construccion():
  return render_template('en_construccion.html')

@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
  return render_template('403.html'), 403

@app.errorhandler(500)
def internal_server_error(e):
  return render_template('500.html'), 500

@app.route('/logo-cserrano.png')
@app.route('/logo-aera.png')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

###########
# APP RUN #
###########

if __name__ == '__main__':
  app.run()
  #app.run(threaded=True)

