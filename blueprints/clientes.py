#!/usr/bin/python
# -*- encoding: utf-8 -*-
from flask import Blueprint, Flask, redirect, url_for, request, render_template, session, Response, g
from settings import models
from settings.config import *
from blueprints import defaults
from modules.validate import Validate

from pprint import pprint

model = models.clientes

clientes = Blueprint('clientes', __name__, template_folder='templates')

@clientes.before_request
def check_login():
  from modules.sessions import Sessions
  if Sessions().user['tipo'] != 1:
    return render_template("errors.html", errors = ['No tienes suficientes permisos para entrar a esta sección.'])

@clientes.route('/clientes/editar/<id>/', methods=['GET', 'POST'])
def editar(id = 0):
  cliente = g.db.read("SELECT * FROM clientes WHERE id = ?", [ int(id) ] )
  if not cliente:
    return render_template("errors.html", errors = ['Cliente no encontrado.'], href = url_for('clientes.main'))

  if request.method == 'POST':
    try:
      rut = Validate().dni(str(request.form['rut']))
      direccion = str(request.form['direccion'])
      razon_social = str(request.form['razon_social'])
      telefono = str(request.form['telefono'])
      email = str(request.form['email'])
      giro = str(request.form['giro'])
      if email:
        if not Validate().email(email):
          return render_template("errors.html", errors = ['Email inválido.'], href = url_for('clientes.main'))
        check = g.db.read("SELECT * FROM clientes WHERE id != ? AND email = ?", [ int(id), email ] )
        if check:
          return render_template("errors.html", errors = ['El correo ingresado esta en uso por otro cliente.'], href = url_for('clientes.main'))
      check = g.db.read("SELECT * FROM clientes WHERE id != ? AND rut = ?", [ int(id), rut ] )
      if check:
        return render_template("errors.html", errors = ['El RUT ingresado esta en uso por otro cliente.'], href = url_for('clientes.main'))
      giro = str(request.form['giro'])
      g.db.mod("UPDATE clientes SET rut = ?, direccion = ?, razon_social = ?, telefono = ?, email = ?, giro = ? WHERE id = ?", 
          [ rut, direccion, razon_social, telefono, email, giro, int(id) ] )
      return render_template("success.html", messages = ['Datos Guardados.'], href = url_for('clientes.main') )
    except Exception as e:
      print e
      return render_template("errors.html", errors = ['No se ha podido crear el cliente. Hay datos incorrectos.'], href = url_for('clientes.crear'))

  return render_template("clientes.html", section = 'editar', cliente = cliente[0])

@clientes.route('/clientes/crear/', methods=['GET', 'POST'])
def crear(search_query = None):
  if request.method == 'POST':
    try:
      rut = Validate().dni(str(request.form['rut']))
      direccion = str(request.form['direccion'])
      razon_social = str(request.form['razon_social'])
      telefono = str(request.form['telefono'])
      email = str(request.form['email'])
      giro = str(request.form['giro'])
      observaciones = str(request.form['observaciones'])
      if email:
        if not Validate().email(email):
          raise ValueError('Email incorrecto')
      if not rut or not telefono or not razon_social:
        raise ValueError('Datos requeridos incompletos')
    except Exception as e:
      print e
      return render_template("errors.html", errors = ['No se ha podido crear el cliente. Hay datos incorrectos.'], href = url_for('clientes.crear'))
    cliente = g.db.read("SELECT id FROM clientes WHERE rut = ?", [ rut ] )
    if cliente:
      return render_template("errors.html", errors = ['El RUT ingresado ya existe en la base de datos.'])
    if email:
      check = g.db.read("SELECT * FROM clientes WHERE email = ?", [ email ] )
      if check:
        return render_template("errors.html", errors = ['El correo ingresado esta en uso por otro cliente.'], href = url_for('clientes.main'))
    g.db.mod("INSERT INTO clientes (rut, direccion, razon_social, telefono, email, giro, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?)", 
        [rut, direccion, razon_social, telefono, email, giro, observaciones] )
    return render_template("success.html", messages = ['Cliente creado correctamente.'], href = url_for('clientes.main') )
  return render_template("clientes.html", section="crear")

  #return defaults.crear(model)

@clientes.route('/clientes/', methods=['GET'])
def main(search_query = None):
  #data = g.db.read("SELECT razon_social, rut, direccion, email, giro FROM clientes")
  #tbody = []
  #for row in data:
  #  tbody.append([row['razon_social'], row['rut'], row['direccion'], row['email'], row['giro']])
  #table = {
  #    'thead' : ['Nombre o Razon Social', 'RUT', 'Dirección', 'Email', 'Giro'],
  #    'tbody' : tbody
  #    }
  #return render_template("clientes.html", section = 'main', table = table)

  print request.url_root

  data = g.db.d_read(model)
  return render_template("default.html", model=model, data=data, settings = ['create', 'edit'])

