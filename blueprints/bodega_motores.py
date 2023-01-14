#!/usr/bin/python
# -*- encoding: utf-8 -*-
from flask import Blueprint, Flask, redirect, url_for, request, render_template, session, Response, g
from settings import models
from settings.config import *
from blueprints import defaults
from modules.validate import Validate
from pprint import pprint
import json

model = models.bodega_motores

bodega_motores = Blueprint('bodega_motores', __name__, template_folder='templates')

@bodega_motores.before_request
def check_login():
  from modules.sessions import Sessions
  if Sessions().user['tipo'] not in [1,4]:
    return render_template("errors.html", errors = ['No tienes suficientes permisos para entrar a esta sección.'])

@bodega_motores.route('/bodega-motores/editar/<index>/', methods=['GET', 'POST'])
def editar(index = None):
  return render_template( "errors.html", errors = ['Sección en construcción.'], href = url_for('bodega_motores.main') )

@bodega_motores.route('/bodega-motores/crear/', methods=['GET', 'POST'])
def crear():
  #return defaults.crear(model)
  if request.method == 'POST':
    try:
      id_orden_de_trabajo = int(request.form['presupuesto'])
      motor = str(request.form['motor'])
      fecha_ingreso = request.form['fecha_ingreso']
      observaciones = str(request.form['observaciones'])
    except Exception as e:
      print e
      return render_template( "errors.html", errors = ['Error de usuario.'], href = url_for('bodega_motores.crear') )
    presupuesto = g.db.read("SELECT id, fecha_creacion FROM ordenes_de_trabajo WHERE id = ?", [ id_orden_de_trabajo ] )
    if not presupuesto:
      return render_template(
        "errors.html", 
        errors = ['El presuesto ingresado no existe.'], 
        href = url_for('bodega_motores.crear')
      )
    try:
      fecha_ingreso = str(request.form['fecha_ingreso'])
      fecha_ingreso = datetime.strptime(fecha_ingreso, '%d-%m-%Y')
      g.db.mod("INSERT INTO bodega_motores (fecha_ingreso, presupuesto, motor, observaciones) "
          "VALUES (?, ?, ?, ? )", 
          [ fecha_ingreso, id_orden_de_trabajo, motor, observaciones   ] )
      return render_template("success.html", messages = ['Motor ingresado a bodega.'], href = url_for('bodega_motores.crear' ))
    except Exception as e:
      print e
      return render_template("errors.html", errors = ['Hay un error en los campos ingresados.'], href = url_for('bodega_motores.crear' ))

  return render_template("bodega_motores.html", 
      section = 'crear'
      )

@bodega_motores.route('/bodega-motores/', methods=['GET'])
@bodega_motores.route('/bodega-motores/search/<search_query>/', methods=['GET'])
def main(search_query = None):
  if search_query:
    #search_query = '%' + str(search_query) + '%'
    #data = g.db.read(str(query) + " WHERE presupuesto LIKE ? ", [ search_query ])
    try:
      data = g.db.read("SELECT bodega_motores.*, ordenes_de_trabajo.id, ordenes_de_trabajo.rut_cliente, ordenes_de_trabajo.fecha_creacion as fecha_ppto, clientes.* "
      "FROM bodega_motores "
      "LEFT JOIN ordenes_de_trabajo "
      "ON bodega_motores.presupuesto = ordenes_de_trabajo.id "
      "LEFT JOIN clientes "
      "ON ordenes_de_trabajo.rut_cliente = clientes.rut "
      "WHERE presupuesto = ? ", [ int(search_query) ] )
    except Exception as e:
      print e
      data = None
    if not data:
      return render_template( "errors.html", errors = ['No se ha encontrado ningún resultado.'], href = url_for('bodega_motores.main') )
  else:
    data = g.db.read("SELECT bodega_motores.*, ordenes_de_trabajo.id, ordenes_de_trabajo.rut_cliente, ordenes_de_trabajo.fecha_creacion as fecha_ppto, clientes.* "
  "FROM bodega_motores "
  "LEFT JOIN ordenes_de_trabajo "
  "ON bodega_motores.presupuesto = ordenes_de_trabajo.id "
  "LEFT JOIN clientes "
  "ON ordenes_de_trabajo.rut_cliente = clientes.rut "
  "ORDER BY bodega_motores.id DESC LIMIT 40 "
  )

  tbody = []
  table_data = {}
  for row in data:
    pprint(row)
    pprint(row['rut_cliente'])
    print row['presupuesto']
    tbody.append([ row['id'], row['razon_social'], row['rut_cliente'], row['telefono'], row['email'], row['fecha_ppto'], row['fecha_creacion'], row['presupuesto'], row['motor'], row['observaciones'] ])
    table_data = {
      'thead' : ['Razón Social', 'RUT', 'Teléfono', 'Email', 'Fecha PPTO', 'Fecha Ingreso', 'Presupuesto', 'Motor', 'Observaciones'],
      'tbody' : tbody
      }
  return render_template("bodega_motores.html", 
      table_data = table_data,
      section = 'main'
      )
