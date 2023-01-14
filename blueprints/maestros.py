#!/usr/bin/python
# -*- encoding: utf-8 -*-
from flask import Blueprint, Flask, redirect, url_for, request, render_template, session, Response, g
from settings import models
from settings.config import *
from blueprints import defaults
from pprint import pprint

from modules.smtpsend import SmtpSend

model = models.maestros

maestros = Blueprint('maestros', __name__, template_folder='templates')

@maestros.before_request
def check_login():
  from modules.sessions import Sessions
  if Sessions().user['tipo'] != 1:
    return render_template("errors.html", errors = ['No tienes suficientes permisos para entrar a esta sección.'])

@maestros.route('/maestros/seleccion-maestros/<id_trabajo>/', methods=['GET', 'POST'])
def seleccion_maestros(id_trabajo = None):
  if not id_trabajo:
    return render_template("errors.html", errors = ['No hay un trabajo seleccionado.'])

  if request.method == 'POST':
    try:
      ids = request.form.getlist('ids')
      if ids:
        ids = map(int, ids)
        insert = []
        for id in ids:
          insert.append([id, int(id_trabajo)])
        print insert
        g.db.mod("DELETE FROM asignacion_de_maestros_trabajos WHERE trabajo = ?", [ id_trabajo ] )
        g.db.mod("INSERT INTO asignacion_de_maestros_trabajos "
        "(maestro, trabajo) VALUES (?, ?)", 
        insert )
        return redirect(url_for('maestros.asignacion' ))
    except Exception as e:
      print e
      return render_template("errors.html", errors = ['Error de usuario.'], href = url_for('maestros.seleccion_maestros', id_trabajo = id_trabajo))

  trabajo = g.db.read( "SELECT * FROM trabajos WHERE id = ?", [ id_trabajo  ] )
  maestros = g.db.read("SELECT * FROM maestros WHERE estado")
  if not trabajo or not maestros:
    return render_template("errors.html", errors = ['Es necesario que seleccionar un trabajo y que exista al menos un maestro.'])
  maestros_asignados = g.db.read("SELECT maestro FROM asignacion_de_maestros_trabajos WHERE trabajo = ?", [ id_trabajo ] )
  if maestros_asignados:
    tmp = []
    for row in maestros_asignados:
      tmp.append(row['maestro'])
    for maestro in maestros:
      if maestro['id'] in tmp:
        maestro['asignado'] = 1
      else:
        maestro['asignado'] = 0

  data = {
    'trabajo' : trabajo[0],
    'maestros' : maestros
    }
  pprint(data)

  return render_template("maestros.html", section = 'seleccion-maestros', data = data)

@maestros.route('/maestros/asignacion/', methods=['GET', 'POST'])
def asignacion():
  categorias = g.db.read("SELECT * FROM categorias_trabajos")
  trabajos = g.db.read(
    "SELECT trabajos.id, trabajos.nombre, trabajos.categoria, "
    "GROUP_CONCAT(asignacion_de_maestros_trabajos.maestro SEPARATOR ', ') AS ids_maestros, "
    "GROUP_CONCAT(maestros.nombre SEPARATOR ', ') AS nombres_maestros "
    "FROM trabajos "
    "LEFT JOIN asignacion_de_maestros_trabajos "
    "ON trabajos.id = asignacion_de_maestros_trabajos.trabajo "
    "LEFT JOIN maestros "
    "ON maestros.id = asignacion_de_maestros_trabajos.maestro "
    "GROUP BY trabajos.id "
  )

  data = []
  for categoria in categorias:
    tmp = []
    for trabajo in trabajos:
      if trabajo['categoria'] == categoria['id']:
        tmp.append(trabajo)
    data.append({
      'categoria' : categoria,
      'trabajos' : tmp
      })

  return render_template("maestros.html", section = 'asignacion', data = data)

@maestros.route('/maestros/crear/', methods=['GET', 'POST'])
def crear(search_query = None):
  return defaults.crear(model)
  #return render_template("errors.html", errors = ['No tienes permisos suficienes para acceder a esta sección.'])

@maestros.route('/maestros/', methods=['GET'])
def main(search_query = None):
  #return render_template("errors.html", errors = ['En construcción.'])
  #data = g.db.read("SELECT * FROM " + model['table'])
  data = g.db.d_read(model)
  return render_template("maestros.html", data = data, model = model, section = 'main')
