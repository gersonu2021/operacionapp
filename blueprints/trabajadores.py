#!/usr/bin/python
# -*- encoding: utf-8 -*-
from flask import Blueprint, Flask, redirect, url_for, request, render_template, session, Response, g
from settings import models
from settings.config import *
from blueprints import defaults
from pprint import pprint
from datetime import datetime
import sys

#from modules.smtpsend import SmtpSend

model = models.maestros

now = datetime.now()

trabajadores = Blueprint('trabajadores', __name__, template_folder='templates')

@trabajadores.before_request
def check_login():
  from modules.sessions import Sessions
  if Sessions().user['tipo'] not in [1,2]:
    return render_template("errors.html", errors = ['No tienes suficientes permisos para entrar a esta sección.'])

@trabajadores.route('/trabajador/iniciar/<trabajo>', methods=['GET', 'POST'])
@trabajadores.route('/trabajador/iniciar/<trabajo>/<ot>/', methods=['GET', 'POST'])
def iniciar(trabajo = 0, ot = 0):
  try:
    maestro = session['maestro']
  except:
    #return render_template("errors.html", errors = ['Maestro no encontrado.'], href = url_for('trabajadores.main'))
    return redirect(url_for('trabajadores.salir' ))

  try:
    cola_de_trabajo = g.db.read(
      "SELECT GROUP_CONCAT(trabajo_orden_de_trabajo SEPARATOR ',') AS trabajos FROM cola_de_trabajos "
      "WHERE trabajo IN (SELECT trabajo FROM asignacion_de_maestros_trabajos WHERE maestro = ?) "
      ,[ maestro['id'] ]
    )
    if not cola_de_trabajo:
      raise ValueError('No se encuentra la cola de trabajos')

    trabajos = str(cola_de_trabajo[0]['trabajos'])
    if not trabajos:
      raise ValueError('No hay trabajos')

    g.db.mod("UPDATE trabajos_orden_de_trabajo "
    "SET fecha_inicio = CURRENT_TIMESTAMP, maestro = ? "
    "WHERE id = ? "
    "AND fecha_termino IS NULL "
    "AND maestro IS NULL "
    "AND id IN (" + trabajos + ") "
    ,[ maestro['id'], int(trabajo) ]
    )
    check = g.db.read("SELECT id FROM trabajos_orden_de_trabajo WHERE fecha_inicio IS NOT NULL AND maestro = ? AND id = ?", [ maestro['id'], int(trabajo) ] )
    print check
    if check:
      g.db.mod("UPDATE cola_de_trabajos SET maestro = ? WHERE trabajo_orden_de_trabajo = ?", [ maestro['id'], int(trabajo) ] )
    print 'Updated'
  except Exception as e:
    print 'Error on line {} '.format(sys.exc_info()[-1].tb_lineno), e

  if int(ot):
    return redirect(url_for('trabajadores.main', orden_de_trabajo = ot ))
  else:
    return redirect(url_for('trabajadores.main' ))
    return render_template("errors.html", errors = ['OT no encontrada.'], href = url_for('trabajadores.main'))

@trabajadores.route('/trabajador/terminar/<trabajo>', methods=['GET', 'POST'])
@trabajadores.route('/trabajador/terminar/<trabajo>/<ot>/', methods=['GET', 'POST'])
def terminar(trabajo = 0, ot = 0):
  try:
    maestro = session['maestro']
  except:
    return render_template("errors.html", errors = ['Maestro no encontrado.'], href = url_for('trabajadores.main'))

  try:
    cola_de_trabajo = g.db.read(
      "SELECT GROUP_CONCAT(trabajo_orden_de_trabajo SEPARATOR ',') AS trabajos FROM cola_de_trabajos "
      "WHERE trabajo IN (SELECT trabajo FROM asignacion_de_maestros_trabajos WHERE maestro = ?) "
      ,[ maestro['id'] ]
    )

    if not cola_de_trabajo:
      raise ValueError('No se encuentra la cola de trabajos')

    trabajos = str(cola_de_trabajo[0]['trabajos'])
    if not trabajos:
      raise ValueError('No hay trabajos')

    g.db.mod("UPDATE trabajos_orden_de_trabajo "
    "SET fecha_termino = CURRENT_TIMESTAMP "
    "WHERE maestro = ? "
    "AND id = ? "
    "AND fecha_inicio IS NOT NULL "
    "AND fecha_termino IS NULL "
    "AND id IN (" + trabajos + ") "
    ,[ maestro['id'], int(trabajo) ]
    )
    check = g.db.read("SELECT id FROM trabajos_orden_de_trabajo WHERE fecha_inicio IS NOT NULL AND fecha_termino IS NOT NULL AND maestro = ? AND id = ?", [ maestro['id'], int(trabajo) ] )
    if check:
      g.db.mod("DELETE FROM cola_de_trabajos WHERE maestro = ? AND trabajo_orden_de_trabajo = ?", [ maestro['id'], int(trabajo) ] )
  except Exception as e:
    print 'Error on line {} '.format(sys.exc_info()[-1].tb_lineno), e
    return render_template("errors.html", errors = ['Ha ocurrido un error.'], href = url_for('trabajadores.main'))

  if int(ot):
    return redirect(url_for('trabajadores.main', orden_de_trabajo = ot ))
  else:
    return redirect(url_for('trabajadores.main' ))

@trabajadores.route('/trabajador/salir/', methods=['GET', 'POST'])
def salir():
  session['maestro'] = []
  return redirect(url_for('trabajadores.main' ))

@trabajadores.route('/trabajador/', methods=['GET', 'POST'])
@trabajadores.route('/trabajador/orden_de_trabajo/<orden_de_trabajo>/', methods=['GET', 'POST'])
def main(orden_de_trabajo = None):
  #return render_template("errors.html", errors = ['En construcción.'])
  #data = g.db.read("SELECT * FROM " + model['table'])
  #data = g.db.d_read(model)

  if request.method == 'POST':
    try:
      id_maestro = int(request.form['id_maestro'])
      maestro = g.db.read("SELECT * FROM maestros WHERE id = ? AND estado", [ id_maestro  ])
      if not maestro:
        raise ValueError('Maestro no encontrado')
      if maestro:
        session['maestro'] = maestro[0]
    except Exception as e:
      print 'Error on line {} '.format(sys.exc_info()[-1].tb_lineno), e
      return render_template("errors.html", errors = ['El número de usuario ingresado no es válido.'])

  try:
    maestro = session['maestro']
  except:
    maestro = None

  #if not maestro:
  #  return 'Maestro no existe'

  if maestro:

    trabajos_maestro = g.db.read("SELECT GROUP_CONCAT(trabajo SEPARATOR ',') AS trabajos FROM asignacion_de_maestros_trabajos WHERE maestro = ?", [ maestro['id'] ] )
    if not trabajos_maestro:
      return render_template("errors.html", errors = ['No tienes trabajos asignados.'])

    # Seleccion de orden de trabajo por parte del maestro. Culatas 1 y Block 3
    try:
      culatas = g.db.read("SELECT categoria FROM trabajos WHERE id IN (" + str(trabajos_maestro[0]['trabajos']) + ") "
          "AND categoria = 1 "
          )
      block = g.db.read("SELECT categoria FROM trabajos WHERE id IN (" + str(trabajos_maestro[0]['trabajos']) + ") "
          "AND categoria = 3 "
          )
    except:
      culatas = None
      block = None

    especial_categoria = []
    if culatas and not orden_de_trabajo:
      #cola_de_trabajos = g.db.read("SELECT * FROM cola_de_trabajos WHERE categoria_trabajo = 1 GROUP BY orden_de_trabajo ")
      #especial_categoria = 1
      especial_categoria.append(1)
    if block and not orden_de_trabajo:
      #especial_categoria = 3
      especial_categoria.append(3)

    if especial_categoria:
      especial_categoria = ','.join(str(e) for e in especial_categoria)
      parameters = []
      query = "SELECT * FROM cola_de_trabajos "
      query += "WHERE categoria_trabajo IN (%s) " % (especial_categoria)
      #parameters.append(especial_categoria)
      query += "AND trabajo IN (SELECT trabajo FROM asignacion_de_maestros_trabajos WHERE maestro = ?) "
      parameters.append(maestro['id'])
      query += "GROUP BY orden_de_trabajo "
      cola_de_trabajos = g.db.read(query, parameters)
      return render_template(
        "trabajadores.html", 
        section = 'seleccion_ot',
        maestro = maestro,
        cola_de_trabajos = cola_de_trabajos
      )
    
    # Obtiene trabajos en curso
    if orden_de_trabajo:
      cola_de_trabajo = g.db.read("SELECT * FROM cola_de_trabajos WHERE orden_de_trabajo = ?", [ orden_de_trabajo ])
    else:
      cola_de_trabajo = g.db.read("SELECT * FROM cola_de_trabajos WHERE maestro = ? LIMIT 1", [ maestro['id'] ])

    # Si no hay trabajo en curso, toma el trabajo siguiente por prioridad y por orden de OT
    if not cola_de_trabajo:
      parameters = []
      query = "SELECT * FROM cola_de_trabajos "
      query += "WHERE NOT maestro "
      query += "AND trabajo IN (SELECT trabajo FROM asignacion_de_maestros_trabajos WHERE maestro = ?) "
      parameters.append( maestro['id'] )
      if orden_de_trabajo:
        query += "AND orden_de_trabajo = ? "
        parameters.append( orden_de_trabajo )
      query += "ORDER BY prioridad DESC, id ASC LIMIT 1 "
        
      cola_de_trabajo = g.db.read(query, parameters)

    if not cola_de_trabajo:
      return render_template("success.html", messages = ['No hay trabajos en cola.'], href = url_for('trabajadores.salir'))

    ot = g.db.read("SELECT * FROM ordenes_de_trabajo WHERE id = ?",
        [ cola_de_trabajo[0]['orden_de_trabajo'] ] )

    if not ot:
      return render_template("errors.html", errors = ['Ha ocurrido un error.'])

    trabajos = g.db.read(
      "SELECT GROUP_CONCAT(trabajo_orden_de_trabajo SEPARATOR ',') AS ids "
      "FROM cola_de_trabajos "
      "WHERE orden_de_trabajo = ? "
      "AND trabajo IN (SELECT trabajo FROM asignacion_de_maestros_trabajos WHERE maestro = ?) ",
      #"AND NOT maestro ", 
      [ ot[0]['id'], maestro['id'] ] 
      )

    if not trabajos[0]['ids'] and ot:
      #return 'No hay trabajos asignados'
      return redirect(url_for('trabajadores.main'))

    trabajos = g.db.read(
      "SELECT trabajos.categoria, trabajos.nombre, categorias_trabajos.nombre, "
      "trabajos_orden_de_trabajo.*, maestros.nombre "
      "FROM trabajos_orden_de_trabajo "
      "LEFT JOIN trabajos "
      "ON trabajos.id = trabajos_orden_de_trabajo.trabajo "
      "LEFT JOIN categorias_trabajos "
      "ON trabajos.categoria = categorias_trabajos.id "
      "LEFT JOIN maestros "
      "ON trabajos_orden_de_trabajo.maestro = maestros.id "
      "AND trabajos_orden_de_trabajo.orden_de_trabajo = ? "
      "WHERE trabajos_orden_de_trabajo.id IN (" + str(trabajos[0]['ids']) + ") ",
      [ ot[0]['id'] ] 
    )

    categorias = []
    for trabajo in trabajos:
      if str(trabajo['categoria']) not in categorias:
        categorias.append(str(trabajo['categoria']))

    categorias_trabajos = g.db.read("SELECT id, nombre, color FROM categorias_trabajos WHERE id IN (" + ','.join(categorias) + ")")

    data = []
    for categoria in categorias_trabajos:
      tmp = []
      for trabajo in trabajos:
        if trabajo['categoria'] == categoria['id']:
          tmp.append(trabajo)
      data.append({
        'categoria' : categoria,
        'trabajos' : tmp
        })

    if orden_de_trabajo:
      ot  = orden_de_trabajo
    else:
      ot = 0
    
    return render_template(
      "trabajadores.html", 
      section = 'ot',
      data = data,
      maestro = maestro,
      ot = ot
    )

  return render_template("trabajadores.html", section = 'main')
