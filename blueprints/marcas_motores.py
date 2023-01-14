#!/usr/bin/python
# -*- encoding: utf-8 -*-
from flask import Blueprint, Flask, redirect, url_for, request, render_template, session, Response, g
from settings import models
from settings.config import *
from blueprints import defaults
from modules.validate import Validate

from pprint import pprint

model = models.marcas_motores

marcas_motores = Blueprint('marcas_motores', __name__, template_folder='templates')

@marcas_motores.before_request
def check_login():
  from modules.sessions import Sessions
  if Sessions().user['tipo'] != 1:
    return render_template("errors.html", errors = ['No tienes suficientes permisos para entrar a esta sección.'])

@marcas_motores.route('/marcas-motores/editar/<index>', methods=['GET', 'POST'])
def editar(index=None):
  return defaults.editar(index, model)

@marcas_motores.route('/marcas-motores/eliminar/<id>', methods=['GET', 'POST'])
def eliminar(id=None):
  return defaults.eliminar(id, model)

@marcas_motores.route('/marcas-motores/crear/', methods=['GET', 'POST'])
def crear(search_query = None):
  return defaults.crear(model)

@marcas_motores.route('/marcas-motores/', methods=['GET'])
def main():
  data = g.db.d_read(model)
  return render_template("default.html", model=model, data=data, settings = ['create', 'edit', 'delete'])

